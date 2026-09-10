import logging
import threading
import time
from queue import Empty
from backend.core.shared import app_state, packet_queue, stop_event
from backend.core.state import VpnState
from backend.capture.capture_thread import set_current_cipher

# These imports will work once we stub out the services
from backend.services.ike_parser import parse_ike
from backend.services.esp_analyzer import extract_esp_features
from backend.services.rule_engine import run_rules
from backend.services.ml_engine import classify_traffic
from backend.database.db import save_findings, finalize_session, close_conn

logger = logging.getLogger(__name__)

# Track ESP packets for flow analysis
_esp_buffer = []
_last_packet_time = None
_last_bw_tick = time.time()  # bandwidth computation interval

INACTIVITY_WARN_SECONDS = 10
INACTIVITY_DISC_SECONDS = 60
BW_TICK_SECONDS = 2  # how often to compute bandwidth
_quiet_since = None
_is_quiet = False

def _check_disconnect(session_esp_count: int) -> bool:
    """
    Returns True only when multiple indicators suggest disconnection.
    Single inactivity period is NOT enough.
    """
    global _quiet_since, _is_quiet, _last_packet_time

    now = time.time()

    if _last_packet_time is None:
        return False

    inactive_for = now - _last_packet_time

    if inactive_for > INACTIVITY_WARN_SECONDS and not _is_quiet:
        _is_quiet = True
        _quiet_since = now
        logger.info("No ESP traffic for 10s — marking as quiet (not disconnected)")

    if _is_quiet and (now - _quiet_since) > INACTIVITY_DISC_SECONDS:
        # 60s total inactivity — probable disconnect
        logger.info("60s inactivity — assuming VPN disconnected")
        return True

    return False

def _reset_quiet():
    global _quiet_since, _is_quiet
    _quiet_since = None
    _is_quiet = False


def _analyze_batch(ike_packets: list, esp_packets: list) -> dict:
    """Full analysis pipeline. Runs in worker thread."""
    findings = {}

    # IKE analysis — deterministic, always works
    if ike_packets:
        ike_meta = parse_ike(ike_packets)
        rule_results = run_rules(ike_meta)
        findings["ike"] = ike_meta
        findings["security_rules"] = rule_results
        # Update cipher label for session peer tracking
        cipher = ike_meta.get("encryption_algorithm", "unknown")
        if cipher != "unknown":
            set_current_cipher(cipher)

    # ESP flow analysis + ML
    if esp_packets:
        features = extract_esp_features(esp_packets)
        findings["esp_features"] = features
        ml_result = classify_traffic(features)
        findings["ml"] = ml_result
        # Push latency estimate to SharedState
        latency = features.get("esp_mean_interarrival", 0.0)
        if latency > 0:
            app_state.update_latency(latency)

    findings["risk_level"] = _compute_risk(findings)
    return findings


def _compute_risk(findings: dict) -> str:
    """Simple risk aggregation from rule results."""
    rules = findings.get("security_rules", {})
    critical = sum(1 for v in rules.values() if v.get("severity") == "HIGH")
    if critical >= 2:
        return "HIGH"
    elif critical == 1:
        return "MEDIUM"
    return "LOW"


def run_worker():
    """Entry point for Thread 3."""
    global _last_packet_time, _last_bw_tick
    ike_buffer = []
    esp_buffer = []
    total_esp_count = 0

    logger.info("WorkerThread starting")
    
    try:
        while not stop_event.is_set():
            app_state.update_worker_heartbeat()
            state = app_state.get_state()
    
            if state != VpnState.ANALYZING:
                # Not analyzing — drain and discard queue, wait
                try:
                    packet_queue.get(timeout=1)
                    packet_queue.task_done()
                except Empty:
                    pass
                continue
    
            # Pull from queue with 1s timeout so we can check stop_event
            try:
                packet = packet_queue.get(timeout=1)
                packet_queue.task_done()
                _last_packet_time = time.time()
                _reset_quiet()

                from backend.services.ike_parser import classify_vpn_packet
                ptype = classify_vpn_packet(packet)
                if ptype in ("ike", "ike_natt"):
                    ike_buffer.append(packet)
                elif ptype in ("esp_native", "esp_natt"):
                    esp_buffer.append(packet)
                    total_esp_count += 1

            except Empty:
                # Compute bandwidth every BW_TICK_SECONDS even when no packets
                now = time.time()
                if now - _last_bw_tick >= BW_TICK_SECONDS:
                    app_state.compute_bandwidth()
                    _last_bw_tick = now

                if _check_disconnect(total_esp_count):
                    # finalize session
                    if ike_buffer or esp_buffer:
                        try:
                            findings = _analyze_batch(ike_buffer, esp_buffer)
                            app_state.update_findings(findings)
                            session_id = app_state.get_session()
                            if session_id:
                                save_findings(session_id, findings)
                        except Exception as e:
                            logger.error(f"Final analysis error: {e}")
    
                    # Close the session in DB
                    session_id = app_state.get_session()
                    if session_id:
                        finalize_session(session_id)
    
                    app_state.set_state(VpnState.DISCONNECTED)
                    app_state.set_session(None)
                    _last_packet_time = None
                    ike_buffer.clear()
                    esp_buffer.clear()
                    total_esp_count = 0
    
            # Analyze every 30 packets — also compute bandwidth
            if len(ike_buffer) + len(esp_buffer) >= 30:
                try:
                    findings = _analyze_batch(ike_buffer, esp_buffer)
                    app_state.update_findings(findings)
                    # Also tick bandwidth
                    app_state.compute_bandwidth()
                    _last_bw_tick = time.time()
                    session_id = app_state.get_session()
                    if session_id:
                        save_findings(session_id, findings)
                except Exception as e:
                    logger.error(f"Analysis pipeline error: {e}")
                finally:
                    ike_buffer.clear()
                    esp_buffer.clear()
    finally:
        close_conn()
        logger.info("WorkerThread stopped")


def start_worker_thread() -> threading.Thread:
    t = threading.Thread(target=run_worker, name="WorkerThread", daemon=True)
    t.start()
    return t
