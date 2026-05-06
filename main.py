from dotenv import load_dotenv
load_dotenv()

import argparse
import json

from agents import PlannerAgent, ExecutorAgent
from agents.schema import Graph

# metrics from module 3
SAMPLE_METRICS = {
    "BYTES": 0.92, "CONTROL": 1450, "DUTY": 380, "INFERENCE": 380,
    "LORA": True, "MODEL": 1.0, "PIPELINE": 1.0, "QPS": 10, "QUEUE_RT": 6,
}

def print_trace(
    planner: PlannerAgent, 
    executor: ExecutorAgent
) -> None:
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

def run_replan_loop(executor, planner, graph_id, max_iter):
    graph = executor.fetch_graph(graph_id)
    if graph is None:
        print(f"no graph: {graph_id}")
        return

    request = graph["request"]
    accumulated = []
    answer = None

    for i in range(1, max_iter + 1):
        print(f"\n=== iter {i}: {graph_id} ===")
        results = executor.execute(graph_id)
        if results:
            print(results)
        else:
            print("(nothing above threshold)")
        accumulated.extend(results)

        decision = planner.replan(request, accumulated)
        status = decision.get("status")

        if status == "done":
            answer = decision.get("answer") or ""
            if answer:
                print(f"\n=== answer ===\n{answer}")
            followup = decision.get("followup")
            if followup and i < max_iter:
                # treat followup as a fresh top-level query
                print(f"\nfollowup: {followup}")
                g = planner.plan(followup)
                planner.save_graph(g["id"], g)
                graph_id, request, accumulated = g["id"], followup, []
                answer = None
                continue
            break

        if status == "continue":
            g = decision.get("graph")
            if not g:
                break
            valid = Graph(**g).model_dump()
            planner.save_graph(valid["id"], valid)
            graph_id = valid["id"]
            print(f"\nplan extended: {graph_id}")
            continue

        # unknown status, bail
        break

    # if the loop exits without an answer for any reason, synthesize from
    # whatever we collected so the caller never sees nothing
    if not answer:
        answer = planner.synthesize(request, accumulated)
        print(f"\n=== final answer ===\n{answer}")

    print_trace(planner, executor)


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
        run_replan_loop(executor, planner, args.execute, args.max_iterations)

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
