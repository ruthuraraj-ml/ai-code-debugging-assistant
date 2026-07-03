"""
LLM factory functions.
"""

from crewai import LLM

from config.settings import (
    GOOGLE_API_KEY,
    GROQ_API_KEY,
    MANAGER_MODEL,
    ANALYZER_MODEL,
    CORRECTOR_MODEL,
    CORRECTOR_FALLBACK_MODEL
)


def get_manager_llm() -> LLM:
    """Returns the Manager LLM."""

    return LLM(
        model=MANAGER_MODEL,
        api_key=GOOGLE_API_KEY,
    )


def get_analyzer_llm() -> LLM:
    """Returns the Analyzer LLM."""

    return LLM(
        model=ANALYZER_MODEL,
        api_key=GROQ_API_KEY,
    )


def get_corrector_llm() -> LLM:
    """Returns the Corrector LLM."""

    return LLM(
        model=CORRECTOR_MODEL,
        api_key=GOOGLE_API_KEY,
    )