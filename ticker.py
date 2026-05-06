"""Continuous scaling-decision loop.

The classifier runs on a fixed-interval tick over live container metrics.
The expensive LLM agent only fires when the classifier disagrees with itself
across ticks (flip) or when its confidence drops below threshold (uncertain).
This is the sustainability story: routine decisions stay cheap; novelty
escalates to reasoning.

Usage:
    python ticker.py                          # 10s tick, conf<0.7 escalates
    python ticker.py --interval 5 --threshold 0.6
    python ticker.py --plan-only              # don't auto-execute escalations
    python ticker.py --once                   # single tick, then exit
"""
from dotenv import load_dotenv
load_dotenv()

import argparse
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents import ExecutorAgent, PlannerAgent
from tools.scaling_log import log_decision

def _fmt_metrics(m: dict) -> str:
    return (f"DUTY={m['DUTY']:>5.1f}  INFERENCE={m['INFERENCE']:>6.1f}  "
            f"BYTES={m['BYTES']:.4f}  QPS={m['QPS']:.2f}")


def _escalate(planner: PlannerAgent, executor: ExecutorAgent, reason: str,
              metrics: dict, auto_execute: bool) -> None:
    """Build a graph from the planner; persist to etcd; optionally run it."""
    print(f"  ↑ ESCALATE: {reason}")
    request = f"scaling decision needs review: {reason}. Investigate and act."
    try:
        graph = planner.plan(request, metrics=metrics)
        planner.save_graph(graph["id"], graph)
        print(f"    planner emitted graph {graph['id']} ({len(graph['steps'])} steps)")
    except Exception as e:
        print(f"    planner failed: {type(e).__name__}: {e}")
        return

    if not auto_execute:
        return
    try:
        results = executor.execute(graph["id"])
        for r in results:
            print(f"    [{r['weight']:.2f}] {r['id']} ({r['location']}): "
                  f"{str(r['output'])[:120]}")
    except Exception as e:
        print(f"    executor failed: {type(e).__name__}: {e}")


def tick_loop(interval_s: int, conf_threshold: float, auto_execute: bool,
              once: bool, cooldown_s: float = 60.0) -> None:
    executor = ExecutorAgent()
    if executor.metrics is None:
        print("ERR: docker not reachable — ticker has nothing to read", file=sys.stderr)
        sys.exit(1)
    planner = PlannerAgent()

    last_pred: dict | None = None
    last_escalated_at: float = 0.0
    n = 0
    while True:
        n += 1
        t0 = time.monotonic()
        try:
            metrics = executor.metrics.as_features()
        except Exception as e:
            print(f"#{n:04d} sample failed: {type(e).__name__}: {e}")
            if once:
                return
            time.sleep(interval_s)
            continue
        if metrics is None:
            print(f"#{n:04d}  [idle ] no agent containers running — skipping")
            if once:
                return
            time.sleep(interval_s)
            continue
        assert metrics is not None
        try:
            pred = executor.scaler.forward(metrics=metrics)
        except Exception as e:
            print(f"#{n:04d} predict failed: {type(e).__name__}: {e}")
            if once:
                return
            time.sleep(interval_s)
            continue

        flipped = last_pred is not None and pred["scale_up"] != last_pred["scale_up"]
        uncertain = pred["confidence"] < conf_threshold

        decision = "SCALE_UP" if pred["scale_up"] else "hold    "
        flag = "FLIP " if flipped else ("UNCRT" if uncertain else "ok   ")
        print(f"#{n:04d}  [{flag}] {decision}  conf={pred['confidence']:.2f}  "
              f"{_fmt_metrics(metrics)}")

        log_decision(
            source="ticker",
            features=metrics,
            decision=pred,
            thresholds={"confidence": conf_threshold},
            context={
                "tick_n": n,
                "prev_decision": (
                    None if last_pred is None
                    else ("scale_up" if last_pred["scale_up"] else "hold")
                ),
                "flipped": flipped,
                "uncertain": uncertain,
                "escalated": flipped or uncertain,
                "auto_execute": auto_execute,
            },
        )

        if flipped or uncertain:
            since_last = time.monotonic() - last_escalated_at
            if since_last < cooldown_s:
                print(f"  · suppressed (cooldown {cooldown_s - since_last:.0f}s left)")
            else:
                reasons = []
                if flipped and last_pred is not None:
                    prev = "scale_up" if last_pred["scale_up"] else "hold"
                    cur = "scale_up" if pred["scale_up"] else "hold"
                    reasons.append(f"prediction flipped {prev}→{cur}")
                if uncertain:
                    reasons.append(f"confidence {pred['confidence']:.2f} < {conf_threshold}")
                _escalate(planner, executor, "; ".join(reasons), metrics, auto_execute)
                last_escalated_at = time.monotonic()

        last_pred = pred
        if once:
            return
        elapsed = time.monotonic() - t0
        time.sleep(max(interval_s - elapsed, 0))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=10,
                    help="seconds between ticks (default 10)")
    ap.add_argument("--threshold", type=float, default=0.7,
                    help="escalate when classifier confidence falls below this")
    ap.add_argument("--plan-only", action="store_true",
                    help="emit the escalation graph but do NOT auto-execute it")
    ap.add_argument("--once", action="store_true",
                    help="single tick then exit (smoke test)")
    ap.add_argument("--cooldown", type=float, default=60.0,
                    help="min seconds between escalations (default 60)")
    args = ap.parse_args()

    signal.signal(signal.SIGINT, lambda *_: (print("\nstopped"), sys.exit(0)))

    print(f"ticker: every {args.interval}s, escalate at conf<{args.threshold}, "
          f"cooldown={args.cooldown}s, auto_execute={not args.plan_only}")
    tick_loop(args.interval, args.threshold,
              auto_execute=not args.plan_only, once=args.once,
              cooldown_s=args.cooldown)
    return 0


if __name__ == "__main__":
    sys.exit(main())
