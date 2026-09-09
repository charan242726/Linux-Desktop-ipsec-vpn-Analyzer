from fastapi import APIRouter, HTTPException
from backend.core.shared import app_state
from backend.core.state import VpnState
from backend.database.db import create_session
import logging
import time
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

    # Return data for any active/analyzable state — frontend needs bandwidth
    # even during ANALYZING, VPN_DETECTED, DISCONNECTED
    findings = app_state.get_findings()
    bandwidth = app_state.get_bandwidth()
    sessions = app_state.get_active_sessions()

    # Build enriched sessions list for the tunnel table
    enriched_sessions = []
    for i, s in enumerate(sessions):
        enriched_sessions.append({
            "id": f"SES-{1000 + i}",
            "name": s["remote_ip"],
            "remote_ip": s["remote_ip"],
            "local_ip": s["local_ip"],
            "protocol": "IKEv2",
            "cipher": s.get("cipher", "unknown"),
            "bandwidth": f"{round(s['bytes'] / 1_000_000, 2)} MB",
            "latency": f"{bandwidth.get('latency_ms', 0):.1f} ms",
            "jitter": "—",
            "rekeyIn": "—",
            "status": "ESTABLISHED" if (time.time() - s["last_seen"]) < 10 else "IDLE",
            "health": 100,
            "packet_count": s.get("packet_count", 0),
        })

    return {
        "state": state,
        "findings": findings,
        "bandwidth": bandwidth,
        "sessions": enriched_sessions,
        "tunnel_count": len(enriched_sessions),
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
