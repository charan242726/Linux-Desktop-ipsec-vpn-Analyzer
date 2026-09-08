import threading
from queue import Queue
from .state import VpnState

class SharedState:
    def __init__(self):
        self._lock = threading.Lock()
        self._state = VpnState.IDLE
        self._latest_findings = {}
        self._current_session_id = None
        
        self._capture_heartbeat = 0.0
        self._worker_heartbeat = 0.0

    def get_heartbeats(self):
        with self._lock:
            return self._capture_heartbeat, self._worker_heartbeat
            
    def update_capture_heartbeat(self):
        import time
        with self._lock:
            self._capture_heartbeat = time.time()
            
    def update_worker_heartbeat(self):
        import time
        with self._lock:
            self._worker_heartbeat = time.time()

    # --- State ---
    def get_state(self) -> VpnState:
        with self._lock:
            return self._state

    def set_state(self, new_state: VpnState):
        with self._lock:
            self._state = new_state

    def transition(self, expected: VpnState, new: VpnState) -> bool:
        """
        Atomic check-and-set. Returns True if transition succeeded.
        Prevents race where two threads both see VPN_DETECTED
        and both try to start analysis.
        """
        with self._lock:
            if self._state != expected:
                return False
            self._state = new
            return True

    # --- Findings ---
    def update_findings(self, findings: dict):
        # Worker calls this. Never access _lock directly from outside.
        with self._lock:
            self._latest_findings = findings

    def get_findings(self) -> dict:
        with self._lock:
            return dict(self._latest_findings)  # return a copy, not reference

    # --- Session ---
    def set_session(self, session_id: int):
        with self._lock:
            self._current_session_id = session_id

    def get_session(self) -> int | None:
        with self._lock:
            return self._current_session_id


# Global singletons — imported by all threads
app_state = SharedState()

# Thread 2 puts raw packets here. Thread 3 reads from here.
# maxsize=500 prevents memory explosion if worker falls behind.
packet_queue = Queue(maxsize=500)

# Stop signal — set this to shut down all threads cleanly
stop_event = threading.Event()
