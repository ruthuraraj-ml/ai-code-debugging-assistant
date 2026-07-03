"""
Application configuration.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------
# Project Paths
# ------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "outputs"
SAMPLE_CODE_DIR = PROJECT_ROOT / "sample_codes"
ASSETS_DIR = PROJECT_ROOT / "assets"

# ------------------------------------------------------------------
# Application
# ------------------------------------------------------------------

APP_NAME = "Automated Code Debugging Assistant"
APP_VERSION = "1.0.0"

# ------------------------------------------------------------------
# API Keys
# ------------------------------------------------------------------

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ------------------------------------------------------------------
# LLM Models
# ------------------------------------------------------------------

MANAGER_MODEL = "gemini/gemini-3.1-flash-lite"

ANALYZER_MODEL = "groq/llama-3.3-70b-versatile"

CORRECTOR_MODEL = "gemini/gemma-4-31b-it"

CORRECTOR_FALLBACK_MODEL = "gemini/gemma-4-26b-a4b-it"

# ------------------------------------------------------------------
# Observability
# ------------------------------------------------------------------

TRACE_OUTPUT = OUTPUT_DIR / "trace.json"