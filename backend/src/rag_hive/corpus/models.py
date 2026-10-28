"""Corpus manifest entries: which PDFs the benchmark runs on, pinned by URL and checksum."""

from typing import Literal, Self

from pydantic import Field, HttpUrl, model_validator

from rag_hive.core.data import DataModel

type DownloadMode = Literal["auto", "manual"]
"""`auto`: `make corpus` downloads `url`. `manual`: the source sits behind a login, cookie wall,
disclaimer or bot block, so a person downloads it by following `instructions`."""


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


class CorpusEntry(DataModel):
    """One document of the benchmark corpus, pinned to an exact version.

    The PDF itself is never committed (redistribution rights). `make corpus` downloads `auto`
    entries from `url`, checks every file present against `sha256`, and prints `instructions`
    for each `manual` entry whose file is missing. A `manual` entry may leave `sha256` empty
    until someone has downloaded and inspected the file; `pages` and `properties` stay unset
    until then too.
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
    sha256: str = Field(
        pattern=r"^([0-9a-f]{64})?$",
        description="Lowercase hex SHA-256 of the PDF bytes. Empty: not pinned yet (`manual`).",
    )
    pages: int | None = Field(default=None, ge=1, description="Set once the file is pinned.")
    language: str = Field(
        pattern=r"^[a-z]{2}$", description="ISO 639-1 code of the main language, e.g. `en`."
    )
    properties: DocumentProperties | None = Field(
        default=None, description="Set once the file is pinned and inspected."
    )
    notes: str = Field(default="", description="Anything a benchmark reader should know.")

    @model_validator(mode="after")
    def _check_download_fields(self) -> Self:
        """Each mode has its own required fields, and a pinned file has been inspected."""
        if self.download == "auto":
            if self.url is None or not self.sha256:
                msg = f"{self.id}: an auto entry needs `url` and `sha256`"
                raise ValueError(msg)
            if self.source_page is not None or self.instructions is not None:
                msg = f"{self.id}: `source_page` and `instructions` are for manual entries"
                raise ValueError(msg)
        else:
            if self.source_page is None or self.instructions is None:
                msg = f"{self.id}: a manual entry needs `source_page` and `instructions`"
                raise ValueError(msg)
            if self.url is not None:
                msg = f"{self.id}: a manual entry has no direct `url`; use `source_page`"
                raise ValueError(msg)
        if self.sha256 and (self.pages is None or self.properties is None):
            msg = f"{self.id}: a pinned entry (sha256 set) needs `pages` and `properties`"
            raise ValueError(msg)
        return self


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
