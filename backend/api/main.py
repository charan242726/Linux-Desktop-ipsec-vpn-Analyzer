from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.api.analysis_api import (
    start_live_analysis,
    get_analysis,
    stream_analysis,
)

from backend.api.replay_api import router as replay_router
from backend.api.report_api import router as report_router


app = FastAPI(
    title="AI-Powered IPsec VPN Analyzer",
    description="AI-powered IPsec VPN protocol analysis and security assessment platform",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    	"http://localhost:5173",
    	"http://127.0.0.1:5173",
    	"http://localhost:5174",
    	"http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(replay_router)
app.include_router(report_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "AI-Powered IPsec VPN Analyzer",
        "status": "running",
        "version": "1.0.0",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ============================================================
# LIVE ANALYSIS
# ============================================================

@app.post("/api/analysis/start")
def start_analysis():
    return start_live_analysis()


@app.get("/api/analysis/{analysis_id}")
def analysis_status(analysis_id: str):
    result = get_analysis(analysis_id)

    if result is None:
        return {
            "error": "Analysis not found",
            "analysis_id": analysis_id,
        }

    return result


# ============================================================
# LIVE ANALYSIS WEBSOCKET
# ============================================================

@app.websocket("/ws/analysis/{analysis_id}")
async def analysis_websocket(
    websocket: WebSocket,
    analysis_id: str,
):
    await websocket.accept()

    try:
        result = get_analysis(analysis_id)

        if result is None:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": "Analysis not found.",
                    "analysis_id": analysis_id,
                }
            )

            await websocket.close()
            return

        await stream_analysis(
            analysis_id,
            websocket,
        )

    except WebSocketDisconnect:
        return

    except Exception as exc:
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": str(exc),
                    "analysis_id": analysis_id,
                }
            )
        finally:
            await websocket.close()
