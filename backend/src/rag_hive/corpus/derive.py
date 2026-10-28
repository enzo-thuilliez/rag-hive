"""Derived corpus files: an image-only PDF rendered from selected pages of a source PDF.

An image-only variant has the same pages as its source but no text layer, so an OCR parser
faces a true scan while a text-layer parser finds nothing to read. The file records what it was
generated from (source checksum, pages, dpi) in its PDF keywords; `make corpus` regenerates it
whenever that record no longer matches the manifest.
"""

import asyncio
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

import pypdfium2  # type: ignore[import-untyped]  # no type information; wrapped below

from rag_hive.corpus.download import CorpusError, document_path, sha256_of
from rag_hive.corpus.models import CorpusEntry

if TYPE_CHECKING:
    from PIL import Image

_POINTS_PER_INCH = 72


class DerivationSourceError(CorpusError):
    """A derived entry's source file is missing or unpinned, so it cannot be generated."""


def derivation_record(entry: CorpusEntry, source: CorpusEntry, source_sha256: str) -> str:
    """Return the record a derived file stores in its PDF keywords.

    Two files with the same record were generated from the same bytes, pages and settings.
    """
    if entry.derivation is None:
        msg = f"{entry.id}: not a derived entry"
        raise ValueError(msg)
    pages = source.page_range or f"1-{source.pages}"
    return (
        f"rag-hive derivation={entry.derivation.kind} source={source.id} "
        f"source_sha256={source_sha256} pages={pages} dpi={entry.derivation.dpi}"
    )


def read_keywords(path: Path) -> str:
    """Return the `Keywords` entry of a PDF's document information, or "" if absent."""
    document = pypdfium2.PdfDocument(path)
    try:
        metadata: dict[str, str] = document.get_metadata_dict()
    finally:
        document.close()
    return metadata.get("Keywords", "")


def page_count(path: Path) -> int:
    """Return the number of pages of a PDF."""
    document = pypdfium2.PdfDocument(path)
    try:
        count: int = len(document)
    finally:
        document.close()
    return count


def extract_text(path: Path) -> str:
    """Return the text layer of every page of a PDF, concatenated."""
    document = pypdfium2.PdfDocument(path)
    try:
        texts: list[str] = []
        for index in range(len(document)):
            page = document[index]
            text_page = page.get_textpage()
            texts.append(str(text_page.get_text_range()))
            text_page.close()
            page.close()
    finally:
        document.close()
    return "".join(texts)


def render_image_only(
    source_pdf: Path, pages: Sequence[int], output: Path, *, dpi: int, keywords: str
) -> None:
    """Rasterize `pages` of `source_pdf` into a new image-only PDF at `output`.

    Each page is rendered in grayscale at `dpi` and stored as one JPEG image per page, as a
    scanner would, with no text, fonts or vector content. The file is written to a temporary
    name and moved into place when complete.

    Args:
        source_pdf: The PDF to render.
        pages: 1-based page numbers to keep, in order.
        output: Where to write the image-only PDF.
        dpi: Rendering resolution; also recorded as the image resolution.
        keywords: Stored as the PDF `Keywords` entry (see `derivation_record`).

    Raises:
        ValueError: If `pages` is empty or a page is outside the source.
    """
    if not pages:
        msg = "no page to render"
        raise ValueError(msg)
    document = pypdfium2.PdfDocument(source_pdf)
    try:
        count = len(document)
        if pages[0] < 1 or pages[-1] > count:
            msg = f"{source_pdf.name} has {count} pages; cannot render {pages[0]}-{pages[-1]}"
            raise ValueError(msg)
        images: list[Image.Image] = []
        for number in pages:
            page = document[number - 1]
            bitmap = page.render(scale=dpi / _POINTS_PER_INCH, grayscale=True)
            image: Image.Image = bitmap.to_pil().convert("L")
            images.append(image)
            page.close()
    finally:
        document.close()
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name(f".{output.name}.part")
    try:
        images[0].save(
            partial,
            format="PDF",
            save_all=True,
            append_images=images[1:],
            resolution=float(dpi),
            keywords=keywords,
        )
        partial.replace(output)
    finally:
        partial.unlink(missing_ok=True)


async def ensure_derived(
    entry: CorpusEntry, source: CorpusEntry, raw_dir: Path, derived_dir: Path
) -> tuple[Path, bool]:
    """Make sure `entry`'s derived file exists and matches its source and parameters.

    The source file must already be in `raw_dir` with its pinned checksum (run after
    `ensure_document` on the source). A present derived file whose recorded derivation matches
    is kept; otherwise the file is generated again.

    Returns:
        Path of the derived file, `derived_dir / f"{entry.id}.pdf"`, and whether it was
        generated by this call.

    Raises:
        DerivationSourceError: If the source file is missing, unpinned, or does not match its
            pinned checksum.
    """
    source_path = document_path(source, raw_dir)
    if not source.sha256 or not source_path.exists():
        msg = f"{entry.id}: source {source.id} is not downloaded and pinned yet"
        raise DerivationSourceError(msg)
    source_sha256 = await asyncio.to_thread(sha256_of, source_path)
    if source_sha256 != source.sha256:
        msg = f"{entry.id}: source {source_path} does not match its pinned sha256"
        raise DerivationSourceError(msg)
    if entry.derivation is None:  # The model guarantees a derivation for derived entries.
        msg = f"{entry.id}: not a derived entry"
        raise ValueError(msg)

    path = derived_dir / f"{entry.id}.pdf"
    record = derivation_record(entry, source, source_sha256)
    if path.exists() and await asyncio.to_thread(read_keywords, path) == record:
        return path, False
    await asyncio.to_thread(
        render_image_only,
        source_path,
        source.selected_pages(),
        path,
        dpi=entry.derivation.dpi,
        keywords=record,
    )
    return path, True
