"""
Observability models used to trace and summarize workflow execution.
"""

from typing import Optional
from pydantic import Field

from schemas.base import ExecutionBase
from schemas.enums import (
    AgentRole,
    EventType,
    ExecutionOutcome,
)


class ExecutionEvent(ExecutionBase):
    """
    Represents a single event occurring during workflow execution.
    """

    agent: AgentRole = Field(
        description="Agent associated with this event.",
    )

    event_type: EventType = Field(
        description="Type of execution event.",
    )

    outcome: ExecutionOutcome = Field(
        description="Outcome of the execution event.",
    )

    message: str = Field(
        min_length=1,
        description="Human-readable event description.",
    )

    duration_ms: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Execution duration in milliseconds.",
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Additional event metadata.",
    )


class RunMetrics(ExecutionBase):
    """
    Aggregated metrics for a debugging session.
    """

    total_agents: int = Field(
        default=0,
        ge=0,
    )

    total_tasks: int = Field(
        default=0,
        ge=0,
    )

    tool_calls: int = Field(
        default=0,
        ge=0,
    )

    total_events: int = Field(
        default=0,
        ge=0,
    )

    execution_time_ms: float = Field(
        default=0.0,
        ge=0.0,
    )

    issues_found: int = Field(
        default=0,
        ge=0,
    )

    issues_fixed: int = Field(
        default=0,
        ge=0,
    )