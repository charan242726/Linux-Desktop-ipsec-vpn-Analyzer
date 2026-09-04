import json
from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class PDFGenerationError(RuntimeError):
    """Raised when PDF report generation fails."""


def _safe(value, default="Unknown"):
    if value is None or value == "":
        return default
    return str(value)


def _paragraph(text, style):
    return Paragraph(
        _safe(text).replace("\n", "<br/>"),
        style,
    )


def generate_pdf_report(
    report_file,
    output_file,
):
    report_file = Path(report_file)
    output_file = Path(output_file)

    if not report_file.exists():
        raise PDFGenerationError(
            f"Security report not found: {report_file}"
        )

    try:
        with report_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            report = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise PDFGenerationError(
            f"Unable to read security report: {exc}"
        ) from exc

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
        spaceAfter=8 * mm,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=7 * mm,
        spaceAfter=4 * mm,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        spaceAfter=3 * mm,
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=10,
    )

    label_style = ParagraphStyle(
        "ReportLabel",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#555555"),
    )

    value_style = ParagraphStyle(
        "ReportValue",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=12,
    )

    story = []

    report_data = report.get(
        "report",
        {},
    )

    ai = report.get(
        "ai",
        {},
    )

    security = report.get(
        "security",
        {},
    )

    integrity = report.get(
        "integrity",
        {},
    )

    blockchain = report.get(
        "blockchain",
        {},
    )

    executive = report_data.get(
        "executive_summary",
        {},
    )

    technical = report_data.get(
        "technical_analysis",
        {},
    )

    # ------------------------------------------------------------
    # TITLE
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "IPsec VPN Security Assessment",
            title_style,
        )
    )

    story.append(
        Paragraph(
            _safe(
                report_data.get(
                    "report_id"
                ),
                "Security Assessment Report",
            ),
            subtitle_style,
        )
    )

    # ------------------------------------------------------------
    # REPORT METADATA
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Report Information",
            heading_style,
        )
    )

    metadata = [
        [
            _paragraph(
                "REPORT ID",
                label_style,
            ),
            _paragraph(
                report_data.get(
                    "report_id"
                ),
                value_style,
            ),
        ],
        [
            _paragraph(
                "CAPTURE ID",
                label_style,
            ),
            _paragraph(
                report_data.get(
                    "capture_id"
                ),
                value_style,
            ),
        ],
        [
            _paragraph(
                "GENERATED",
                label_style,
            ),
            _paragraph(
                report_data.get(
                    "generated_at"
                ),
                value_style,
            ),
        ],
        [
            _paragraph(
                "STATUS",
                label_style,
            ),
            _paragraph(
                report_data.get(
                    "status"
                ),
                value_style,
            ),
        ],
    ]

    metadata_table = Table(
        metadata,
        colWidths=[
            42 * mm,
            138 * mm,
        ],
        repeatRows=0,
    )

    metadata_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#DDDDDD"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F3F3F3"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        metadata_table
    )

    # ------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Executive Summary",
            heading_style,
        )
    )

    summary = [
        [
            _paragraph(
                "IPsec Detected",
                label_style,
            ),
            _paragraph(
                executive.get(
                    "ipsec_detected",
                    ai.get(
                        "ipsec_detected"
                    ),
                ),
                value_style,
            ),
        ],
        [
            _paragraph(
                "IKE Version",
                label_style,
            ),
            _paragraph(
                executive.get(
                    "ike_version",
                    ai.get(
                        "ike_version"
                    ),
                ),
                value_style,
            ),
        ],
        [
            _paragraph(
                "VPN Mode",
                label_style,
            ),
            _paragraph(
                executive.get(
                    "mode",
                    ai.get(
                        "mode"
                    ),
                ),
                value_style,
            ),
        ],
        [
            _paragraph(
                "Traffic Type",
                label_style,
            ),
            _paragraph(
                executive.get(
                    "traffic_type",
                    ai.get(
                        "traffic_type"
                    ),
                ),
                value_style,
            ),
        ],
        [
            _paragraph(
                "Security Score",
                label_style,
            ),
            _paragraph(
                executive.get(
                    "security_score",
                    security.get(
                        "security_score"
                    ),
                ),
                value_style,
            ),
        ],
        [
            _paragraph(
                "Risk Level",
                label_style,
            ),
            _paragraph(
                executive.get(
                    "risk_level",
                    security.get(
                        "risk_level"
                    ),
                ),
                value_style,
            ),
        ],
        [
            _paragraph(
                "AI Confidence",
                label_style,
            ),
            _paragraph(
                executive.get(
                    "ai_confidence",
                    ai.get(
                        "confidence"
                    ),
                ),
                value_style,
            ),
        ],
    ]

    summary_table = Table(
        summary,
        colWidths=[
            42 * mm,
            138 * mm,
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#DDDDDD"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F3F3F3"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        summary_table
    )

    # ------------------------------------------------------------
    # TECHNICAL ANALYSIS
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Technical Analysis",
            heading_style,
        )
    )

    technical_fields = [
        (
            "Encryption Algorithm",
            technical.get(
                "encryption_algorithm",
                ai.get(
                    "encryption_algorithm"
                ),
            ),
        ),
        (
            "Authentication Algorithm",
            technical.get(
                "authentication_algorithm",
                ai.get(
                    "authentication_algorithm"
                ),
            ),
        ),
        (
            "Key Exchange Method",
            technical.get(
                "key_exchange_method",
                ai.get(
                    "key_exchange_method"
                ),
            ),
        ),
        (
            "IKE Version",
            ai.get(
                "ike_version"
            ),
        ),
        (
            "VPN Mode",
            ai.get(
                "mode"
            ),
        ),
        (
            "Traffic Type",
            ai.get(
                "traffic_type"
            ),
        ),
    ]

    technical_rows = [
        [
            _paragraph(
                label,
                label_style,
            ),
            _paragraph(
                value,
                value_style,
            ),
        ]
        for label, value
        in technical_fields
    ]

    technical_table = Table(
        technical_rows,
        colWidths=[
            60 * mm,
            120 * mm,
        ],
    )

    technical_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#DDDDDD"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F3F3F3"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        technical_table
    )

    # ------------------------------------------------------------
    # FINDINGS
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Security Findings",
            heading_style,
        )
    )

    findings = security.get(
        "findings",
        [],
    )

    if not findings:
        story.append(
            Paragraph(
                "No security findings were reported.",
                body_style,
            )
        )
    else:
        for index, finding in enumerate(
            findings,
            start=1,
        ):
            title = (
                finding.get("title")
                or finding.get("id")
                or f"Finding {index}"
            )

            description = (
                finding.get("description")
                or finding.get("message")
                or "No description available."
            )

            severity = (
                finding.get("severity")
                or finding.get("risk")
                or ""
            )

            story.append(
                Paragraph(
                    f"<b>{_safe(title)}</b>"
                    + (
                        f" — {_safe(severity)}"
                        if severity
                        else ""
                    ),
                    body_style,
                )
            )

            story.append(
                Paragraph(
                    _safe(description),
                    small_style,
                )
            )

            story.append(
                Spacer(
                    1,
                    2 * mm,
                )
            )

    # ------------------------------------------------------------
    # RECOMMENDATIONS
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Recommendations",
            heading_style,
        )
    )

    recommendations = security.get(
        "recommendations",
        [],
    )

    if not recommendations:
        story.append(
            Paragraph(
                "No recommendations were reported.",
                body_style,
            )
        )
    else:
        for index, recommendation in enumerate(
            recommendations,
            start=1,
        ):
            story.append(
                Paragraph(
                    f"{index}. {_safe(recommendation)}",
                    body_style,
                )
            )

    # ------------------------------------------------------------
    # INTEGRITY
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Integrity Verification",
            heading_style,
        )
    )

    report_hash = (
        integrity.get(
            "report_hash"
        )
        or integrity.get(
            "sha256"
        )
    )

    integrity_rows = [
        [
            _paragraph(
                "Hash Algorithm",
                label_style,
            ),
            _paragraph(
                integrity.get(
                    "hash_algorithm",
                    "SHA-256",
                ),
                value_style,
            ),
        ],
        [
            _paragraph(
                "SHA-256 Fingerprint",
                label_style,
            ),
            _paragraph(
                report_hash,
                small_style,
            ),
        ],
    ]

    integrity_table = Table(
        integrity_rows,
        colWidths=[
            48 * mm,
            132 * mm,
        ],
    )

    integrity_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#DDDDDD"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F3F3F3"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        integrity_table
    )

    # ------------------------------------------------------------
    # BLOCKCHAIN
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Blockchain Verification",
            heading_style,
        )
    )

    blockchain_rows = [
        [
            _paragraph(
                "Verification Status",
                label_style,
            ),
            _paragraph(
                "VERIFIED"
                if blockchain.get(
                    "verified"
                )
                else "NOT VERIFIED",
                value_style,
            ),
        ],
        [
            _paragraph(
                "Contract Address",
                label_style,
            ),
            _paragraph(
                blockchain.get(
                    "contract_address"
                ),
                small_style,
            ),
        ],
    ]

    blockchain_table = Table(
        blockchain_rows,
        colWidths=[
            48 * mm,
            132 * mm,
        ],
    )

    blockchain_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#DDDDDD"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F3F3F3"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        blockchain_table
    )

    # ------------------------------------------------------------
    # FOOTER
    # ------------------------------------------------------------

    story.append(
        Spacer(
            1,
            8 * mm,
        )
    )

    story.append(
        Paragraph(
            "Generated by AI-Powered IPsec VPN Analyzer",
            subtitle_style,
        )
    )

    try:
        document = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
            title=_safe(
                report_data.get(
                    "report_id"
                ),
                "IPsec VPN Security Assessment",
            ),
            author="AI-Powered IPsec VPN Analyzer",
        )

        document.build(story)

    except Exception as exc:
        raise PDFGenerationError(
            f"PDF generation failed: {exc}"
        ) from exc

    if not output_file.exists():
        raise PDFGenerationError(
            f"PDF was not generated: {output_file}"
        )

    return {
        "pdf_path": str(
            output_file
        ),
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "PDF_GENERATED",
    }
