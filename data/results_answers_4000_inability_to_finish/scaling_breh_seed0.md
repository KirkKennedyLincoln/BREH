# scaling | breh | seed=0

**Prompt:** given metrics QPS=10 QUEUE_RT=6 INFERENCE=380, should I scale up?

---

Based on the provided metrics (QPS=10, QUEUE_RT=6ms, INFERENCE=380ms), **YES, you should scale up**. Here's why:

1. **High Inference Latency**: 380ms is significantly high. For most production systems, inference latency should be well below 100-200ms. This suggests your inference workload is either compute-bound or your current capacity is insufficient.

2. **Queue Response Time**: 6ms queue time is reasonable, but combined with the high inference latency, indicates requests are waiting for compute resources.

3. **Low QPS with High Latency**: Even at only 10 queries per second, you're experiencing 380ms inference time. This is a red flag that your current instance size or resource allocation cannot handle even modest traffic efficiently.

**Recommendation**: Scale up your compute resources (CPU/GPU, memory, or replica count) to reduce inference latency. Monitor after scaling to ensure you reach your target latency SLA (typically <100-200ms for most use cases).