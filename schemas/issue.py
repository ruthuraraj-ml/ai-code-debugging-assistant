"""
Domain model representing a single issue detected during code analysis.
"""

from uuid import UUID, uuid4

from typing import Optional
from pydantic import Field, PositiveInt

from schemas.base import BaseSchema
from schemas.enums import (
    IssueCategory,
    IssueCode,
    IssueSeverity,
)


class Issue(BaseSchema):
    """
    Represents a single code issue identified during analysis.

    One Issue == One Problem.

    This model is intentionally immutable and framework-agnostic.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    issue_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for this issue.",
    )

    issue_code: IssueCode = IssueCode.UNKNOWN

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    category: IssueCategory = Field(
        description="High-level issue category."
    )

    severity: IssueSeverity = Field(
        description="Severity of the detected issue."
    )

    # ------------------------------------------------------------------
    # Location
    # ------------------------------------------------------------------

    line_number: Optional[PositiveInt] = Field(
        description="Line number of the issue (1-indexed)."
    )

    column_number: Optional[PositiveInt] = Field(
        default=None,
        description="Column number of the issue (1-indexed).",
    )
    
    # ------------------------------------------------------------------
    # Description
    # ------------------------------------------------------------------

    title: str = Field(
        min_length=1,
        description="Short human-readable issue title.",
    )

    details: str = Field(
        min_length=1,
        description="Detailed explanation of the issue.",
    )

    code_snippet: Optional[str] = Field(
        default=None,
        description="Relevant source code snippet.",
    )

    # ------------------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------------------

    suggested_fix: Optional[str] = Field(
        default=None,
        description="Suggested correction for the issue.",
    )

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    detection_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score assigned by the analyzer.",
    )