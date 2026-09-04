import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_GENERATOR = (
    PROJECT_ROOT
    / "security"
    / "reports"
    / "report_generator.py"
)


class ReportGenerationError(RuntimeError):
    """Raised when report generation fails."""


def run_report_generation(
    ai_result_file,
    security_result_file,
    output_file,
):
    ai_result_file = Path(ai_result_file)
    security_result_file = Path(security_result_file)
    output_file = Path(output_file)

    if not ai_result_file.exists():
        raise ReportGenerationError(
            f"AI result not found: {ai_result_file}"
        )

    if not security_result_file.exists():
        raise ReportGenerationError(
            f"Security assessment not found: {security_result_file}"
        )

    if not REPORT_GENERATOR.exists():
        raise ReportGenerationError(
            f"Report generator not found: {REPORT_GENERATOR}"
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        sys.executable,
        str(REPORT_GENERATOR),
        str(ai_result_file),
        str(security_result_file),
        str(output_file),
    ]

    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        raise ReportGenerationError(
            "Report generation failed.\n"
            f"STDOUT:\n{process.stdout}\n"
            f"STDERR:\n{process.stderr}"
        )

    if not output_file.exists():
        raise ReportGenerationError(
            f"Report was not generated: {output_file}"
        )

    with output_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)
