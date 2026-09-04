import json
import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BLOCKCHAIN_DIR = PROJECT_ROOT / "blockchain"
BLOCKCHAIN_SCRIPT = (
    BLOCKCHAIN_DIR
    / "scripts"
    / "register_and_verify.ts"
)


class BlockchainIntegrationError(RuntimeError):
    """Raised when blockchain registration or verification fails."""


def register_and_verify_report(
    report_id,
    report_hash,
):
    report_id = str(report_id)
    report_hash = str(report_hash)

    if not report_id:
        raise BlockchainIntegrationError(
            "Report ID is required."
        )

    if not report_hash:
        raise BlockchainIntegrationError(
            "Report hash is required."
        )

    if not BLOCKCHAIN_DIR.exists():
        raise BlockchainIntegrationError(
            f"Blockchain directory not found: {BLOCKCHAIN_DIR}"
        )

    if not BLOCKCHAIN_SCRIPT.exists():
        raise BlockchainIntegrationError(
            f"Blockchain script not found: {BLOCKCHAIN_SCRIPT}"
        )

    rpc_url = os.getenv(
        "BLOCKCHAIN_RPC_URL",
        "http://127.0.0.1:8545",
    )

    contract_address = os.getenv(
        "VPN_REGISTRY_ADDRESS",
        "0x5fbdb2315678afecb367f032d93f642f64180aa3",
    )

    environment = os.environ.copy()

    environment["REPORT_ID"] = report_id
    environment["REPORT_HASH"] = (
        "0x" + report_hash
        if not report_hash.startswith("0x")
        else report_hash
    )
    environment["VPN_REGISTRY_ADDRESS"] = contract_address
    environment["HARDHAT_NETWORK"] = "localhost"

    # Keep the RPC configuration available to the blockchain process.
    environment["BLOCKCHAIN_RPC_URL"] = rpc_url

    command = [
        "npx",
        "hardhat",
        "run",
        str(BLOCKCHAIN_SCRIPT.relative_to(BLOCKCHAIN_DIR)),
        "--network",
        "localhost",
    ]

    process = subprocess.run(
        command,
        cwd=BLOCKCHAIN_DIR,
        capture_output=True,
        text=True,
        env=environment,
    )

    if process.returncode != 0:
        raise BlockchainIntegrationError(
            "Blockchain integration failed.\n"
            f"STDOUT:\n{process.stdout}\n"
            f"STDERR:\n{process.stderr}"
        )

    # Hardhat can print additional output before the JSON.
    # Extract the final JSON object from stdout.
    stdout = process.stdout.strip()

    json_start = stdout.find("{")

    if json_start == -1:
        raise BlockchainIntegrationError(
            "Blockchain script did not return JSON.\n"
            f"Output:\n{stdout}"
        )

    json_output = stdout[json_start:]

    try:
        result = json.loads(json_output)
    except json.JSONDecodeError as exc:
        raise BlockchainIntegrationError(
            "Unable to parse blockchain result JSON.\n"
            f"Output:\n{stdout}"
        ) from exc

    if not result.get("verified", False):
        raise BlockchainIntegrationError(
            "Blockchain verification failed."
        )

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Register and verify a VPN assessment on blockchain."
    )

    parser.add_argument(
        "report_id",
        help="Unique VPN assessment report ID.",
    )

    parser.add_argument(
        "report_hash",
        help="SHA-256 report hash.",
    )

    args = parser.parse_args()

    result = register_and_verify_report(
        args.report_id,
        args.report_hash,
    )

    print(json.dumps(result, indent=2))
