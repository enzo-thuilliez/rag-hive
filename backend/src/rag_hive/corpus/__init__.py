"""The benchmark corpus: a manifest of pinned PDFs and the downloader behind `make corpus`.

PDFs are never committed. The manifest records where each one comes from and its SHA-256, and
the downloader refuses any file whose checksum differs. Loading and downloading are not
implemented yet.
"""

from rag_hive.corpus.models import CorpusEntry, DocumentProperties

__all__ = ["CorpusEntry", "DocumentProperties"]
