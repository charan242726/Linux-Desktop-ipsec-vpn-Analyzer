import pytest
from backend.core.state import VpnState
from backend.core.shared import SharedState

def test_initial_state():
    state = SharedState()
    assert state.get_state() == VpnState.IDLE

def test_valid_transitions():
    state = SharedState()
    
    # IDLE -> VPN_DETECTED
    state.set_state(VpnState.VPN_DETECTED)
    assert state.get_state() == VpnState.VPN_DETECTED
    
    # VPN_DETECTED -> ANALYZING
    assert state.transition(VpnState.VPN_DETECTED, VpnState.ANALYZING) == True
    assert state.get_state() == VpnState.ANALYZING
    
    # ANALYZING -> PAUSED
    state.set_state(VpnState.PAUSED)
    assert state.get_state() == VpnState.PAUSED
    
    # PAUSED -> ANALYZING
    state.set_state(VpnState.ANALYZING)
    assert state.get_state() == VpnState.ANALYZING
    
    # ANALYZING -> DISCONNECTED
    state.set_state(VpnState.DISCONNECTED)
    assert state.get_state() == VpnState.DISCONNECTED
    
    # DISCONNECTED -> FINALIZED (or IDLE)
    state.set_state(VpnState.IDLE)
    assert state.get_state() == VpnState.IDLE

def test_invalid_transitions():
    state = SharedState()
    # IDLE -> ANALYZING should fail if using transition()
    assert state.transition(VpnState.VPN_DETECTED, VpnState.ANALYZING) == False
    assert state.get_state() == VpnState.IDLE
