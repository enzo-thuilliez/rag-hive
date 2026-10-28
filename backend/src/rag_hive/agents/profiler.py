"""Profiler: the first agent. Describes the PDF so the Planner can pick fitting pipelines."""

from pathlib import Path
from typing import TypedDict

from pydantic import Field

from rag_hive.core.data import DataModel
from rag_hive.corpus.models import DocumentProperties


class ProfilerInput(DataModel):
    """What the Profiler reads from the workflow state."""

    run_id: str
    pdf_path: Path


class DocumentProfile(DataModel):
    """What the document looks like, measured rather than guessed where possible."""

    pages: int = Field(ge=1)
    language: str = Field(pattern=r"^[a-z]{2}$", description="ISO 639-1 code.")
    chars_per_page: float = Field(
        ge=0, description="Mean extractable characters per page; near 0 means scanned."
    )
    properties: DocumentProperties = Field(
        description="Same flags as the corpus manifest, so detection can be checked against it."
    )
    notes: str = Field(default="", description="Anything else the Planner should know.")


class ProfilerUpdate(TypedDict):
    """State keys the Profiler node writes."""

    profile: DocumentProfile


async def run_profiler(inp: ProfilerInput) -> DocumentProfile:
    """Profile the PDF: page count, language, text density and layout properties.

    Cheap checks (text layer, page count) come from a fast parser; the LLM only labels what
    heuristics cannot, such as the language. Emits `agent_started`, then `result` or `error`.
    """
    raise NotImplementedError


async def profiler_node(state: ProfilerInput) -> ProfilerUpdate:
    """LangGraph node: run the Profiler on the state's PDF and store `profile`."""
    raise NotImplementedError
