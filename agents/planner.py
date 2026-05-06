import os
import re
import json
import time
import uuid

import grpc # type: ignore
import litellm
from pydantic import ValidationError

from tools import build_step_tools
from gen.python import storage_pb2_grpc, storage_pb2
from .schema import Graph


def record_usage(response, model_id: str, call_type: str, duration: float) -> dict:
    """Tracking usage of invoked agents input/output tokens, etc."""
    usage = getattr(response, "usage", None)
    return {
        "call": call_type,
        "model": model_id,
        "duration_s": round(duration, 3),
        "input_tokens": getattr(usage, "prompt_tokens", None),
        "output_tokens": getattr(usage, "completion_tokens", None),
    }

def shrink(value, char_cap: int):
    if isinstance(value, str) and len(value) > char_cap:
        return value[:char_cap] + "..."
    if isinstance(value, dict):
        return {k: shrink(v, char_cap) for k, v in value.items()}
    if isinstance(value, list):
        return [shrink(v, char_cap) for v in value]
    return value


def compress_results(results: list, char_cap: int = 1200, keep: int = 10) -> list:
    recent = results[-keep:]
    return [shrink(dict(r), char_cap) for r in recent]


class PlannerAgent:
    def __init__(
        self,
        storage_addr: str = "localhost:50054",
        model_id: str = "anthropic/claude-haiku-4-5",
    ):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Please set ANTHROPIC_API_KEY in your .env!")
        self.api_key = api_key
        self.model_id = model_id

        channel = grpc.insecure_channel(storage_addr)
        self.stub = storage_pb2_grpc.GraphStoreStub(channel=channel)

        self.tools = build_step_tools(models_dir="models")
        self.trace: list[dict] = []  # one entry per LLM round-trip

    def plan(self, request: str, metrics: dict | None = None) -> dict:
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        metrics_line = (
            f"Current metrics (use only if a step actually needs them): "
            f"{json.dumps(metrics)}\n" if metrics else ""
        )
        tools_block = "\n".join(
            f"\t- {name}: {tool.description}\n\t\tinputs: {json.dumps(tool.inputs)}"
            for name, tool in self.tools.items()
        )
        prompt = (f"""
            You are a planning agent. Given a user request, emit a JSON DAG
            of steps. Each step invokes ONE of the available tools. Steps
            may depend on earlier ones via depends_on. Pick whichever tools
            fit the request — you do not have to use all of them.

            User request: {request}
            {metrics_line}
            Available tools:
            {tools_block}

            Output ONLY valid JSON (no prose, no markdown fences) matching:
            {{
            "id": "{plan_id}",
            "request": "{request}",
            "created_at": {int(time.time())},
            "steps": [
                {{
                "id": "s1",
                "tool": "<tool_name>",
                "args": {{<inputs satisfying the tool schema>}},
                "weight": <0.0-1.0>,
                "depends_on": []
                }}
            ]
            }}

            Constraints:
            - at least 3 steps
            - each step's args must satisfy the chosen tool's input schema
            - weights reflect your confidence the step is worth executing
            - use depends_on for steps that logically need earlier outputs
        """)

        t0 = time.monotonic()
        response = litellm.completion(
            model=self.model_id,
            api_key=self.api_key,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        self.trace.append(record_usage(response, self.model_id, "plan", time.monotonic() - t0))
        raw = response.choices[0].message.content or ""
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        try:
            graph_dict = json.loads(match.group(0) if match else raw)
            graph = Graph(**graph_dict)
        except (json.JSONDecodeError, ValidationError) as e:
            return {
                "id": plan_id, "request": request, "created_at": int(time.time()),
                "steps": [], "_plan_failed": True, "_error": str(e), "_raw": raw[:500],
            }
        return graph.model_dump()

    def replan(self, request: str, prior_results: list) -> dict:
        prior_results = compress_results(prior_results)
        tools_block = "\n".join(
            f"\t- {name}: {tool.description}\n\t\tinputs: {json.dumps(tool.inputs)}"
            for name, tool in self.tools.items()
        )
        prompt = (f"""
            You previously emitted a DAG of work. The high-confidence steps
            (weight above the threshold) have been executed; results are
            below. Decide whether the original request is now answerable or
            whether more work is needed.

            Original request: {request}

            Results so far (most-confident first):
            {json.dumps(prior_results, indent=2, default=str)}

            Respond with ONLY valid JSON. ONE of these two shapes:

            ```json{{
            "status": "done",
            "answer": "<final answer to the original request>",
            "followup": "<optional new top-level query, or null>",
            "extension_confidence": <0.0-1.0, REQUIRED if followup is set>
            }}```

            ```json{{
            "status": "continue",
            "graph": {{<new graph dict>}},
            "extension_confidence": <0.0-1.0, REQUIRED>
            }}```

            Rules for the `done` case:
            - `answer` must fully address the ORIGINAL request.
            - `followup` is OPTIONAL. Include it ONLY if your answer
            contains concrete next-steps the user would profitably research
            as a SEPARATE top-level query (specific URLs to evaluate, sub-
            topics to deep-dive, libraries to compare). Phrase it as a
            natural-language query string. Set null or omit if the answer
            is self-contained.
            - `extension_confidence` is REQUIRED whenever `followup` is
            set, and reflects how strongly you believe pursuing the followup
            would materially improve the answer. Use 0.9+ ONLY if you are
            highly confident the current answer is not suffice. In education,
            .70 is considered passing, so if you are able to say this answer has
            less than 70% of what was asked for then return a 0.9+ score.
            Otherwise, score honestly below 0.9 or 0.89 (auto-pass) so we can
            return the answer as the final answer (circuit-breaker).

            Rules for the `continue` case:
            - Use this when the original request is NOT yet answered and
            more work in the same DAG is needed. The new graph extends the
            same `request`.
            - `extension_confidence` is REQUIRED: how strongly you believe
            the new sub-DAG materially improves the answer vs synthesizing
            from current results. Use 0.9+ only when extension is essential, which
            means the answer does not provide a rough estimation of 70% of the idea
            or concept asked for.

            Available tools (for the continue case):
            {tools_block}

            If continuing, the graph must match this shape:
            ```json{{
            "id": "plan-<8-hex>",
            "request": "{request}",
            "created_at": <unix-seconds>,
            "steps": [
                {{
                "id": "...",
                "tool": "...",
                "args": {{...}},
                "weight": <0-1>,
                "depends_on": []
                }},
                ...
            ]
            }}```
        """)
        t0 = time.monotonic()
        response = litellm.completion(
            model=self.model_id,
            api_key=self.api_key,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
        )
        self.trace.append(record_usage(response, self.model_id, "replan", time.monotonic() - t0))
        raw = response.choices[0].message.content or ""
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            return json.loads(
                match.group(0) if match else raw
            )
        except json.JSONDecodeError:
            return {"status": "done", "answer": "", "_replan_failed": True, "_raw": raw[:500]}

    def synthesize(self, request: str, prior_results: list) -> str:
        """Final answer to either enforce or call when agent is ready."""
        prior_results = compress_results(prior_results)
        prompt = (
            "You have accumulated research results from earlier iterations. "
            "Produce a FINAL answer to the original request now. No further "
            "research is possible — work only from the results below.\n\n"
            f"Original request: {request}\n\n"
            f"Accumulated results:\n"
            f"{json.dumps(prior_results, indent=2, default=str)}\n\n"
            "Respond with ONLY the answer text. No JSON, no preamble, no "
            "metadata, no apologies about missing data — synthesize what "
            "you can from what you have."
        )
        t0 = time.monotonic()
        response = litellm.completion(
            model=self.model_id,
            api_key=self.api_key,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000,
        )
        self.trace.append(record_usage(response, self.model_id, "synthesize", time.monotonic() - t0))
        return response.choices[0].message.content or "(empty)"

    def save_graph(self, graph_id: str, graph_data: dict) -> bool:
        graph = storage_pb2.Graph(
            id=graph_id,
            data=json.dumps(graph_data),
            created_at=int(time.time()),
        )
        return self.stub.Put(
            request=storage_pb2.PutRequest(graph=graph)
        ).success
