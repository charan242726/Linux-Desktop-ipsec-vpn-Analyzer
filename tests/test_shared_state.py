import threading
import time
from backend.core.shared import SharedState
from backend.core.state import VpnState

def test_atomic_transition_race_condition():
    """Simulate two threads trying to transition from VPN_DETECTED to ANALYZING."""
    state = SharedState()
    state.set_state(VpnState.VPN_DETECTED)
    
    results = []
    
    def worker():
        success = state.transition(VpnState.VPN_DETECTED, VpnState.ANALYZING)
        results.append(success)
        
    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    # Only one thread should have succeeded
    assert results.count(True) == 1
    assert results.count(False) == 1
    assert state.get_state() == VpnState.ANALYZING

def test_heartbeats():
    state = SharedState()
    c, w = state.get_heartbeats()
    assert c == 0.0
    assert w == 0.0
    
    state.update_capture_heartbeat()
    c2, w2 = state.get_heartbeats()
    assert c2 > 0.0
    assert w2 == 0.0
