"""
Analysis task definition.
"""

from crewai import Task

from schemas.responses.analysis_response import AnalysisResponse


def create_analysis_task(analyzer) -> Task:
    """
    Creates the code analysis task.
    """

    return Task(
        description="""
You are the Code Analyzer in an AI Debugging System.

Your job is to analyze ONLY the Python source code supplied by the user.

====================================================================
SOURCE CODE
====================================================================

{source_code}

====================================================================
GENERAL RULES
====================================================================

1. Analyze ONLY the source code shown above.
2. Do NOT invent, modify, or replace the program.
3. Do NOT assume missing code.
4. Do NOT create your own example program.
5. Every reported issue must correspond to the supplied source code.
6. If a line number is unknown, return null.

====================================================================
CODE INTERPRETER TOOL CONTRACT
====================================================================

Use the Code Interpreter Tool whenever execution is required to verify
syntax errors, runtime errors, or program behaviour.

When invoking the tool you MUST follow this schema EXACTLY:

{
    "code": "<complete source code>",
    "libraries_used": ["library1", "library2"]
}

Rules

• libraries_used MUST ALWAYS be a JSON array.

Examples

No imports

{
    "code": "...",
    "libraries_used": []
}

One import

{
    "code": "...",
    "libraries_used": ["numpy"]
}

Two imports

{
    "code": "...",
    "libraries_used": ["numpy", "pandas"]
}

Never generate

"libraries_used": ""

Never generate

"libraries_used": "numpy"

Never generate

"libraries_used": "numpy,pandas"

Execute ONLY the supplied source code.

====================================================================
ANALYSIS RESPONSIBILITIES
====================================================================

Identify:

1. Syntax errors
2. Runtime errors
3. Logical errors

For every issue provide:

- title
- description
- line_number
- suggested_fix

Also provide:

- summary
- execution_result

====================================================================
OUTPUT FORMAT
====================================================================

Return ONLY a valid JSON object.

Return EXACTLY this schema.

{
    "issues": [
        {
            "title": "string",
            "description": "string",
            "line_number": integer or null,
            "suggested_fix": "string or null"
        }
    ],

    "summary": "string",

    "execution_result": {
        "executed": boolean,
        "success": boolean,
        "stdout": "string",
        "stderr": "string",
        "exception": "string or null"
    }
}

====================================================================
OUTPUT RULES
====================================================================

- Return ONLY JSON.
- Do NOT wrap JSON in markdown.
- Do NOT add explanations.
- Do NOT generate UUIDs.
- Do NOT generate timestamps.
- Do NOT generate metadata.
- Do NOT add fields that are not part of the schema.
- Every reported issue must correspond to the supplied source code.
""",

        expected_output="""
A valid AnalysisResponse JSON object.
""",

        agent=analyzer,

        output_pydantic=AnalysisResponse,
    )