from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from rag_hive.config import REPO_ROOT
from rag_hive.corpus.manifest import load_manifest

MANIFEST = REPO_ROOT / "data" / "corpus" / "manifest.yaml"


def test_committed_manifest_is_valid() -> None:
    entries = load_manifest(MANIFEST)

    assert len(entries) == 11
    assert entries[0].id == "msci-gimi-methodology"


def test_committed_manifest_pins_every_auto_entry() -> None:
    for entry in load_manifest(MANIFEST):
        if entry.download == "auto":
            assert entry.sha256, entry.id
            assert entry.properties is not None, entry.id


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    documents = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["documents"]
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump({"documents": [documents[0], documents[0]]}), encoding="utf-8")

    with pytest.raises(ValidationError, match="duplicate corpus ids: msci-gimi-methodology"):
        load_manifest(path)


def test_missing_manifest_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_manifest(tmp_path / "manifest.yaml")


def test_committed_manifest_derives_the_fraser_scan_from_its_page_range() -> None:
    by_id = {entry.id: entry for entry in load_manifest(MANIFEST)}
    derived = by_id["frb-annual-report-1920-image-only"]

    assert derived.derivation is not None
    source = by_id[derived.derivation.source]
    assert source.page_range is not None
    assert len(source.selected_pages()) == derived.pages == 40
