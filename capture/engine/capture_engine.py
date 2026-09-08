"""
LEGACY / UNUSED on Windows
──────────────────────────
This file uses `tcpdump` and Linux-only commands (`ip route show default`).
It is NOT used in the live backend pipeline.

The active packet capture on Windows is:
    backend/capture/capture_thread.py  ← uses Scapy + Npcap

This file was kept for reference (possible Linux deployment) but should NOT
be imported or called from any production code path.
"""
import json
import subprocess
import sys

from datetime import datetime, timezone
from pathlib import Path


DEFAULT_DURATION = 30


def get_default_interface():
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        for line in result.stdout.splitlines():
            parts = line.split()

            if "dev" in parts:
                index = parts.index("dev")

                if index + 1 < len(parts):
                    return parts[index + 1]

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None


def capture_traffic(
    interface,
    output_file,
    duration=DEFAULT_DURATION,
):
    output_path = Path(output_file).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "timeout",
        str(duration),
        "tcpdump",
        "-i",
        interface,
        "-w",
        str(output_path),
    ]

    started_at = datetime.now(timezone.utc)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=duration + 10,
        )

    except subprocess.TimeoutExpired:
        return {
            "status": "CAPTURE_TIMEOUT",
            "interface": interface,
            "output_file": str(output_path),
        }

    completed_at = datetime.now(timezone.utc)

    if result.returncode not in (0, 124):
        return {
            "status": "CAPTURE_FAILED",
            "interface": interface,
            "output_file": str(output_path),
            "error": result.stderr.strip(),
        }

    packet_count = get_packet_count(output_path)

    return {
        "status": "CAPTURE_COMPLETED",
        "interface": interface,
        "output_file": str(output_path),
        "packet_count": packet_count,
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_seconds": duration,
    }


def get_packet_count(pcap_file):
    if not Path(pcap_file).exists():
        return 0

    try:
        result = subprocess.run(
            [
                "tcpdump",
                "-nn",
                "-r",
                str(pcap_file),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

        lines = result.stdout.splitlines()

        return len(lines)

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 0


def main():
    interface = None
    output_file = None
    duration = DEFAULT_DURATION

    if len(sys.argv) >= 2:
        interface = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]

    if len(sys.argv) >= 4:
        duration = int(sys.argv[3])

    if not interface:
        interface = get_default_interface()

    if not interface:
        print(
            json.dumps(
                {
                    "status": "NO_ACTIVE_INTERFACE",
                    "message": "No default network interface was detected.",
                },
                indent=2,
            )
        )
        sys.exit(1)

    if not output_file:
        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d_%H%M%S")

        output_file = (
            Path("capture/runtime")
            / f"vpn_capture_{timestamp}.pcap"
        )

    result = capture_traffic(
        interface=interface,
        output_file=output_file,
        duration=duration,
    )

    print(json.dumps(result, indent=2))

    if result["status"] != "CAPTURE_COMPLETED":
        sys.exit(1)


if __name__ == "__main__":
    main()
