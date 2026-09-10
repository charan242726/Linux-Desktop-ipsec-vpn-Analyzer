from scapy.all import rdpcap, UDP
from backend.services.ike_parser import classify_vpn_packet, _detect_ike_version
packets = rdpcap("/home/charan/ipsec-testbed/dataset/siteB_hardened_ping.pcap")
for pkt in packets:
    ptype = classify_vpn_packet(pkt)
    if ptype in ("ike", "ike_natt"):
        raw = bytes(pkt[UDP].payload)
        if ptype == "ike_natt": raw = raw[4:]
        if len(raw) < 28: continue
        print(f"--- IKE Version: {_detect_ike_version(raw)}")
        offset = 28
        next_payload = raw[16]
        print(f"First Next Payload: {next_payload}")
        while offset < len(raw) - 4 and next_payload != 0:
            payload_type = next_payload
            next_payload = raw[offset]
            payload_len = int.from_bytes(raw[offset+2:offset+4], 'big')
            print(f"  Found Payload Type: {payload_type}, Length: {payload_len}")
            offset += payload_len
            if payload_len < 4: break
