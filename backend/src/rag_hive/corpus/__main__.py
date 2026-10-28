"""`make corpus`: download and verify every document of the corpus manifest.

Exits 0 when every PDF is present with its pinned checksum. Otherwise it reports every problem
(checksum mismatch, failed download, unpinned file), prints the instructions for each missing
manual download, and exits 1.
"""

import argparse
import asyncio
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx

from rag_hive.config import Settings, get_settings
from rag_hive.corpus.download import (
    CorpusError,
    ManualDownloadRequiredError,
    document_path,
    ensure_document,
)
from rag_hive.corpus.manifest import load_manifest
from rag_hive.corpus.models import CorpusEntry

logger = logging.getLogger("rag_hive.corpus")


async def sync_corpus(
    entries: Sequence[CorpusEntry], raw_dir: Path, client: httpx.AsyncClient
) -> bool:
    """Ensure every entry's PDF, logging one line per entry. Returns whether all succeeded.

    Entries are processed one at a time and a failure does not stop the others. Missing manual
    downloads are listed together at the end with their instructions.
    """
    manual_missing: list[CorpusEntry] = []
    failures = 0
    for entry in entries:
        try:
            path, downloaded = await ensure_document(entry, raw_dir, client=client)
        except ManualDownloadRequiredError:
            manual_missing.append(entry)
            failures += 1
            logger.error("MISSING %s: manual download required", entry.id)  # noqa: TRY400
        except (CorpusError, httpx.HTTPError) as error:
            failures += 1
            logger.error("FAIL    %s: %s", entry.id, error)  # noqa: TRY400
        else:
            logger.info("%s %s (%s)", "GOT    " if downloaded else "OK     ", entry.id, path)

    if manual_missing:
        logger.error("\n%d document(s) must be downloaded by hand:", len(manual_missing))
        for entry in manual_missing:
            logger.error(
                "\n- %s (%s)\n  page: %s\n  what: %s\n  save as: %s",
                entry.id,
                entry.title,
                entry.source_page,
                entry.instructions,
                document_path(entry, raw_dir),
            )
    if failures:
        logger.error("\n%d of %d document(s) not ready.", failures, len(entries))
    return failures == 0


async def _run(settings: Settings, manifest: Path, raw_dir: Path) -> bool:
    """Load the manifest and sync the corpus with a client configured from `settings`."""
    entries = load_manifest(manifest)
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=settings.corpus_download_timeout_seconds,
        headers={"User-Agent": settings.corpus_user_agent},
    ) as client:
        return await sync_corpus(entries, raw_dir, client)


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, sync the corpus and return the process exit code."""
    settings = get_settings()
    parser = argparse.ArgumentParser(prog="python -m rag_hive.corpus", description=__doc__)
    parser.add_argument("--manifest", type=Path, default=settings.corpus_manifest_path)
    parser.add_argument("--raw-dir", type=Path, default=settings.corpus_raw_dir)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    ok = asyncio.run(_run(settings, args.manifest, args.raw_dir))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
