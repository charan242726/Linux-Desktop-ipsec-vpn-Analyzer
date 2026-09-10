from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from backend.database.db import get_all_reports, get_report_by_id

router = APIRouter(prefix="/reports")

@router.get("")
def list_reports():
    return get_all_reports()

@router.get("/{report_id}")
def get_report(report_id: int):
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/latest/pdf")
def export_latest_pdf(type: str = 'technical'):
    reports = get_all_reports()
    if not reports:
        raise HTTPException(status_code=404, detail="No reports available")
    latest_report = sorted(reports, key=lambda x: x["id"], reverse=True)[0]
    return export_pdf(latest_report["id"], type)

@router.get("/{report_id}/pdf")
def export_pdf(report_id: int, type: str = 'technical'):
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    from backend.services.pdf_generator import generate_professional_pdf
    pdf_bytes = generate_professional_pdf(report)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=vpn_report_{report_id}.pdf"
        }
    )
