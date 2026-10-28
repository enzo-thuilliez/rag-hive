import asyncio
import hashlib
from pathlib import Path

import pytest

from rag_hive.corpus.derive import (
    DerivationSourceError,
    derivation_record,
    ensure_derived,
    extract_text,
    page_count,
    read_keywords,
    render_image_only,
)
from rag_hive.corpus.models import CorpusEntry

PROPERTIES = {
    "tables": False,
    "images": False,
    "multi_column": False,
    "scanned": False,
    "formulas": False,
}


def text_pdf(pages: list[str]) -> bytes:
    """Build a minimal valid PDF with one line of Helvetica text per page."""
    count = len(pages)
    kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(count))
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {count} >>".encode(),
    ]
    font = 3 + 2 * count
    for index, text in enumerate(pages):
        content = 4 + 2 * index
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] "
            f"/Resources << /Font << /F1 {font} 0 R >> >> /Contents {content} 0 R >>".encode()
        )
        stream = f"BT /F1 18 Tf 20 100 Td ({text}) Tj ET".encode()
        objects.append(
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
        )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets)
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode()
    out += f"startxref\n{xref}\n%%EOF\n".encode()
    return bytes(out)


SOURCE_BYTES = text_pdf(["Page one text", "Page two text", "Page three text"])
SOURCE_SHA = hashlib.sha256(SOURCE_BYTES).hexdigest()


def source_entry(**overrides: object) -> CorpusEntry:
    payload: dict[str, object] = {
        "id": "source",
        "title": "Source",
        "publisher": "Pub",
        "url": "https://example.com/source.pdf",
        "sha256": SOURCE_SHA,
        "pages": 3,
        "page_range": "1,3",
        "language": "en",
        "properties": PROPERTIES,
    }
    return CorpusEntry.model_validate(payload | overrides)


def derived_entry(dpi: int = 72) -> CorpusEntry:
    return CorpusEntry.model_validate(
        {
            "id": "source-image-only",
            "title": "Source, image only",
            "publisher": "Derived",
            "download": "derived",
            "derivation": {"kind": "image_only", "source": "source", "dpi": dpi},
            "pages": 2,
            "language": "en",
            "properties": PROPERTIES | {"scanned": True},
        }
    )


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "source.pdf").write_bytes(SOURCE_BYTES)
    return raw


def test_fixture_source_has_a_text_layer(raw_dir: Path) -> None:
    assert "Page three text" in extract_text(raw_dir / "source.pdf")


def test_image_only_pdf_has_the_selected_pages_and_no_text(raw_dir: Path, tmp_path: Path) -> None:
    output = tmp_path / "derived.pdf"

    render_image_only(raw_dir / "source.pdf", [1, 3], output, dpi=72, keywords="record")

    assert page_count(output) == 2
    assert extract_text(output).strip() == ""
    assert read_keywords(output) == "record"


def test_render_rejects_pages_outside_the_source(raw_dir: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="has 3 pages"):
        render_image_only(raw_dir / "source.pdf", [2, 4], tmp_path / "x.pdf", dpi=72, keywords="")


def test_ensure_derived_generates_then_keeps_an_up_to_date_file(
    raw_dir: Path, tmp_path: Path
) -> None:
    derived_dir = tmp_path / "derived"

    entry, source = derived_entry(), source_entry()

    path, generated = asyncio.run(ensure_derived(entry, source, raw_dir, derived_dir))
    _, again = asyncio.run(ensure_derived(entry, source, raw_dir, derived_dir))

    assert generated
    assert not again
    assert path == derived_dir / "source-image-only.pdf"
    assert read_keywords(path) == derivation_record(derived_entry(), source_entry(), SOURCE_SHA)
    assert extract_text(path).strip() == ""


def test_ensure_derived_regenerates_when_parameters_change(raw_dir: Path, tmp_path: Path) -> None:
    derived_dir = tmp_path / "derived"
    asyncio.run(ensure_derived(derived_entry(dpi=72), source_entry(), raw_dir, derived_dir))

    _, generated = asyncio.run(
        ensure_derived(derived_entry(dpi=96), source_entry(), raw_dir, derived_dir)
    )

    assert generated


def test_ensure_derived_needs_a_verified_source(raw_dir: Path, tmp_path: Path) -> None:
    (raw_dir / "source.pdf").write_bytes(b"tampered")

    with pytest.raises(DerivationSourceError, match="does not match its pinned sha256"):
        asyncio.run(ensure_derived(derived_entry(), source_entry(), raw_dir, tmp_path))


def test_ensure_derived_needs_the_source_file(tmp_path: Path) -> None:
    with pytest.raises(DerivationSourceError, match="not downloaded and pinned yet"):
        asyncio.run(ensure_derived(derived_entry(), source_entry(), tmp_path, tmp_path))
