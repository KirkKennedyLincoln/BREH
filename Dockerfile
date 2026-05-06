FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gen/ ./gen/
COPY models/ ./models/
COPY tools/ ./tools/
COPY agents/ ./agents/
COPY ./agent_entrypoint.py .

ENTRYPOINT ["python", "agent_entrypoint.py"]
