# scaling | breh | seed=0

**Prompt:** given metrics QPS=10 QUEUE_RT=6 INFERENCE=380, should I scale up?

---

Based on the available metrics and industry best practices:

**YES, you should consider scaling up**, with the following analysis:

1. **Queue Response Time (QUEUE_RT=6ms)**: This is a moderate queue depth indicator. According to inference optimization best practices, request queue depth is a primary autoscaling signal for ML workloads.

2. **Inference Latency (INFERENCE=380ms)**: This is relatively high for a single inference operation. For comparison, most optimized inference systems target sub-100ms latencies. This suggests your inference is either compute-intensive or your current capacity is being strained.

3. **QPS (Queries Per Second=10)**: At 10 QPS, you're still at modest load, but combined with the high inference latency and queue buildup, this indicates a capacity mismatch.

**Recommendation**: Scale up because:
- Your inference latency (380ms) is high relative to queue time (6ms), suggesting computational bottleneck
- You should use **inference-specific scaling metrics** (GPU utilization, queue depth, P95 latency) rather than generic CPU/memory metrics
- Even at moderate QPS, the system is showing stress signs

**Next steps**: Monitor GPU utilization and P95 latency metrics to trigger autoscaling policies on those signals rather than just QPS.