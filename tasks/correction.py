"""
Correction task definition.
"""

from crewai import Task

from schemas.responses.correction_response import (
    CorrectionResponse
    )


def create_correction_task(corrector) -> Task:
    """
    Creates the code correction task.
    """

    return Task(

        description="""
Correct the supplied Python source code using the analysis report produced by the previous task.

Responsibilities

1. Fix every identified syntax issue.
2. Fix every identified runtime issue.
3. Fix every identified logical issue.
4. Preserve the original functionality.
5. Make the minimum necessary changes.
6. Produce clean, readable Python code.

Return ONLY valid JSON.

Return the following structure:

{
    "corrected_source": "string",

    "modification_summary": "string",

    "correction_notes": "string or null"
}

Rules

- Return ONLY JSON.
- Do not wrap the JSON inside markdown.
- Do not explain your answer.
- Do not generate UUIDs.
- Do not generate timestamps.
- Do not generate artifact IDs.
- Do not generate metadata.
- Do not invent additional fields.
""",

        expected_output="""
A valid CorrectionResponse JSON object.
""",

        agent=corrector,

        context=[],

        output_pydantic=CorrectionResponse,
    )