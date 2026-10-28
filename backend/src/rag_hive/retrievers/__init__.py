"""Retrievers index chunks and return the most relevant ones for a query.

Dense retrievers get their `Embedder` from the caller; sparse ones (BM25) need none.
Implementations register with `@retriever_registry.register`. No implementation exists yet.
"""

from rag_hive.retrievers.base import Retriever, RetrieverConfig, retriever_registry

__all__ = ["Retriever", "RetrieverConfig", "retriever_registry"]
