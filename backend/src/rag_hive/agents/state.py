"""The LangGraph state shared by the workflow's nodes.

Each node declares the subset it reads as its own input model (`ProfilerInput`...) and returns
only the keys it writes (`ProfilerUpdate`...), so agent modules never depend on this module.
"""

import operator
from pathlib import Path
from typing import Annotated

from pydantic import Field

from rag_hive.agents.judge import Scores
from rag_hive.agents.planner import Plan
from rag_hive.agents.profiler import DocumentProfile
from rag_hive.agents.qa_generator import QuestionSet
from rag_hive.agents.reporter import Report
from rag_hive.agents.worker import WorkerOutput
from rag_hive.core.data import DataModel
from rag_hive.evaluation.golden import GoldenQuestion


class WorkflowState(DataModel):
    """Everything a run knows, filled in agent by agent.

    The first four fields are set when the run starts; each later field is written by one
    agent and stays None (or empty) until that agent has run.
    """

    run_id: str
    document_id: str = Field(description="`CorpusEntry.id`, or a slug of the uploaded file.")
    pdf_path: Path
    ks: list[int] = Field(min_length=1, description="Cut-offs the retrieval metrics use.")
    golden_set: list[GoldenQuestion] = Field(default_factory=list)

    profile: DocumentProfile | None = None
    plan: Plan | None = None
    question_set: QuestionSet | None = None
    worker_outputs: Annotated[list[WorkerOutput], operator.add] = Field(
        default_factory=list, description="One per config; parallel workers append to it."
    )
    scores: Scores | None = None
    report: Report | None = None
