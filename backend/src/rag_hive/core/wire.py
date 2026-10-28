"""Base model for everything sent to the frontend."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class WireModel(BaseModel):
    """Immutable model serialized as camelCase JSON.

    Python code uses snake_case field names; the JSON on the wire (and the TypeScript mirror in
    `frontend/src/api/`) uses camelCase. Both spellings are accepted on input.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        frozen=True,
        extra="forbid",
        # Defaults are always serialized, so the exported schema marks them required.
        json_schema_serialization_defaults_required=True,
    )
