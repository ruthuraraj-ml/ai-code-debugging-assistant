"""
Workflow Manager Agent.
"""

from crewai import Agent

from config.llm import get_manager_llm


def create_manager() -> Agent:
    """
    Creates the Manager agent responsible for coordinating the
    debugging workflow.
    """

    return Agent(
        role="AI Debugging Workflow Manager",

        goal=(
            "Plan, coordinate, and supervise the automated code debugging "
            "workflow by ensuring the analyzer and corrector collaborate "
            "effectively to produce accurate and reliable results."
        ),

        backstory=(
            "You are an experienced software engineering manager with "
            "expertise in AI-assisted development workflows. Your role is "
            "to coordinate specialists, review their outputs, ensure task "
            "completion, and maintain the overall quality of the debugging "
            "process."
        ),

        llm=get_manager_llm(),

        verbose=True,

        allow_delegation=True,
    )