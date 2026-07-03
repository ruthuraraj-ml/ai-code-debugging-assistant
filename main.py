from pathlib import Path

from schemas.artifacts import SourceCodeArtifact
from services.debugging_service import DebuggingService


def main():

    code = Path(
        "sample_codes/sudoku.py"
    ).read_text(encoding="utf-8")

    source = SourceCodeArtifact(
        run_id=None,      # we'll discuss this below
        source_code=code,
    )

    service = DebuggingService()

    result = service.debug_code(source)

    analysis = result["analysis"]
    correction = result["correction"]
    verification = result["verification"]
    metrics = result["metrics"]

    print("=" * 80)
    print("METRICS")
    print("=" * 80)
    print(metrics)

    #for i, task in enumerate(crew_output.tasks_output, start=1):
        #print(f"\n{'='*80}")
        #print(f"TASK {i}")
        #print(f"{'='*80}")

        #print("RAW:")
        #print(task.raw)

        #print("\nPYDANTIC:")
        #print(task.pydantic)

        #print("\nJSON DICT:")
        #print(task.json_dict)

    print("=" * 80)
    print("ISSUES")
    print("=" * 80)

    for issue in analysis.issues:
        print(f"{issue.severity.upper()} : {issue.title}")
        print(f"Line : {issue.line_number}")
        print(f"Fix  : {issue.suggested_fix}")
        print()

    print("=" * 80)
    print("CORRECTED CODE")
    print("=" * 80)

    print(correction.corrected_source.source_code)

if __name__ == "__main__":
    main()