from scapy.all import rdpcap, UDP
from backend.services.ike_parser import classify_vpn_packet, _detect_ike_version, _parse_sa_payload
import logging

logging.basicConfig(level=logging.DEBUG)

packets = rdpcap("/home/charan/ipsec-testbed/dataset/siteB_hardened_ping.pcap")
for pkt in packets:
    ptype = classify_vpn_packet(pkt)
    if ptype in ("ike", "ike_natt"):
        raw = bytes(pkt[UDP].payload)
        if ptype == "ike_natt": raw = raw[4:]
        if len(raw) < 28: continue
        print(f"IKE Packet: {ptype}, Version: {_detect_ike_version(raw)}")
        offset = 28
        next_payload = raw[16]
        while offset < len(raw) - 4 and next_payload != 0:
            payload_type = next_payload
            next_payload = raw[offset]
            payload_len = int.from_bytes(raw[offset+2:offset+4], 'big')
            if payload_type == 33:
                print(f"SA Payload found, len {payload_len}")
                res = {"dh_group": 0, "pfs_enabled": "NOT_DETERMINED"}
                sa_data = raw[offset+4:offset+payload_len]
                print(f"SA Data hex: {sa_data.hex()}")
                _parse_sa_payload(sa_data, res)
                print(f"Parsed Result: {res}")
            offset += payload_len
            if payload_len < 4: break
