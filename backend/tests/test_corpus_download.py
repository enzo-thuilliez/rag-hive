import asyncio
import hashlib
import logging
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest

from rag_hive.corpus.__main__ import sync_corpus
from rag_hive.corpus.download import (
    ChecksumMismatchError,
    ManualDownloadRequiredError,
    UnpinnedChecksumError,
    ensure_document,
    sha256_of,
)
from rag_hive.corpus.models import CorpusEntry

PDF = b"%PDF-1.7 pinned bytes"
PDF_SHA = hashlib.sha256(PDF).hexdigest()
URL = "https://example.com/doc.pdf"
PROPERTIES = {
    "tables": False,
    "images": False,
    "multi_column": False,
    "scanned": False,
    "formulas": False,
}

type Handler = Callable[[httpx.Request], httpx.Response]


def auto_entry(sha256: str = PDF_SHA) -> CorpusEntry:
    return CorpusEntry.model_validate(
        {
            "id": "doc",
            "title": "Doc",
            "publisher": "Pub",
            "url": URL,
            "sha256": sha256,
            "pages": 1,
            "language": "en",
            "properties": PROPERTIES,
        }
    )


def manual_entry(sha256: str = PDF_SHA) -> CorpusEntry:
    pinned = {"pages": 1, "properties": PROPERTIES} if sha256 else {}
    return CorpusEntry.model_validate(
        {
            "id": "gated",
            "title": "Gated doc",
            "publisher": "Pub",
            "download": "manual",
            "source_page": "https://example.com/documents",
            "instructions": "Accept the disclaimer and download the PDF.",
            "sha256": sha256,
            "language": "en",
            **pinned,
        }
    )


def serve(body: bytes = PDF, status: int = 200) -> tuple[Handler, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status, content=body)

    return handler, requests


def ensure(entry: CorpusEntry, raw_dir: Path, handler: Handler) -> tuple[Path, bool]:
    async def run() -> tuple[Path, bool]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await ensure_document(entry, raw_dir, client=client)

    return asyncio.run(run())


def test_downloads_and_verifies_a_missing_file(tmp_path: Path) -> None:
    handler, requests = serve()

    path, downloaded = ensure(auto_entry(), tmp_path / "raw", handler)

    assert downloaded
    assert path == tmp_path / "raw" / "doc.pdf"
    assert path.read_bytes() == PDF
    assert [str(request.url) for request in requests] == [URL]


def test_skips_a_file_already_present_and_valid(tmp_path: Path) -> None:
    (tmp_path / "doc.pdf").write_bytes(PDF)
    handler, requests = serve()

    _, downloaded = ensure(auto_entry(), tmp_path, handler)

    assert not downloaded
    assert requests == []


def test_checksum_mismatch_fails_and_leaves_no_file(tmp_path: Path) -> None:
    handler, _ = serve(body=b"%PDF-1.7 something else")

    with pytest.raises(ChecksumMismatchError, match="manifest pins"):
        ensure(auto_entry(), tmp_path, handler)

    assert list(tmp_path.iterdir()) == []


def test_replaces_a_present_auto_file_with_the_wrong_checksum(tmp_path: Path) -> None:
    (tmp_path / "doc.pdf").write_bytes(b"stale")
    handler, requests = serve()

    path, downloaded = ensure(auto_entry(), tmp_path, handler)

    assert downloaded
    assert len(requests) == 1
    assert sha256_of(path) == PDF_SHA


def test_http_error_propagates_and_leaves_no_file(tmp_path: Path) -> None:
    handler, _ = serve(body=b"not found", status=404)

    with pytest.raises(httpx.HTTPStatusError):
        ensure(auto_entry(), tmp_path, handler)

    assert list(tmp_path.iterdir()) == []


def test_missing_manual_file_is_never_downloaded(tmp_path: Path) -> None:
    handler, requests = serve()

    with pytest.raises(ManualDownloadRequiredError):
        ensure(manual_entry(), tmp_path, handler)

    assert requests == []


def test_present_manual_file_is_verified(tmp_path: Path) -> None:
    (tmp_path / "gated.pdf").write_bytes(PDF)
    handler, requests = serve()

    _, downloaded = ensure(manual_entry(), tmp_path, handler)

    assert not downloaded
    assert requests == []


def test_present_manual_file_with_the_wrong_checksum_fails(tmp_path: Path) -> None:
    (tmp_path / "gated.pdf").write_bytes(b"other bytes")
    handler, requests = serve()

    with pytest.raises(ChecksumMismatchError):
        ensure(manual_entry(), tmp_path, handler)

    assert requests == []
    assert (tmp_path / "gated.pdf").read_bytes() == b"other bytes"


def test_unpinned_present_file_reports_its_checksum(tmp_path: Path) -> None:
    (tmp_path / "gated.pdf").write_bytes(PDF)
    handler, _ = serve()

    with pytest.raises(UnpinnedChecksumError, match=PDF_SHA):
        ensure(manual_entry(sha256=""), tmp_path, handler)


def test_sync_reports_every_problem_and_the_manual_instructions(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    handler, _ = serve(body=b"tampered")
    entries = [auto_entry(), manual_entry(sha256="")]

    async def run() -> bool:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await sync_corpus(entries, tmp_path, client)

    with caplog.at_level(logging.INFO, logger="rag_hive.corpus"):
        ok = asyncio.run(run())

    assert not ok
    assert "FAIL    doc" in caplog.text
    assert "MISSING gated" in caplog.text
    assert "Accept the disclaimer and download the PDF." in caplog.text
    assert str(tmp_path / "gated.pdf") in caplog.text
    assert "2 of 2 document(s) not ready" in caplog.text


def test_sync_succeeds_when_every_file_is_ready(tmp_path: Path) -> None:
    (tmp_path / "gated.pdf").write_bytes(PDF)
    handler, _ = serve()

    async def run() -> bool:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await sync_corpus([auto_entry(), manual_entry()], tmp_path, client)

    assert asyncio.run(run())
