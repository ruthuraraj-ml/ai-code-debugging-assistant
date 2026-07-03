"""
Builds rich AnalysisReport artifacts from lightweight LLM responses.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from schemas.analysis import AnalysisReport
from schemas.execution import ExecutionResult
from schemas.issue import Issue
from schemas.responses.analysis_response import (
    AnalysisResponse,
    IssueResponse,
)
from schemas.artifacts import SourceCodeArtifact
from schemas.enums import (
    ArtifactType,
    CreatorType,
    IssueCategory,
    IssueCode,
    IssueSeverity,
)


class AnalysisBuilder:
    """
    Constructs AnalysisReport artifacts from AnalysisResponse objects.
    """

    @classmethod
    def build(
        cls,
        response: AnalysisResponse,
        source: SourceCodeArtifact,
        run_id: UUID,
    ) -> AnalysisReport:
        
        issues = [
            cls._build_issue(issue, source)
            for issue in response.issues
        ]

        execution = ExecutionResult(
            executed=response.execution_result.executed,
            success=response.execution_result.success,
            stdout=response.execution_result.stdout,
            stderr=response.execution_result.stderr,
            exception=response.execution_result.exception,
        )

        return AnalysisReport(
            run_id=run_id,

            artifact_type=ArtifactType.ANALYSIS_REPORT,

            origin=CreatorType.ANALYZER,

            issues=issues,

            summary=response.summary,

            execution_result=execution,
        )
    

    @classmethod
    def _build_issue(
        cls,
        issue: IssueResponse,
        source: SourceCodeArtifact,
    ) -> Issue:
        """
        Build a rich Issue artifact from a lightweight IssueResponse.
        """

        return Issue(
            issue_id=uuid4(),

            issue_code=cls._infer_issue_code(issue),

            category=cls._infer_category(issue),

            severity=cls._infer_severity(issue),

            line_number=issue.line_number,

            title=issue.title,

            details=issue.description,

            suggested_fix=issue.suggested_fix,

            code_snippet=cls._extract_code_snippet(
                source,
                issue.line_number,
            ),
        )
    
    
    @classmethod
    def _infer_issue_code(
        cls,
        issue: IssueResponse,
    ) -> IssueCode:
        """
        Infer the IssueCode from the issue title and description.
        """

        text = f"{issue.title} {issue.description}".lower()

        if "indent" in text:
            return IssueCode.INDENTATION_ERROR

        if "syntax" in text:
            return IssueCode.SYNTAX_ERROR

        if "missing colon" in text:
            return IssueCode.MISSING_COLON

        if "zero division" in text or "zerodivisionerror" in text:
            return IssueCode.ZERO_DIVISION

        if "index" in text:
            return IssueCode.INDEX_ERROR

        if "typeerror" in text or "type error" in text:
            return IssueCode.TYPE_ERROR

        if "nameerror" in text or "name error" in text:
            return IssueCode.NAME_ERROR

        if "off-by-one" in text or "off by one" in text:
            return IssueCode.OFF_BY_ONE

        if "infinite loop" in text:
            return IssueCode.INFINITE_LOOP

        if "condition" in text:
            return IssueCode.INCORRECT_CONDITION

        if "unused import" in text:
            return IssueCode.UNUSED_IMPORT

        if "unused variable" in text:
            return IssueCode.UNUSED_VARIABLE

        if "inefficient loop" in text:
            return IssueCode.INEFFICIENT_LOOP

        return IssueCode.UNKNOWN
    

    @classmethod
    def _infer_category(
        cls,
        issue: IssueResponse,
    ) -> IssueCategory:
        """
        Infer the high-level issue category.
        """

        issue_code = cls._infer_issue_code(issue)

        syntax_codes = {
            IssueCode.INDENTATION_ERROR,
            IssueCode.SYNTAX_ERROR,
            IssueCode.MISSING_COLON,
        }

        runtime_codes = {
            IssueCode.ZERO_DIVISION,
            IssueCode.INDEX_ERROR,
            IssueCode.TYPE_ERROR,
            IssueCode.NAME_ERROR,
        }

        logic_codes = {
            IssueCode.OFF_BY_ONE,
            IssueCode.INFINITE_LOOP,
            IssueCode.INCORRECT_CONDITION,
        }

        style_codes = {
            IssueCode.UNUSED_IMPORT,
            IssueCode.UNUSED_VARIABLE,
        }

        performance_codes = {
            IssueCode.INEFFICIENT_LOOP,
        }

        if issue_code in syntax_codes:
            return IssueCategory.SYNTAX

        if issue_code in runtime_codes:
            return IssueCategory.RUNTIME

        if issue_code in logic_codes:
            return IssueCategory.LOGIC

        if issue_code in style_codes:
            return IssueCategory.STYLE

        if issue_code in performance_codes:
            return IssueCategory.PERFORMANCE

        # Conservative default
        return IssueCategory.LOGIC
    

    @classmethod
    def _infer_severity(
        cls,
        issue: IssueResponse,
    ) -> IssueSeverity:
        """
        Infer issue severity.
        """

        category = cls._infer_category(issue)

        if category == IssueCategory.SYNTAX:
            return IssueSeverity.ERROR

        if category == IssueCategory.RUNTIME:
            return IssueSeverity.ERROR

        if category == IssueCategory.LOGIC:
            return IssueSeverity.WARNING

        if category == IssueCategory.STYLE:
            return IssueSeverity.INFO

        if category == IssueCategory.PERFORMANCE:
            return IssueSeverity.WARNING

        # Conservative default
        return IssueSeverity.INFO
    

    @classmethod
    def _extract_code_snippet(
        cls,
        source: SourceCodeArtifact,
        line_number: int | None,
    ) -> str | None:
        """
        Extract the corresponding source line.
        """

        if line_number is None:
            return None

        lines = source.source_code.splitlines()

        if line_number < 1 or line_number > len(lines):
            return None

        return lines[line_number - 1]