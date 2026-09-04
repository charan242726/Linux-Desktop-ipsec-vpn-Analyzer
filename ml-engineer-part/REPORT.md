# Member 3 — AI/ML Engineer: Technical Report & Workflow
## SIH26160 — AI-Powered IPsec VPN Protocol Analyzer

---

## 1. Scope of this role

Build a system that, given a captured IPsec traffic sample, produces:
```json
{ "ipsec": true, "ike_version": "IKEv2", "mode": "Tunnel",
  "traffic_type": "Video", "confidence": 0.93 }
```
This output is the fixed contract consumed by Member 4's security assessment engine.

**Critical distinction maintained throughout this component**: `ipsec`, `ike_version`, and `mode` are **parsed, not predicted** — they come from cleartext fields in the IKE handshake and are reported with no uncertainty. Only `traffic_type` is a genuine machine-learning prediction, and only it carries a `confidence` score. This separation is deliberate and should be stated explicitly in the demo and report — ESP payload is encrypted, so traffic type cannot be read directly; it is *inferred* from observable metadata (packet size, timing, direction), never decrypted. Judges are expected to ask "how do you know that if it's encrypted?" — this is the honest answer.

---

## 2. Pipeline overview

```
pcap file
   │
   ├──► extract_ike_features.py   (deterministic parsing)
   │        └─► ipsec, ike_version, mode
   │
   └──► extract_esp_features.py   (flow-level stats)
            └─► aggregate_dataset.py (training time only)
            └─► train_model.py       (training time only)
                     └─► traffic_classifier.joblib
                              └─► main.py (FastAPI /predict)
                                       └─► traffic_type, confidence
```

Two independent extraction paths feed one combined output. The IKE path never touches ML. The ESP path is where all the machine learning lives.

---

## 3. Feature engineering — what the model actually sees

ESP encrypts the payload; what survives unencrypted is packet **size**, **timing**, and **direction**. The model is trained on flow-level aggregates of exactly these, computed per SPI (Security Parameter Index — one SPI = one tunnel/flow):

| Feature | Why it's discriminative |
|---|---|
| `packet_count` | Short bursts (ICMP) vs. sustained flows (video/streaming) differ sharply |
| `duration_sec` | Flow length — a ping burst is seconds, a video call is minutes |
| `size_mean`, `size_std`, `size_min`, `size_max` | VoIP is small and uniform (fixed codec frame size); video/streaming is large and near-MTU; web is bursty and variable |
| `iat_mean`, `iat_std` | Inter-arrival time — VoIP has famously regular, low-jitter timing (fixed 20ms codec frames); web/video is irregular and bursty |
| `fwd_bwd_byte_ratio` | Streaming/download is asymmetric (server sends much more); VoIP/video-calls are roughly symmetric (bidirectional real-time) |

**Deliberately excluded from the feature set**: `cipher`, `dh_group`, `pfs`, `mode`, `is_aead`. These are config metadata, not traffic-shape signal. Including them risks the model learning "this cipher implies this traffic type" — an artifact of how the testbed happened to generate the dataset, not a genuine traffic-fingerprinting signal. This is the feature-leakage risk to actively guard against; see Section 6.

---

## 4. Model choice: Random Forest, and why not deep learning

Given a ~6-day build window and a dataset generated in-house (necessarily smaller than published traffic-classification datasets), Random Forest was chosen over sequence models (LSTM/CNN) for concrete reasons:

- **Data efficiency** — RF performs reasonably on small tabular datasets; LSTMs typically need substantially more labeled sequences to outperform simpler baselines, which this project's timeline doesn't allow for reliably.
- **Interpretability** — `feature_importances_` gives a direct, defensible answer to "how does the model decide?", useful both for debugging and for judge questions.
- **No tuning budget needed** — sane defaults (`n_estimators=200`, `class_weight="balanced"`) work out of the box; deep learning requires real architecture/hyperparameter iteration this timeline doesn't support.

Prior work — e.g. LSTM-based time-series modeling of packet flows — has shown deep sequence models can outperform hand-engineered features for encrypted traffic classification given sufficient data. This is noted as a legitimate future-work direction in Section 7, not attempted here, to avoid spending scarce days chasing an approach unlikely to beat the baseline at this dataset scale.

---

## 5. Workflow — exact commands, in order

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build the labeled dataset from captured pcaps + Member 2's manifest.json
python3 scripts/aggregate_dataset.py \
    --captures /path/to/captures \
    --manifest /path/to/manifest.json \
    --out data/training_dataset.csv

# 3. Train the classifier (stratified split, held-out test set saved automatically)
python3 scripts/train_model.py \
    --data data/training_dataset.csv \
    --out models/traffic_classifier.joblib

# 4. Evaluate honestly — full classification report + confusion matrix
python3 scripts/evaluate_model.py \
    --model models/traffic_classifier.joblib \
    --test models/test_set.csv

# 5. Serve predictions
cd api && uvicorn main:app --host 0.0.0.0 --port 8001

# 6. Test the endpoint
curl -X POST -F "pcap=@sample.pcap" http://localhost:8001/predict
```

---

## 6. Validation checklist before trusting any reported number

- [ ] **Verify pyshark field names** against your actual tshark version on a real capture before trusting `extract_ike_features.py` output — field names are version-dependent (flagged in the script itself).
- [ ] **Confirm flow-level, not packet-level, train/test split** — `train_model.py`'s `train_test_split` operates on already-aggregated flow rows (one row per SPI), so this is satisfied structurally, but double-check your `aggregate_dataset.py` output truly has one row per flow, not per packet.
- [ ] **Leakage check**: train two models — one on data from only cipher/mode config A, test on config A held-out data; then test that *same* model on config B's data for the *same* traffic types. If accuracy collapses, the model may be learning config-specific artifacts rather than genuine traffic-shape signal. Report this test if you run it — it's a strong credibility signal.
- [ ] **Class balance**: check `value_counts()` on `traffic_type` before training — the `class_weight="balanced"` setting helps but doesn't fix a severely lopsided dataset (e.g., 200 web samples vs. 10 VoIP samples).
- [ ] **Never report accuracy without the confusion matrix behind it.**

---

## 7. Known limitations — state these upfront, don't wait to be asked

- Traffic generated via `iperf3`/`curl` loops approximates real VoIP/video traffic patterns but is not real codec output (real RTP has precise 20ms framing from an actual codec) — this is a reasonable simplification for a prototype, not real-world traffic.
- Dataset size is inherently limited by hackathon capture time — reported metrics reflect performance on this dataset, not a claim of general real-world accuracy.
- `mode` (Tunnel/Transport) detection in `api/main.py` is currently a placeholder — needs to be wired to actual packet-structure-based detection (packet size / header analysis) before the API's output is fully trustworthy.
- Sequence-model approaches (LSTM/CNN on raw packet sequences) were not attempted — noted as future work, per Section 4.

---

## 8. Deployment note

This service is containerized (`api/Dockerfile`) to be dropped into the team's shared `docker-compose.yml`, exposed internally on port 8001 for the dashboard/backend to call. No public cloud deployment is planned or needed — the team demo runs locally via `docker compose up`, standard practice for a hackathon prototype.
