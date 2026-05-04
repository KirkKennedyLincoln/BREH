# Executor Agent - Executes graphs locally without LLM
# Fetches plans from storage and runs tool calls

import json

import grpc

from tools import ScalingPredictorTool
from gen.python import storage_pb2, storage_pb2_grpc


class ExecutorAgent:
    def __init__(self, storage_addr: str = "localhost:50054"):
        self.channel = grpc.insecure_channel("localhost:50054") 
        self.stub = storage_pb2_grpc.GraphStoreStub(self.channel)
        self.scaler = ScalingPredictorTool()
        
    def fetch_graph(self, graph_id: str) -> dict | None:
        resp = self.stub.Get(storage_pb2.GetRequest(id=graph_id))
        if not resp.graph.id:
            return None
        return json.loads(resp)

    def delete_graph(self, graph_id: str) -> bool:
        request = storage_pb2.DeleteRequest(id=graph_id)
        response = self.stub.Delete(request=request)

        if response.success:
            return True
        return False

    def update_graph(self, graph_id: str, data: dict) -> dict:
        graph = storage_pb2.Graph(
            id=graph_id, 
            data=json.dumps(data), 
            created_at=123
        )

        request = storage_pb2.PutRequest(graph=graph)
        response = self.stub.Put(request)

        return json.loads(response)

    def execute(self, graph_id: str) -> list:
        graph = self.fetch_graph(graph_id=graph_id)
        if graph is None:
            return []


        return [(key, value) for key, value in graph.items()]
        # TODO: For each step, call appropriate tool
        # TODO: Collect and return results

    def list_graphs(self, prefix: str = "") -> list:
        request = storage_pb2.ListRequest(prefix=prefix)
        response = self.stub.List(request=request)
        
        return response
