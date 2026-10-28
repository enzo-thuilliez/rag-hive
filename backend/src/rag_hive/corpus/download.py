"""Downloading corpus PDFs and checking them against their pinned checksum."""

from pathlib import Path

from rag_hive.corpus.models import CorpusEntry


class ChecksumMismatchError(Exception):
    """A file's SHA-256 differs from the one pinned in the manifest."""


def sha256_of(path: Path) -> str:
    """Return the lowercase hex SHA-256 of the file at `path`."""
    raise NotImplementedError


async def ensure_document(entry: CorpusEntry, raw_dir: Path) -> Path:
    """Make sure `entry`'s PDF is in `raw_dir` with the pinned checksum.

    A file already present with the right checksum is kept and not downloaded again. A
    download is written to a temporary file and only moved into place once its checksum
    matches, so `raw_dir` never holds a partial or wrong file under the final name.

    Args:
        entry: The manifest entry to fetch.
        raw_dir: Directory holding the downloaded PDFs (`data/corpus/raw/`).

    Returns:
        Path of the verified PDF, `raw_dir / f"{entry.id}.pdf"`.

    Raises:
        ChecksumMismatchError: If the downloaded bytes do not match `entry.sha256`.
    """
    raise NotImplementedError
