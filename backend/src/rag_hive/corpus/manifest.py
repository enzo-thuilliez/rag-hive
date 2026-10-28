"""Reading the corpus manifest (`data/corpus/manifest.yaml`)."""

from pathlib import Path

import yaml

from rag_hive.corpus.models import CorpusEntry, CorpusManifest


def load_manifest(path: Path) -> list[CorpusEntry]:
    """Read and validate the corpus manifest.

    Args:
        path: The manifest YAML file, a mapping with a `documents` list.

    Returns:
        The entries in file order.

    Raises:
        FileNotFoundError: If `path` does not exist.
        pydantic.ValidationError: If an entry does not match `CorpusEntry`, or two entries
            share an `id`.
        yaml.YAMLError: If the file is not valid YAML.
    """
    with path.open(encoding="utf-8") as file:
        raw: object = yaml.safe_load(file)
    return CorpusManifest.model_validate(raw).documents
