"""Base model for snake_case data that is not a wire type (repo files, agent state)."""

from pydantic import BaseModel, ConfigDict


class DataModel(BaseModel):
    """Immutable model for hand-written files (corpus manifest, golden sets) and agent state.

    Unlike `WireModel`, keys stay snake_case, so a YAML file, the Python model and the exported
    JSON Schema (`make schema`) all use the same spelling. Unknown keys are rejected so a typo
    in a hand-written file fails validation instead of being dropped.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")
