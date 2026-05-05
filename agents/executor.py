import json
import time

import grpc

from tools import ScalingPredictorTool
from gen.python import storage_pb2, storage_pb2_grpc


class ExecutorAgent:
    def __init__(
        self,
        storage_addr: str = "localhost:50054",
        models_dir: str = "models",
        weight_threshold: float = 0.0,
    ):
        self.channel = grpc.insecure_channel(storage_addr)
        self.stub = storage_pb2_grpc.GraphStoreStub(self.channel)
        self.scaler = ScalingPredictorTool(models_dir=models_dir)
        self.weight_threshold = weight_threshold

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
        by_id = {s["id"]: s for s in steps}
        visited: set[str] = set()
        order: list = []

        def visit(sid: str):
            if sid in visited:
                return
            visited.add(sid)
            for dep in by_id[sid].get("depends_on", []):
                visit(dep)
            order.append(by_id[sid])

        for s in steps:
            visit(s["id"])
        return order

    def execute(self, graph_id: str) -> list:
        graph = self.fetch_graph(graph_id)
        if graph is None:
            return []

        tools = {"scaling_predictor": self.scaler}
        ordered = self._topo_sort(graph["steps"])
        results = []

        for step in ordered:
            if step["weight"] < self.weight_threshold:
                continue
            output = tools[step["tool"]].forward(**step["args"])
            results.append({
                "id": step["id"],
                "tool": step["tool"],
                "weight": step["weight"],
                "output": output,
            })

        results.sort(key=lambda r: r["weight"], reverse=True)
        return results

    def list_graphs(self, prefix: str = "") -> list:
        return list(self.stub.List(storage_pb2.ListRequest(prefix=prefix)).ids)
