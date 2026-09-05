import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_mode(ai):
    """
    Resolve VPN mode from the AI result without inventing a value.

    Supported forms:
      mode = "Tunnel"
      mode = {"mode": "Tunnel", ...}
      mode_analysis = {"mode": "Tunnel", ...}
      mode_analysis = {"vpn_mode": "Tunnel", ...}
    """

    candidates = [
        ai.get("mode"),
        ai.get("vpn_mode"),
        ai.get("mode_analysis"),
    ]

    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip()

        if isinstance(value, dict):
            for key in (
                "mode",
                "vpn_mode",
                "detected_mode",
                "name",
            ):
                candidate = value.get(key)

                if isinstance(candidate, str) and candidate.strip():
                    return candidate.strip()

    return "Unknown"


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python3 report_generator.py "
            "<ai_result> <security_result> <output_file>"
        )
        sys.exit(1)

    ai_file = Path(sys.argv[1])
    security_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])

    ai = load_json(ai_file)
    security = load_json(security_file)

    traffic = ai.get("traffic") or {}
    crypto_evidence = ai.get("crypto_evidence") or {}

    # ---------------------------------------------------------
    # Normalize detected VPN mode
    # ---------------------------------------------------------

    vpn_mode = extract_mode(ai)

    # ---------------------------------------------------------
    # Normalize traffic
    # ---------------------------------------------------------

    traffic_type = (
        traffic.get("traffic_type")
        or ai.get("traffic_type")
        or "Unknown"
    )

    # ---------------------------------------------------------
    # Build report
    # ---------------------------------------------------------

    report = {
        "report_id": "REPORT-" + security.get(
            "assessment_id",
            "UNKNOWN"
        ),

        "capture_id": ai.get(
            "capture_id",
            "UNKNOWN"
        ),

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "executive_summary": {
            "ipsec_detected": ai.get(
                "ipsec_detected",
                False
            ),

            "ike_version": ai.get(
                "ike_version",
                "Unknown"
            ),

            "vpn_mode": vpn_mode,

            "traffic_type": traffic_type,

            "security_score": security.get(
                "security_score",
                0
            ),

            "risk_level": security.get(
                "risk_level",
                "UNKNOWN"
            ),

            "ai_confidence": ai.get(
                "confidence",
                0.0
            )
        },

        "technical_analysis": {
            "encryption_algorithm": ai.get(
                "encryption_algorithm",
                "Unknown"
            ),

            "integrity_algorithm": ai.get(
                "integrity_algorithm",
                ai.get(
                    "authentication_algorithm",
                    "Unknown"
                )
            ),

            "authentication_method": ai.get(
                "authentication_method",
                "Unknown"
            ),

            "key_exchange_method": ai.get(
                "key_exchange_method",
                "Unknown"
            ),

            "prf": ai.get(
                "prf",
                "Unknown"
            ),

            "pfs": ai.get(
                "pfs",
                "Unknown"
            ),

            "ike_version": ai.get(
                "ike_version",
                "Unknown"
            ),

            "vpn_mode": vpn_mode,

            "traffic_type": traffic_type,

            "component_confidence": ai.get(
                "crypto_confidence",
                ai.get(
                    "component_confidence",
                    {}
                )
            ),

            "crypto_evidence": crypto_evidence,

            "traffic": traffic,

            "evidence": ai.get(
                "evidence",
                {}
            )
        },

        "security_assessment": {
            "score": security.get(
                "security_score",
                0
            ),

            "risk_level": security.get(
                "risk_level",
                "UNKNOWN"
            ),

            "findings": security.get(
                "findings",
                []
            ),

            "recommendations": security.get(
                "recommendations",
                []
            ),

            "methodology": security.get(
                "methodology",
                {}
            )
        },

        # These values are populated after the report is generated.
        "integrity": {
            "status": "PENDING",
            "hash_algorithm": "SHA-256"
        },

        # Blockchain registration happens after hashing.
        "blockchain": {
            "status": "PENDING"
        },

        "status": "REPORT_GENERATED"
    }

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            report,
            f,
            indent=2
        )

    print("Security report generated.")
    print(f"AI Result : {ai_file}")
    print(f"Assessment: {security_file}")
    print(f"Output    : {output_file}")
    print(f"VPN Mode  : {vpn_mode}")


if __name__ == "__main__":
    main()
