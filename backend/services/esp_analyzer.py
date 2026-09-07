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
            else:
                directions_bwd += 1

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

    flow_duration = (timestamps[-1] - timestamps[0]) if len(timestamps) > 1 else 0
    total_bytes = sum(sizes)
    n = len(sizes)

    avg_size = total_bytes / n
    min_size = min(sizes)
    max_size = max(sizes)
    std_size = _std(sizes, avg_size)

    avg_iat = sum(inter_arrivals) / len(inter_arrivals) if inter_arrivals else 0
    std_iat = _std(inter_arrivals, avg_iat) if inter_arrivals else 0

    bps = total_bytes / flow_duration if flow_duration > 0 else 0
    pps = n / flow_duration if flow_duration > 0 else 0

    return {
        # These keys must match your training feature columns exactly
        "flow_duration":         round(flow_duration, 4),
        "total_packets":         n,
        "total_bytes":           total_bytes,
        "avg_packet_size":       round(avg_size, 2),
        "min_packet_size":       min_size,
        "max_packet_size":       max_size,
        "std_packet_size":       round(std_size, 2),
        "avg_inter_arrival_ms":  round(avg_iat * 1000, 2),
        "std_inter_arrival_ms":  round(std_iat * 1000, 2),
        "bytes_per_second":      round(bps, 2),
        "packets_per_second":    round(pps, 2),
        "fwd_packets":           directions_fwd,
        "bwd_packets":           directions_bwd,
        "fwd_bwd_ratio":         round(directions_fwd / n, 3),
    }


def _std(values: list, mean: float) -> float:
    if len(values) < 2:
        return 0.0
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5


def _empty_features() -> dict:
    return {k: 0 for k in [
        "flow_duration", "total_packets", "total_bytes",
        "avg_packet_size", "min_packet_size", "max_packet_size",
        "std_packet_size", "avg_inter_arrival_ms", "std_inter_arrival_ms",
        "bytes_per_second", "packets_per_second",
        "fwd_packets", "bwd_packets", "fwd_bwd_ratio"
    ]}
