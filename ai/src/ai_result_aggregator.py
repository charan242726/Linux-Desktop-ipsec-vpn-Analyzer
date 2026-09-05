#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def load_json(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Required analysis file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parameter_value(parameter):
    if isinstance(parameter, dict):
        return parameter.get("value", "Unknown")

    return parameter or "Unknown"


def parameter_status(parameter):
    if isinstance(parameter, dict):
        return parameter.get("status", "UNKNOWN")

    return "UNKNOWN"


def parameter_confidence(parameter):
    if isinstance(parameter, dict):
        value = parameter.get("confidence", 0.0)

        if isinstance(value, (int, float)):
            return value

    return 0.0


def main():
    if len(sys.argv) != 5:
        print(
            "Usage: python ai_result_aggregator.py "
            "<pcap_file> <output_dir> <output_file> <capture_id>"
        )
        sys.exit(1)

    pcap_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_file = Path(sys.argv[3])
    capture_id = sys.argv[4]

    if not pcap_file.exists():
        print(f"PCAP file not found: {pcap_file}")
        sys.exit(1)

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    traffic_file = output_dir / "traffic_analysis.json"
    ipsec_file = output_dir / "ipsec_analysis.json"
    ike_file = output_dir / "ike_analysis.json"
    mode_file = output_dir / "mode_analysis.json"

    traffic = load_json(traffic_file)
    ipsec = load_json(ipsec_file)
    ike = load_json(ike_file)
    mode = load_json(mode_file)

    crypto = ike.get(
        "cryptographic_parameters",
        {},
    )

    encryption = crypto.get(
        "encryption_algorithm",
        {"value": "Unknown"},
    )

    integrity = crypto.get(
        "integrity_algorithm",
        crypto.get(
            "authentication_algorithm",
            {"value": "Unknown"},
        ),
    )

    authentication_method = crypto.get(
        "authentication_method",
        {"value": "Unknown"},
    )

    key_exchange = crypto.get(
        "key_exchange_method",
        {"value": "Unknown"},
    )

    prf = crypto.get(
        "prf",
        {"value": "Unknown"},
    )

    pfs = crypto.get(
        "pfs",
        {"value": "Unknown"},
    )

    # Keep the legacy authentication_algorithm field because
    # the existing security engine uses it. Its value represents
    # the observed IKE/IPsec integrity algorithm.
    authentication_algorithm = parameter_value(
        integrity
    )

    component_confidences = [
        ipsec.get("confidence", 0.0),
        ike.get("confidence", 0.0),
        mode.get("confidence", 0.0),
        traffic.get("confidence", 0.0),
    ]

    component_confidences = [
        value
        for value in component_confidences
        if isinstance(value, (int, float))
    ]

    base_confidence = (
        sum(component_confidences)
        / len(component_confidences)
        if component_confidences
        else 0.0
    )

    result = {
        "status": "ANALYZED",
        "capture_id": capture_id,

        "capture_file": str(
            pcap_file
        ),

        "ipsec_detected": ipsec.get(
            "ipsec_detected",
            False,
        ),

        "ike_version": ike.get(
            "ike_version",
            "Unknown",
        ),

        "mode": mode.get(
            "mode",
            mode.get(
                "value",
                "Unknown",
            ),
        ),

        "encryption_algorithm": parameter_value(
            encryption
        ),

        "authentication_algorithm": authentication_algorithm,

        "integrity_algorithm": parameter_value(
            integrity
        ),

        "authentication_method": parameter_value(
            authentication_method
        ),

        "key_exchange_method": parameter_value(
            key_exchange
        ),

        "prf": parameter_value(
            prf
        ),

        "pfs": parameter_value(
            pfs
        ),

        "crypto_evidence": {
            "encryption_algorithm": encryption,
            "integrity_algorithm": integrity,
            "authentication_method": authentication_method,
            "key_exchange_method": key_exchange,
            "prf": prf,
            "pfs": pfs,
        },

        "crypto_status": {
            "encryption_algorithm": parameter_status(
                encryption
            ),
            "integrity_algorithm": parameter_status(
                integrity
            ),
            "authentication_method": parameter_status(
                authentication_method
            ),
            "key_exchange_method": parameter_status(
                key_exchange
            ),
            "prf": parameter_status(
                prf
            ),
            "pfs": parameter_status(
                pfs
            ),
        },

        "crypto_confidence": {
            "encryption_algorithm": parameter_confidence(
                encryption
            ),
            "integrity_algorithm": parameter_confidence(
                integrity
            ),
            "authentication_method": parameter_confidence(
                authentication_method
            ),
            "key_exchange_method": parameter_confidence(
                key_exchange
            ),
            "prf": parameter_confidence(
                prf
            ),
            "pfs": parameter_confidence(
                pfs
            ),
        },

        "traffic": traffic,

        "evidence": {
            "ipsec": ipsec,
            "ike": ike,
            "mode": mode,
            "traffic": traffic,
            "sa_characteristics": ike.get(
                "sa_characteristics",
                {},
            ),
        },

        "confidence": round(
            base_confidence,
            2,
        ),
    }

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
        )

    print("AI result aggregation complete.")
    print(f"Capture ID: {capture_id}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
