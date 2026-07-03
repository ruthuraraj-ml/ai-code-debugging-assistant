"""
Analysis report artifact produced by the Code Analyzer agent.
"""

from typing import Optional
from pydantic import Field, computed_field

from schemas.base import ArtifactBase
from schemas.enums import (
    ArtifactType,
    CreatorType,
    IssueCategory,
    IssueSeverity,
)
from schemas.execution import ExecutionResult
from schemas.issue import Issue


class AnalysisReport(ArtifactBase):
    """
    Artifact generated after analyzing Python source code.

    Contains all detected issues together with execution results and
    high-level analysis information.
    """

    artifact_type: ArtifactType = ArtifactType.ANALYSIS_REPORT

    origin: CreatorType = CreatorType.ANALYZER

    issues: list[Issue] = Field(
        default_factory=list,
        description="Issues detected during analysis.",
    )

    summary: Optional[str] = Field(
        default=None,
        description="High-level analysis summary.",
    )

    analysis_notes: Optional[str] = Field(
        default=None,
        description="Additional observations from the analysis process.",
    )

    execution_result: Optional[ExecutionResult] = Field(
        default=None,
        description="Execution details captured during analysis.",
    )

    detection_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the analysis.",
    )

    # ---------------------------------------------------------
    # Computed Statistics
    # ---------------------------------------------------------

    @computed_field
    @property
    def total_issues(self) -> int:
        return len(self.issues)

    @computed_field
    @property
    def critical_issue_count(self) -> int:
        return sum(
            issue.severity == IssueSeverity.CRITICAL
            for issue in self.issues
        )

    @computed_field
    @property
    def error_count(self) -> int:
        return sum(
            issue.severity == IssueSeverity.ERROR
            for issue in self.issues
        )

    @computed_field
    @property
    def warning_count(self) -> int:
        return sum(
            issue.severity == IssueSeverity.WARNING
            for issue in self.issues
        )

    @computed_field
    @property
    def syntax_issue_count(self) -> int:
        return sum(
            issue.category == IssueCategory.SYNTAX
            for issue in self.issues
        )

    @computed_field
    @property
    def runtime_issue_count(self) -> int:
        return sum(
            issue.category == IssueCategory.RUNTIME
            for issue in self.issues
        )

    @computed_field
    @property
    def logic_issue_count(self) -> int:
        return sum(
            issue.category == IssueCategory.LOGIC
            for issue in self.issues
        )

    # ---------------------------------------------------------
    # Computed Flags
    # ---------------------------------------------------------

    @computed_field
    @property
    def has_issues(self) -> bool:
        return self.total_issues > 0

    @computed_field
    @property
    def has_critical_issues(self) -> bool:
        return self.critical_issue_count > 0

    @computed_field
    @property
    def has_runtime_issues(self) -> bool:
        return self.runtime_issue_count > 0

    @computed_field
    @property
    def has_syntax_issues(self) -> bool:
        return self.syntax_issue_count > 0
    