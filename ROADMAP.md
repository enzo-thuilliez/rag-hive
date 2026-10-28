# Roadmap

Local-first: no paid API at runtime. First target: MSCI Global Investable Market Indexes Methodology.

## Done

- Scaffold: FastAPI + React monorepo, strict typing, CI, event schema, `/api` routes

## Next

1. **Corpus** — manifest of the 10 PDFs (URL, checksum, properties) + `make corpus`; PDFs never committed
2. **Golden set (MSCI)** — Q/A with expected passages, reviewed by an LLM-as-judge workflow
3. **Components** — parsers (pypdf, pdfplumber, PyMuPDF, Docling), chunkers (fixed, recursive, markdown-header, parent-child), BGE-M3 embeddings, retrievers (BM25, dense, hybrid)
4. **Benchmark CLI** — run every config on MSCI, report recall@k, MRR, nDCG, parsing quality
5. **Agents** — LangGraph workflow on Ollama (Qwen)
6. **Dashboard** — live agent map, results, drill-down
7. **Scale out** — full corpus, semantic/agentic chunking, rerankers, ColPali
