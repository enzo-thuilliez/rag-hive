"""Evaluation used by the Judge: golden sets, span matching, retrieval and parsing metrics.

- `golden`: the `GoldenQuestion` model and golden set loading.
- `span_matching`: which retrieved chunks cover which expected passages, chunker-independent.
- `metrics.retrieval`: recall@k, hit rate@k, MRR, nDCG@k over span matches.
- `metrics.parsing`: normalized edit distance and TEDS against reference transcriptions.

Models and signatures only; no metric is implemented yet.
"""
