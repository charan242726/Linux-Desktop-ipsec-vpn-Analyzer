import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.core.shared import app_state, packet_queue
from backend.core.state import VpnState
from backend.database.db import init_db
from backend.capture.capture_thread import _process_packet, _rolling_buffer
from scapy.all import IP, UDP, Raw
import threading

@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    # Reset app state
    app_state.set_state(VpnState.IDLE)
    app_state.set_session(None)
    app_state._latest_findings = {}
    _rolling_buffer.clear()
    while not packet_queue.empty():
        packet_queue.get()

def test_rolling_buffer_and_session_start():
    client = TestClient(app)
    
    # 1. Simulate IKE packet to capture thread
    pkt = IP(dst="1.1.1.1")/UDP(sport=500, dport=500)/Raw(b"IKEv2")
    _process_packet(pkt)
    
    assert app_state.get_state() == VpnState.ANALYZING
    
    # 2. Add another packet
    pkt2 = IP(dst="1.1.1.1")/UDP(sport=500, dport=500)/Raw(b"ESP")
    _process_packet(pkt2)
    
    # The queue should now have the initial packet and the new packet
    assert packet_queue.qsize() == 2
    # 3. Verify buffer flushed to queue
    assert app_state.get_state() == VpnState.ANALYZING
    assert len(_rolling_buffer) == 0
    assert packet_queue.qsize() == 2
    
    p1 = packet_queue.get()
    p2 = packet_queue.get()
    assert UDP in p1 and p1[UDP].sport == 500
