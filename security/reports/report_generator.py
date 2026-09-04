import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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
            "mode": ai.get(
                "mode",
                "Unknown"
            ),
            "traffic_type": ai.get(
                "traffic_type",
                "Unknown"
            ),
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
            "authentication_algorithm": ai.get(
                "authentication_algorithm",
                "Unknown"
            ),
            "key_exchange_method": ai.get(
                "key_exchange_method",
                "Unknown"
            ),
            "component_confidence": ai.get(
                "component_confidence",
                {}
            ),
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

        # The report is generated BEFORE its SHA-256 hash exists.
        "integrity": {
            "status": "PENDING",
            "hash_algorithm": "SHA-256"
        },

        # Blockchain registration happens AFTER report generation.
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


if __name__ == "__main__":
    main()
