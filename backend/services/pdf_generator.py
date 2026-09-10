import json
import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def generate_professional_pdf(report: dict) -> bytes:
    session_id = report.get('id', 'Unknown')
    started_at = report.get('started_at', 'Unknown')
    ended_at = report.get('ended_at') or 'Ongoing'
    risk_level = report.get('risk_level', 'UNKNOWN')
    
    findings_list = report.get('findings', [])
    latest_finding = findings_list[-1] if findings_list else {}
    
    # IKE parameters occur during the handshake (early batches)
    ike = {}
    rules = {}
    for f in findings_list:
        if f.get('ike'):
            ike.update(f['ike'])
        if f.get('security_rules'):
            rules.update(f['security_rules'])
            
    # ML and ESP stats are most accurate in the final batch
    ml = latest_finding.get('ml', {})
    esp_features = latest_finding.get('esp_features', {})
    
    crit_c, high_c, med_c, low_c = 0, 0, 0, 0
    for r_name, r_data in rules.items():
        sev = str(r_data.get('severity', '')).upper()
        if sev == 'CRITICAL': crit_c += 1
        elif sev == 'HIGH': high_c += 1
        elif sev == 'MEDIUM': med_c += 1
        elif sev == 'LOW': low_c += 1
    total_findings = crit_c + high_c + med_c + low_c

    overall_sec = "SECURE" if risk_level == "LOW" else "HIGH RISK" if risk_level in ["HIGH", "CRITICAL"] else "WARNING"

    total_packets = esp_features.get('esp_packet_count', 0)
    has_ike = bool(ike)
    has_esp = bool(esp_features)
    
    raw_json = json.dumps(latest_finding, indent=2)
    if len(raw_json) > 3000:
        raw_json = raw_json[:3000] + "\n... [TRUNCATED FOR PDF]"

    # Setup Jinja2 Environment
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('report_template.html')

    # Render HTML string
    rendered_html = template.render(
        report_id=session_id,
        started_at=started_at,
        ended_at=ended_at,
        risk_level=risk_level,
        total_packets=total_packets,
        overall_sec=overall_sec,
        ike=ike,
        ml=ml,
        rules=rules,
        esp_features=esp_features,
        raw_json=raw_json,
        crit_c=crit_c,
        high_c=high_c,
        med_c=med_c,
        low_c=low_c,
        total_findings=total_findings,
        has_ike=has_ike,
        has_esp=has_esp
    )

    # Convert HTML to PDF using WeasyPrint
    pdf_bytes = HTML(string=rendered_html).write_pdf()
    
    return pdf_bytes
