import os
import re
import json
import time
import uuid

import grpc
import litellm

from tools import build_step_tools
from gen.python import storage_pb2_grpc, storage_pb2
from .schema import Graph


def _record_usage(response, model_id: str, call_type: str, duration: float) -> dict:
    usage = getattr(response, "usage", None)
    return {
        "call": call_type,
        "model": model_id,
        "duration_s": round(duration, 3),
        "input_tokens": getattr(usage, "prompt_tokens", None),
        "output_tokens": getattr(usage, "completion_tokens", None),
    }


def _extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


def _shrink(value, char_cap: int):
    """Recursively cap any long strings inside a result. Web_search and
    visit_webpage outputs are huge raw markdown — replan doesn't need the
    full body, just enough signal to decide next steps."""
    if isinstance(value, str) and len(value) > char_cap:
        return value[:char_cap] + f"\n... [truncated, original {len(value)} chars]"
    if isinstance(value, dict):
        return {k: _shrink(v, char_cap) for k, v in value.items()}
    if isinstance(value, list):
        return [_shrink(v, char_cap) for v in value]
    return value


def _compress_results(results: list, char_cap: int = 1200, keep_last: int = 10) -> list:
    """Drop everything but the last `keep_last` step results, then cap any
    string field at `char_cap`. Keeps replan input bounded regardless of how
    long the loop has been running."""
    recent = results[-keep_last:] if len(results) > keep_last else results
    return [_shrink(dict(r), char_cap) for r in recent]


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

    def _tool_block(self) -> str:
        lines = []
        for name, tool in self.tools.items():
            lines.append(
                f"  - {name}: {tool.description}\n"
                f"      inputs: {json.dumps(tool.inputs)}"
            )
        return "\n".join(lines)

    def plan(self, request: str, metrics: dict | None = None) -> dict:
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        metrics_line = (
            f"Current metrics (use only if a step actually needs them): "
            f"{json.dumps(metrics)}\n" if metrics else ""
        )
        prompt = (
            "You are a planning agent. Given a user request, emit a JSON DAG "
            "of steps. Each step invokes ONE of the available tools. Steps "
            "may depend on earlier ones via depends_on. Pick whichever tools "
            "fit the request — you do not have to use all of them.\n\n"
            f"User request: {request}\n"
            f"{metrics_line}"
            f"Available tools:\n{self._tool_block()}\n\n"
            "Output ONLY valid JSON (no prose, no markdown fences) matching:\n"
            "{\n"
            f'  "id": "{plan_id}",\n'
            f'  "request": "{request}",\n'
            f'  "created_at": {int(time.time())},\n'
            '  "steps": [\n'
            '    {"id": "s1", "tool": "<tool_name>",\n'
            '     "args": {<inputs satisfying the tool schema>},\n'
            '     "weight": <0.0-1.0>, "depends_on": []}\n'
            '  ]\n'
            "}\n\n"
            "Constraints: at least 3 steps. Each step's args must satisfy "
            "the chosen tool's input schema. Weights reflect your confidence "
            "the step is worth executing. Use depends_on for steps that "
            "logically need earlier outputs."
        )

        t0 = time.monotonic()
        response = litellm.completion(
            model=self.model_id,
            api_key=self.api_key,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        self.trace.append(_record_usage(response, self.model_id, "plan", time.monotonic() - t0))
        raw = response.choices[0].message.content or ""
        graph_dict = json.loads(_extract_json(raw))
        graph = Graph(**graph_dict)
        return graph.model_dump()

    def replan(self, request: str, prior_results: list) -> dict:
        prior_results = _compress_results(prior_results)
        """Round-trip back to the mother LLM with the high-confidence results
        already gathered. The LLM decides one of:

          - we have enough → return {"status": "done", "answer": "<text>"}
          - need more work → return {"status": "continue", "graph": <new DAG>}

        The new DAG follows the same Pydantic schema as `plan()` — a fresh
        plan_id, the same `request`, and steps using the available tools.
        """
        prompt = (
            "You previously emitted a DAG of work. The high-confidence steps "
            "(weight above the threshold) have been executed; results are "
            "below. Decide whether the original request is now answerable or "
            "whether more work is needed.\n\n"
            f"Original request: {request}\n"
            f"Results so far (most-confident first):\n"
            f"{json.dumps(prior_results, indent=2, default=str)}\n\n"
            "Respond with ONLY valid JSON. ONE of these two shapes:\n\n"
            '  {"status": "done",\n'
            '   "answer": "<final answer to the original request>",\n'
            '   "followup": "<optional new top-level query, or null>",\n'
            '   "extension_confidence": <0.0-1.0, REQUIRED if followup is set>}\n\n'
            '  {"status": "continue",\n'
            '   "graph": {<new graph dict>},\n'
            '   "extension_confidence": <0.0-1.0, REQUIRED>}\n\n'
            "Rules for the `done` case:\n"
            " - `answer` must fully address the ORIGINAL request.\n"
            " - `followup` is OPTIONAL. Include it ONLY if your answer "
            "contains concrete next-steps the user would profitably research "
            "as a SEPARATE top-level query (specific URLs to evaluate, sub-"
            "topics to deep-dive, libraries to compare). Phrase it as a "
            "natural-language query string. Set null or omit if the answer "
            "is self-contained.\n"
            " - `extension_confidence` is REQUIRED whenever `followup` is "
            "set, and reflects how strongly you believe pursuing the followup "
            "would materially improve the answer. Use 0.9+ ONLY if you are "
            "highly confident the followup uncovers something the current "
            "answer misses. Otherwise, score honestly below 0.9 (or omit "
            "followup entirely).\n\n"
            "Rules for the `continue` case:\n"
            " - Use this when the original request is NOT yet answered and "
            "more work in the same DAG is needed. The new graph extends the "
            "same `request`.\n"
            " - `extension_confidence` is REQUIRED: how strongly you believe "
            "the new sub-DAG materially improves the answer vs synthesizing "
            "from current results. Use 0.9+ only when extension is essential.\n\n"
            f"Available tools (for the continue case):\n{self._tool_block()}\n\n"
            "If continuing, the graph must match this shape:\n"
            "{\n"
            f'  "id": "plan-<8-hex>",\n'
            f'  "request": "{request}",\n'
            f'  "created_at": <unix-seconds>,\n'
            '  "steps": [{"id": "...", "tool": "...", "args": {...},\n'
            '             "weight": <0-1>, "depends_on": []}, ...]\n'
            "}\n"
        )
        t0 = time.monotonic()
        response = litellm.completion(
            model=self.model_id,
            api_key=self.api_key,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        self.trace.append(_record_usage(response, self.model_id, "replan", time.monotonic() - t0))
        raw = response.choices[0].message.content or ""
        return json.loads(_extract_json(raw))

    def synthesize(self, request: str, prior_results: list) -> str:
        """Final-answer call. Used when the loop has hit max_iterations
        without a 'done' status — forces the LLM to produce an answer from
        whatever has accumulated, with no option to continue/research more."""
        prior_results = _compress_results(prior_results)
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
            max_tokens=2000,
        )
        self.trace.append(_record_usage(response, self.model_id, "synthesize", time.monotonic() - t0))
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
