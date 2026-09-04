import json
import sys
from scapy.all import rdpcap, ESP


def analyze_ipsec(pcap_file):
    packets = rdpcap(pcap_file)

    esp_packets = 0

    for packet in packets:
        if ESP in packet:
            esp_packets += 1

    if esp_packets > 0:
        return {
            "ipsec_detected": True,
            "confidence": 0.95,
            "detection_reason": "ESP packets detected in the capture.",
            "observations": {
                "esp_packets": esp_packets,
                "ipsec_candidate": True,
                "encrypted_traffic_candidate": True
            }
        }

    return {
        "ipsec_detected": False,
        "confidence": 0.0,
        "detection_reason": "No ESP packets detected in the capture.",
        "observations": {
            "esp_packets": 0,
            "ipsec_candidate": False,
            "encrypted_traffic_candidate": False
        }
    }


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python3 ipsec_analyzer.py "
            "<pcap_file> <output_file>"
        )
        sys.exit(1)

    pcap_file = sys.argv[1]
    output_file = sys.argv[2]

    result = analyze_ipsec(pcap_file)

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print("IPsec analysis complete.")
    print(f"Input : {pcap_file}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
