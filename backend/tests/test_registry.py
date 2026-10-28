from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_hive.core.models import ParsedDocument
from rag_hive.core.registry import (
    DuplicateComponentError,
    InvalidComponentError,
    Registry,
    UnknownComponentError,
)
from rag_hive.parsers import Parser, ParserConfig


class FakeParserConfig(ParserConfig):
    max_pages: int = 10


class FakeParser(Parser):
    name = "fake"
    config_model = FakeParserConfig

    async def parse(self, path: Path) -> ParsedDocument:
        return ParsedDocument(source_path=path, parser=self.name, elements=[])


@pytest.fixture
def registry() -> Registry[Parser]:
    return Registry("parser")


def test_register_get_and_names(registry: Registry[Parser]) -> None:
    registry.register(FakeParser)

    assert registry.get("fake") is FakeParser
    assert registry.names() == ["fake"]
    assert "fake" in registry


def test_reregistering_the_same_class_is_a_no_op(registry: Registry[Parser]) -> None:
    registry.register(FakeParser)
    registry.register(FakeParser)

    assert registry.names() == ["fake"]


def test_duplicate_name_is_rejected(registry: Registry[Parser]) -> None:
    class OtherParser(FakeParser):
        pass

    registry.register(FakeParser)
    with pytest.raises(DuplicateComponentError):
        registry.register(OtherParser)


def test_class_without_name_is_rejected(registry: Registry[Parser]) -> None:
    class NamelessParser(Parser):
        async def parse(self, path: Path) -> ParsedDocument:
            raise NotImplementedError

    with pytest.raises(InvalidComponentError):
        registry.register(NamelessParser)


def test_unknown_name_lists_registered_ones(registry: Registry[Parser]) -> None:
    registry.register(FakeParser)

    with pytest.raises(UnknownComponentError, match="fake"):
        registry.get("missing")


def test_create_validates_config(registry: Registry[Parser]) -> None:
    registry.register(FakeParser)

    parser = registry.create("fake", {"max_pages": 3})
    assert parser.config == FakeParserConfig(max_pages=3)

    with pytest.raises(ValidationError):
        registry.create("fake", {"unknown_option": 1})


def test_component_rejects_config_of_the_wrong_type() -> None:
    with pytest.raises(TypeError, match="FakeParserConfig"):
        FakeParser(ParserConfig())
