# Agent image. Built once, spawned per-step by the Go Runner service.
# The container only needs to: connect to host etcd via gRPC, fetch its
# assigned step, run it, write the result back.
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Order copies from least- to most-frequently-changed so layer cache reuse
# stays high during iteration.
COPY gen/ ./gen/
COPY models/ ./models/
COPY tools/ ./tools/
COPY agents/ ./agents/
COPY agent_entrypoint.py .

ENTRYPOINT ["python", "agent_entrypoint.py"]
