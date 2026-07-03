"""
Generic workflow artifacts.

These artifacts are reusable across multiple workflow stages.
"""

from typing import Optional
from pydantic import Field, computed_field

from schemas.base import ArtifactBase
from schemas.enums import (
    ArtifactType,
    CreatorType,
    Language,
)


class SourceCodeArtifact(ArtifactBase):
    """
    Represents Python source code flowing through the debugging workflow.
    """

    artifact_type: ArtifactType = ArtifactType.SOURCE_CODE

    origin: CreatorType = CreatorType.USER

    source_code: str = Field(
        min_length=1,
        description="Source code to be analyzed or corrected.",
    )

    language: Language = Field(
        default=Language.PYTHON,
        description="Programming language.",
    )

    filename: Optional[str] = Field(
        default=None,
        description="Optional filename.",
    )

    @computed_field
    @property
    def line_count(self) -> int:
        """Number of lines in the source code."""
        return len(self.source_code.splitlines())

    @computed_field
    @property
    def character_count(self) -> int:
        """Number of characters in the source code."""
        return len(self.source_code)
