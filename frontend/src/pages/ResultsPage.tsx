import { useParams } from "react-router";

/** Benchmark results for one run. Will chart pipeline scores with Recharts. */
export function ResultsPage() {
  const { runId } = useParams();
  return (
    <section>
      <h1 className="text-2xl font-semibold">Results</h1>
      <p className="mt-2 text-slate-600">
        Run <code>{runId}</code>: retrieval and answer-quality scores per pipeline configuration.
      </p>
    </section>
  );
}
