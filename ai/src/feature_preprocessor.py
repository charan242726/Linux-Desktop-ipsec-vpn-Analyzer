import json
import sys
from pathlib import Path


def load_features(features_path: str) -> dict:
    path = Path(features_path)

    if not path.exists():
        raise FileNotFoundError(f"Features file not found: {features_path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def prepare_ai_features(data: dict) -> dict:
    protocol_counts = data.get("protocol_counts", {})

    packet_count = data.get("packet_count", 0)

    ipv4_count = protocol_counts.get("IPv4", 0)
    ipv6_count = protocol_counts.get("IPv6", 0)
    tcp_count = protocol_counts.get("TCP", 0)
    udp_count = protocol_counts.get("UDP", 0)
    icmp_count = protocol_counts.get("ICMP", 0)
    esp_count = protocol_counts.get("ESP", 0)

    return {
        "capture": {
            "pcap_file": data.get("pcap_file"),
            "packet_count": packet_count,
            "total_bytes": data.get("total_bytes", 0),
            "average_packet_size": data.get("average_packet_size", 0),
            "min_packet_size": data.get("min_packet_size", 0),
            "max_packet_size": data.get("max_packet_size", 0),
        },

        "protocol_features": {
            "ipv4_packets": ipv4_count,
            "ipv6_packets": ipv6_count,
            "tcp_packets": tcp_count,
            "udp_packets": udp_count,
            "icmp_packets": icmp_count,
            "esp_packets": esp_count,
        },

        "derived_features": {
            "ipv4_ratio": ipv4_count / packet_count if packet_count else 0,
            "ipv6_ratio": ipv6_count / packet_count if packet_count else 0,
            "tcp_ratio": tcp_count / packet_count if packet_count else 0,
            "udp_ratio": udp_count / packet_count if packet_count else 0,
            "icmp_ratio": icmp_count / packet_count if packet_count else 0,
            "esp_ratio": esp_count / packet_count if packet_count else 0,
        },

        "ai_observations": {
            "ipsec_candidate": esp_count > 0,
            "encrypted_traffic_candidate": esp_count > 0,
        },
    }


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python3 feature_preprocessor.py "
            "<input.json> <output.json>"
        )
        sys.exit(1)

    input_json = sys.argv[1]
    output_json = sys.argv[2]

    try:
        data = load_features(input_json)
        result = prepare_ai_features(data)

        output_path = Path(output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=2)

        print("Feature preprocessing complete.")
        print(f"Input : {input_json}")
        print(f"Output: {output_json}")

    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

