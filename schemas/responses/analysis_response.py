"""
Lightweight response schema produced by the Analyzer agent.

These models intentionally contain only the information that an LLM
can reliably reason about.

Application metadata (UUIDs, timestamps, artifact IDs, etc.)
is added later by the AnalysisBuilder.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ExecutionResultResponse(BaseModel):
    """
    Result returned by the Code Interpreter tool.
    """

    executed: bool

    success: bool

    stdout: str = ""

    stderr: str = ""

    exception: Optional[str] = None


class IssueResponse(BaseModel):
    """
    Lightweight issue description.
    """

    title: str

    description: str

    line_number: Optional[int] = None

    suggested_fix: Optional[str] = None


class AnalysisResponse(BaseModel):
    """
    Analyzer output returned by CrewAI.
    """

    issues: list[IssueResponse] = Field(
        default_factory=list
    )

    summary: str

    execution_result: ExecutionResultResponse