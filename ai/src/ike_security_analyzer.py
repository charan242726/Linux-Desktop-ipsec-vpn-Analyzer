import json
import sys
from pathlib import Path

from scapy.all import rdpcap, UDP, ISAKMP


def analyze_ike_security(pcap_path: str) -> dict:
    path = Path(pcap_path)

    if not path.exists():
        raise FileNotFoundError(f"PCAP file not found: {pcap_path}")

    packets = rdpcap(str(path))

    ike_packets = 0
    ikev2_packets = 0

    encryption_algorithm = "Unknown"
    authentication_algorithm = "Unknown"
    key_exchange_method = "Unknown"

    for packet in packets:

        if not packet.haslayer(UDP):
            continue

        udp = packet[UDP]

        if udp.sport not in (500, 4500) and udp.dport not in (500, 4500):
            continue

        if not packet.haslayer(ISAKMP):
            continue

        ike_packets += 1

        version = int(packet[ISAKMP].version)
        major_version = version >> 4

        if major_version == 2:
            ikev2_packets += 1

    if ike_packets == 0:
        status = "No IKE packets detected."

    elif ikev2_packets > 0:
        status = (
            "IKEv2 detected, but no Security Association "
            "proposal information was available in the test capture."
        )

    else:
        status = (
            "IKE traffic detected, but security proposal "
            "information could not be determined."
        )

    return {
        "ike_security_detected": ike_packets > 0,

        "ike_version": (
            "IKEv2"
            if ikev2_packets > 0
            else "Unknown"
        ),

        "encryption_algorithm": encryption_algorithm,

        "authentication_algorithm": authentication_algorithm,

        "key_exchange_method": key_exchange_method,

        "status": status,

        "evidence": {
            "ike_packets": ike_packets,
            "ikev2_packets": ikev2_packets,
            "security_proposals_observed": False
        }
    }


def main():

    if len(sys.argv) != 3:
        print(
            "Usage: python3 ike_security_analyzer.py "
            "<input.pcap> <output.json>"
        )
        sys.exit(1)

    input_pcap = sys.argv[1]
    output_json = sys.argv[2]

    try:

        result = analyze_ike_security(input_pcap)

        output_path = Path(output_json)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result,
                file,
                indent=2
            )

        print("IKE security analysis complete.")
        print(f"Input : {input_pcap}")
        print(f"Output: {output_json}")

    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
