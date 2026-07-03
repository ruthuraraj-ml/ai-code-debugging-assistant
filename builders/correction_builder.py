"""
Builds rich CorrectedCodeArtifact artifacts from lightweight LLM responses.
"""

from __future__ import annotations

from uuid import UUID

from schemas.analysis import AnalysisReport
from schemas.artifacts import (
    SourceCodeArtifact
)
from schemas.correction import (
    CorrectedCodeArtifact
)
from schemas.enums import (
    ArtifactType,
    CreatorType,
)
from schemas.responses.correction_response import (
    CorrectionResponse
)


class CorrectionBuilder:
    """
    Constructs CorrectedCodeArtifact objects from
    lightweight CorrectionResponse objects.
    """

    @classmethod
    def build(
        cls,
        response: CorrectionResponse,
        source: SourceCodeArtifact,
        analysis: AnalysisReport,
        run_id: UUID,
    ) -> CorrectedCodeArtifact:
        """
        Build a rich CorrectedCodeArtifact.
        """
        
        corrected_source = SourceCodeArtifact(
            run_id=run_id,
            origin=CreatorType.CORRECTOR,
            artifact_type=ArtifactType.SOURCE_CODE,
            source_code=response.corrected_source,
            language=source.language,
            filename=source.filename,
        )

        return CorrectedCodeArtifact(

            run_id=run_id,

            origin=CreatorType.CORRECTOR,

            artifact_type=ArtifactType.CORRECTED_CODE,

            corrected_source=corrected_source,

            modification_summary=response.modification_summary,

            correction_notes=response.correction_notes,

            fixed_issue_ids=[
                issue.issue_id
                for issue in analysis.issues
            ],
        )