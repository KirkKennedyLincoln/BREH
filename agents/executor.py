# Executor Agent - Executes graphs locally without LLM
# Fetches plans from storage and runs tool calls

# TODO: Import grpc, json
import grpc
import json

# TODO: Import ScalingPredictorTool from tools
# TODO: Import generated protos from gen.python
from tools import ScalingPredictorTool
from gen.python import storage_pb2, storage_pb2_grpc


class ExecutorAgent:
    def __init__(self, storage_addr: str = "localhost:50054"):
        channel = grpc.insecure_channel("localhost:50054") 
        self.stub = storage_pb2_grpc.GraphStoreStub(channel)
        self.scaler = ScalingPredictorTool()
        # TODO: Initialize gRPC channel to storage server
        # TODO: Initialize ScalingPredictorTool for execution
        pass
        
    def fetch_graph(self, graph_id: str) -> dict:
         
        # TODO: Call stub.Get() via gRPC
        # TODO: Parse graph.data JSON
        # TODO: Return graph dict or None
        return {}

    def delete_graph(self, graph_id: str) -> dict:
        graph = storage_pb2_grpc
        request = storage_pb2.PutRequest(graph=graph)
        response = self.stub.Put(request)

        return {}

    def update_graph(self, graph_id: str) -> dict:
        graph = storage_pb2.Graph(id="...", data="...", created_at=123)
        request = storage_pb2.PutRequest(graph=graph)
        response = self.stub.Put(request)
        return {}

    def execute(self, graph_id: str) -> list:
        graph: storage_pb2_grpc.GraphStore = storage_pb2_grpc.GraphStore()
        request = self.stub.Put()
        response = self.stub.Get(request)
        return []
        # TODO: Fetch graph
        # TODO: Loop through graph steps
        # TODO: For each step, call appropriate tool
        # TODO: Collect and return results

    def list_graphs(self, prefix: str = "") -> list:
        # TODO: Call stub.List() via gRPC
        # TODO: Return list of graph IDs

        return {}
