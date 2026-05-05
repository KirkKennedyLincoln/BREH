from dotenv import load_dotenv
load_dotenv()

import argparse
import json

from agents import PlannerAgent, ExecutorAgent
from agents.schema import Graph


SAMPLE_METRICS = {
    "BYTES": 0.92, "CONTROL": 1450, "DUTY": 380, "INFERENCE": 380,
    "LORA": True, "MODEL": 1.0, "PIPELINE": 1.0, "QPS": 10, "QUEUE_RT": 6,
}


def _print_results(results: list) -> None:
    for r in results:
        loc = r.get("location", "?")
        print(f"  [{r['weight']:.2f}] {r['id']} ({loc}) → {r['tool']}: {r['output']}")


def _print_trace(planner: PlannerAgent, executor: ExecutorAgent) -> None:
    print("\n=== Trace ===")
    print(f"\nLLM calls: {len(planner.trace)}")
    for i, c in enumerate(planner.trace, 1):
        in_t = c.get("input_tokens") or "?"
        out_t = c.get("output_tokens") or "?"
        print(f"  {i}. {c['call']:<7}  {c['duration_s']:>6.3f}s  in={in_t:<5} out={out_t:<5}  {c['model']}")

    executed = [s for s in executor.trace if s["location"] != "skipped"]
    skipped = [s for s in executor.trace if s["location"] == "skipped"]
    print(f"\nSteps: {len(executed)} executed, {len(skipped)} skipped")
    for s in executor.trace:
        if s["location"] == "skipped":
            print(f"  {s['step_id']:<5} {s['tool']:<18} {s['location']:<10} weight={s['weight']:.2f}")
        else:
            print(f"  {s['step_id']:<5} {s['tool']:<18} {s['location']:<10} weight={s['weight']:.2f}  {s['duration_s']:.3f}s")

    llm_time = sum(c["duration_s"] for c in planner.trace)
    tool_time = sum(s["duration_s"] for s in executor.trace)
    in_tokens = sum((c.get("input_tokens") or 0) for c in planner.trace)
    out_tokens = sum((c.get("output_tokens") or 0) for c in planner.trace)
    print(f"\nLLM time:    {llm_time:>7.3f}s   tokens: in={in_tokens}  out={out_tokens}")
    print(f"Tool time:   {tool_time:>7.3f}s")
    print(f"Total time:  {llm_time + tool_time:>7.3f}s")


def _execute_with_replan(executor: ExecutorAgent, planner: PlannerAgent,
                         graph_id: str, max_iterations: int) -> None:
    """Execute → replan loop. Stops when the LLM says 'done', when the LLM
    can't produce a continuation, or when max_iterations is hit."""
    graph = executor.fetch_graph(graph_id)
    if graph is None:
        print(f"no graph found for id: {graph_id}")
        return
    request = graph["request"]
    accumulated: list = []

    for iteration in range(1, max_iterations + 1):
        print(f"\n=== Iteration {iteration}: executing {graph_id} ===")
        results = executor.execute(graph_id)
        if not results:
            print("(no steps above threshold)")
        else:
            _print_results(results)
        accumulated.extend(results)

        decision = planner.replan(request, accumulated)
        status = decision.get("status")

        if status == "done":
            answer = decision.get("answer", "(no answer)")
            print(f"\n=== Iteration {iteration} answer ===\n{answer}")
            followup = decision.get("followup")
            if followup and iteration < max_iterations:
                # The answer was high-confidence AND suggested concrete next
                # steps — treat the followup as a fresh top-level query and
                # plan from scratch. Reset accumulated so the next replan
                # judges the new query on its own merits.
                print(f"\n--- LLM suggested follow-up: {followup}\n")
                new_graph = planner.plan(followup)
                planner.save_graph(new_graph["id"], new_graph)
                graph_id = new_graph["id"]
                request = followup
                accumulated = []
                continue
            _print_trace(planner, executor)
            return
        if status == "continue":
            new_graph = decision.get("graph")
            if not new_graph:
                print("LLM said continue but provided no graph; stopping.")
                return
            # Validate against the schema before persisting.
            validated = Graph(**new_graph).model_dump()
            planner.save_graph(validated["id"], validated)
            graph_id = validated["id"]
            print(f"\nLLM extended the plan → {graph_id}")
            continue
        print(f"unexpected replan status: {status!r}; stopping.")
        _print_trace(planner, executor)
        return

    # Loop exhausted without a 'done' status — force a final synthesis from
    # whatever has been gathered. One extra LLM call, but the user always
    # gets an answer instead of a silent exit with results discarded.
    print(f"\n=== max iterations ({max_iterations}) reached — "
          f"synthesizing from {len(accumulated)} accumulated step result(s) ===")
    answer = planner.synthesize(request, accumulated)
    print(f"\n=== Final answer ===\n{answer}")
    _print_trace(planner, executor)


def main():
    parser = argparse.ArgumentParser(description="CLI Tool for BREH invocation")
    parser.add_argument("-pl", "--plan", help="plan a request, e.g. 'High latency detected'")
    parser.add_argument("-ex", "--execute", help="execute graph by id (with replan loop)")
    parser.add_argument("-ls", "--list", action="store_true", help="list stored graph ids")
    parser.add_argument("-t", "--threshold", type=float, default=0.85,
                        help="skip steps with weight below this threshold (default 0.85)")
    parser.add_argument("--max-iterations", type=int, default=3,
                        help="cap on execute→replan rounds (default 3)")

    args = parser.parse_args()

    if args.plan:
        planner = PlannerAgent()
        graph = planner.plan(args.plan, SAMPLE_METRICS)
        ok = planner.save_graph(graph["id"], graph)
        print(json.dumps(graph, indent=2))
        print(f"\nsaved: {ok}  id: {graph['id']}")

    elif args.execute:
        executor = ExecutorAgent(weight_threshold=args.threshold)
        planner = PlannerAgent()
        _execute_with_replan(executor, planner, args.execute, args.max_iterations)

    elif args.list:
        ids = ExecutorAgent().list_graphs()
        if not ids:
            print("(no graphs stored)")
            return
        for graph_id in ids:
            print(graph_id)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
