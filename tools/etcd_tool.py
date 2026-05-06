import json # type: ignore
import os # type: ignore
import time # type: ignore

import grpc # type: ignore
from smolagents import Tool  # type: ignore[import-untyped]

from gen.python import storage_pb2, storage_pb2_grpc


def stub() -> storage_pb2_grpc.GraphStoreStub:
    """Build a GraphStore client against $STORAGE_ADDR (default localhost:50054)."""
    addr = os.getenv("STORAGE_ADDR", "localhost:50054")
    return storage_pb2_grpc.GraphStoreStub(grpc.insecure_channel(addr))


class GetGraphTool(Tool):
    """Fetch a planning graph by id from the BREH etcd-backed store."""

    name = "get_graph"
    description = (
        "Fetch a planning graph by id from the BREH key-value store. "
        "Returns the parsed graph dict, or {'error': 'not found'} if absent."
    )
    inputs = {
        "graph_id": {"type": "string", "description": "the graph id to fetch"},
    }
    output_type = "object"

    def __init__(self):
        super().__init__()
        self.stub = stub()

    def forward(self, graph_id: str) -> dict:
        resp = self.stub.Get(storage_pb2.GetRequest(id=graph_id))
        if not resp.graph.id:
            return {"error": "not found", "graph_id": graph_id}
        return json.loads(resp.graph.data)


class ListGraphsTool(Tool):
    """List stored graph ids, optionally filtered by prefix."""

    name = "list_graphs"
    description = (
        "List stored graph ids in the BREH key-value store, optionally "
        "filtered by an id prefix. Empty prefix lists all."
    )
    inputs = {
        "prefix": {
            "type": "string",
            "description": "optional id prefix filter; empty string lists all",
            "nullable": True,
        },
    }
    output_type = "array"

    def __init__(self):
        super().__init__()
        self.stub = stub()

    def forward(self, prefix: str = "") -> list:
        resp = self.stub.List(storage_pb2.ListRequest(prefix=prefix))
        return list(resp.ids)


class PutGraphTool(Tool):
    """Persist a planning graph (or step result) back to the BREH store."""

    name = "put_graph"
    description = (
        "Persist a planning graph or step-result dict to the BREH key-value "
        "store under the given id. Overwrites any existing entry."
    )
    inputs = {
        "graph_id": {"type": "string", "description": "id to write under"},
        "data": {"type": "object", "description": "graph or result dict to store"},
    }
    output_type = "object"

    def __init__(self):
        super().__init__()
        self.stub = stub()

    def forward(self, graph_id: str, data: dict) -> dict:
        graph = storage_pb2.Graph(
            id=graph_id,
            data=json.dumps(data),
            created_at=int(time.time()),
        )
        resp = self.stub.Put(storage_pb2.PutRequest(graph=graph))
        return {"success": resp.success, "graph_id": graph_id}