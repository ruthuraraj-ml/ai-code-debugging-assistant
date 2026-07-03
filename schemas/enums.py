"""
Common enumerations used throughout the Automated Code Debugging Assistant.

These enums define the shared vocabulary for the application and are intentionally
framework-agnostic. They should not depend on CrewAI, Streamlit, or any other
implementation-specific library.
"""

from enum import StrEnum, auto


class AutoLowerStrEnum(StrEnum):
    """Base enum that automatically generates lowercase string values."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()


class RunStatus(AutoLowerStrEnum):
    """Lifecycle states of a debugging session."""

    INITIALIZED = auto()
    PLANNING = auto()
    ANALYZING = auto()
    CORRECTING = auto()
    VERIFYING = auto()
    COMPLETED = auto()
    FAILED = auto()


class AgentRole(AutoLowerStrEnum):
    """Available AI agent roles."""

    MANAGER = auto()
    ANALYZER = auto()
    CORRECTOR = auto()


class IssueCode(AutoLowerStrEnum):
    """Specific issue identifiers."""

    UNKNOWN = auto()

    # Syntax
    INDENTATION_ERROR = auto()
    SYNTAX_ERROR = auto()
    MISSING_COLON = auto()

    # Runtime
    ZERO_DIVISION = auto()
    INDEX_ERROR = auto()
    TYPE_ERROR = auto()
    NAME_ERROR = auto()

    # Logic
    OFF_BY_ONE = auto()
    INFINITE_LOOP = auto()
    INCORRECT_CONDITION = auto()

    # Style
    UNUSED_IMPORT = auto()
    UNUSED_VARIABLE = auto()

    # Performance
    INEFFICIENT_LOOP = auto()


class IssueCategory(AutoLowerStrEnum):
    """Categories used to classify code issues."""

    SYNTAX = auto()
    LOGIC = auto()
    RUNTIME = auto()
    STYLE = auto()
    PERFORMANCE = auto()


class IssueSeverity(AutoLowerStrEnum):
    """Severity assigned to detected issues."""

    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class EventType(AutoLowerStrEnum):
    """Execution events captured by the observability subsystem."""

    RUN_STARTED = auto()
    RUN_COMPLETED = auto()

    AGENT_STARTED = auto()
    AGENT_COMPLETED = auto()

    TASK_STARTED = auto()
    TASK_COMPLETED = auto()

    TOOL_STARTED = auto()
    TOOL_COMPLETED = auto()

    VALIDATION_STARTED = auto()
    VALIDATION_COMPLETED = auto()

    ERROR = auto()


class ArtifactType(AutoLowerStrEnum):
    """Artifacts generated during the debugging workflow."""

    SOURCE_CODE = auto()
    ANALYSIS_REPORT = auto()
    CORRECTED_CODE = auto()
    VERIFICATION_REPORT = auto()
    SESSION_SUMMARY = auto()


class Language(AutoLowerStrEnum):
    """Programming languages supported by the assistant."""

    PYTHON = auto()


class ExecutionOutcome(AutoLowerStrEnum):
    """Result of executing a workflow step."""

    SUCCESS = auto()
    FAILURE = auto()
    WARNING = auto()
    SKIPPED = auto()


class CreatorType(AutoLowerStrEnum):

    USER = auto()
    SYSTEM = auto()
    MANAGER = auto()
    ANALYZER = auto()
    CORRECTOR = auto()