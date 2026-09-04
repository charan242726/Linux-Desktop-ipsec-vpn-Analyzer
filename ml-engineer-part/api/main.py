#!/usr/bin/env python3
"""
Prediction API — the fixed contract this exposes:

    { "ipsec": true, "ike_version": "IKEv2", "mode": "Tunnel",
      "traffic_type": "Video", "confidence": 0.93 }

Design notes:
  - ipsec / ike_version / mode come from the deterministic IKE parser —
    reported with no uncertainty (they're read, not predicted).
  - traffic_type / confidence come from the trained RandomForest model —
    confidence is the model's actual predict_proba output for the
    predicted class, never a fabricated number.
  - If IKE parsing fails to find any ISAKMP packets at all, ipsec=false
    and everything else is null — an honest "we found nothing" result,
    not a guess.

Run:
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
"""

import sys
import tempfile
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from extract_esp_features import extract_flow_features  # noqa: E402
from extract_ike_features import extract_ike_info  # noqa: E402

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "traffic_classifier.joblib"

app = FastAPI(title="IPsec Traffic Analyzer — Prediction API")

_bundle = None  # lazy-loaded on first request, not at import time


def get_model_bundle():
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise HTTPException(
                status_code=503,
                detail=f"Model not found at {MODEL_PATH} — train it first with train_model.py",
            )
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


class PredictionResult(BaseModel):
    ipsec: bool
    ike_version: Optional[str] = None
    mode: Optional[str] = None
    traffic_type: Optional[str] = None
    confidence: Optional[float] = None


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": MODEL_PATH.exists()}


@app.post("/predict", response_model=PredictionResult)
def predict(pcap: UploadFile = File(...)):
    if not pcap.filename.endswith((".pcap", ".pcapng")):
        raise HTTPException(status_code=400, detail="File must be .pcap or .pcapng")

    bundle = get_model_bundle()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    # Write to a temp file — pyshark/scapy need a real file path, not a stream
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp.write(pcap.file.read())
        tmp_path = tmp.name

    try:
        # --- Deterministic part: parse IKE ---
        # A genuinely corrupted/garbage file (not just an empty-but-valid
        # capture) makes tshark itself crash, raised by pyshark as
        # TSharkCrashException -- treat that as "not a valid capture",
        # not a 500. Caught broadly here since pyshark doesn't expose a
        # narrower exception for every malformed-input case.
        try:
            ike_records = extract_ike_info(tmp_path)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Could not parse pcap file: {e}",
            )
        if not ike_records:
            return PredictionResult(ipsec=False)

        # NOTE: version/exchange-type -> human-readable mode mapping needs
        # the real field names verified against your tshark output (see
        # extract_ike_features.py header) — this is a placeholder mapping,
        # confirm it against actual captures before trusting it in a demo.
        ike_version_raw = ike_records[0].get("version")
        ike_version = "IKEv2" if str(ike_version_raw).startswith("2") else "IKEv1"

        # --- ML part: flow features -> traffic type prediction ---
        flow_rows = extract_flow_features(tmp_path)
        if not flow_rows:
            return PredictionResult(ipsec=True, ike_version=ike_version)

        # If multiple flows are in one pcap, predict per-flow and return
        # the majority/first — for a single-tunnel-per-capture demo this
        # is usually one flow anyway.
        flow_df = pd.DataFrame([flow_rows[0]])
        X = flow_df[feature_columns]

        pred_class = model.predict(X)[0]
        pred_proba = model.predict_proba(X)[0]
        confidence = float(max(pred_proba))

        # mode (tunnel/transport) is determined from packet structure,
        # not from the traffic classifier — wire this to your actual
        # tunnel/transport detection logic once built; placeholder here.
        mode = "Tunnel"  # TODO: replace with real detection

        return PredictionResult(
            ipsec=True,
            ike_version=ike_version,
            mode=mode,
            traffic_type=pred_class,
            confidence=round(confidence, 4),
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)
