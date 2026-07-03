"""
Lightweight response schema produced by the Corrector agent.

The LLM is responsible only for reasoning about the corrected code.
Application metadata is added later by the CorrectionBuilder.
"""

from typing import Optional

from pydantic import BaseModel


class CorrectionResponse(BaseModel):
    """
    Lightweight response returned by the Corrector agent.
    """

    corrected_source: str

    modification_summary: str

    correction_notes: Optional[str] = None