import pytest
from pydantic import ValidationError

from rag_hive.corpus.models import CorpusEntry, CorpusManifest
from rag_hive.evaluation.golden import GoldenQuestion

SHA = "a" * 64


def corpus_entry(**overrides: object) -> dict[str, object]:
    entry: dict[str, object] = {
        "id": "msci-gimi-methodology",
        "title": "MSCI Global Investable Market Indexes Methodology",
        "publisher": "MSCI",
        "url": "https://example.com/methodology.pdf",
        "sha256": SHA,
        "pages": 120,
        "language": "en",
        "properties": {
            "tables": True,
            "images": False,
            "multi_column": False,
            "scanned": False,
            "formulas": True,
        },
    }
    return entry | overrides


def golden_question(**overrides: object) -> dict[str, object]:
    question: dict[str, object] = {
        "id": "msci-free-float",
        "document_id": "msci-gimi-methodology",
        "question": "What is the minimum free float requirement?",
        "answer": "15%",
        "type": "factual",
        "difficulty": "easy",
        "expected_passages": [{"page": 12, "text": "a minimum free float of 15%"}],
    }
    return question | overrides


def test_corpus_entry_accepts_a_valid_entry() -> None:
    entry = CorpusEntry.model_validate(corpus_entry())

    assert entry.properties is not None
    assert entry.properties.formulas
    assert entry.download == "auto"
    assert entry.notes == ""


@pytest.mark.parametrize(
    "overrides",
    [
        {"id": "MSCI Methodology"},
        {"sha256": "A" * 64},
        {"sha256": "a" * 63},
        {"pages": 0},
        {"language": "eng"},
        {"url": "not a url"},
        {"unexpected": "key"},
    ],
)
def test_corpus_entry_rejects_invalid_fields(overrides: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        CorpusEntry.model_validate(corpus_entry(**overrides))


def manual_entry(**overrides: object) -> dict[str, object]:
    entry = corpus_entry(
        download="manual",
        url=None,
        source_page="https://example.com/documents",
        instructions="Accept the disclaimer and download the PDF.",
        sha256="",
        pages=None,
        properties=None,
    )
    return entry | overrides


def derived_entry(**overrides: object) -> dict[str, object]:
    entry = corpus_entry(
        id="msci-image-only",
        download="derived",
        url=None,
        sha256="",
        pages=3,
        derivation={"kind": "image_only", "source": "msci-gimi-methodology"},
    )
    return entry | overrides


def test_page_range_selects_listed_pages() -> None:
    entry = CorpusEntry.model_validate(corpus_entry(page_range="2-4,7,10-11"))

    assert entry.selected_pages() == [2, 3, 4, 7, 10, 11]


def test_without_page_range_every_page_is_selected() -> None:
    entry = CorpusEntry.model_validate(corpus_entry(pages=3))

    assert entry.selected_pages() == [1, 2, 3]


@pytest.mark.parametrize("page_range", ["", "0-3", "1-", "a-b", "1 - 3", "1,,2"])
def test_malformed_page_range_is_rejected(page_range: str) -> None:
    with pytest.raises(ValidationError):
        CorpusEntry.model_validate(corpus_entry(page_range=page_range))


def test_derived_entry_defaults_to_200_dpi() -> None:
    entry = CorpusEntry.model_validate(derived_entry())

    assert entry.derivation is not None
    assert entry.derivation.dpi == 200
    assert entry.sha256 == ""


def test_manifest_rejects_a_derivation_of_an_unknown_source() -> None:
    with pytest.raises(ValidationError, match="not a source entry"):
        CorpusManifest.model_validate(
            {
                "documents": [
                    corpus_entry(),
                    derived_entry(derivation={"kind": "image_only", "source": "nowhere"}),
                ]
            }
        )


def test_manifest_rejects_a_derived_page_count_unlike_its_source() -> None:
    source = corpus_entry(page_range="1-5")

    with pytest.raises(ValidationError, match="has 3 pages, its source selects 5"):
        CorpusManifest.model_validate({"documents": [source, derived_entry()]})


def test_manifest_accepts_a_matching_derivation() -> None:
    source = corpus_entry(page_range="1-3")

    manifest = CorpusManifest.model_validate({"documents": [source, derived_entry()]})

    assert [entry.download for entry in manifest.documents] == ["auto", "derived"]


def test_unpinned_manual_entry_needs_no_pages_or_properties() -> None:
    entry = CorpusEntry.model_validate(manual_entry())

    assert entry.sha256 == ""
    assert entry.properties is None


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (corpus_entry(url=None), "auto entries need url"),
        (corpus_entry(sha256=""), "an auto entry needs `sha256`"),
        (corpus_entry(instructions="Click here."), "auto entries need url and none of"),
        (manual_entry(instructions=None), "manual entries need instructions, source_page"),
        (manual_entry(url="https://example.com/doc.pdf"), "manual entries need"),
        (manual_entry(sha256=SHA), "needs `pages` and `properties`"),
        (derived_entry(url="https://example.com/doc.pdf"), "derived entries need derivation"),
        (derived_entry(derivation=None), "derived entries need derivation"),
        (derived_entry(sha256=SHA), "has no `sha256`"),
        (derived_entry(pages=None), "needs `pages` and `properties`"),
        (derived_entry(page_range="1-2"), "uses its source's `page_range`"),
        (corpus_entry(page_range="100-130"), "goes up to 130, the file has 120"),
        (corpus_entry(page_range="5-3"), "ends before it starts"),
        (corpus_entry(page_range="1-5,4-8"), "ascending, non-overlapping"),
    ],
)
def test_corpus_entry_fields_must_match_download_mode(
    payload: dict[str, object], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        CorpusEntry.model_validate(payload)


def test_corpus_entry_requires_every_property() -> None:
    properties = {"tables": True, "images": False, "multi_column": False, "formulas": False}

    with pytest.raises(ValidationError):
        CorpusEntry.model_validate(corpus_entry(properties=properties))


def test_corpus_entry_is_immutable() -> None:
    entry = CorpusEntry.model_validate(corpus_entry())

    with pytest.raises(ValidationError):
        entry.pages = 1  # type: ignore[misc]


def test_golden_question_accepts_a_valid_question() -> None:
    question = GoldenQuestion.model_validate(golden_question())

    assert question.expected_passages[0].page == 12


def test_unanswerable_question_needs_no_passage() -> None:
    question = GoldenQuestion.model_validate(
        golden_question(type="unanswerable", answer="Not covered.", expected_passages=[])
    )

    assert question.expected_passages == []


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"type": "unanswerable"}, "cannot have expected passages"),
        ({"expected_passages": []}, "at least 1"),
        ({"type": "multi_hop"}, "at least 2"),
    ],
)
def test_golden_question_passages_must_match_type(
    overrides: dict[str, object], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        GoldenQuestion.model_validate(golden_question(**overrides))


@pytest.mark.parametrize(
    "overrides",
    [
        {"type": "opinion"},
        {"difficulty": "trivial"},
        {"expected_passages": [{"page": 0, "text": "x"}]},
        {"expected_passages": [{"page": 1, "text": ""}]},
    ],
)
def test_golden_question_rejects_invalid_fields(overrides: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        GoldenQuestion.model_validate(golden_question(**overrides))
