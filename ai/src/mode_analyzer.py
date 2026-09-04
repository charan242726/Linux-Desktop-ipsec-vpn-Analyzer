import json
import sys
from pathlib import Path

from scapy.all import rdpcap, IP, IPv6, ESP


def looks_like_inner_ip(data: bytes) -> bool:
    """
    Check whether ESP data begins with an IPv4 or IPv6 header.

    This is useful for our synthetic development PCAP.
    In real encrypted ESP traffic, the inner IP header is normally
    encrypted and therefore may not be visible.
    """

    if not data:
        return False

    first_byte = data[0]

    # IPv4: version = 4
    if (first_byte >> 4) == 4:
        return True

    # IPv6: version = 6
    if (first_byte >> 4) == 6:
        return True

    return False


def analyze_mode(pcap_path: str) -> dict:
    path = Path(pcap_path)

    if not path.exists():
        raise FileNotFoundError(f"PCAP file not found: {pcap_path}")

    packets = rdpcap(str(path))

    esp_packets = 0
    tunnel_candidates = 0
    transport_candidates = 0

    for packet in packets:

        if not packet.haslayer(ESP):
            continue

        esp_packets += 1

        esp = packet[ESP]

        # Scapy stores the encrypted/encapsulated bytes
        # in the ESP data field when it cannot decode them.
        data = bytes(esp.data)

        if looks_like_inner_ip(data):
            tunnel_candidates += 1
        else:
            transport_candidates += 1

    if esp_packets == 0:
        mode = "Unknown"
        confidence = 0.0
        reason = "No ESP packets were found."

    elif tunnel_candidates > transport_candidates:
        mode = "Tunnel"
        confidence = tunnel_candidates / esp_packets
        reason = (
            "ESP data begins with an IP header, indicating "
            "an encapsulated inner IP packet in this test capture."
        )

    elif transport_candidates > tunnel_candidates:
        mode = "Transport"
        confidence = transport_candidates / esp_packets
        reason = (
            "ESP data does not expose an inner IP header; "
            "traffic resembles Transport mode."
        )

    else:
        mode = "Unknown"
        confidence = 0.0
        reason = (
            "Insufficient packet structure evidence to determine "
            "Tunnel or Transport mode."
        )

    return {
        "mode": mode,
        "confidence": round(confidence, 2),
        "reason": reason,
        "statistics": {
            "esp_packets": esp_packets,
            "tunnel_candidates": tunnel_candidates,
            "transport_candidates": transport_candidates
        }
    }


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python3 mode_analyzer.py "
            "<input.pcap> <output.json>"
        )
        sys.exit(1)

    input_pcap = sys.argv[1]
    output_json = sys.argv[2]

    try:
        result = analyze_mode(input_pcap)

        output_path = Path(output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=2)

        print("Mode analysis complete.")
        print(f"Input : {input_pcap}")
        print(f"Output: {output_json}")

    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
