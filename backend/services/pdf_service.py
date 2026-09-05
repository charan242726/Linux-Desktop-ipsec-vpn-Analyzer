import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


def _safe(value, default="Unknown"):
    if value is None:
        return default

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, (list, tuple)):
        if not value:
            return default
        return ", ".join(_safe(item, "") for item in value)

    if isinstance(value, dict):
        if not value:
            return default
        return "; ".join(
            f"{key}: {_safe(val, '')}"
            for key, val in value.items()
        )

    text = str(value).strip()
    return text if text else default


def _paragraph(text, style):
    return Paragraph(_safe(text).replace("\n", "<br/>"), style)


def _section_title(text, styles):
    return Paragraph(text, styles["SectionTitle"])


def _kv_table(rows, styles):
    data = []

    for key, value in rows:
        data.append([
            Paragraph(f"<b>{_safe(key)}</b>", styles["Body"]),
            Paragraph(_safe(value).replace("\n", "<br/>"), styles["Body"]),
        ])

    table = Table(data, colWidths=[55 * mm, 125 * mm], repeatRows=0)

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    return table


def _find_security_findings(security):
    findings = (
        security.get("findings")
        or security.get("security_findings")
        or []
    )

    if isinstance(findings, dict):
        findings = [findings]

    return findings if isinstance(findings, list) else []


def _find_recommendations(security):
    recommendations = security.get("recommendations") or []

    if isinstance(recommendations, str):
        return [recommendations]

    return recommendations if isinstance(recommendations, list) else []


def generate_security_report_pdf(report, output_path):
    """
    Generate a PDF from either:

    1. final_result.json structure:
       {
           "report": {...},
           "ai": {...},
           "security": {...},
           "integrity": {...},
           "blockchain": {...}
       }

    2. standalone security_report.json structure:
       {
           "report_id": ...,
           "capture_id": ...,
           "executive_summary": {...},
           "technical_analysis": {...},
           "security_assessment": {...},
           "integrity": {...},
           "blockchain": {...}
       }
    """

    # ---------------------------------------------------------
    # Normalize input structure
    # ---------------------------------------------------------

    if isinstance(report.get("report"), dict):
        # Nested final_result.json
        report_data = report.get("report") or {}
        ai = report.get("ai") or {}
        security = report.get("security") or {}
        integrity = report.get("integrity") or report_data.get("integrity") or {}
        blockchain = report.get("blockchain") or report_data.get("blockchain") or {}
    else:
        # Standalone security_report.json
        report_data = report
        ai = report.get("ai") or {}
        security = report.get("security_assessment") or {}
        integrity = report.get("integrity") or {}
        blockchain = report.get("blockchain") or {}

    executive = report_data.get("executive_summary") or {}
    technical = report_data.get("technical_analysis") or {}

    # ---------------------------------------------------------
    # Fallback values from AI result
    # ---------------------------------------------------------

    ipsec = ai.get("ipsec") or {}
    ike = ai.get("ike") or {}
    mode = ai.get("mode") or {}
    crypto = ai.get("crypto") or {}
    traffic = ai.get("traffic") or {}

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    report_id = (
        report_data.get("report_id")
        or report.get("report_id")
        or ai.get("report_id")
        or "Unknown"
    )

    capture_id = (
        report_data.get("capture_id")
        or report.get("capture_id")
        or ai.get("capture_id")
        or "Unknown"
    )

    generated = (
        report_data.get("generated_at")
        or report_data.get("generated")
        or report.get("generated_at")
        or "Unknown"
    )

    status = (
        report_data.get("status")
        or report.get("status")
        or "Unknown"
    )

    # ---------------------------------------------------------
    # Executive summary fallbacks
    # ---------------------------------------------------------

    ipsec_detected = executive.get("ipsec_detected")

    if ipsec_detected is None:
        ipsec_detected = ipsec.get("detected")

    ike_version = (
        executive.get("ike_version")
        or ike.get("version")
        or technical.get("ike_version")
    )

    vpn_mode = (
        executive.get("vpn_mode")
        or mode.get("mode")
        or technical.get("vpn_mode")
    )

    traffic_type = (
        executive.get("traffic_type")
        or traffic.get("traffic_type")
        or technical.get("traffic_type")
    )

    security_score = (
        executive.get("security_score")
        or security.get("security_score")
        or security.get("score")
    )

    risk_level = (
        executive.get("risk_level")
        or security.get("risk_level")
        or security.get("risk")
    )

    ai_confidence = (
        executive.get("ai_confidence")
        or ai.get("overall_confidence")
        or ai.get("confidence")
    )

    # ---------------------------------------------------------
    # Technical analysis fallbacks
    # ---------------------------------------------------------

    encryption = (
        technical.get("encryption_algorithm")
        or crypto.get("encryption_algorithm")
    )

    integrity_algorithm = (
        technical.get("integrity_algorithm")
        or crypto.get("integrity_algorithm")
    )

    authentication_method = (
        technical.get("authentication_method")
        or crypto.get("authentication_method")
    )

    key_exchange = (
        technical.get("key_exchange_method")
        or technical.get("key_exchange")
        or crypto.get("key_exchange_method")
        or crypto.get("dh_group")
    )

    prf = (
        technical.get("prf")
        or crypto.get("prf")
    )

    pfs = (
        technical.get("pfs")
        or crypto.get("pfs")
    )

    # ---------------------------------------------------------
    # PDF styles
    # ---------------------------------------------------------

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            leading=24,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=11,
            leading=14,
            spaceAfter=18,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            spaceBefore=14,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=13,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10,
        )
    )

    # ---------------------------------------------------------
    # Document
    # ---------------------------------------------------------

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="IPsec VPN Security Assessment",
        author="AI-Powered IPsec VPN Analyzer",
    )

    story = []

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "IPsec VPN Security Assessment",
            styles["ReportTitle"],
        )
    )

    story.append(
        Paragraph(
            "Security Assessment Report",
            styles["ReportSubtitle"],
        )
    )

    # ---------------------------------------------------------
    # Report information
    # ---------------------------------------------------------

    story.append(_section_title("Report Information", styles))

    story.append(
        _kv_table(
            [
                ("Report ID", report_id),
                ("Capture ID", capture_id),
                ("Generated", generated),
                ("Status", status),
            ],
            styles,
        )
    )

    # ---------------------------------------------------------
    # Executive summary
    # ---------------------------------------------------------

    story.append(_section_title("Executive Summary", styles))

    story.append(
        _kv_table(
            [
                ("IPsec Detected", ipsec_detected),
                ("IKE Version", ike_version),
                ("VPN Mode", vpn_mode),
                ("Traffic Type", traffic_type),
                ("Security Score", security_score),
                ("Risk Level", risk_level),
                ("AI Confidence", ai_confidence),
            ],
            styles,
        )
    )

    # ---------------------------------------------------------
    # Technical analysis
    # ---------------------------------------------------------

    story.append(_section_title("Technical Analysis", styles))

    story.append(
        _kv_table(
            [
                ("Encryption Algorithm", encryption),
                ("Integrity Algorithm", integrity_algorithm),
                ("Authentication Method", authentication_method),
                ("Key Exchange Method", key_exchange),
                ("PRF", prf),
                ("PFS", pfs),
                ("IKE Version", ike_version),
                ("VPN Mode", vpn_mode),
                ("Traffic Type", traffic_type),
            ],
            styles,
        )
    )

    # ---------------------------------------------------------
    # Security findings
    # ---------------------------------------------------------

    story.append(_section_title("Security Findings", styles))

    findings = _find_security_findings(security)

    if findings:
        for index, finding in enumerate(findings, start=1):
            if isinstance(finding, dict):
                title = (
                    finding.get("title")
                    or finding.get("rule")
                    or finding.get("id")
                    or f"Finding {index}"
                )

                severity = finding.get("severity")
                description = (
                    finding.get("description")
                    or finding.get("message")
                    or finding.get("details")
                    or ""
                )

                story.append(
                    Paragraph(
                        f"<b>{_safe(title)}</b>",
                        styles["Body"],
                    )
                )

                if severity:
                    story.append(
                        Paragraph(
                            f"Severity: {_safe(severity)}",
                            styles["Small"],
                        )
                    )

                if description:
                    story.append(
                        Paragraph(
                            _safe(description),
                            styles["Body"],
                        )
                    )

            else:
                story.append(
                    Paragraph(
                        f"<b>Finding {index}</b>: {_safe(finding)}",
                        styles["Body"],
                    )
                )

            story.append(Spacer(1, 6))
    else:
        story.append(
            Paragraph(
                "No security findings were reported.",
                styles["Body"],
            )
        )

    # ---------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------

    story.append(_section_title("Recommendations", styles))

    recommendations = _find_recommendations(security)

    if recommendations:
        for index, recommendation in enumerate(recommendations, start=1):
            story.append(
                Paragraph(
                    f"{index}. {_safe(recommendation)}",
                    styles["Body"],
                )
            )
            story.append(Spacer(1, 4))
    else:
        story.append(
            Paragraph(
                "No recommendations were reported.",
                styles["Body"],
            )
        )

    # ---------------------------------------------------------
    # Integrity verification
    # ---------------------------------------------------------

    story.append(_section_title("Integrity Verification", styles))

    integrity_status = (
        integrity.get("status")
        or ("VERIFIED" if integrity.get("report_hash") else "UNKNOWN")
    )

    hash_algorithm = (
        integrity.get("hash_algorithm")
        or "SHA-256"
    )

    report_hash = (
        integrity.get("report_hash")
        or integrity.get("sha256")
        or integrity.get("fingerprint")
    )

    story.append(
        _kv_table(
            [
                ("Verification Status", integrity_status),
                ("Hash Algorithm", hash_algorithm),
                ("SHA-256 Fingerprint", report_hash),
            ],
            styles,
        )
    )

    # ---------------------------------------------------------
    # Blockchain verification
    # ---------------------------------------------------------

    story.append(_section_title("Blockchain Verification", styles))

    blockchain_verified = blockchain.get("verified")

    blockchain_status = blockchain.get("status")

    if blockchain_verified is True:
        verification_status = "VERIFIED"
    elif blockchain_status:
        verification_status = blockchain_status
    else:
        verification_status = "NOT VERIFIED"

    contract_address = (
        blockchain.get("contract_address")
        or blockchain.get("contract")
    )

    blockchain_hash = (
        blockchain.get("blockchain_hash")
        or blockchain.get("report_hash")
    )

    blockchain_rows = [
        ("Verification Status", verification_status),
        ("Contract Address", contract_address),
    ]

    if blockchain_hash:
        blockchain_rows.append(
            ("Blockchain Hash", blockchain_hash)
        )

    if blockchain.get("report_id"):
        blockchain_rows.append(
            ("Blockchain Report ID", blockchain.get("report_id"))
        )

    story.append(
        _kv_table(
            blockchain_rows,
            styles,
        )
    )

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "Generated by AI-Powered IPsec VPN Analyzer",
            styles["Small"],
        )
    )

    # ---------------------------------------------------------
    # Build
    # ---------------------------------------------------------

    doc.build(story)

    return str(output_path)


# Backward-compatible entry point used by the replay and web application.
def generate_pdf_report(report, output_path):
    # The replay pipeline passes the JSON report path.
    # Accept both a Path/string and an already-loaded dictionary.
    if isinstance(report, (str, Path)):
        report_path = Path(report)
        with report_path.open("r", encoding="utf-8") as f:
            report = json.load(f)

    return generate_security_report_pdf(report, output_path)
