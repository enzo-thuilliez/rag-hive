import { useParams } from "react-router";

/** Live map of the agent workflow for one run. Will render `/runs/:runId/graph` with React Flow. */
export function AgentMapPage() {
  const { runId } = useParams();
  return (
    <section>
      <h1 className="text-2xl font-semibold">Agent Map</h1>
      <p className="mt-2 text-slate-600">
        Run <code>{runId}</code>: Profiler → Planner → QA Generator → Workers → Judge → Reporter,
        animated from the run&apos;s event stream.
      </p>
    </section>
  );
}
