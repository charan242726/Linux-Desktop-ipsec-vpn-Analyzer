import logging
from scapy.all import UDP, Raw, IP, IPv6
from scapy.layers.isakmp import ISAKMP

logger = logging.getLogger(__name__)

def classify_vpn_packet(packet) -> str:
    """
    Returns: 'ike', 'esp_native', 'esp_natt', 'ike_natt', 'unknown'
    Let the parser decide what the packet is — not the capture filter.
    """
    if IP not in packet and IPv6 not in packet:
        return "unknown"

    # Native ESP
    layer = IP if IP in packet else IPv6
    if packet[layer].proto == 50:
        return "esp_native"

    if UDP not in packet:
        return "unknown"

    dport = packet[UDP].dport
    sport = packet[UDP].sport

    # IKE — standard port
    if dport in (500,) or sport in (500,):
        return "ike"

    # NAT-T port — could be IKE or ESP-in-UDP
    if dport == 4500 or sport == 4500:
        payload = bytes(packet[UDP].payload)
        if len(payload) < 4:
            return "unknown"
        # ESP-in-UDP has 4 zero bytes as non-ESP marker for IKE
        if payload[:4] == b'\x00\x00\x00\x00':
            return "ike_natt"   # IKE over NAT-T
        return "esp_natt"       # ESP encapsulated in UDP

    return "unknown"

# IKEv2 constants
ENCR_MAP = {
    1: "DES", 3: "3DES", 12: "AES-CBC",
    13: "AES-CTR", 20: "AES-GCM"
}
AUTH_MAP = {
    1: "HMAC-MD5", 2: "HMAC-SHA1",
    12: "HMAC-SHA256", 14: "HMAC-SHA512"
}
DH_MAP = {
    1: "Group1-768", 2: "Group2-1024", 5: "Group5-1536",
    14: "Group14-2048", 19: "Group19-P256", 20: "Group20-P384"
}

def _detect_ike_version(raw_bytes: bytes) -> str:
    """
    IKEv2 sets bit 4 of byte 17 (flags byte).
    IKEv1 has exchange types 1-5, IKEv2 has 34-37.
    """
    if len(raw_bytes) < 18:
        return "unknown"
    exchange_type = raw_bytes[18]
    if exchange_type in (34, 35, 36, 37):
        return "IKEv2"
    elif exchange_type in (1, 2, 3, 4, 5):
        return "IKEv1"
    return "unknown"

def _extract_proposals(raw_bytes: bytes) -> dict:
    """
    Parse proposal payloads from IKEv2 SA payload.
    Scapy's IKEv2 dissector is incomplete — manual byte parsing needed.
    Returns best-effort extraction.
    """
    result = {
        "encryption_algorithm": "unknown",
        "auth_algorithm": "unknown",
        "dh_group": 0,
        "pfs_enabled": False,
        "sa_lifetime_seconds": 86400
    }

    try:
        # SA payload starts after 28-byte IKE header
        # Next payload byte tells us what follows
        if len(raw_bytes) < 28:
            return result

        # Walk payloads — each has: next_payload(1) + critical(1) + length(2)
        offset = 28
        next_payload = raw_bytes[16]  # first payload type from IKE header

        while offset < len(raw_bytes) - 4 and next_payload != 0:
            payload_type = next_payload
            next_payload = raw_bytes[offset]
            payload_len = int.from_bytes(raw_bytes[offset+2:offset+4], 'big')

            if payload_type == 33:  # SA payload (IKEv2)
                _parse_sa_payload(raw_bytes[offset+4:offset+payload_len], result)

            offset += payload_len
            if payload_len < 4:
                break  # malformed, stop

    except Exception as e:
        logger.debug(f"Proposal parsing partial: {e}")

    return result

def _parse_sa_payload(data: bytes, result: dict):
    """Parse transforms inside SA payload."""
    offset = 0
    while offset < len(data) - 8:
        # Transform: last(1) + reserved(1) + length(2) + type(1) + reserved(1) + id(2)
        transform_type = data[offset + 4] if offset + 4 < len(data) else 0
        transform_id = int.from_bytes(data[offset+6:offset+8], 'big') if offset + 7 < len(data) else 0
        transform_len = int.from_bytes(data[offset+2:offset+4], 'big') if offset + 3 < len(data) else 8

        if transform_type == 1:  # Encryption
            result["encryption_algorithm"] = ENCR_MAP.get(transform_id, f"unknown({transform_id})")
        elif transform_type == 2:  # PRF / Auth
            result["auth_algorithm"] = AUTH_MAP.get(transform_id, f"unknown({transform_id})")
        elif transform_type == 4:  # DH Group
            result["dh_group"] = transform_id
            result["pfs_enabled"] = transform_id > 0

        offset += max(transform_len, 8)


def parse_ike(packets: list) -> dict:
    """
    Main entry point called by worker_thread.
    Takes a list of scapy packets, returns parsed IKE metadata.
    """
    result = {
        "ike_version": "unknown",
        "encryption_algorithm": "unknown",
        "auth_algorithm": "unknown",       # integrity/PRF only — observable
        "authentication_method": "unobservable",  # PSK/cert inside IKE_AUTH — encrypted
        "dh_group": 0,
        "pfs_enabled": False,
        "sa_lifetime_seconds": 86400,
        "mode": "tunnel",
        "packet_count": len(packets),
        "note": "auth_method unobservable via passive capture — IKE_AUTH payload is encrypted"
    }

    for pkt in packets:
        ptype = classify_vpn_packet(pkt)
        if ptype not in ("ike", "ike_natt"):
            continue

        try:
            raw = bytes(pkt[UDP].payload)
            if ptype == "ike_natt":
                raw = raw[4:] # Strip non-ESP marker
            if len(raw) < 28:
                continue

            version = _detect_ike_version(raw)
            if version != "unknown":
                result["ike_version"] = version

            proposals = _extract_proposals(raw)
            # Only overwrite if we got real data
            for key, val in proposals.items():
                if val not in ("unknown", 0, False, 86400):
                    result[key] = val

        except Exception as e:
            logger.debug(f"Packet parse error: {e}")
            continue

    return result
