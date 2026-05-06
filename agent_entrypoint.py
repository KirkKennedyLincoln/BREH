"""Entrypoint for agent containers.

Reads STORAGE_ADDR, GRAPH_ID, STEP_ID from env. Fetches its assigned step
from etcd via GetGraphTool, runs the step via the local tool registry, and
writes the result back under '{GRAPH_ID}:results:{STEP_ID}' via PutGraphTool.

Exit codes:
  0 — success
  1 — graph not found
  2 — step not found in graph
  3 — unknown tool referenced by step
"""

import os
import sys
import json

from tools import GetGraphTool, PutGraphTool, build_step_tools

def main() -> int:
    graph_id = os.environ["GRAPH_ID"]
    step_id = os.environ["STEP_ID"]

    get = GetGraphTool()
    put = PutGraphTool()

    tools = build_step_tools(models_dir="models")

    graph = get.forward(graph_id=graph_id)
    if graph.get("error"):
      return 1

    step = next((s for s in graph["steps"] if s["id"] == step_id), None)
    if step is None:
       return 2

    tool = tools.get(step["tool"])
    if tool is None:
      return 3

    live_metrics = os.environ.get("STEP_METRICS_JSON")
    if live_metrics and step["tool"] == "scaling_predictor":
        step.setdefault("args", {})["metrics"] = json.loads(live_metrics)

    output = tool.forward(**step["args"])
    put.forward(f"{graph_id}:results:{step_id}", output)

    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
