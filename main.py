from dotenv import load_dotenv
load_dotenv()

import argparse
import json

from agents import PlannerAgent, ExecutorAgent


SAMPLE_METRICS = {
    "BYTES": 0.92, "CONTROL": 1450, "DUTY": 380, "INFERENCE": 380,
    "LORA": True, "MODEL": 1.0, "PIPELINE": 1.0, "QPS": 10, "QUEUE_RT": 6,
}


def main():
    parser = argparse.ArgumentParser(description="CLI Tool for BREH invocation")
    parser.add_argument("-pl", "--plan", help="plan a request, e.g. 'High latency detected'")
    parser.add_argument("-ex", "--execute", help="execute graph by id")
    parser.add_argument("-ls", "--list", action="store_true", help="list stored graph ids")
    parser.add_argument("-t", "--threshold", type=float, default=0.0,
                        help="skip steps with weight below this threshold (default 0.0)")

    args = parser.parse_args()

    if args.plan:
        planner = PlannerAgent()
        graph = planner.plan(args.plan, SAMPLE_METRICS)
        ok = planner.save_graph(graph["id"], graph)
        print(json.dumps(graph, indent=2))
        print(f"\nsaved: {ok}  id: {graph['id']}")

    elif args.execute:
        results = ExecutorAgent(weight_threshold=args.threshold).execute(args.execute)
        if not results:
            print(f"no graph found (or all steps below threshold) for id: {args.execute}")
            return
        print(f"executed {len(results)} step(s) ranked by weight:\n")
        for r in results:
            print(f"  [{r['weight']:.2f}] {r['id']} → {r['tool']}: {r['output']}")

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
