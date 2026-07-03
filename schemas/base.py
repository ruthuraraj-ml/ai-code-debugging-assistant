"""
Base schema definitions shared across the application.

These models provide common metadata for artifacts and execution records while
remaining independent of CrewAI or any infrastructure layer.
"""

from typing import Optional
from datetime import datetime, UTC
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from schemas.enums import ArtifactType, CreatorType


class BaseSchema(BaseModel):
    """Common base model for all domain schemas."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        use_enum_values=True,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the object was created.",
    )


class ArtifactBase(BaseSchema):
    """Base class for all workflow artifacts."""

    artifact_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for this artifact.",
    )

    run_id: Optional[UUID] = Field(
        description="Identifier of the debugging session.",
    )

    artifact_type: ArtifactType

    origin: Optional[CreatorType] = Field(
        default=None,
        description="Entity responsible for creating this artifact.",
    )


class ExecutionBase(BaseSchema):
    """Base class for execution-related records."""

    event_id: UUID = Field(
        default_factory=uuid4,
        description="Unique execution event identifier.",
    )

    run_id: UUID = Field(
        description="Identifier of the debugging session."
    )