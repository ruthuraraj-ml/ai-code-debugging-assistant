"""
Verification task definition.
"""

from crewai import Task


def create_verification_task(manager) -> Task:
    """
    Creates the verification task.
    """

    return Task(
        description="""
Review the analysis and corrected code.

Verify that:

1. All reported issues were addressed.
2. The corrected code is internally consistent.
3. The debugging workflow completed successfully.

Provide a concise debugging session summary.
""",

        expected_output="""
A final verification summary indicating whether the debugging
process was successful together with any remaining concerns.
""",

        agent=manager,
    )