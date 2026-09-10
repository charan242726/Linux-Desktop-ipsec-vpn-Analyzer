import logging
import time
from scapy.all import IP, IPv6

logger = logging.getLogger(__name__)

def extract_esp_features(packets: list) -> dict:
    """
    Extract flow-level features from ESP packets.
    These features must match exactly what the ML model was trained on.
    No payload decryption — metadata only.
    """
    if not packets:
        return _empty_features()

    sizes = []
    timestamps = []
    directions_fwd = 0
    directions_bwd = 0
    forward_esp_bytes = 0
    reverse_esp_bytes = 0
    first_src = None

    from backend.services.ike_parser import classify_vpn_packet

    for pkt in packets:
        try:
            ptype = classify_vpn_packet(pkt)
            if ptype not in ("esp_native", "esp_natt"):
                continue

            layer = IP if IP in pkt else (IPv6 if IPv6 in pkt else None)
            if not layer:
                continue

            size = len(pkt)
            sizes.append(size)

            ts = float(pkt.time) if hasattr(pkt, 'time') else time.time()
            timestamps.append(ts)

            # Direction detection using first packet's src as reference
            src = pkt[layer].src
            if first_src is None:
                first_src = src
            if src == first_src:
                directions_fwd += 1
                forward_esp_bytes += size
            else:
                directions_bwd += 1
                reverse_esp_bytes += size

        except Exception as e:
            logger.debug(f"ESP packet feature error: {e}")
            continue

    if not sizes:
        return _empty_features()

    # Inter-arrival times
    inter_arrivals = []
    for i in range(1, len(timestamps)):
        diff = timestamps[i] - timestamps[i-1]
        if diff >= 0:
            inter_arrivals.append(diff)

    # Convert timestamps to microseconds to match ISCX dataset
    flow_duration_us = (timestamps[-1] - timestamps[0]) * 1000000 if len(timestamps) > 1 else 0
    total_bytes = sum(sizes)
    n = len(sizes)

    # Duration in seconds for rates
    flow_duration_sec = flow_duration_us / 1000000.0 if flow_duration_us > 0 else 0.001
    
    flowPktsPerSecond = n / flow_duration_sec
    flowBytesPerSecond = total_bytes / flow_duration_sec

    # IAT in microseconds
    iats_us = [x * 1000000 for x in inter_arrivals]
    avg_iat = sum(iats_us) / len(iats_us) if iats_us else 0
    std_iat = _std(iats_us, avg_iat) if iats_us else 0
    min_iat = min(iats_us) if iats_us else 0
    max_iat = max(iats_us) if iats_us else 0

    return {
        "duration":           round(flow_duration_us, 2),
        "flowPktsPerSecond":  round(flowPktsPerSecond, 2),
        "flowBytesPerSecond": round(flowBytesPerSecond, 2),
        "mean_flowiat":       round(avg_iat, 2),
        "std_flowiat":        round(std_iat, 2),
        "min_flowiat":        round(min_iat, 2),
        "max_flowiat":        round(max_iat, 2),
        "esp_packet_count":   n  # Kept for frontend dashboard display
    }


def _std(values: list, mean: float) -> float:
    if len(values) < 2:
        return 0.0
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5


def _empty_features() -> dict:
    return {
        "duration": 0,
        "flowPktsPerSecond": 0,
        "flowBytesPerSecond": 0,
        "mean_flowiat": 0,
        "std_flowiat": 0,
        "min_flowiat": 0,
        "max_flowiat": 0,
        "esp_packet_count": 0
    }
