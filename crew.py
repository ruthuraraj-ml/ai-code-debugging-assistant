"""
Crew assembly.
"""

from crewai import Crew, Process

from agents.analyzer import create_analyzer
from agents.corrector import create_corrector
from agents.manager import create_manager

from tasks.analysis import create_analysis_task
from tasks.correction import create_correction_task
from tasks.verification import create_verification_task

from config.llm import get_manager_llm


def create_debugging_crew(task_callback=None) -> Crew:
    """
    Creates the Automated Code Debugging Crew.

    task_callback, if provided, is invoked by CrewAI with the TaskOutput
    after each task finishes — used by DebuggingService to emit
    TASK_COMPLETED trace events per stage.
    """

    # ---------------------------------------------------------
    # Agents
    # ---------------------------------------------------------

    analyzer = create_analyzer()
    corrector = create_corrector()
    manager = create_manager()

    # ---------------------------------------------------------
    # Tasks
    # ---------------------------------------------------------

    analysis_task = create_analysis_task(analyzer)

    correction_task = create_correction_task(corrector)
    correction_task.context = [analysis_task]

    verification_task = create_verification_task(manager)
    verification_task.context = [
        analysis_task,
        correction_task,
    ]

    # ---------------------------------------------------------
    # Crew
    # ---------------------------------------------------------

    return Crew(
        agents=[
            manager,
            analyzer,
            corrector,
        ],
        tasks=[
            analysis_task,
            correction_task,
            verification_task,
        ],
        process=Process.sequential,
        planning=True,
        planning_llm=get_manager_llm(),
        verbose=True,
        task_callback=task_callback,
    )