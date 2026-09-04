from pathlib import Path
from threading import Thread
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from backend.services.replay_service import run_replay_analysis


router = APIRouter(prefix="/api/replay", tags=["Replay Analysis"])

DEFAULT_CAPTURE = (
    Path(__file__).resolve().parents[2]
    / "testbed"
    / "captures"
    / "capture_combined_vpn.pcap"
)

_replay_results = {}


def _run_replay(replay_id: str, capture_file: str):
    try:
        result = run_replay_analysis(capture_file)

        _replay_results[replay_id] = {
            "status": "COMPLETED",
            "result": result,
        }

    except Exception as exc:
        _replay_results[replay_id] = {
            "status": "FAILED",
            "error": str(exc),
        }


@router.post("/start")
def start_replay(capture_file: str | None = None):
    capture_path = Path(capture_file) if capture_file else DEFAULT_CAPTURE

    if not capture_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Capture file not found: {capture_path}",
        )

    replay_id = f"REPLAY-WEB-{uuid4().hex[:8].upper()}"

    _replay_results[replay_id] = {
        "status": "RUNNING",
        "capture_file": str(capture_path),
    }

    thread = Thread(
        target=_run_replay,
        args=(replay_id, str(capture_path)),
        daemon=True,
    )

    thread.start()

    return {
        "replay_id": replay_id,
        "status": "RUNNING",
        "capture_file": str(capture_path),
    }


@router.get("/{replay_id}")
def get_replay(replay_id: str):
    result = _replay_results.get(replay_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Replay analysis not found",
        )

    return {
        "replay_id": replay_id,
        **result,
    }
