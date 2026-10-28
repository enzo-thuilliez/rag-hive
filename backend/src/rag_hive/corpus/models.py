"""Corpus manifest entries: which PDFs the benchmark runs on, pinned by URL and checksum."""

from typing import Literal, Self

from pydantic import Field, HttpUrl, model_validator

from rag_hive.core.data import DataModel

type DownloadMode = Literal["auto", "manual", "derived"]
"""`auto`: `make corpus` downloads `url`. `manual`: the source sits behind a login, cookie wall,
disclaimer or bot block, so a person downloads it by following `instructions`. `derived`:
`make corpus` generates the file from another entry, as described by `derivation`."""

type DerivationKind = Literal["image_only"]
"""`image_only`: the source's selected pages rasterized into a PDF with no text layer."""

_PAGE_RANGE_PATTERN = r"^[1-9][0-9]*(-[1-9][0-9]*)?(,[1-9][0-9]*(-[1-9][0-9]*)?)*$"


def parse_page_range(spec: str) -> list[int]:
    """Expand a page range such as `"20-31,141-154,163"` into its 1-based page numbers.

    Args:
        spec: Comma-separated pages or inclusive `start-end` ranges, ascending and
            non-overlapping.

    Returns:
        Every selected page, in ascending order.

    Raises:
        ValueError: If a range is reversed, or ranges are not ascending and disjoint.
    """
    pages: list[int] = []
    for part in spec.split(","):
        start_text, _, end_text = part.partition("-")
        start = int(start_text)
        end = int(end_text) if end_text else start
        if end < start:
            msg = f"page range {part!r} ends before it starts"
            raise ValueError(msg)
        if pages and start <= pages[-1]:
            msg = f"page range {spec!r} must list ascending, non-overlapping ranges"
            raise ValueError(msg)
        pages.extend(range(start, end + 1))
    return pages


class DocumentProperties(DataModel):
    """Layout features that make a PDF hard to parse. Each flag is true when present.

    Filled by hand in the manifest after inspecting the PDF, and detected by the Profiler at
    run time, so the two can be compared.
    """

    tables: bool = Field(description="Has data tables whose structure carries meaning.")
    images: bool = Field(description="Has charts, figures or photos with information in them.")
    multi_column: bool = Field(description="Body text is laid out in two or more columns.")
    scanned: bool = Field(
        description="Pages are scanned images; any text layer comes from OCR, not the source."
    )
    formulas: bool = Field(description="Has mathematical notation beyond inline numbers.")


class Derivation(DataModel):
    """How a `derived` entry's file is generated from its source entry."""

    kind: DerivationKind
    source: str = Field(description="`id` of the entry the file is generated from.")
    dpi: int = Field(default=200, ge=72, le=600, description="Rasterization resolution.")


class CorpusEntry(DataModel):
    """One document of the benchmark corpus, pinned to an exact version.

    The PDF itself is never committed (redistribution rights). `make corpus` downloads `auto`
    entries from `url`, checks every file present against `sha256`, prints `instructions` for
    each `manual` entry whose file is missing, and generates `derived` entries from their
    source. A `manual` entry may leave `sha256` empty until someone has downloaded and
    inspected the file; `pages` and `properties` stay unset until then too. A `derived` entry
    has no `sha256`: its bytes depend on the rasterizer's version, so it is checked against
    the source checksum and parameters it was generated from instead.
    """

    id: str = Field(
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Stable kebab-case slug; golden sets and results reference it.",
    )
    title: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    download: DownloadMode = "auto"
    url: HttpUrl | None = Field(
        default=None, description="Direct download URL of the pinned version. `auto` only."
    )
    source_page: HttpUrl | None = Field(
        default=None, description="Page a person downloads the file from. `manual` only."
    )
    instructions: str | None = Field(
        default=None, min_length=1, description="One line on what to download there. `manual` only."
    )
    derivation: Derivation | None = Field(
        default=None, description="How the file is generated. `derived` only."
    )
    sha256: str = Field(
        default="",
        pattern=r"^([0-9a-f]{64})?$",
        description="Lowercase hex SHA-256 of the PDF bytes. Empty: not pinned yet (`manual`) "
        "or generated (`derived`).",
    )
    pages: int | None = Field(
        default=None, ge=1, description="Pages in the file. Set once the file is pinned."
    )
    page_range: str | None = Field(
        default=None,
        pattern=_PAGE_RANGE_PATTERN,
        description="Pages the benchmark uses, e.g. `20-31,141-154`, 1-based and inclusive. "
        "None: every page. The file itself stays whole.",
    )
    language: str = Field(
        pattern=r"^[a-z]{2}$", description="ISO 639-1 code of the main language, e.g. `en`."
    )
    properties: DocumentProperties | None = Field(
        default=None, description="Set once the file is pinned and inspected."
    )
    notes: str = Field(default="", description="Anything a benchmark reader should know.")

    def selected_pages(self) -> list[int]:
        """Return the 1-based pages the benchmark uses: `page_range`, or every page.

        Raises:
            ValueError: If `page_range` is None and `pages` is not known yet.
        """
        if self.page_range is not None:
            return parse_page_range(self.page_range)
        if self.pages is None:
            msg = f"{self.id}: page count unknown until the entry is pinned"
            raise ValueError(msg)
        return list(range(1, self.pages + 1))

    @model_validator(mode="after")
    def _check_download_fields(self) -> Self:
        """Each mode has its own required fields, and a pinned file has been inspected."""
        given = {
            "url": self.url is not None,
            "source_page": self.source_page is not None,
            "instructions": self.instructions is not None,
            "derivation": self.derivation is not None,
        }
        required = {
            "auto": {"url"},
            "manual": {"source_page", "instructions"},
            "derived": {"derivation"},
        }[self.download]
        missing = sorted(name for name in required if not given[name])
        extra = sorted(name for name, present in given.items() if present and name not in required)
        if missing or extra:
            msg = (
                f"{self.id}: {self.download} entries need {', '.join(sorted(required))}"
                f" and none of {', '.join(sorted(set(given) - required))}"
            )
            raise ValueError(msg)
        if self.download == "auto" and not self.sha256:
            msg = f"{self.id}: an auto entry needs `sha256`"
            raise ValueError(msg)
        if self.download == "derived":
            self._check_derived()
        if self.sha256 and (self.pages is None or self.properties is None):
            msg = f"{self.id}: a pinned entry (sha256 set) needs `pages` and `properties`"
            raise ValueError(msg)
        self._check_page_range()
        return self

    def _check_derived(self) -> None:
        """A derived entry is generated, so it has no checksum, but it is fully described."""
        if self.sha256:
            msg = f"{self.id}: a derived entry has no `sha256`; it is regenerated, not pinned"
            raise ValueError(msg)
        if self.pages is None or self.properties is None:
            msg = f"{self.id}: a derived entry needs `pages` and `properties`"
            raise ValueError(msg)
        if self.page_range is not None:
            msg = f"{self.id}: a derived entry uses its source's `page_range`, not its own"
            raise ValueError(msg)

    def _check_page_range(self) -> None:
        """`page_range` is well formed and stays within the file's pages when known."""
        if self.page_range is None:
            return
        selected = parse_page_range(self.page_range)
        if self.pages is not None and selected[-1] > self.pages:
            msg = f"{self.id}: page_range goes up to {selected[-1]}, the file has {self.pages}"
            raise ValueError(msg)


class CorpusManifest(DataModel):
    """The whole manifest file: every corpus document, with unique ids."""

    documents: list[CorpusEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def _check_unique_ids(self) -> Self:
        """Two entries cannot share an id: files and golden sets are keyed by it."""
        ids = [entry.id for entry in self.documents]
        duplicates = sorted({entry_id for entry_id in ids if ids.count(entry_id) > 1})
        if duplicates:
            msg = f"duplicate corpus ids: {', '.join(duplicates)}"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_derivations(self) -> Self:
        """Each derived entry names a non-derived source and has one page per selected page."""
        by_id = {entry.id: entry for entry in self.documents}
        for entry in self.documents:
            if entry.derivation is None:
                continue
            source = by_id.get(entry.derivation.source)
            if source is None or source.derivation is not None:
                msg = f"{entry.id}: derived from {entry.derivation.source!r}, not a source entry"
                raise ValueError(msg)
            if source.page_range is None and source.pages is None:
                continue  # Source not pinned yet: its page count is unknown.
            expected = len(source.selected_pages())
            if entry.pages != expected:
                msg = f"{entry.id}: has {entry.pages} pages, its source selects {expected}"
                raise ValueError(msg)
        return self
