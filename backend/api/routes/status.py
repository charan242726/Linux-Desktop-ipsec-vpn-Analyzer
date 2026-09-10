from fastapi import APIRouter
from backend.core.shared import app_state

router = APIRouter()

import time

@router.get("/health")
def health():
    cap_time, work_time = app_state.get_heartbeats()
    now = time.time()
    
    # 5 second threshold for heartbeats (capture uses 2s timeout, worker uses 1s)
    capture_running = "running" if (now - cap_time) < 5 else "dead"
    worker_running = "running" if (now - work_time) < 5 else "dead"
    
    from backend.services.ml_engine import ML_AVAILABLE
    
    status = "ok" if capture_running == "running" and worker_running == "running" else "degraded"
    
    return {
        "status": status,
        "state": app_state.get_state().value,
        "capture": capture_running,
        "worker": worker_running,
        "ml_available": ML_AVAILABLE
    }

@router.get("/status")
def get_status():
    return {
        "state": app_state.get_state(),
        "session_id": app_state.get_session()
    }

import subprocess
import os

@router.post("/simulate")
def simulate_traffic():
    # Trigger docker-compose up -d to spawn alice/bob VPN nodes
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        subprocess.Popen(["docker-compose", "up", "-d"], cwd=project_root)
        return {"status": "success", "message": "Simulation started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
