# Behavior Regulation Environment Handler

## Focusing on Sustainable Cloud Scaling Utilizing Agentic AI

Masters capstone integrating:
- **Project 3**: ML scaling prediction (Gradient Boost classifier)
- **Project 5**: Function calling insight (LLM native tool use)
- **Project 6**: Agentic orchestration patterns (smolagents)

## Quickstart

Five commands cover the full reviewer experience. Run from the repo root.

```bash
task setup                                        # one-time: venv, deps, protos, agent image
python -m venv .venv
source .venv/bin/activate
# edit .env and set ANTHROPIC_API_KEY (template at .env.example)

task up                                           # start etcd + storage :50054 + runner :50055
task bench -- prompts.sample.json results.csv     # run BREH vs smolagent benchmark
task main -- --plan "High latency detected"       # optional: invoke the BREH CLI directly
task down                                         # stop everything (idempotent)
```

`task --list` shows only these user-facing commands. The proto-gen, etcd, and
storage/runner sub-tasks are hidden but still invokable by name.

### Prerequisites

`task setup` checks for these and fails with a clear message if any are missing:

- Python 3.13+ (`python3 --version`)
- Go (`go version`)
- Docker Desktop, daemon running (`docker info`)
- [Task](https://taskfile.dev/) (the runner this README assumes)

### Outputs

| Path | What it is |
|---|---|
| `results.csv` | Per-prompt benchmark numbers (wall, tokens, cost USD, parallelism) |
| `results_answers/` | Per-prompt answer markdown for human review |
| `logs/storage.log` | Storage gRPC server stdout/stderr |
| `logs/runner.log` | Runner gRPC server stdout/stderr |
| `logs/bench.log` | Captured `task bench` output |
| `logs/main.log` | Captured `task main` output |
| `logs/scaling.jsonl` | Append-only audit log of every scaling decision |

### Project 3 — training pipeline

The `models/*.pkl` artifacts were trained in
[machine-learning-foundations-project](https://github.com/KirkKennedyLincoln/machine-learning-foundations-project).
See `modeling.ipynb` in that repo for data generation, feature engineering,
hyperparameter selection, and evaluation.

To retrain cleanly, execute `python generate_models.py`

Final classifier:
- `sklearn.ensemble.GradientBoostingClassifier`
- 9 features: BYTES, CONTROL, DUTY, INFERENCE, LORA, MODEL, PIPELINE, QPS, QUEUE_RT
- StandardScaler preprocessing
- n_estimators=200, learning_rate=0.1, max_depth=4, random_state=42

### White Paper
`reflective_synthesis_paper.pdf`

### PowerPoint
`breh.pdf`

## Architecture

The system splits planning, storage, execution, and isolation across language
boundaries (Python orchestration, Go infrastructure) connected by gRPC. The
central thesis: a single LLM round-trip emits a DAG, the executor walks that
DAG with frontier-based parallel dispatch, and per-step routing decides
between fast inline calls and isolated container spawns.

### UML Class Diagram — domain model

The orchestration classes, their public surface, and how they relate. `Graph`
and `Step` are the pydantic-validated data contract that flows through every
edge of the system.

```mermaid
classDiagram
    direction LR

    class Graph {
        <<pydantic>>
        +str id
        +str request
        +int created_at
        +list~Step~ steps
    }

    class Step {
        <<pydantic>>
        +str id
        +str tool
        +dict args
        +float weight
        +list~str~ depends_on
    }

    class PlannerAgent {
        -str api_key
        -str model_id
        -GraphStoreStub stub
        -dict tools
        -list trace
        +plan(request, metrics) dict
        +replan(request, prior_results) dict
        +synthesize(request, prior_results) str
        +save_graph(graph_id, graph_data) bool
    }

    class ExecutorAgent {
        -GraphStoreStub stub
        -RunnerStub runner
        -dict tools
        -ScalingPredictorTool scaler
        -str image_name
        -float weight_threshold
        -DockerMetricsSource metrics
        -list trace
        +execute(graph_id, max_workers) list
        +fetch_graph(graph_id) dict
        +should_spawn(step) bool
        +resolve_metrics(step) void
        +run_step_in_container(graph_id, step) dict
        +list_graphs(prefix) list
    }

    class ScalingPredictorTool {
        <<smolagents.Tool>>
        +str name
        +str description
        +dict inputs
        +forward(metrics) dict
    }

    class DockerMetricsSource {
        -str name_prefix
        -DockerClient client
        +as_features() dict
    }

    class GetGraphTool {
        <<smolagents.Tool>>
        +forward(graph_id) dict
    }

    class PutGraphTool {
        <<smolagents.Tool>>
        +forward(key, value) bool
    }

    Graph "1" *-- "*" Step : composition
    PlannerAgent ..> Graph : produces / consumes
    ExecutorAgent ..> Graph : consumes
    ExecutorAgent o-- ScalingPredictorTool : aggregates
    ExecutorAgent o-- DockerMetricsSource : aggregates
    PlannerAgent o-- ScalingPredictorTool : aggregates
```

### UML Component Diagram — system topology

Components, their stereotypes, and the gRPC / HTTP / Docker interfaces that
connect them. Following the standard Mermaid convention for component
diagrams (`<<component>>`, `<<node>>`, `<<artifact>>` stereotypes) since
Mermaid lacks a dedicated component-diagram type.

```mermaid
flowchart TB
    subgraph clients ["Entry-point clients"]
        direction LR
        CLI["<<component>><br/>main.py"]
        BENCH["<<component>><br/>bench.py"]
    end

    subgraph host ["Host process (Python)"]
        direction TB
        PLAN["<<component>><br/>PlannerAgent"]
        EXEC["<<component>><br/>ExecutorAgent"]
        TOOLS["<<component>><br/>tool registry<br/>(scaling_predictor,<br/>web_search, visit_webpage)"]
        METRICS["<<component>><br/>DockerMetricsSource"]
        SLOG["<<component>><br/>scaling_log"]
    end

    subgraph services ["Go gRPC services"]
        direction LR
        STORAGE["<<component>><br/>GraphStore<br/>:50054"]
        RUNNER["<<component>><br/>Runner<br/>:50055"]
    end

    subgraph nodes ["Backing nodes"]
        direction LR
        ETCD["<<node>><br/>etcd"]
        DOCKER["<<node>><br/>Docker daemon"]
    end

    subgraph cnt ["Spawned agent container"]
        ENTRY["<<artifact>><br/>agent_entrypoint.py"]
    end

    LLM[("<<external>><br/>Anthropic API")]
    JSONL[/"<<artifact>><br/>logs/scaling.jsonl"/]

    CLI --> PLAN
    CLI --> EXEC
    BENCH --> PLAN
    BENCH --> EXEC

    PLAN -- "litellm" --> LLM
    PLAN -- "gRPC: Put / Get" --> STORAGE
    EXEC -- "gRPC: Get / Put" --> STORAGE
    EXEC -- "gRPC: Spawn / Wait / Kill" --> RUNNER
    EXEC --> TOOLS
    EXEC --> METRICS
    EXEC --> SLOG
    SLOG --> JSONL

    STORAGE -- "client/v3" --> ETCD
    RUNNER -- "Docker SDK" --> DOCKER
    DOCKER -. "spawns" .-> ENTRY
    ENTRY -- "gRPC: Get step / Put result" --> STORAGE
```

### UML Sequence Diagram — plan → execute → replan

One LLM round-trip emits a DAG; the executor runs every ready step in
parallel; one `replan` call decides whether the request is answered or
another DAG is needed. This is the round-trip asymmetry that beats smolagent
on wall-clock for decomposable tasks.

```mermaid
sequenceDiagram
    participant U as main_py
    participant P as PlannerAgent
    participant S as GraphStore
    participant E as ExecutorAgent
    participant L as LLM

    U->>P: plan request and metrics
    P->>L: prompt with tools and metrics
    L-->>P: JSON DAG
    P->>P: pydantic validate Graph
    P->>S: Put graph
    P-->>U: graph dict

    loop until done or max iterations
        U->>E: execute graph_id
        E->>S: Get graph_id
        S-->>E: graph
        E->>E: frontier dispatch see Activity
        E-->>U: results list
        U->>P: replan with accumulated results
        P->>L: prompt with compressed results
        L-->>P: status answer or graph
        alt status is continue
            P->>S: Put new graph
            U->>U: graph_id assigned to new
        else status is done
            U-->>U: print answer then break
        end
    end
    Note over U,P: fallback if loop exits without answer
    U->>P: synthesize from accumulated results
    P->>L: prompt for final answer from partial results
    L-->>P: text
```

### UML Activity Diagram — `ExecutorAgent.execute`

The frontier-based dispatch loop, rendered as a state-machine activity
diagram (Mermaid's UML-compatible activity-flavor). The closed-loop part is
the `resolve_metrics` action: live container telemetry overrides the
LLM-fabricated args at execute time, so the trained classifier reads real
metrics, not whatever the planner guessed.

```mermaid
stateDiagram-v2
    direction TB
    [*] --> FetchGraph
    FetchGraph --> BuildIndex : graph != null
    FetchGraph --> [*] : graph == null (return [])
    BuildIndex --> CheckReady : in_degrees, successors

    state CheckReady <<choice>>
    CheckReady --> SortReturn : ready empty AND no in-flight
    CheckReady --> Submit : ready non-empty
    Submit --> Wait : pool.submit each ready step
    Wait --> RunOne : FIRST_COMPLETED future
    state RunOne {
        [*] --> WeightGate
        state WeightGate <<choice>>
        WeightGate --> Skipped : weight < threshold
        WeightGate --> ResolveMetrics : weight >= threshold
        ResolveMetrics --> RouteDecision : inject live telemetry<br/>(scaling_predictor only)
        state RouteDecision <<choice>>
        RouteDecision --> Container : RUNNER_ADDR AND should_spawn
        RouteDecision --> Inline : otherwise

        state Container {
            [*] --> Spawn
            Spawn --> WaitContainer : Runner.Spawn
            WaitContainer --> GetResult : Runner.Wait
            GetResult --> KillContainer : GraphStore.Get<br/>graph_id:results:step_id
            KillContainer --> [*] : Runner.Kill (best-effort)
        }

        state Inline {
            [*] --> Forward
            Forward --> [*] : tools[step.tool].forward(args)
        }

        Container --> LogDecision
        Inline --> LogDecision
        LogDecision --> TraceAppend : if scaling_predictor:<br/>scaling_log.log_decision
        TraceAppend --> [*] : append result
        Skipped --> [*]
    }

    RunOne --> Advance
    Advance --> CheckReady : decrement successors[sid]
    SortReturn --> [*] : results.sort by weight
```

### File index

| Path | Role |
|---|---|
| `main.py` | CLI driver: `--plan`, `--execute` (with replan loop), `--list` |
| `bench.py` | Runs BREH and smolagent over the same prompts, emits CSV |
| `agent_entrypoint.py` | Container-side: read env, run one step, write result to etcd |
| `agents/planner.py` | LLM round-trips: `plan`, `replan`, `synthesize`, `save_graph` |
| `agents/executor.py` | DAG fetch, frontier dispatch, container/inline routing |
| `agents/schema.py` | Pydantic `Graph` / `Step` validation models |
| `tools/scaling_tool.py` | Gradient Boost `ScalingPredictorTool` (Project 3 model) |
| `tools/docker_metrics.py` | Live container metrics → feature dict |
| `tools/scaling_log.py` | Append-only JSONL audit log of every scaling decision |
| `tools/etcd_tool.py` | `GetGraphTool` / `PutGraphTool` for the in-container path |
| `cmd/storage/` | Go gRPC server wrapping etcd (port 50054) |
| `cmd/runner/` | Go gRPC server wrapping Docker (port 50055) |
| `proto/` | Source-of-truth schemas; regenerated into `gen/` by `task` |
| `models/` | Trained classifier artifacts (`*.pkl`) |
| `logs/scaling.jsonl` | Per-decision audit log written by `scaling_log` |
