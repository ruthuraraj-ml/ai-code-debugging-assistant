"""
Lightweight observability tracer for the debugging workflow.
"""

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from schemas.enums import (
    AgentRole,
    EventType,
    ExecutionOutcome,
)
from schemas.observability import (
    ExecutionEvent,
    RunMetrics,
)


class Tracer:
    """
    Records workflow execution events and produces run metrics.
    """

    def __init__(self) -> None:
        self._run_id: UUID | None = None

        self._start_time: datetime | None = None
        self._end_time: datetime | None = None

        self._start_perf: float | None = None

        self._events: list[ExecutionEvent] = []
        self._metrics: RunMetrics | None = None

    def start_run(self) -> UUID:
        """
        Starts a new tracing session.
        """
        self._run_id = uuid4()

        self._start_time = datetime.now(UTC)
        self._end_time = None

        self._start_perf = time.perf_counter()

        self._events.clear()
        self._metrics = None

        return self._run_id

    def record_event(
        self,
        *,
        agent: AgentRole,
        event_type: EventType,
        outcome: ExecutionOutcome,
        message: str,
        duration_ms: float | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """
        Records a workflow execution event.
        """

        if self._run_id is None:
            raise RuntimeError("Run has not been started.")

        event = ExecutionEvent(
            run_id=self._run_id,
            agent=agent,
            event_type=event_type,
            outcome=outcome,
            message=message,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )

        self._events.append(event)

    def end_run(self) -> RunMetrics:
        """
        Ends the tracing session and computes execution metrics.
        """

        if (
            self._run_id is None
            or self._start_time is None
            or self._start_perf is None
        ):
            raise RuntimeError("Run has not been started.")

        self._end_time = datetime.now(UTC)

        execution_time_ms = (
            time.perf_counter() - self._start_perf
        ) * 1000

        self._metrics = RunMetrics(
            run_id=self._run_id,
            total_events=len(self._events),
            execution_time_ms=execution_time_ms,
        )

        return self._metrics

    def get_events(self) -> list[ExecutionEvent]:
        """
        Returns all recorded execution events.
        """
        return self._events

    def get_metrics(self) -> RunMetrics | None:
        """
        Returns computed run metrics.
        """
        return self._metrics

    def export_json(self, filepath: str | Path) -> None:
        """
        Exports trace information to a JSON file.
        """

        if self._metrics is None:
            raise RuntimeError("Run has not been completed.")

        filepath = Path(filepath)

        payload = {
            "run_id": str(self._run_id),
            "metrics": self._metrics.model_dump(mode="json"),
            "events": [
                event.model_dump(mode="json")
                for event in self._events
            ],
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with filepath.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4)