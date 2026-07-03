"""
Execution-related domain models.

These models represent the outcome of executing Python code and are shared
between the analysis and verification stages.
"""

from typing import Optional
from pydantic import Field

from schemas.base import BaseSchema


class ExecutionResult(BaseSchema):
    """
    Represents the result of executing Python code.
    """

    executed: bool = Field(
        description="Whether execution was attempted."
    )

    success: bool = Field(
        description="Whether execution completed successfully."
    )

    exit_code: Optional[int] = Field(
        default=None,
        description="Interpreter exit code if available.",
    )

    stdout: Optional[str] = Field(
        default=None,
        description="Captured standard output.",
    )

    stderr: Optional[str] = Field(
        default=None,
        description="Captured standard error.",
    )

    exception: Optional[str] = Field(
        default=None,
        description="Exception message if execution failed.",
    )

    execution_time_ms: Optional[float] = Field(
        default=None,
        ge=0,
        description="Execution time in milliseconds.",
    )

    interpreter: Optional[str] = Field(
        default=None,
        description="Python interpreter version used.",
    )