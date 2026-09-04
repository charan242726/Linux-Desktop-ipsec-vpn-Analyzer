import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_json(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def determine_score_risk(score):
    if score >= 80:
        return "LOW"
    elif score >= 60:
        return "MEDIUM"
    elif score >= 40:
        return "HIGH"
    else:
        return "CRITICAL"


def determine_final_risk(score, findings):
    """
    Determine final risk using both:
    1. Numerical security score
    2. Highest severity finding

    The highest finding severity acts as a safety floor.
    """

    severity_rank = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
    }

    score_risk = determine_score_risk(score)

    highest_finding_risk = "LOW"

    for finding in findings:
        severity = finding.get("severity", "LOW").upper()

        if severity_rank.get(severity, 1) > severity_rank.get(
            highest_finding_risk, 1
        ):
            highest_finding_risk = severity

    if severity_rank[highest_finding_risk] > severity_rank[score_risk]:
        return highest_finding_risk

    return score_risk


def rule_matches(ai_result, rule):
    """
    Determine whether a security rule matches the AI result.

    Rules use:
        id
        parameter
        condition
    """

    parameter = rule.get("parameter")
    condition = rule.get("condition")

    if not parameter:
        return False

    actual_value = ai_result.get(parameter)

    # Normalize boolean values.
    if isinstance(actual_value, bool):
        if condition == "true":
            return actual_value is True

        if condition == "false":
            return actual_value is False

    # Normalize strings.
    if actual_value is None:
        actual_value = "Unknown"

    actual_value = str(actual_value)
    condition = str(condition)

    return actual_value == condition


def assess_security(ai_result, rules):
    score = 100
    findings = []
    recommendations = []

    for rule in rules:

        # Your rules file uses "id", not "rule_id".
        rule_id = rule.get("id")

        severity = rule.get(
            "severity",
            "LOW",
        )

        title = rule.get(
            "title",
            "",
        )

        description = rule.get(
            "description",
            "",
        )

        recommendation = rule.get(
            "recommendation",
            "",
        )

        score_impact = rule.get(
            "score_impact",
            0,
        )

        # Check whether the rule matches the AI result.
        matched = rule_matches(
            ai_result,
            rule,
        )

        if matched:

            score += score_impact

            findings.append(
                {
                    "rule_id": rule_id,
                    "severity": severity,
                    "title": title,
                    "description": description,
                    "score_impact": score_impact,
                }
            )

            recommendations.append(
                {
                    "rule_id": rule_id,
                    "recommendation": recommendation,
                }
            )

    # Keep score within 0-100.
    score = max(
        0,
        min(100, score),
    )

    # Determine final risk.
    risk_level = determine_final_risk(
        score,
        findings,
    )

    return (
        score,
        risk_level,
        findings,
        recommendations,
    )


def main():

    if len(sys.argv) != 4:
        print(
            "Usage: python security_assessor.py "
            "<ai_result.json> "
            "<security_rules.json> "
            "<output.json>"
        )
        sys.exit(1)

    ai_result_file = sys.argv[1]
    rules_file = sys.argv[2]
    output_file = sys.argv[3]

    try:

        # ---------------------------------------------------------
        # Load AI result
        # ---------------------------------------------------------

        ai_result = load_json(
            ai_result_file
        )

        # ---------------------------------------------------------
        # Load security rules
        # ---------------------------------------------------------

        rules_data = load_json(
            rules_file
        )

        if isinstance(
            rules_data,
            list,
        ):
            rules = rules_data
        else:
            rules = rules_data.get(
                "rules",
                [],
            )

        # ---------------------------------------------------------
        # Run security assessment
        # ---------------------------------------------------------

        (
            score,
            risk_level,
            findings,
            recommendations,
        ) = assess_security(
            ai_result,
            rules,
        )

        # ---------------------------------------------------------
        # IDs
        # ---------------------------------------------------------

        capture_id = ai_result.get(
            "capture_id",
            "UNKNOWN",
        )

        assessment_id = (
            f"ASSESS-{capture_id}"
        )

        # ---------------------------------------------------------
        # Final result
        # ---------------------------------------------------------

        result = {

            "assessment_id": assessment_id,

            "capture_id": capture_id,

            "security_score": score,

            "risk_level": risk_level,

            "findings": findings,

            "recommendations": recommendations,

            "methodology": {

                "base_score": 100,

                "description": (
                    "Security score starts at 100 "
                    "and is reduced according to "
                    "matched security rules. "
                    "Final risk level is determined "
                    "using both the numerical score "
                    "and the highest severity finding."
                ),

                "risk_logic": {

                    "score_thresholds": {

                        "LOW": "80-100",

                        "MEDIUM": "60-79",

                        "HIGH": "40-59",

                        "CRITICAL": "0-39",
                    },

                    "severity_floor": True,

                    "description": (
                        "The highest finding severity "
                        "acts as a minimum risk level."
                    ),
                },
            },

            "source": {

                "ai_status": ai_result.get(
                    "status",
                    "UNKNOWN",
                ),

                "ai_confidence": ai_result.get(
                    "confidence",
                    0.0,
                ),
            },

            "status": "ASSESSED",

            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        # ---------------------------------------------------------
        # Create output directory
        # ---------------------------------------------------------

        output_path = Path(
            output_file
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ---------------------------------------------------------
        # Write JSON
        # ---------------------------------------------------------

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                result,
                file,
                indent=2,
            )

        # ---------------------------------------------------------
        # Console output
        # ---------------------------------------------------------

        print(
            f"Security assessment generated: "
            f"{output_path}"
        )

        print(
            f"Security Score: {score}"
        )

        print(
            f"Risk Level: {risk_level}"
        )

        print(
            f"Findings: {len(findings)}"
        )

    except Exception as error:

        print(
            f"Security assessment failed: {error}"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
