import json
import sys
from collections import Counter
from pathlib import Path

from scapy.all import rdpcap


def analyze_pcap(pcap_path: str) -> dict:
    path = Path(pcap_path)

    if not path.exists():
        raise FileNotFoundError(f"PCAP file not found: {pcap_path}")

    packets = rdpcap(str(path))

    protocol_counter = Counter()
    packet_sizes = []

    ike_port_500 = 0
    ike_port_4500 = 0

    for packet in packets:
        packet_sizes.append(len(packet))

        if packet.haslayer("IP"):
            protocol_counter["IPv4"] += 1

        if packet.haslayer("IPv6"):
            protocol_counter["IPv6"] += 1

        if packet.haslayer("UDP"):
            protocol_counter["UDP"] += 1

            sport = packet["UDP"].sport
            dport = packet["UDP"].dport

            if sport == 500 or dport == 500:
                ike_port_500 += 1

            if sport == 4500 or dport == 4500:
                ike_port_4500 += 1

        if packet.haslayer("TCP"):
            protocol_counter["TCP"] += 1

        if packet.haslayer("ICMP"):
            protocol_counter["ICMP"] += 1

        if packet.haslayer("ESP"):
            protocol_counter["ESP"] += 1

    result = {
        "pcap_file": path.name,
        "packet_count": len(packets),
        "total_bytes": sum(packet_sizes),
        "average_packet_size": (
            sum(packet_sizes) / len(packet_sizes)
            if packet_sizes
            else 0
        ),
        "min_packet_size": min(packet_sizes) if packet_sizes else 0,
        "max_packet_size": max(packet_sizes) if packet_sizes else 0,

        "protocol_counts": dict(protocol_counter),

        "ike_indicators": {
            "udp_port_500_packets": ike_port_500,
            "udp_port_4500_packets": ike_port_4500,
            "ike_candidate": (
                ike_port_500 > 0 or ike_port_4500 > 0
            )
        }
    }

    return result


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python3 pcap_parser.py <input.pcap> <output.json>"
        )
        sys.exit(1)

    input_pcap = sys.argv[1]
    output_json = sys.argv[2]

    try:
        result = analyze_pcap(input_pcap)

        output_path = Path(output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=2)

        print("Analysis complete.")
        print(f"Input : {input_pcap}")
        print(f"Output: {output_json}")

    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
