import logging
import threading
from collections import deque
from scapy.all import sniff, UDP, IP
from backend.core.shared import app_state, packet_queue, stop_event
from backend.core.state import VpnState
from backend.config import CAPTURE_FILTER

logger = logging.getLogger(__name__)

# Rolling buffer — keeps last 200 VPN packets before user starts analysis
_rolling_buffer = deque(maxlen=200)
_buffer_lock = threading.Lock()

def get_and_clear_buffer() -> list:
    with _buffer_lock:
        packets = list(_rolling_buffer)
        _rolling_buffer.clear()
        return packets

IKE_PORTS = {500, 4500}
ESP_PROTO = 50

def _is_ike(packet) -> bool:
    return UDP in packet and (
        packet[UDP].dport in IKE_PORTS or
        packet[UDP].sport in IKE_PORTS
    )

def _is_esp(packet) -> bool:
    return IP in packet and packet[IP].proto == ESP_PROTO

def _is_natt(packet) -> bool:
    """UDP/4500 carries both IKE and ESP-in-UDP (NAT traversal)."""
    return UDP in packet and (
        packet[UDP].dport == 4500 or packet[UDP].sport == 4500
    )

def _process_packet(packet):
    state = app_state.get_state()

    # Classify packet type first
    is_ike = _is_ike(packet)
    is_esp = _is_esp(packet)
    is_natt = _is_natt(packet)  # UDP/4500 — could be IKE or ESP-in-UDP

    if not (is_ike or is_esp or is_natt):
        return  # ignore non-VPN traffic

    if state == VpnState.IDLE:
        # Always buffer VPN candidate packets
        with _buffer_lock:
            _rolling_buffer.append(packet)
        app_state.set_state(VpnState.VPN_DETECTED)
        logger.info("VPN traffic detected")

    elif state == VpnState.VPN_DETECTED:
        # Keep buffering — user hasn't clicked start yet
        with _buffer_lock:
            _rolling_buffer.append(packet)

    elif state == VpnState.ANALYZING:
        # Push to queue for worker
        if not packet_queue.full():
            packet_queue.put(packet)


def run_capture():
    """Entry point for Thread 2. Blocks until stop_event is set."""
    logger.info("CaptureThread starting — requires admin/root privileges")
    try:
        while not stop_event.is_set():
            app_state.update_capture_heartbeat()
            sniff(
                filter=CAPTURE_FILTER,
                prn=_process_packet,
                store=False,                          # don't accumulate in memory
                timeout=2,
                stop_filter=lambda p: stop_event.is_set()
            )
    except PermissionError:
        logger.critical(
            "Packet capture failed: insufficient privileges. "
            "Run as Administrator on Windows or root on Linux."
        )
    except Exception as e:
        logger.error(f"CaptureThread crashed: {e}")
    finally:
        logger.info("CaptureThread stopped")


def start_capture_thread() -> threading.Thread:
    t = threading.Thread(target=run_capture, name="CaptureThread", daemon=True)
    t.start()
    return t
