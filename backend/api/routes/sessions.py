from fastapi import APIRouter, HTTPException
from backend.core.shared import app_state
from backend.core.state import VpnState
from backend.database.db import create_session
import logging
from backend.core.shared import packet_queue

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis")

@router.post("/start")
def start_session():
    success = app_state.transition(
        expected=VpnState.VPN_DETECTED,
        new=VpnState.ANALYZING
    )
    if not success:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot start from state: {app_state.get_state()}"
        )
        
    session_id = create_session()
    app_state.set_session(session_id)

    # Flush pre-captured handshake packets into queue
    from backend.capture.capture_thread import get_and_clear_buffer
    buffered = get_and_clear_buffer()
    for pkt in buffered:
        if not packet_queue.full():
            packet_queue.put(pkt)
    logger.info(f"Flushed {len(buffered)} buffered packets into session")

    return {"session_id": session_id, "state": VpnState.ANALYZING}

@router.get("")
def get_current():
    state = app_state.get_state()
    if state not in (VpnState.ANALYZING, VpnState.DISCONNECTED):
        raise HTTPException(status_code=404, detail="No active session")
    return {
        "state": state,
        "findings": app_state.get_findings()
    }

@router.patch("/current/pause")
def pause_session():
    if app_state.get_state() != VpnState.ANALYZING:
        raise HTTPException(status_code=409, detail="Not currently analyzing")
    app_state.set_state(VpnState.PAUSED)
    return {"state": VpnState.PAUSED}

@router.patch("/current/resume")
def resume_session():
    if app_state.get_state() != VpnState.PAUSED:
        raise HTTPException(status_code=409, detail="Not paused")
    app_state.set_state(VpnState.ANALYZING)
    return {"state": VpnState.ANALYZING}
