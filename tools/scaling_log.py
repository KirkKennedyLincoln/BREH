"""Append-only audit log of every scaling decision.

JSONL format — one record per scaling_predictor inference made by the
executor during DAG execution.

Record shape:
    {
      "ts": "2026-05-06T01:30:42.123+00:00",
      "source": "executor",
      "features": {BYTES: ..., DUTY: ..., ...},
      "decision": {scale_up: bool, confidence: float, recommendation: str},
      "thresholds": {"confidence": 0.7},      # whatever's relevant
      "context": {graph_id, step_id, location, weight}
    }
"""
import json
import os
import threading
from datetime import datetime, timezone

_LOCK = threading.Lock()
DEFAULT_PATH = "logs/scaling.jsonl"

# Module-level run context — bench.py sets this around each bench iteration so
# every scaling decision logged during that run carries its prompt/system/seed.
# Cleared between runs. Globals are fine since bench is single-process.
_CONTEXT: dict = {}
_COUNTS: dict = {"decisions": 0, "escalations": 0}


def set_context(**kw) -> None:
    _CONTEXT.clear()
    _CONTEXT.update(kw)
    _COUNTS["decisions"] = 0
    _COUNTS["escalations"] = 0


def clear_context() -> None:
    _CONTEXT.clear()


def get_counts() -> dict:
    return dict(_COUNTS)


def log_decision(
    *,
    source: str,
    features: dict | None,
    decision: dict | None,
    thresholds: dict | None = None,
    context: dict | None = None,
    path: str = DEFAULT_PATH,
) -> None:
    merged_ctx = {**_CONTEXT, **(context or {})}
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "source": source,
        "features": features or {},
        "decision": decision or {},
        "thresholds": thresholds or {},
        "context": merged_ctx,
    }
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    line = json.dumps(rec, default=str) + "\n"
    with _LOCK:
        with open(path, "a") as f:
            f.write(line)
        _COUNTS["decisions"] += 1
        if merged_ctx.get("escalated") or merged_ctx.get("flipped"):
            _COUNTS["escalations"] += 1
