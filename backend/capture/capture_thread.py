import logging
import threading
from collections import deque
from scapy.all import sniff, UDP, IP, IPv6
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

# Best-known cipher from IKE exchange (updated by worker)
_current_cipher = "unknown"
_cipher_lock = threading.Lock()

def set_current_cipher(cipher: str):
    global _current_cipher
    with _cipher_lock:
        _current_cipher = cipher

def get_current_cipher() -> str:
    with _cipher_lock:
        return _current_cipher

def _process_packet(packet):
    state = app_state.get_state()

    is_ike = _is_ike(packet)
    is_esp = _is_esp(packet)
    is_natt = _is_natt(packet)

    if not (is_ike or is_esp or is_natt):
        return  # ignore non-VPN traffic

    if state in [VpnState.IDLE, VpnState.DISCONNECTED]:
        from backend.database.db import create_session
        session_id = create_session()
        app_state.set_session(session_id)
        
        with _buffer_lock:
            _rolling_buffer.append(packet)
            buffered = list(_rolling_buffer)
            _rolling_buffer.clear()
            
        for pkt in buffered:
            if not packet_queue.full():
                packet_queue.put(pkt)
                
        app_state.set_state(VpnState.ANALYZING)
        logger.info("VPN traffic detected — Auto-started analysis")

    elif state == VpnState.VPN_DETECTED:
        with _buffer_lock:
            _rolling_buffer.append(packet)

    elif state == VpnState.ANALYZING:
        # Track bandwidth and peer sessions for live UI
        pkt_size = len(packet)

        if is_esp or is_natt:
            layer = IP if IP in packet else (IPv6 if IPv6 in packet else None)
            if layer:
                src_ip = packet[layer].src
                dst_ip = packet[layer].dst

                # Determine direction — heuristic: private src = outbound
                is_private_src = (
                    src_ip.startswith("10.") or
                    src_ip.startswith("192.168.") or
                    src_ip.startswith("172.") or
                    src_ip == "127.0.0.1"
                )
                is_inbound = not is_private_src

                app_state.record_packet(pkt_size, is_inbound)

                # Track the remote peer
                remote_ip = dst_ip if is_inbound else src_ip
                local_ip = src_ip if is_inbound else dst_ip
                cipher = get_current_cipher()
                app_state.upsert_session_peer(remote_ip, local_ip, cipher, pkt_size)

        # Push to queue for worker analysis
        if not packet_queue.full():
            packet_queue.put(packet)


def run_capture():
    """Entry point for Thread 2. Blocks until stop_event is set."""
    logger.info("CaptureThread starting — requires admin/root privileges")
    try:
        from backend.config import CAPTURE_IFACE
        while not stop_event.is_set():
            app_state.update_capture_heartbeat()
            sniff(
                iface=CAPTURE_IFACE,
                filter=CAPTURE_FILTER,
                prn=_process_packet,
                store=False,
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
