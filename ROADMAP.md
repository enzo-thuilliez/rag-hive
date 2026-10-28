# Roadmap

Local-first: no paid API at runtime. First target: MSCI Global Investable Market Indexes Methodology.

## Done

- Scaffold: FastAPI + React monorepo, strict typing, CI, event schema, `/api` routes
- Corpus: manifest of the 10 PDFs (URL, checksum, properties) + `make corpus`; PDFs never committed; FRASER page range and image-only variant

## Next

1. **Golden set (MSCI)** — Q/A with expected passages, reviewed by an LLM-as-judge workflow
2. **Components** — parsers (pypdf, pdfplumber, PyMuPDF, Docling), chunkers (fixed, recursive, markdown-header, parent-child), BGE-M3 embeddings, retrievers (BM25, dense, hybrid)
3. **Benchmark CLI** — run every config on MSCI, report recall@k, MRR, nDCG, parsing quality
4. **Agents** — LangGraph workflow on Ollama (Qwen)
5. **Dashboard** — live agent map, results, drill-down
6. **Scale out** — full corpus, semantic/agentic chunking, rerankers, ColPali
