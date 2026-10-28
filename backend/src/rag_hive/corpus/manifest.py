"""Reading the corpus manifest (`data/corpus/manifest.yaml`)."""

from pathlib import Path

from rag_hive.corpus.models import CorpusEntry


def load_manifest(path: Path) -> list[CorpusEntry]:
    """Read and validate the corpus manifest.

    Args:
        path: The manifest YAML file.

    Returns:
        The entries in file order.

    Raises:
        FileNotFoundError: If `path` does not exist.
        pydantic.ValidationError: If an entry does not match `CorpusEntry`.
        ValueError: If two entries share an `id`.
    """
    raise NotImplementedError
