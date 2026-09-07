import tempfile
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from scapy.all import rdpcap, UDP, IP
from backend.services.ike_parser import parse_ike
from backend.services.esp_analyzer import extract_esp_features
from backend.services.rule_engine import run_rules
from backend.services.ml_engine import classify_traffic
from backend.database.db import create_session, save_findings

router = APIRouter(prefix="/analyze-pcap")

ESP_PROTO = 50
IKE_PORTS = {500, 4500}

@router.post("")
async def analyze_pcap(file: UploadFile = File(...)):
    if not file.filename.endswith((".pcap", ".pcapng")):
        raise HTTPException(status_code=400, detail="Only .pcap/.pcapng files accepted")

    # Write upload to temp file — scapy needs a file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pcap") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        packets = rdpcap(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read PCAP: {e}")
    finally:
        os.unlink(tmp_path)

    ike_pkts = [p for p in packets if UDP in p and
                (p[UDP].dport in IKE_PORTS or p[UDP].sport in IKE_PORTS)]
    esp_pkts = [p for p in packets if IP in p and p[IP].proto == ESP_PROTO]

    if not ike_pkts and not esp_pkts:
        raise HTTPException(status_code=422, detail="No IKE or ESP packets found in PCAP")

    ike_meta   = parse_ike(ike_pkts)
    rules      = run_rules(ike_meta)
    features   = extract_esp_features(esp_pkts)
    ml_result  = classify_traffic(features)

    findings = {
        "source":         "pcap_upload",
        "filename":       file.filename,
        "ike":            ike_meta,
        "security_rules": rules,
        "esp_features":   features,
        "ml":             ml_result,
        "risk_level":     _risk(rules)
    }

    session_id = create_session()
    save_findings(session_id, findings)

    return {"session_id": session_id, "findings": findings}


def _risk(rules: dict) -> str:
    high = sum(1 for v in rules.values() if v.get("severity") == "HIGH")
    if high >= 2: return "HIGH"
    if high == 1: return "MEDIUM"
    return "LOW"
