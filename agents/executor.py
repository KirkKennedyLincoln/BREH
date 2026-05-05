import os
import json
import time
import concurrent.futures
import grpc

from tools import ScalingPredictorTool, build_step_tools
from gen.python import storage_pb2, storage_pb2_grpc, runner_pb2, runner_pb2_grpc


class ExecutorAgent:
    def __init__(
        self,
        storage_addr: str = "localhost:50054",
        runner_addr: str = "localhost:50055",
        image_name: str = "synthesis-agent:latest",
        models_dir: str = "models",
        weight_threshold: float = 0.0,
    ):
        self.channel = grpc.insecure_channel(storage_addr)
        self.runner_channel = grpc.insecure_channel(runner_addr)
        self.stub = storage_pb2_grpc.GraphStoreStub(self.channel)
        self.runner = runner_pb2_grpc.RunnerStub(self.runner_channel)
        self.tools = build_step_tools(models_dir=models_dir)
        self.scaler: ScalingPredictorTool = self.tools["scaling_predictor"]
        self.image_name = image_name
        self.weight_threshold = weight_threshold
        self.trace: list[dict] = []  # one entry per step (executed or skipped)

    def fetch_graph(self, graph_id: str) -> dict | None:
        resp = self.stub.Get(storage_pb2.GetRequest(id=graph_id))
        if not resp.graph.id:
            return None
        return json.loads(resp.graph.data)

    def delete_graph(self, graph_id: str) -> bool:
        return self.stub.Delete(storage_pb2.DeleteRequest(id=graph_id)).success

    def update_graph(self, graph_id: str, data: dict) -> bool:
        graph = storage_pb2.Graph(
            id=graph_id,
            data=json.dumps(data),
            created_at=int(time.time()),
        )
        return self.stub.Put(storage_pb2.PutRequest(graph=graph)).success

    @staticmethod
    def _topo_sort(steps: list) -> list:
        """Topo-sort tolerating a few common LLM hallucinations:
          - depends_on references a step id that doesn't exist in this graph
          - depends_on contains the step's own id (self-loop)
          - depends_on contains duplicates
        Bad refs are dropped with a warning; the rest of the DAG still runs.
        """
        by_id = {s["id"]: s for s in steps}
        visited: set[str] = set()
        on_stack: set[str] = set()
        order: list = []

        def visit(sid: str):
            if sid in visited:
                return
            if sid not in by_id:
                # Hallucinated reference — skip silently after warning.
                print(f"  [warn] depends_on references unknown step '{sid}'; skipping")
                return
            if sid in on_stack:
                # Cycle detected (e.g. s1 depends on s2 depends on s1).
                print(f"  [warn] cycle detected at step '{sid}'; breaking")
                return
            on_stack.add(sid)
            for dep in by_id[sid].get("depends_on") or []:
                visit(dep)
            on_stack.discard(sid)
            visited.add(sid)
            order.append(by_id[sid])

        for s in steps:
            visit(s["id"])
        return order

    def _run_step_in_container(self, graph_id: str, step: dict) -> dict:
        """Spawn an agent container for one step, wait for it, then fetch the
        result the container wrote back to etcd under
        '{graph_id}:results:{step_id}'."""
        env = [
            # The container talks to the host's storage server; on Mac Docker
            # this is reachable as host.docker.internal.
            "STORAGE_ADDR=host.docker.internal:50054",
            f"GRAPH_ID={graph_id}",
            f"STEP_ID={step['id']}",
        ]
        # Don't pass cmd — the image's ENTRYPOINT (`python agent_entrypoint.py`)
        # is already correct. Setting cmd here would append to ENTRYPOINT and
        # produce `python agent_entrypoint.py python agent_entrypoint.py`.
        spawn_resp = self.runner.Spawn(runner_pb2.SpawnRequest(
            env=env, image_name=self.image_name,
        ))
        self.runner.Wait(runner_pb2.WaitRequest(id=spawn_resp.id))

        result_key = f"{graph_id}:results:{step['id']}"
        resp = self.stub.Get(storage_pb2.GetRequest(id=result_key))
        if not resp.graph.id:
            return {"error": "container produced no result", "key": result_key}
        return json.loads(resp.graph.data)

    def _should_spawn(self, step: dict) -> bool:
        """Container-allocation router. The trained scaler decides for steps
        that carry workload metrics in their args (i.e. scaling_predictor
        steps). For other tools we fall back to a simple weight heuristic —
        spawn for high-confidence work, run inline for the rest."""
        if step["tool"] == "scaling_predictor":
            try:
                decision = self.scaler.forward(**step["args"])
                return bool(decision.get("scale_up"))
            except Exception:
                pass
        return step.get("weight", 0.0) >= 0.5

    def execute(self, graph_id: str, max_workers: int = 8) -> list:
        """Walk the DAG layer-by-layer, firing all in-degree-zero steps in
        parallel via a thread pool. gRPC sync stubs and list.append are both
        thread-safe under CPython's GIL, so no extra locking needed.
        Skipped (below-threshold) steps still unblock their successors."""
        graph = self.fetch_graph(graph_id)
        if graph is None:
            return []

        runner_available = bool(os.getenv("RUNNER_ADDR"))
        by_id = {s["id"]: s for s in graph["steps"]}
        in_deg: dict[str, int] = {sid: 0 for sid in by_id}
        succ: dict[str, list[str]] = {sid: [] for sid in by_id}
        for s in graph["steps"]:
            for dep in s.get("depends_on") or []:
                if dep in by_id:
                    in_deg[s["id"]] += 1
                    succ[dep].append(s["id"])

        def run_one(step: dict) -> dict | None:
            if step["weight"] < self.weight_threshold:
                self.trace.append({
                    "step_id": step["id"], "tool": step["tool"],
                    "weight": step["weight"], "location": "skipped",
                    "duration_s": 0.0,
                })
                return None
            t0 = time.monotonic()
            if runner_available and self._should_spawn(step):
                output, location = self._run_step_in_container(graph_id, step), "container"
            else:
                output, location = self.tools[step["tool"]].forward(**step["args"]), "inline"
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

        frontier = [sid for sid, d in in_deg.items() if d == 0]
        results: list = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            while frontier:
                futs = {pool.submit(run_one, by_id[sid]): sid for sid in frontier}
                done_ids = []
                for fut in concurrent.futures.as_completed(futs):
                    sid = futs[fut]
                    done_ids.append(sid)  # advance the frontier even on error
                    try:
                        r = fut.result()
                    except Exception as e:
                        step = by_id[sid]
                        print(f"  [step {sid} errored: {type(e).__name__}: {e}]")
                        self.trace.append({
                            "step_id": sid, "tool": step.get("tool", "?"),
                            "weight": step.get("weight", 0.0),
                            "location": "error", "duration_s": 0.0,
                        })
                        results.append({
                            "id": sid, "tool": step.get("tool", "?"),
                            "weight": step.get("weight", 0.0),
                            "location": "error",
                            "output": {"error": f"{type(e).__name__}: {e}"},
                        })
                        continue
                    if r is not None:
                        results.append(r)
                next_frontier: list = []
                for sid in done_ids:
                    for s in succ.get(sid, []):
                        in_deg[s] -= 1
                        if in_deg[s] == 0:
                            next_frontier.append(s)
                frontier = next_frontier

        results.sort(key=lambda r: r["weight"], reverse=True)
        return results

    def list_graphs(self, prefix: str = "") -> list:
        return list(self.stub.List(storage_pb2.ListRequest(prefix=prefix)).ids)
