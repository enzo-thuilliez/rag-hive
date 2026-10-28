"""Every module imports cleanly: the stubs are wired together without cycles or missing names."""

import importlib
import pkgutil

import pytest

import rag_hive

MODULES = sorted(
    info.name for info in pkgutil.walk_packages(rag_hive.__path__, prefix=f"{rag_hive.__name__}.")
)


def test_walk_finds_the_planned_modules() -> None:
    assert {
        "rag_hive.agents.graph",
        "rag_hive.agents.judge",
        "rag_hive.corpus.download",
        "rag_hive.embedders.sentence_transformer",
        "rag_hive.evaluation.golden",
        "rag_hive.evaluation.metrics.parsing",
        "rag_hive.evaluation.metrics.retrieval",
        "rag_hive.evaluation.span_matching",
        "rag_hive.llm.ollama",
    } <= set(MODULES)


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module: str) -> None:
    importlib.import_module(module)
