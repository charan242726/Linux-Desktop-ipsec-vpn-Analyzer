import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ASSESSOR_SCRIPT = PROJECT_ROOT / "security" / "scoring" / "security_assessor.py"
RULES_FILE = PROJECT_ROOT / "security" / "rules" / "security_rules.json"


class SecurityAssessmentError(RuntimeError):
    pass


def run_security_assessment(ai_result_file, output_file):
    ai_result_file = Path(ai_result_file)
    output_file = Path(output_file)

    if not ai_result_file.exists():
        raise SecurityAssessmentError(
            f"AI result not found: {ai_result_file}"
        )

    if not ASSESSOR_SCRIPT.exists():
        raise SecurityAssessmentError(
            f"Security assessor not found: {ASSESSOR_SCRIPT}"
        )

    if not RULES_FILE.exists():
        raise SecurityAssessmentError(
            f"Security rules not found: {RULES_FILE}"
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        str(ASSESSOR_SCRIPT),
        str(ai_result_file),
        str(RULES_FILE),
        str(output_file),
    ]

    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        raise SecurityAssessmentError(
            "Security assessment failed.\n"
            f"STDOUT:\n{process.stdout}\n"
            f"STDERR:\n{process.stderr}"
        )

    if not output_file.exists():
        raise SecurityAssessmentError(
            f"Security assessment output was not created: {output_file}"
        )

    with output_file.open("r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run VPN security assessment."
    )

    parser.add_argument(
        "ai_result",
        help="Path to ai_result.json",
    )

    parser.add_argument(
        "output",
        help="Path for security_assessment.json",
    )

    args = parser.parse_args()

    result = run_security_assessment(
        args.ai_result,
        args.output,
    )

    print(json.dumps(result, indent=2))
