"""
Application service coordinating the debugging workflow.
"""

import time

from crew import create_debugging_crew
from observability.tracer import Tracer

from schemas.enums import (
    AgentRole,
    EventType,
    ExecutionOutcome,
)
from schemas.artifacts import SourceCodeArtifact

from config.settings import TRACE_OUTPUT

from builders.analysis_builder import AnalysisBuilder

from builders.correction_builder import CorrectionBuilder


# Order in which our 3 tasks complete under Process.sequential. Not derived
# from the Task/agent objects themselves — if task order in crew.py ever
# changes, this mapping needs to change with it.

# TODO:
# Derive the agent role from task_output when CrewAI exposes
# a stable callback API instead of relying on task order.

TASK_COMPLETION_ORDER = [
    AgentRole.ANALYZER,
    AgentRole.CORRECTOR,
    AgentRole.MANAGER,
]


class DebuggingService:
    """
    Coordinates the end-to-end debugging workflow.
    """

    def __init__(self) -> None:
        self._tracer = Tracer()

    def _make_task_callback(self):
        """
        Returns a CrewAI task_callback that records one TASK_COMPLETED
        event per finished task, tagged with the agent role responsible
        for it. This is what lets the console draw an honest pipeline
        strip instead of a single "something happened" checkmark.
        """

        state = {"index": 0, "last_perf": time.perf_counter()}

        def _on_task_complete(task_output) -> None:

            # task_output intentionally unused.
            # Current CrewAI callback API does not reliably expose the originating agent across versions.

            now = time.perf_counter()
            duration_ms = (now - state["last_perf"]) * 1000
            state["last_perf"] = now

            if state["index"] < len(TASK_COMPLETION_ORDER):
                role = TASK_COMPLETION_ORDER[state["index"]]
            else:
                role = AgentRole.MANAGER
            state["index"] += 1

            self._tracer.record_event(
                agent=role,
                event_type=EventType.TASK_COMPLETED,
                outcome=ExecutionOutcome.SUCCESS,
                message=f"{role.value.title()} task completed.",
                duration_ms=duration_ms,
            )

        return _on_task_complete

    def debug_code(self, source: SourceCodeArtifact):

        run_id = self._tracer.start_run()

        source = source.model_copy(
            update={
                "run_id": run_id,
            }
        )

        self._tracer.record_event(
            agent=AgentRole.MANAGER,
            event_type=EventType.RUN_STARTED,
            outcome=ExecutionOutcome.SUCCESS,
            message="Debugging workflow started.",
        )

        # Built per-run (not cached on self) so the task_callback's
        # ordering state starts fresh each time, and to avoid reusing a
        # CrewAI Crew instance across separate kickoff() calls.
        crew = create_debugging_crew(task_callback=self._make_task_callback())

        analysis = None
        correction = None
        verification = None

        print("=" * 80)
        print("SOURCE CODE SENT TO CREW")
        print("=" * 80)
        print(repr(source.source_code))
        print("=" * 80)

        try:
            crew_output = crew.kickoff(
                inputs={
                    "source_code": source.source_code,
                }
            )

            if crew_output.tasks_output:
                if len(crew_output.tasks_output) >= 1:
                    analysis_response = crew_output.tasks_output[0].pydantic

                    analysis = AnalysisBuilder.build(
                        response=analysis_response,
                        source=source,
                        run_id=run_id,
                    )

                    print("=" * 80)
                    print("ANALYSIS RESPONSE")
                    print("=" * 80)
                    print(analysis_response)

                    print()

                    print("=" * 80)
                    print("ANALYSIS REPORT")
                    print("=" * 80)
                    print(analysis)

                    print()

                    print("=" * 80)
                    print("ISSUES")
                    print("=" * 80)

                    for issue in analysis.issues:
                        print(issue)

                if len(crew_output.tasks_output) >= 2:

                    correction_response = crew_output.tasks_output[1].pydantic

                    correction = CorrectionBuilder.build(
                        response=correction_response,
                        source=source,
                        analysis=analysis,
                        run_id=run_id,
                    )

                    print("=" * 80)
                    print("CORRECTION RESPONSE")
                    print("=" * 80)
                    print(correction_response)

                    print()

                    print("=" * 80)
                    print("CORRECTED ARTIFACT")
                    print("=" * 80)
                    print(correction)

                if len(crew_output.tasks_output) >= 3:
                    verification = crew_output.tasks_output[2].raw

            self._tracer.record_event(
                agent=AgentRole.MANAGER,
                event_type=EventType.RUN_COMPLETED,
                outcome=ExecutionOutcome.SUCCESS,
                message="Debugging workflow completed.",
            )

        except Exception as exc:
            self._tracer.record_event(
                agent=AgentRole.MANAGER,
                event_type=EventType.ERROR,
                outcome=ExecutionOutcome.FAILURE,
                message=str(exc),
            )
            raise

        finally:
            metrics = self._tracer.end_run()
            self._tracer.export_json(TRACE_OUTPUT)

        return {
            "analysis": analysis,
            "correction": correction,
            "verification": verification,
            "metrics": metrics,
            "events": self._tracer.get_events(),
        }