import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.shared import stop_event
from backend.capture.capture_thread import start_capture_thread
from backend.worker.worker_thread import start_worker_thread
from backend.services.ml_engine import load_model
from backend.database.db import init_db
from backend.api.routes import status, sessions, reports, pcap

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)

_threads: list[threading.Thread] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("VPN Analyzer starting up")
    init_db()
    load_model()

    t_capture = start_capture_thread()
    t_worker = start_worker_thread()
    _threads.extend([t_capture, t_worker])
    logger.info("All threads started")

    yield  # FastAPI runs here

    # SHUTDOWN
    logger.info("Shutting down — stopping threads")
    stop_event.set()
    for t in _threads:
        t.join(timeout=5)
    logger.info("Shutdown complete")


app = FastAPI(title="VPN Analyzer", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*"],  # Electron only
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)

app.include_router(status.router)
app.include_router(sessions.router)
app.include_router(reports.router)
app.include_router(pcap.router)
