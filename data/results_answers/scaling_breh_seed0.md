# scaling | breh | seed=0

**Prompt:** given metrics QPS=10 QUEUE_RT=6 INFERENCE=380, should I scale up?

---

Based on the available metrics and industry best practices, **YES, you should consider scaling up**, but the decision depends on your specific SLA and system configuration:

**Analysis of your metrics:**
- **QPS=10**: This is relatively low absolute throughput, but scaling need isn't solely determined by QPS.
- **QUEUE_RT=6ms**: Queue wait time of 6ms is reasonable but indicates requests are queuing.
- **INFERENCE=380ms**: This is your inference latency. According to industry guidance, inference latency typically sets a hard floor on response time (you cannot respond faster than inference takes).

**Scaling signals:**
1. **Queue depth is the key metric**: The fact that you have a QUEUE_RT of 6ms while inference takes 380ms suggests your system is experiencing queueing. Industry best practice (per Mirantis and DigitalOcean sources) is to scale up when queue depth or latency exceeds thresholds that risk violating your target P95 latency.

2. **Total latency concern**: Your end-to-end latency is approximately 386ms (380ms inference + 6ms queue). If your target latency SLA is below this, or if queue times are growing, scaling is warranted.

3. **Headroom principle**: Best practices recommend scaling proactively before hitting resource limits, not reactively after. With queue buildup already visible, you're showing early warning signs.

**Recommendation:**
- **Scale up if**: (a) your target P95 latency SLA is <386ms, OR (b) queue times are trending upward, OR (c) you expect traffic to increase
- **Monitor before scaling if**: your current SLA comfortably accommodates 386ms+ latency and queue times are stable
- **Use autoscaling rules** based on queue depth thresholds rather than just CPU/memory, as inference workloads are often queue-bound rather than utilization-bound