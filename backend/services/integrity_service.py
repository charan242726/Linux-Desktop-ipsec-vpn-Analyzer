import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

HASH_GENERATOR = (
    PROJECT_ROOT
    / "security"
    / "reports"
    / "hash_report.py"
)


class IntegrityError(RuntimeError):
    """Raised when report integrity generation fails."""


def generate_report_hash(
    report_file,
    output_file,
):
    report_file = Path(report_file)
    output_file = Path(output_file)

    if not report_file.exists():
        raise IntegrityError(
            f"Report not found: {report_file}"
        )

    if not HASH_GENERATOR.exists():
        raise IntegrityError(
            f"Hash generator not found: {HASH_GENERATOR}"
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        sys.executable,
        str(HASH_GENERATOR),
        str(report_file),
        str(output_file),
    ]

    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        raise IntegrityError(
            "SHA-256 generation failed.\n"
            f"STDOUT:\n{process.stdout}\n"
            f"STDERR:\n{process.stderr}"
        )

    if not output_file.exists():
        raise IntegrityError(
            f"Hash output was not generated: {output_file}"
        )

    with output_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)
