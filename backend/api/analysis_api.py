import asyncio
import threading
from datetime import datetime, timezone

from backend.services.analysis_orchestrator import (
    AnalysisOrchestrator,
)


_ANALYSES = {}
_LOCK = threading.Lock()


def _run_analysis(analysis_id, orchestrator):

    try:
        result = orchestrator.run()

        with _LOCK:
            entry = _ANALYSES.get(analysis_id)

            if entry:
                entry["status"] = result.get(
                    "status",
                    "UNKNOWN",
                )

                entry["result"] = result

                entry["completed"] = True

    except Exception as exc:

        with _LOCK:
            entry = _ANALYSES.get(analysis_id)

            if entry:
                entry["status"] = "FAILED"

                entry["result"] = {
                    "analysis_id":
                        analysis_id,

                    "status":
                        "FAILED",

                    "error":
                        str(exc),

                    "events":
                        orchestrator.events,
                }

                entry["completed"] = True


def start_live_analysis():

    orchestrator = AnalysisOrchestrator()

    analysis_id = orchestrator.analysis_id

    with _LOCK:

        _ANALYSES[analysis_id] = {
            "status": "STARTING",

            "result": {
                "analysis_id":
                    analysis_id,

                "status":
                    "STARTING",

                "events": [],

                "started_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            },

            "orchestrator":
                orchestrator,

            "completed":
                False,
        }

    worker = threading.Thread(
        target=_run_analysis,

        args=(
            analysis_id,
            orchestrator,
        ),

        daemon=True,
    )

    worker.start()

    return {
        "analysis_id":
            analysis_id,

        "status":
            "STARTING",
    }


def get_analysis(analysis_id):

    with _LOCK:

        analysis = _ANALYSES.get(
            analysis_id
        )

    if analysis is None:
        return None

    orchestrator = analysis.get(
        "orchestrator"
    )

    result = dict(
        analysis.get(
            "result",
            {},
        )
    )

    if orchestrator is not None:

        result["status"] = (
            orchestrator.status
        )

        result["events"] = (
            list(
                orchestrator.events
            )
        )

    return result


async def stream_analysis(
    analysis_id,
    websocket,
):

    last_event_count = 0

    while True:

        result = get_analysis(
            analysis_id
        )

        if result is None:

            await websocket.send_json({
                "type": "error",

                "message":
                    "Analysis not found.",
            })

            return

        events = result.get(
            "events",
            [],
        )

        # Send newly generated events.
        if len(events) > last_event_count:

            new_events = events[
                last_event_count:
            ]

            for event in new_events:

                await websocket.send_json({
                    "type":
                        "event",

                    "analysis_id":
                        analysis_id,

                    "event":
                        event,
                })

            last_event_count = len(
                events
            )

        # Send current status.
        await websocket.send_json({
            "type":
                "status",

            "analysis_id":
                analysis_id,

            "status":
                result.get(
                    "status",
                    "UNKNOWN",
                ),
        })

        terminal_statuses = {
            "COMPLETED",
            "FAILED",
            "WAITING_FOR_VPN",
        }

        if result.get("status") in terminal_statuses:

            await websocket.send_json({
                "type":
                    "completed",

                "analysis_id":
                    analysis_id,

                "status":
                    result.get(
                        "status"
                    ),

                "result":
                    result,
            })

            return

        await asyncio.sleep(0.5)
