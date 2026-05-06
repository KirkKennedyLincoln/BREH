import os
import json
import time
import concurrent.futures
import grpc # type: ignore

from tools import ScalingPredictorTool, build_step_tools
from tools.scaling_log import log_decision

try:
    from tools.docker_metrics import DockerMetricsSource
except ImportError:
    DockerMetricsSource = None  # type: ignore[assignment,misc]

from gen.python import storage_pb2, storage_pb2_grpc, runner_pb2, runner_pb2_grpc

class ExecutorAgent:
    def __init__(
        self,
        storage_addr: str = "localhost:50054",
        runner_addr: str = "localhost:50055",
        image_name: str = "synthesis-agent:latest",
        models_dir: str = "models",
        weight_threshold: float = 0.85,
        name_prefix: str = "makakasiguro",
    ):
        channel = grpc.insecure_channel(storage_addr)
        runner_channel = grpc.insecure_channel(runner_addr)
        self.stub = storage_pb2_grpc.GraphStoreStub(channel)
        self.runner = runner_pb2_grpc.RunnerStub(runner_channel)
        self.tools = build_step_tools(models_dir=models_dir)
        self.scaler: ScalingPredictorTool = self.tools["scaling_predictor"]
        self.image_name = image_name
        self.weight_threshold = weight_threshold
        self.trace: list[dict] = []
        self.metrics = DockerMetricsSource() if DockerMetricsSource is not None else None

    def fetch_graph(self, graph_id):
        res = self.stub.Get(request=storage_pb2.GetRequest(id=graph_id))

        # success == false
        if not res.graph.id:
            return None
        return json.loads(res.graph.data)

    def delete_graph(self, graph_id):
        return self.stub.Delete(storage_pb2.DeleteRequest(id=graph_id)).success

    def update_graph(self, graph_id, data):
        graph = storage_pb2.Graph(id=graph_id, data=json.dumps(data), created_at=int(time.time()))
        return self.stub.Put(storage_pb2.PutRequest(graph=graph)).success

    def list_graphs(self, prefix=""):
        return self.stub.List(storage_pb2.ListRequest(prefix=prefix)).ids

    def should_spawn(self, step):
        prediction = step.get("prediction", None)
        if prediction is not None:
            return bool(prediction)
        if step["tool"] == "scaling_predictor":
            pred = self.scaler.forward(**step["args"])
            step["prediction"] = pred
            return bool(pred.get("scale_up", False))
        return step.get("weight", 0.0) >= 0.5
    
    def resolve_metrics(self, step: dict) -> None:
        if step["tool"] != "scaling_predictor" or self.metrics is None:
            return
        try:
            step.setdefault("args", {})["metrics"] = self.metrics.as_features()
        except Exception:
            pass

    def run_step_in_container(self, graph_id: str, step: dict) -> dict:
        step_id = step.get("id", None)

        env = [
            "STORAGE_ADDR=host.docker.internal:50054",
            f"GRAPH_ID={graph_id}",
            f"STEP_ID={step_id}",
        ]
        live = (step.get("args") or {}).get("metrics")
        if step["tool"] == "scaling_predictor" and isinstance(live, dict):
            env.append(f"STEP_METRICS_JSON={json.dumps(live)}")

        spawn = self.runner.Spawn(
            runner_pb2.SpawnRequest(
                env=env,
                image_name=self.image_name,
            )
        )
        self.runner.Wait(runner_pb2.WaitRequest(id=spawn.id))

        id_slug = f"{graph_id}:results:{step_id}"
        result = self.stub.Get(storage_pb2.GetRequest(id=id_slug))
        try:
            self.runner.Kill(runner_pb2.KillRequest(id=spawn.id))
        except Exception:
            pass
        if not result.graph.id:
            return {"error": "container produced no result", "key": id_slug}
        return json.loads(result.graph.data)

    def execute(self, graph_id, max_workers=8):
        graph = self.fetch_graph(graph_id=graph_id)
        if graph is None:
            return []

        is_runner = bool(os.getenv("RUNNER_ADDR"))
        id_to_step = {s["id"]: s for s in graph["steps"]}
        in_degrees = {sid: 0 for sid in id_to_step}
        successors = {sid: [] for sid in id_to_step}
        for s in graph["steps"]:
            for dep in s.get("depends_on") or []:
                if dep in id_to_step:
                    in_degrees[s["id"]] += 1
                    successors[dep].append(s["id"])

        def run_one(step: dict) -> dict | None:
            if step["weight"] < self.weight_threshold:
                self.trace.append({
                    "step_id": step["id"], "tool": step["tool"],
                    "weight": step["weight"], "location": "skipped",
                    "duration_s": 0.0,
                })
                return None

            t0 = time.monotonic()
            self.resolve_metrics(step=step)
            if is_runner and self.should_spawn(step=step):
                output, location = self.run_step_in_container(graph_id=graph_id, step=step), "container"
            else:
                output, location = self.tools[step["tool"]].forward(**step["args"]), "inline"

            if step["tool"] == "scaling_predictor" and isinstance(output, dict):
                log_decision(
                    source="executor",
                    features=(step.get("args") or {}).get("metrics"),
                    decision=output,
                    context={
                        "graph_id": graph_id,
                        "step_id": step["id"],
                        "location": location,
                        "weight": step["weight"],
                    },
                )
            self.trace.append({
                "step_id": step["id"], "tool": step["tool"],
                "weight": step["weight"], "location": location,
                "duration_s": round(time.monotonic() - t0, 3),
            })
            return {
                "id": step["id"], "tool": step["tool"],
                "weight": step["weight"], "location": location,
                "output": output,
            }

        ready = [sid for sid, d in in_degrees.items() if d == 0]
        in_flight: dict = {}
        results: list = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            while ready or in_flight:
                # dispatch everything currently ready
                for sid in ready:
                    fut = pool.submit(run_one, id_to_step[sid])
                    in_flight[fut] = sid
                ready = []

                # advance as soon as ANY step finishes (not the whole batch)
                done, _ = concurrent.futures.wait(
                    in_flight.keys(),
                    return_when=concurrent.futures.FIRST_COMPLETED,
                )
                for fut in done:
                    sid = in_flight.pop(fut)
                    step = id_to_step[sid]
                    try:
                        r = fut.result()
                    except Exception as e:
                        self.trace.append({
                            "step_id": sid, "tool": step.get("tool", "?"),
                            "weight": step.get("weight", 0.0), "location": "error",
                            "duration_s": 0.0,
                        })
                        results.append({
                            "id": sid, "tool": step.get("tool", "?"),
                            "weight": step.get("weight", 0.0),
                            "location": "error",
                            "output": {"error": f"{type(e).__name__}: {e}"},
                        })
                    else:
                        if r is not None:
                            results.append(r)

                    # advance the frontier for THIS step's successors only
                    for nxt in successors.get(sid, []):
                        in_degrees[nxt] -= 1
                        if in_degrees[nxt] == 0:
                            ready.append(nxt)

        results.sort(key=lambda r: r["weight"], reverse=True)
        return results
