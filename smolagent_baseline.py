"""Naive smolagents baseline — for side-by-side comparison with BREH.

Runs the same tool set + same LLM as our planner/executor, but in the classic
agentic loop where the LLM sits on the critical path for every tool call.
Each `[LLM #N]` line printed during the run is a blocking model round-trip:
the next tool cannot start until the model returns.

Usage:
    python smolagent_baseline.py "your research prompt"

Default prompt matches the BREH demo so the traces are directly comparable.
"""
import os
import sys
import time

from dotenv import load_dotenv
load_dotenv()

import litellm

from smolagents import (  # type: ignore[import-untyped]
    DuckDuckGoSearchTool,
    LiteLLMModel,
    ToolCallingAgent,
    VisitWebpageTool,
)

from tools import ScalingPredictorTool


DEFAULT_PROMPT = "research best approaches to building a J2EE Spring Boot server"


# Monkey-patch litellm.completion so we catch every API hit no matter how
# smolagents wraps the model class (it calls .generate() internally, not the
# .__call__ I originally overrode — patching at the SDK call level is robust
# to any wrapper changes in smolagents).
TRACE: list[dict] = []
_real_completion = litellm.completion


def _tracked_completion(*args, **kwargs):
    t0 = time.monotonic()
    response = _real_completion(*args, **kwargs)
    elapsed = time.monotonic() - t0

    usage = getattr(response, "usage", None)
    in_t = getattr(usage, "prompt_tokens", None) if usage else None
    out_t = getattr(usage, "completion_tokens", None) if usage else None

    n = len(TRACE) + 1
    TRACE.append({
        "n": n,
        "duration_s": round(elapsed, 3),
        "input_tokens": in_t,
        "output_tokens": out_t,
    })
    print(
        f"  [LLM #{n:02d}] {elapsed:>6.3f}s blocking  "
        f"in={in_t if in_t is not None else '?':<5} "
        f"out={out_t if out_t is not None else '?':<5}",
        flush=True,
    )
    return response


litellm.completion = _tracked_completion


def main() -> int:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY in your .env", file=sys.stderr)
        return 1

    prompt = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROMPT
    print(f"=== Naive smolagents baseline ===")
    print(f"Prompt: {prompt}\n")
    print("(Each [LLM #N] line is a blocking model call — tools cannot start")
    print(" until the previous round-trip returns.)\n")

    model = LiteLLMModel(
        model_id="anthropic/claude-sonnet-4-20250514",
        api_key=api_key,
    )
    agent = ToolCallingAgent(
        tools=[
            DuckDuckGoSearchTool(),
            VisitWebpageTool(),
            ScalingPredictorTool(models_dir="models"),
        ],
        model=model,
        max_steps=12,
    )

    t_start = time.monotonic()
    try:
        answer = agent.run(prompt)
    except Exception as e:
        answer = f"(agent raised: {e})"
    total = time.monotonic() - t_start

    llm_time = sum(c["duration_s"] for c in TRACE)
    in_tokens = sum((c.get("input_tokens") or 0) for c in TRACE)
    out_tokens = sum((c.get("output_tokens") or 0) for c in TRACE)
    tool_time = max(total - llm_time, 0.0)

    print(f"\n=== Final answer ===\n{answer}\n")
    print("=== Trace ===")
    print(f"\nLLM calls: {len(TRACE)}")
    for c in TRACE:
        in_t = c.get("input_tokens") if c.get("input_tokens") is not None else "?"
        out_t = c.get("output_tokens") if c.get("output_tokens") is not None else "?"
        print(f"  {c['n']:>2}. agent_step  {c['duration_s']:>6.3f}s  "
              f"in={in_t!s:<5} out={out_t!s:<5}  {model.model_id}")

    print(f"\nLLM time:    {llm_time:>7.3f}s   tokens: in={in_tokens}  out={out_tokens}")
    print(f"Tool time:   {tool_time:>7.3f}s   (derived: total - llm_time)")
    print(f"Total time:  {total:>7.3f}s")
    print()
    print(f"Critical-path note: all {len(TRACE)} LLM calls were on the "
          f"critical path. The agent could not invoke a tool until the prior "
          f"call returned. BREH amortizes this: one plan + N replans, regardless "
          f"of how many tools execute.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
