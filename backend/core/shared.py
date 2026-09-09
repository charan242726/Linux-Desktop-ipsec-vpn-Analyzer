import threading
import time
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

        # ── Live bandwidth & session tracking ──────────────────────────────────
        # Accumulated byte counters reset every interval by worker
        self._inbound_bytes = 0
        self._outbound_bytes = 0
        self._bw_window_start = time.time()

        # Last computed rates (bytes/s)
        self._inbound_bps = 0.0
        self._outbound_bps = 0.0

        # Active peer IPs seen in this session  {remote_ip: {local_ip, cipher, last_seen, bytes}}
        self._sessions: dict[str, dict] = {}

        # Latency estimate from ESP inter-arrival
        self._latency_ms = 0.0

        # Total packet counts
        self._total_packets = 0

    # ── Heartbeats ─────────────────────────────────────────────────────────────
    def get_heartbeats(self):
        with self._lock:
            return self._capture_heartbeat, self._worker_heartbeat

    def update_capture_heartbeat(self):
        with self._lock:
            self._capture_heartbeat = time.time()

    def update_worker_heartbeat(self):
        with self._lock:
            self._worker_heartbeat = time.time()

    # ── State ──────────────────────────────────────────────────────────────────
    def get_state(self) -> VpnState:
        with self._lock:
            return self._state

    def set_state(self, new_state: VpnState):
        with self._lock:
            self._state = new_state

    def transition(self, expected: VpnState, new: VpnState) -> bool:
        with self._lock:
            if self._state != expected:
                return False
            self._state = new
            return True

    # ── Findings ───────────────────────────────────────────────────────────────
    def update_findings(self, findings: dict):
        with self._lock:
            self._latest_findings = findings

    def get_findings(self) -> dict:
        with self._lock:
            return dict(self._latest_findings)

    # ── Session ────────────────────────────────────────────────────────────────
    def set_session(self, session_id: int):
        with self._lock:
            self._current_session_id = session_id

    def get_session(self) -> int | None:
        with self._lock:
            return self._current_session_id

    # ── Live Bandwidth ─────────────────────────────────────────────────────────
    def record_packet(self, size: int, is_inbound: bool):
        """Called by capture thread for every ESP packet."""
        with self._lock:
            if is_inbound:
                self._inbound_bytes += size
            else:
                self._outbound_bytes += size
            self._total_packets += 1

    def compute_bandwidth(self):
        """
        Called by worker thread every ~2s to compute rates and reset counters.
        Returns (inbound_bps, outbound_bps).
        """
        now = time.time()
        with self._lock:
            elapsed = now - self._bw_window_start
            if elapsed < 0.1:
                return self._inbound_bps, self._outbound_bps

            self._inbound_bps = self._inbound_bytes / elapsed
            self._outbound_bps = self._outbound_bytes / elapsed
            self._inbound_bytes = 0
            self._outbound_bytes = 0
            self._bw_window_start = now
            return self._inbound_bps, self._outbound_bps

    def get_bandwidth(self) -> dict:
        with self._lock:
            return {
                "inbound_bps": round(self._inbound_bps, 1),
                "outbound_bps": round(self._outbound_bps, 1),
                "inbound_mbps": round(self._inbound_bps / 1_000_000, 3),
                "outbound_mbps": round(self._outbound_bps / 1_000_000, 3),
                "total_packets": self._total_packets,
                "latency_ms": round(self._latency_ms, 2),
            }

    def update_latency(self, latency_ms: float):
        with self._lock:
            self._latency_ms = latency_ms

    # ── Active Sessions (peer IP table) ────────────────────────────────────────
    def upsert_session_peer(self, remote_ip: str, local_ip: str, cipher: str, size: int):
        """Called by capture thread for each ESP packet to track active peers."""
        with self._lock:
            if remote_ip not in self._sessions:
                self._sessions[remote_ip] = {
                    "remote_ip": remote_ip,
                    "local_ip": local_ip,
                    "cipher": cipher,
                    "bytes": 0,
                    "packet_count": 0,
                    "first_seen": time.time(),
                    "last_seen": time.time(),
                    "status": "ESTABLISHED",
                }
            sess = self._sessions[remote_ip]
            sess["bytes"] += size
            sess["packet_count"] += 1
            sess["last_seen"] = time.time()

    def get_active_sessions(self) -> list:
        """Return sessions active in the last 30 seconds."""
        now = time.time()
        with self._lock:
            active = []
            for s in self._sessions.values():
                if now - s["last_seen"] < 30:
                    active.append(dict(s))
            return active

    def clear_sessions(self):
        with self._lock:
            self._sessions.clear()
            self._total_packets = 0
            self._inbound_bps = 0.0
            self._outbound_bps = 0.0


# Global singletons — imported by all threads
app_state = SharedState()

# Thread 2 puts raw packets here. Thread 3 reads from here.
packet_queue = Queue(maxsize=500)

# Stop signal — set this to shut down all threads cleanly
stop_event = threading.Event()
