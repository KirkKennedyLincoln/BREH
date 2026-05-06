"""Drive BREH and smolagents over the same prompts; emit a CSV.

Usage:
    python bench.py prompts.json results.csv
    python bench.py prompts.json results.csv --model anthropic/claude-haiku-4-5
    python bench.py prompts.json results.csv --skip smolagent --seeds 3

prompts.json:
    [
      {"id": "q1", "prompt": "..."},
      {"id": "q2", "prompt": "..."}
    ]

Both systems must run on the SAME model for the comparison to mean anything.
The storage server (task storage:run) must be up — BREH writes graphs to etcd.
"""
import os
import re
import sys
import csv
import json
import time
import argparse
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

import litellm
# litellm._turn_on_debug()

from smolagents import (  # type: ignore[import-untyped]
    DuckDuckGoSearchTool,
    LiteLLMModel,
    ToolCallingAgent,
    VisitWebpageTool,
)

from agents import PlannerAgent, ExecutorAgent
from agents.schema import Graph
from tools import ScalingPredictorTool
from tools.scaling_log import set_context, clear_context, get_counts


# Both PlannerAgent and smolagents' LiteLLMModel bottom out in litellm.completion,
# so one global patch captures every model round-trip from either system.
_LLM_TRACE: list[dict] = []
_real_completion = litellm.completion


def _tracked_completion(*args, **kwargs):
    kwargs.setdefault("num_retries", 6)
    kwargs.setdefault("timeout", 120)
    t0 = time.monotonic()
    resp = _real_completion(*args, **kwargs)
    usage = getattr(resp, "usage", None)
    _LLM_TRACE.append({
        "duration_s": time.monotonic() - t0,
        "input_tokens": (getattr(usage, "prompt_tokens", 0) or 0) if usage else 0,
        "output_tokens": (getattr(usage, "completion_tokens", 0) or 0) if usage else 0,
    })
    return resp


litellm.completion = _tracked_completion


@contextmanager
def fresh_trace():
    _LLM_TRACE.clear()
    yield _LLM_TRACE


def _summarize(trace: list[dict]) -> dict:
    return {
        "llm_calls": len(trace),
        "llm_time_s": round(sum(c["duration_s"] for c in trace), 3),
        "input_tokens": sum(c["input_tokens"] for c in trace),
        "output_tokens": sum(c["output_tokens"] for c in trace),
    }


def run_breh(prompt: str, model_id: str, max_iterations: int) -> dict:
    planner = PlannerAgent(model_id=model_id)
    executor = ExecutorAgent()
    answer = ""
    accumulated: list = []
    t0 = time.monotonic()
    try:
        graph = planner.plan(prompt)
        planner.save_graph(graph["id"], graph)
        graph_id = graph["id"]
        request = prompt

        for _ in range(max_iterations):
            accumulated.extend(executor.execute(graph_id))
            decision = planner.replan(request, accumulated)
            status = decision.get("status")
            if status == "done":
                answer = decision.get("answer", "")
                break
            if status == "continue":
                new_graph = decision.get("graph")
                if not new_graph:
                    break
                validated = Graph(**new_graph).model_dump()
                planner.save_graph(validated["id"], validated)
                graph_id = validated["id"]
                continue
            break
        if not answer:
            answer = planner.synthesize(request, accumulated)
    except Exception as e:
        print(f"  [breh] {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    wall = time.monotonic() - t0

    tool_calls = sum(1 for s in executor.trace if s["location"] != "skipped")
    tool_time = round(sum(s["duration_s"] for s in executor.trace), 3)
    return {
        "answer": answer, "wall_s": round(wall, 3),
        "tool_calls": tool_calls, "tool_time_s": tool_time,
    }


def run_smolagent(prompt: str, model_id: str, max_steps: int) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = LiteLLMModel(model_id=model_id, api_key=api_key)
    tools = [
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
        ScalingPredictorTool(models_dir="models"),
    ]
    n_tool_calls = [0]
    tool_times = [0.0]
    for t in tools:
        orig = t.forward
        def make_wrapped(fn):
            def wrapped(*a, **kw):
                n_tool_calls[0] += 1
                t0 = time.monotonic()
                try:
                    return fn(*a, **kw)
                finally:
                    tool_times[0] += time.monotonic() - t0
            return wrapped
        t.forward = make_wrapped(orig)

    agent = ToolCallingAgent(tools=tools, model=model, max_steps=max_steps)

    answer = ""
    t0 = time.monotonic()
    try:
        answer = str(agent.run(prompt))
    except Exception as e:
        print(f"  [smolagent] {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    wall = time.monotonic() - t0
    return {
        "answer": answer, "wall_s": round(wall, 3),
        "tool_calls": n_tool_calls[0],
        "tool_time_s": round(tool_times[0], 3),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompts", help="JSON file: [{id, prompt}]")
    ap.add_argument("out_csv")
    ap.add_argument("--model", default="anthropic/claude-haiku-4-5",
                    help="model id used by BOTH systems (parity)")
    ap.add_argument("--max-iterations", type=int, default=5,
                    help="BREH replan cap")
    ap.add_argument("--max-steps", type=int, default=12,
                    help="smolagent step cap")
    ap.add_argument("--skip", choices=["breh", "smolagent"], default=None)
    ap.add_argument("--seeds", type=int, default=1,
                    help="repeats per prompt to bound variance")
    ap.add_argument("--throttle", type=float, default=5.0,
                    help="seconds to sleep between system runs (rate-limit mitigation)")
    args = ap.parse_args()

    with open(args.prompts) as f:
        prompts = json.load(f)

    answers_dir = os.path.splitext(args.out_csv)[0] + "_answers"
    os.makedirs(answers_dir, exist_ok=True)

    # Pricing: Anthropic Claude Haiku 4.5 list price as of paper run
    # ($1/MTok input, $5/MTok output). If you swap models, update these.
    PRICE_IN_PER_MTOK = 1.00
    PRICE_OUT_PER_MTOK = 5.00

    fields = [
        "prompt_id", "system", "seed", "wall_s",
        "llm_calls", "llm_time_s", "input_tokens", "output_tokens",
        "input_cost_usd", "output_cost_usd", "cost_usd",
        "tool_calls", "tool_time_s", "tools_per_llm", "parallelism",
        "scaling_decisions", "scaling_escalations",
        "model", "answer_path",
    ]
    with open(args.out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()

        first = True
        for p in prompts:
            for seed in range(args.seeds):
                for system in ("breh", "smolagent"):
                    if args.skip == system:
                        continue
                    if not first and args.throttle > 0:
                        time.sleep(args.throttle)
                    first = False
                    print(f"\n>>> {p['id']} | {system} | seed={seed}", flush=True)
                    set_context(prompt_id=p["id"], system=system, seed=seed)
                    with fresh_trace() as trace:
                        if system == "breh":
                            r = run_breh(p["prompt"], args.model, args.max_iterations)
                        else:
                            r = run_smolagent(p["prompt"], args.model, args.max_steps)
                        s = _summarize(trace)
                    counts = get_counts()
                    clear_context()
                    ratio = round(r["tool_calls"] / s["llm_calls"], 2) if s["llm_calls"] else 0
                    parallelism = round(r["tool_time_s"] / r["wall_s"], 2) if r["wall_s"] else 0
                    input_cost_usd = round(s["input_tokens"] * PRICE_IN_PER_MTOK / 1_000_000, 4)
                    output_cost_usd = round(s["output_tokens"] * PRICE_OUT_PER_MTOK / 1_000_000, 4)
                    cost_usd = round(input_cost_usd + output_cost_usd, 4)
                    safe_id = re.sub(r"[^A-Za-z0-9_-]+", "_", p["id"])
                    answer_path = os.path.join(
                        answers_dir, f"{safe_id}_{system}_seed{seed}.md")
                    with open(answer_path, "w") as af:
                        af.write(f"# {p['id']} | {system} | seed={seed}\n\n")
                        af.write(f"**Prompt:** {p['prompt']}\n\n")
                        af.write("---\n\n")
                        af.write(r["answer"] or "(no answer)")
                    row = {
                        "prompt_id": p["id"], "system": system, "seed": seed,
                        "wall_s": r["wall_s"], **s,
                        "input_cost_usd": input_cost_usd,
                        "output_cost_usd": output_cost_usd,
                        "cost_usd": cost_usd,
                        "tool_calls": r["tool_calls"],
                        "tool_time_s": r["tool_time_s"],
                        "tools_per_llm": ratio,
                        "parallelism": parallelism,
                        "scaling_decisions": counts["decisions"],
                        "scaling_escalations": counts["escalations"],
                        "model": args.model,
                        "answer_path": answer_path,
                    }
                    w.writerow(row)
                    f.flush()
                    print(
                        f"    wall={r['wall_s']}s  llm={s['llm_calls']}  "
                        f"tok=in{s['input_tokens']}/out{s['output_tokens']}  "
                        f"cost=${cost_usd:.4f}  "
                        f"tools={r['tool_calls']}  tools/llm={ratio}  "
                        f"parallelism={parallelism}",
                        flush=True,
                    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
