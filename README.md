# Behavior Regulation Environment Handler

## Focusing on Sustainable Cloud Scaling Utilizing Agentic AI

Masters capstone integrating:
- **Project 3**: ML scaling prediction (XGBoost classifier)
- **Project 5**: Function calling insight (LLM native tool use)
- **Project 6**: Agentic orchestration patterns (smolagents)

## Structure

```
cmd/storage/       Go gRPC server (etcd wrapper)
internal/storage/  Go etcd client
proto/             gRPC service definitions
gen/
  storagepb/       Generated Go protos
  python/          Generated Python protos
tools/             ScalingPredictorTool (Project 3)
models/            Trained ML artifacts (.pkl)
agents/            Planner (LLM) and Executor agents
main.py            CLI entry point
```

## Setup

```bash
pip install -r requirements.txt
task install-tools
task vendor-googleapis
task                    # generates Go + Python protos
task etcd:start
```

## Run

```bash
# Terminal 1: storage server
task storage:run

# Terminal 2: CLI
python main.py --plan "High latency detected"
python main.py --execute <graph_id>
python main.py --list
```

## Architecture

```
User Request
     │
     ▼
PlannerAgent (smolagents + LLM)
     ├── ScalingPredictorTool (Project 3 ML model)
     └── LLM native function calling (Project 5 insight)
     │
     ▼
Graph stored via gRPC → etcd
     │
     ▼
ExecutorAgent fetches and executes graph
```
