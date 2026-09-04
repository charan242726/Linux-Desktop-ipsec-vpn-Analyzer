import json
import sys
from pathlib import Path


def analyze_traffic(features: dict) -> dict:
    packet_count = features.get(
        "packet_count",
        features.get("capture", {}).get("packet_count", 0)
    )

    protocol_counts = features.get(
        "protocol_counts",
        {}
    )

    if not protocol_counts:
        protocol_counts = features.get(
            "protocol_features",
            {}
        )

    tcp_count = protocol_counts.get(
        "TCP",
        protocol_counts.get("tcp_packets", 0)
    )

    udp_count = protocol_counts.get(
        "UDP",
        protocol_counts.get("udp_packets", 0)
    )

    icmp_count = protocol_counts.get(
        "ICMP",
        protocol_counts.get("icmp_packets", 0)
    )

    if packet_count == 0:
        return {
            "traffic_type": "Unknown",
            "confidence": 0.0,
            "reason": "No packets available for traffic classification.",
            "status": "UNKNOWN"
        }

    tcp_ratio = tcp_count / packet_count
    udp_ratio = udp_count / packet_count
    icmp_ratio = icmp_count / packet_count

    # --------------------------------------------------------
    # Baseline traffic classification
    # --------------------------------------------------------

    if icmp_ratio >= 0.50:
        traffic_type = "ICMP"
        confidence = icmp_ratio
        reason = "ICMP represents the majority of observed packets."

    elif tcp_ratio >= 0.60:
        traffic_type = "Web/TCP"
        confidence = tcp_ratio
        reason = "TCP represents the majority of observed packets."

    elif udp_ratio >= 0.60:
        traffic_type = "UDP"
        confidence = udp_ratio
        reason = "UDP represents the majority of observed packets."

    elif tcp_count > udp_count and tcp_count > icmp_count:
        traffic_type = "TCP-dominant"
        confidence = tcp_ratio
        reason = "TCP is the dominant observable transport protocol."

    elif udp_count > tcp_count and udp_count > icmp_count:
        traffic_type = "UDP-dominant"
        confidence = udp_ratio
        reason = "UDP is the dominant observable transport protocol."

    else:
        traffic_type = "Mixed"
        confidence = max(
            tcp_ratio,
            udp_ratio,
            icmp_ratio
        )
        reason = "No single transport protocol clearly dominates."

    return {
        "traffic_type": traffic_type,
        "confidence": round(confidence, 2),
        "reason": reason,
        "status": "INFERRED",
        "statistics": {
            "packet_count": packet_count,
            "tcp_packets": tcp_count,
            "udp_packets": udp_count,
            "icmp_packets": icmp_count,
            "tcp_ratio": round(tcp_ratio, 2),
            "udp_ratio": round(udp_ratio, 2),
            "icmp_ratio": round(icmp_ratio, 2)
        }
    }


def main():

    if len(sys.argv) != 3:
        print(
            "Usage: python3 traffic_analyzer.py "
            "<input.json> <output.json>"
        )
        sys.exit(1)

    input_json = sys.argv[1]
    output_json = sys.argv[2]

    try:

        input_path = Path(input_json)

        if not input_path.exists():
            raise FileNotFoundError(
                f"Features file not found: {input_json}"
            )

        with open(
            input_path,
            "r",
            encoding="utf-8"
        ) as file:
            features = json.load(file)

        result = analyze_traffic(features)

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

        print("Traffic analysis complete.")
        print(f"Input : {input_json}")
        print(f"Output: {output_json}")

    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
