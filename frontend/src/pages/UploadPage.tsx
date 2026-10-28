/** Landing page. Will take a PDF and start a benchmark run. */
export function UploadPage() {
  return (
    <section>
      <h1 className="text-2xl font-semibold">Upload</h1>
      <p className="mt-2 text-slate-600">
        Drop a PDF to benchmark parsing × chunking × embedding × retrieval pipelines on it.
      </p>
    </section>
  );
}
