from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from fpdf import FPDF
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

@router.get("/{report_id}/pdf")
def export_pdf(report_id: int):
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    latest = report["findings"][-1] if report["findings"] else {}
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"VPN Security Report (ID: {report_id})", ln=True, align="C")
    
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, f"Start Time: {report['start_time']} | End Time: {report['end_time'] or 'Ongoing'}", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "IKE Configuration", ln=True)
    pdf.set_font("Helvetica", "", 10)
    ike = latest.get("ike")
    if ike:
        pdf.cell(0, 8, f"Initiator SPI: {ike.get('init_spi')}", ln=True)
        pdf.cell(0, 8, f"Responder SPI: {ike.get('resp_spi')}", ln=True)
        pdf.cell(0, 8, f"Exchange Type: {ike.get('exchange_type')}", ln=True)
    else:
        pdf.cell(0, 8, "No IKE data available.", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Security Assessment", ln=True)
    pdf.set_font("Helvetica", "", 10)
    rules = latest.get("security_rules", {})
    if rules:
        for rule_name, rule_data in rules.items():
            pdf.cell(0, 8, f"- {rule_name} [{rule_data.get('severity', 'UNKNOWN')}]: {rule_data.get('message', '')}", ln=True)
    else:
        pdf.cell(0, 8, "No security rules triggered.", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "ML Analysis (Traffic Classification)", ln=True)
    pdf.set_font("Helvetica", "", 10)
    ml = latest.get("ml")
    if ml:
        pdf.cell(0, 8, f"Predicted Traffic Type: {ml.get('predicted_class')}", ln=True)
        pdf.cell(0, 8, f"Confidence: {ml.get('confidence', 0)*100:.1f}%", ln=True)
    else:
        pdf.cell(0, 8, "No ML data available.", ln=True)

    pdf_bytes = bytes(pdf.output())
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=vpn_report_{report_id}.pdf"
        }
    )
