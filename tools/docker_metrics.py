"""Pull live stats from running Docker containers.

Reads `docker stats` for every running container (or those matching a name
prefix) and returns either:
  - raw_stats(): per-container dict of CPU%, mem bytes, mem%, net I/O
  - aggregated(): one rolled-up dict across all matched containers
  - as_features(): same numbers re-shaped into the 9-field schema the
    trained scaling classifier expects. Fields the classifier wants but
    Docker can't give us (LORA, MODEL, PIPELINE, etc.) are filled with
    sensible constants — flagged below so you remember what's faked.

Requires: pip install docker
"""
import time

import docker  # type: ignore


class DockerMetricsSource:
    def __init__(
        self, 
        name_prefix: str | None = None,
        image_filter: str | None = "synthesis-agent"
    ):
        self.client = docker.from_env()
        self.name_prefix = name_prefix
        self.image_filter = image_filter

    def _containers(self):
        cs = self.client.containers.list()
        if self.name_prefix:
            cs = [c for c in cs if c.name.startswith(self.name_prefix)]
        if self.image_filter:
            cs = [c for c in cs
                  if any(self.image_filter in t for t in (c.image.tags or []))]
        return cs

    @staticmethod
    def _cpu_pct(s: dict) -> float:
        cpu = s.get("cpu_stats", {})
        pre = s.get("precpu_stats", {})
        cpu_delta = cpu.get("cpu_usage", {}).get("total_usage", 0) \
                  - pre.get("cpu_usage", {}).get("total_usage", 0)
        sys_delta = cpu.get("system_cpu_usage", 0) - pre.get("system_cpu_usage", 0)
        n = cpu.get("online_cpus") or len(cpu.get("cpu_usage", {}).get("percpu_usage") or []) or 1
        if cpu_delta > 0 and sys_delta > 0:
            return round((cpu_delta / sys_delta) * n * 100.0, 2)
        return 0.0

    @staticmethod
    def _net_io(s: dict) -> tuple[int, int]:
        nets = s.get("networks") or {}
        rx = sum(v.get("rx_bytes", 0) for v in nets.values())
        tx = sum(v.get("tx_bytes", 0) for v in nets.values())
        return rx, tx

    def raw_stats(self) -> list[dict]:
        import json as _json
        out = []
        for c in self._containers():
            try:
                s = c.stats(stream=False)
            except (_json.JSONDecodeError, Exception):
                # container exited between list() and stats() — skip it
                continue
            mem_bytes = s.get("memory_stats", {}).get("usage", 0) or 0
            mem_limit = s.get("memory_stats", {}).get("limit", 0) or 0
            rx, tx = self._net_io(s)
            out.append({
                "name": c.name,
                "id": c.short_id,
                "image": (c.image.tags[0] if c.image.tags else c.image.short_id),
                "cpu_pct": self._cpu_pct(s),
                "mem_bytes": mem_bytes,
                "mem_limit": mem_limit,
                "mem_pct": round((mem_bytes / mem_limit * 100), 2) if mem_limit else 0.0,
                "net_rx": rx,
                "net_tx": tx,
            })
        return out

    def aggregated(self) -> dict:
        rows = self.raw_stats()
        if not rows:
            return {"n_containers": 0, "cpu_pct": 0.0, "mem_bytes": 0,
                    "mem_pct": 0.0, "mem_pct_max": 0.0,
                    "net_rx": 0, "net_tx": 0}
        # Pool-wide mem_pct = total used / total limit. Averaging per-container
        # percents lets a single huge-limit, near-empty container drag the
        # signal down — a load spike on a small container would look like
        # "memory dropped." Pool ratio is the honest aggregate; max is the
        # worst-actor signal kept for visibility.
        total_used = sum(r["mem_bytes"] for r in rows)
        total_limit = sum(r["mem_limit"] for r in rows) or 1
        return {
            "n_containers": len(rows),
            "cpu_pct": round(sum(r["cpu_pct"] for r in rows), 2),
            "mem_bytes": total_used,
            "mem_pct": round(total_used / total_limit * 100, 2),
            "mem_pct_max": round(max(r["mem_pct"] for r in rows), 2),
            "net_rx": sum(r["net_rx"] for r in rows),
            "net_tx": sum(r["net_tx"] for r in rows),
        }

    def as_features(self) -> dict | None:
        """Shape live container stats into the classifier's 9-field schema.
        Returns None when no containers match the filter — feeding zeros
        into a classifier trained on running workloads is out-of-distribution
        garbage; let the caller decide what to do (e.g. skip the tick).

        Real signals: QPS (proxied by net_rx delta/s), INFERENCE (cpu%-derived),
        BYTES (mem%), QUEUE_RT (best-effort 0). Faked constants: LORA, MODEL,
        PIPELINE, DUTY, CONTROL — these were workload-config flags in the
        training set and have no Docker-level analogue."""
        a = self.aggregated()
        if a["n_containers"] == 0:
            return None
        rx0 = a["net_rx"]
        time.sleep(1.0)
        rx1 = self.aggregated()["net_rx"]
        qps_proxy = max(rx1 - rx0, 0) / 1024.0
        return {
            "BYTES":    a["mem_pct"] / 100.0,
            "CONTROL":  1450,
            "DUTY":     a["cpu_pct"],
            "INFERENCE": a["cpu_pct"] * 4,
            "LORA":     True,
            "MODEL":    1.0,
            "PIPELINE": 1.0,
            "QPS":      qps_proxy,
            "QUEUE_RT": 0,
        }
