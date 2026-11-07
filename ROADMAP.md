# Roadmap

Local-first: no paid API at runtime. First target: MSCI Global Investable Market Indexes
Methodology. Each step is a [milestone](https://github.com/enzo-thuilliez/rag-hive/milestones); its issues carry the acceptance criteria.

## Done

- **Scaffold**: FastAPI + React monorepo, strict typing, CI, event schema, `/api` routes
- **Corpus** ([milestone](https://github.com/enzo-thuilliez/rag-hive/milestone/1)): manifest of the 10 PDFs (URL, checksum,
  properties) + `make corpus`; PDFs never committed; FRASER page range and image-only variant

## Next

1. **Golden set** ([milestone](https://github.com/enzo-thuilliez/rag-hive/milestone/2)): Q/A with expected passages for MSCI, reviewed
   by an LLM-as-judge workflow. Ollama provider (#9), loader (#10), drafts (#11), review (#12).
2. **Components** ([milestone](https://github.com/enzo-thuilliez/rag-hive/milestone/3)): parsers (pypdf #13, pdfplumber #14,
   PyMuPDF #15, Docling #16), chunkers (fixed #17, recursive #18, markdown-header #19,
   parent-child #20), BGE-M3 embeddings (#21), retrievers (BM25 #22, dense #23, hybrid #24).
3. **Benchmark CLI** ([milestone](https://github.com/enzo-thuilliez/rag-hive/milestone/4)): run every config on MSCI and report
   recall@k, MRR, nDCG and parsing quality. Span matching (#25), retrieval metrics (#26),
   parsing metrics (#27), CLI (#28), report (#29).
4. **Agents** ([milestone](https://github.com/enzo-thuilliez/rag-hive/milestone/5)): LangGraph workflow on Ollama (Qwen). ADR on
   wiring (#30), event bus (#31), Profiler to Reporter (#32–#37), `POST /api/runs` (#38).
5. **Dashboard** ([milestone](https://github.com/enzo-thuilliez/rag-hive/milestone/6)): upload (#39), live agent map (#40),
   results (#41), chunk drill-down (#42), failing-worker states (#43).
6. **Scale out** ([milestone](https://github.com/enzo-thuilliez/rag-hive/milestone/7)): full corpus (#44), semantic (#45) and agentic
   (#46) chunking, rerankers (#47, #48), ColPali (#49), score regression baseline (#50).
