import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
# We adjusted BASE_DIR to point to the project root so it finds /models instead of backend/models
MODEL_PATH = BASE_DIR / "ml" / "model" / "primary_rf_pipeline.pkl"
DB_PATH = BASE_DIR / "data" / "vpn_analyzer.db"
LOG_PATH = BASE_DIR / "logs" / "service.log"

# BPF filter — captures IKE (UDP 500/4500) and ESP (IP proto 50)
CAPTURE_FILTER = "udp port 500 or udp port 4500 or ip proto 50"
CAPTURE_IFACE = os.getenv("CAPTURE_IFACE", "virbr-lab0")

POLL_INTERVAL = 2  # seconds, matches Electron polling
