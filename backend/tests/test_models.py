import pytest
from pydantic import ValidationError

from rag_hive.corpus.models import CorpusEntry
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


def test_unpinned_manual_entry_needs_no_pages_or_properties() -> None:
    entry = CorpusEntry.model_validate(manual_entry())

    assert entry.sha256 == ""
    assert entry.properties is None


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (corpus_entry(url=None), "needs `url` and `sha256`"),
        (corpus_entry(sha256=""), "needs `url` and `sha256`"),
        (corpus_entry(instructions="Click here."), "are for manual entries"),
        (manual_entry(instructions=None), "needs `source_page` and `instructions`"),
        (manual_entry(url="https://example.com/doc.pdf"), "has no direct `url`"),
        (manual_entry(sha256=SHA), "needs `pages` and `properties`"),
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
