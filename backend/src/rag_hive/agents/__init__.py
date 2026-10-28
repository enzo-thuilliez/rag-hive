"""Multi-agent benchmark workflow (LangGraph). Agent logic is not implemented yet.

    Profiler → Planner → QA Generator → Workers (one per pipeline config, in parallel)
             → Judge → Reporter

- `profiler`, `planner`, `qa_generator`, `worker`, `judge`, `reporter`: one module per agent,
  each with its input model, output model, a `run_*` function and a LangGraph node.
- `state`: the `WorkflowState` the nodes share.
- `graph`: the topology, the `StateGraph` built from it, and the dashboard's `RunGraph`.
- `topology`: the `RunGraph` wire types.

See AGENTS.md for the contract.
"""
