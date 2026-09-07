import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.database.db import init_db
import os

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_pcap_analysis_endpoint():
    client = TestClient(app)
    
    # Path to known PCAP file
    pcap_path = "testbed/captures/aes128gcm_voip_r1.pcapng"
    
    if not os.path.exists(pcap_path):
        pytest.skip(f"PCAP {pcap_path} not found")
        
    with open(pcap_path, "rb") as f:
        response = client.post(
            "/analyze-pcap",
            files={"file": ("test.pcapng", f, "application/vnd.tcpdump.pcap")}
        )
        
    assert response.status_code == 200
    data = response.json()
    
    # Assert pipeline structure executed correctly
    assert "session_id" in data
    assert "findings" in data
    
    # Optional: We could check GET /sessions/current, but /analyze-pcap 
    # creates a background task. Since it's async we might not see findings instantly.
