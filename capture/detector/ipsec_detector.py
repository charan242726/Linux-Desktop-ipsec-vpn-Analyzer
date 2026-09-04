import json
import subprocess
import sys
from datetime import datetime, timezone


def run_command(command, timeout=10):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            return ""

        return result.stdout

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def detect_ipsec_traffic(interface):
    """
    Perform a short passive traffic observation on the selected
    network interface.

    Detection signals:
      UDP/500  -> IKE
      UDP/4500 -> IKE NAT-T / IPsec
      ESP      -> IP protocol 50
      AH       -> IP protocol 51
    """

    command = [
        "timeout",
        "5",
        "tcpdump",
        "-nn",
        "-i",
        interface,
        "-c",
        "100",
        "udp port 500 or udp port 4500 or ip proto 50 or ip proto 51",
    ]

    output = run_command(command, timeout=8)

    ike_packets = 0
    nat_t_packets = 0
    esp_packets = 0
    ah_packets = 0

    for line in output.splitlines():

        if "UDP" in line:

            if ".500" in line:
                ike_packets += 1

            if ".4500" in line:
                nat_t_packets += 1

        if "ESP" in line:
            esp_packets += 1

        if "AH" in line:
            ah_packets += 1

    ipsec_evidence = (
        ike_packets > 0
        or nat_t_packets > 0
        or esp_packets > 0
        or ah_packets > 0
    )

    evidence_count = sum(
        [
            ike_packets > 0,
            nat_t_packets > 0,
            esp_packets > 0,
            ah_packets > 0,
        ]
    )

    if evidence_count >= 2:
        confidence = 0.98
    elif evidence_count == 1:
        confidence = 0.80
    else:
        confidence = 0.0

    if esp_packets > 0 or ah_packets > 0:
        vpn_type = "IPsec"

    elif ike_packets > 0 or nat_t_packets > 0:
        vpn_type = "IKE/IPsec candidate"

    else:
        vpn_type = "None detected"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "interface": interface,

        "ipsec_detected": ipsec_evidence,

        "vpn_type": vpn_type,

        "evidence": {
            "ike_udp_500": ike_packets,
            "ike_nat_t_udp_4500": nat_t_packets,
            "esp_packets": esp_packets,
            "ah_packets": ah_packets,
        },

        "confidence": confidence,

        "status": (
            "IPSEC_DETECTED"
            if ipsec_evidence
            else "NO_IPSEC_DETECTED"
        ),
    }


def get_active_interface():
    output = run_command(
        ["ip", "route", "show", "default"]
    )

    for line in output.splitlines():

        parts = line.split()

        if "dev" in parts:
            index = parts.index("dev")

            if index + 1 < len(parts):
                return parts[index + 1]

    return None


def main():

    interface = None

    if len(sys.argv) > 1:
        interface = sys.argv[1]

    if not interface:
        interface = get_active_interface()

    if not interface:
        print(
            json.dumps(
                {
                    "status": "NO_ACTIVE_INTERFACE",
                    "ipsec_detected": False,
                },
                indent=2,
            )
        )
        return

    result = detect_ipsec_traffic(interface)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
