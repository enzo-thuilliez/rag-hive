"""Corpus manifest entries: which PDFs the benchmark runs on, pinned by URL and checksum."""

from pydantic import Field, HttpUrl

from rag_hive.core.data import DataModel


class DocumentProperties(DataModel):
    """Layout features that make a PDF hard to parse. Each flag is true when present.

    Filled by hand in the manifest after inspecting the PDF, and detected by the Profiler at
    run time, so the two can be compared.
    """

    tables: bool = Field(description="Has data tables whose structure carries meaning.")
    images: bool = Field(description="Has charts, figures or photos with information in them.")
    multi_column: bool = Field(description="Body text is laid out in two or more columns.")
    scanned: bool = Field(description="Pages are images without a text layer; needs OCR.")
    formulas: bool = Field(description="Has mathematical notation beyond inline numbers.")


class CorpusEntry(DataModel):
    """One document of the benchmark corpus, pinned to an exact version.

    The PDF itself is never committed (redistribution rights): `make corpus` downloads it from
    `url` and refuses it unless its SHA-256 matches `sha256`.
    """

    id: str = Field(
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Stable kebab-case slug; golden sets and results reference it.",
    )
    title: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    url: HttpUrl = Field(description="Direct download URL of the pinned version.")
    sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$", description="Lowercase hex SHA-256 of the PDF bytes."
    )
    pages: int = Field(ge=1)
    language: str = Field(
        pattern=r"^[a-z]{2}$", description="ISO 639-1 code of the main language, e.g. `en`."
    )
    properties: DocumentProperties
    notes: str = Field(default="", description="Anything a benchmark reader should know.")
