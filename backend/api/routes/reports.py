from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from pathlib import Path
from backend.database.db import get_all_reports, get_report_by_id

router = APIRouter(prefix="/reports")

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

@router.get("")
def list_reports():
    return get_all_reports()

@router.get("/{report_id}")
def get_report(report_id: int):
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/{report_id}/pdf")
def export_pdf(report_id: int):
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Flatten latest findings for template
    latest = report["findings"][-1] if report["findings"] else {}

    template = jinja_env.get_template("report.html")
    html_str = template.render(
        session=report,
        ike=latest.get("ike"),
        rules=latest.get("security_rules", {}),
        ml=latest.get("ml"),
        esp=latest.get("esp_features"),
    )

    pdf_bytes = HTML(string=html_str).write_pdf()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=vpn_report_{report_id}.pdf"
        }
    )
