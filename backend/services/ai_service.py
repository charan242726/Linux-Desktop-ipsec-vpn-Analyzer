import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AI_SRC = PROJECT_ROOT / "ai" / "src"


class AIAnalysisError(Exception):
    """Raised when the AI analysis pipeline fails."""


def run_script(script_name, *arguments):
    script_path = AI_SRC / script_name

    if not script_path.exists():
        raise AIAnalysisError(
            f"AI module not found: {script_path}"
        )

    command = [
        sys.executable,
        str(script_path),
        *map(str, arguments),
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise AIAnalysisError(
            f"{script_name} failed:\n"
            f"{result.stdout}\n"
            f"{result.stderr}"
        )

    return result.stdout


def run_ai_analysis(pcap_file, output_dir, capture_id=None):
    """
    Run the complete AI analysis pipeline on a PCAP.

    capture_id:
        Optional analysis identity supplied by the orchestrator.
        If omitted, the PCAP filename is used.
    """

    pcap = Path(pcap_file).resolve()
    output = Path(output_dir).resolve()

    if not pcap.exists():
        raise FileNotFoundError(
            f"PCAP file not found: {pcap}"
        )

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    parsed_file = output / "pcap_features.json"
    traffic_file = output / "traffic_analysis.json"
    ipsec_file = output / "ipsec_analysis.json"
    ike_file = output / "ike_analysis.json"
    mode_file = output / "mode_analysis.json"
    ai_result_file = output / "ai_result.json"

    # Use the orchestrator ID when supplied.
    if capture_id is None:
        capture_id = pcap.stem

    # 1. Parse PCAP
    run_script(
        "pcap_parser.py",
        pcap,
        parsed_file,
    )

    # 2. Analyze traffic
    run_script(
        "traffic_analyzer.py",
        parsed_file,
        traffic_file,
    )

    # 3. Detect IPsec
    run_script(
        "ipsec_analyzer.py",
        pcap,
        ipsec_file,
    )

    # 4. Analyze IKE
    run_script(
        "ike_analyzer.py",
        pcap,
        ike_file,
    )

    # 5. Analyze IPsec mode
    run_script(
        "mode_analyzer.py",
        pcap,
        mode_file,
    )

    # 6. Aggregate AI result
    run_script(
        "ai_result_aggregator.py",
        pcap,
        output,
        ai_result_file,
        capture_id,
    )

    if not ai_result_file.exists():
        raise AIAnalysisError(
            "AI result was not generated."
        )

    with open(
        ai_result_file,
        "r",
        encoding="utf-8",
    ) as file:
        result = json.load(file)

    return result
