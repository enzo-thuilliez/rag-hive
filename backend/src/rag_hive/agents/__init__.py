"""Multi-agent benchmark workflow (LangGraph). Agent logic is not implemented yet.

Planned flow, see AGENTS.md for the contract:

    Profiler → Planner → QA Generator → Workers (one per pipeline config, in parallel)
             → Judge → Reporter

Only the static topology shown on the dashboard's agent map exists so far
(`rag_hive.agents.topology`).
"""
