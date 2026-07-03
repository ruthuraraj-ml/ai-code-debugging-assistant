"""
Code Corrector Agent.
"""

from crewai import Agent

from config.llm import get_corrector_llm


def create_corrector() -> Agent:
    """
    Creates the Code Corrector agent.
    """

    return Agent(
        role="Senior Python Code Corrector",

        goal=(
            "Correct syntax, runtime, and logical errors in Python code "
            "based on the analysis provided while preserving the original "
            "functionality and intent of the program."
        ),

        backstory=(
            "You are an experienced Python software engineer specializing "
            "in code refactoring, debugging, and software quality. You "
            "produce clean, readable, and production-ready Python code "
            "while making only the necessary corrections."
        ),

        llm=get_corrector_llm(),

        verbose=True,

        allow_delegation=False,
    )