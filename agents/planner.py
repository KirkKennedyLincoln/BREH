import os
import re
import json
import time
import uuid

import grpc
import litellm

from tools import ScalingPredictorTool
from gen.python import storage_pb2_grpc, storage_pb2
from .schema import Graph


def _extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


class PlannerAgent:
    def __init__(
        self,
        storage_addr: str = "localhost:50054",
        model_id: str = "anthropic/claude-sonnet-4-20250514",
    ):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Please set ANTHROPIC_API_KEY in your .env!")
        self.api_key = api_key
        self.model_id = model_id

        channel = grpc.insecure_channel(storage_addr)
        self.stub = storage_pb2_grpc.GraphStoreStub(channel=channel)

        self.scaler = ScalingPredictorTool(models_dir="models")

    def _tool_schema(self) -> dict:
        return {
            "name": self.scaler.name,
            "description": self.scaler.description,
            "expected_metric_keys": list(self.scaler.features),
        }

    def plan(self, request: str, metrics: dict) -> dict:
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        prompt = (
            "You are a planning agent for a cloud-scaling decision system. Given a "
            "user request, current metrics, and an available tool, produce a JSON "
            "DAG of competing what-if scenarios. Each step calls the tool with a "
            "different hypothetical metrics dict (e.g. current load, doubled QPS, "
            "halved QPS, spiked QUEUE_RT, etc.) and is weighted by your confidence "
            "the scenario is worth evaluating.\n\n"
            f"User request: {request}\n"
            f"Current metrics: {json.dumps(metrics)}\n"
            f"Available tool: {json.dumps(self._tool_schema())}\n\n"
            "Output ONLY valid JSON (no prose, no markdown fences) matching:\n"
            "{\n"
            f'  "id": "{plan_id}",\n'
            f'  "request": "{request}",\n'
            f'  "created_at": {int(time.time())},\n'
            '  "steps": [\n'
            '    {"id": "s1", "tool": "scaling_predictor",\n'
            '     "args": {"metrics": {<all expected_metric_keys with hypothetical values>}},\n'
            '     "weight": <0.0-1.0>, "depends_on": []}\n'
            '  ]\n'
            "}\n\n"
            "Constraints: produce at least 3 steps. Every step's args.metrics must "
            "include ALL expected_metric_keys. Weights must reflect distinct levels "
            "of confidence. depends_on stays [] for now."
        )

        response = litellm.completion(
            model=self.model_id,
            api_key=self.api_key,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        raw = response.choices[0].message.content or ""
        graph_dict = json.loads(_extract_json(raw))
        graph = Graph(**graph_dict)
        return graph.model_dump()

    def save_graph(self, graph_id: str, graph_data: dict) -> bool:
        graph = storage_pb2.Graph(
            id=graph_id,
            data=json.dumps(graph_data),
            created_at=int(time.time()),
        )
        return self.stub.Put(
            request=storage_pb2.PutRequest(graph=graph)
        ).success
