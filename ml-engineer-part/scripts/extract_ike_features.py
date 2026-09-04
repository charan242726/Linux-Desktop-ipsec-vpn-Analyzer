#!/usr/bin/env python3
"""
Parses the IKEv2 handshake out of a pcap using pyshark (a wrapper around
tshark). Extracts version, exchange type, and negotiated Phase 1
transforms (encryption, integrity, PRF, DH group) directly from cleartext
fields — no ML here, this is deterministic protocol parsing.

Requires: pip install pyshark  (and tshark installed on the system)

VERIFY BEFORE TRUSTING: pyshark's field names can vary slightly between
tshark versions. Run this against one known-good capture first and print
packet.isakmp.field_names (or `tshark -V -r file.pcap`) to confirm the
exact field names on your system before relying on this for the full
dataset — don't assume the field names below are exactly right without
checking against your own capture.
"""

import sys
import pyshark
import asyncio

def extract_ike_info(pcap_path):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    cap = pyshark.FileCapture(pcap_path, display_filter="isakmp")

    results = []
    for pkt in cap:
        try:
            isakmp = pkt.isakmp
            info = {
                "frame_number": pkt.number,
                "version": getattr(isakmp, "version", None),
                "exchange_type": getattr(isakmp, "exchangetype", None),
                "flags_initiator": getattr(isakmp, "flags_initiator", None),
            }

            # Transform payloads live nested under the SA payload; pyshark
            # exposes these as repeated fields, not a clean list — you may
            # need to inspect pkt.isakmp.field_names on your tshark version
            # to get the exact attribute names for:
            #   - transform type (ENCR / PRF / INTEG / DH)
            #   - transform ID (e.g. ENCR_AES_GCM_16)
            #   - DH group number
            # Placeholder below shows the general approach; fill in the
            # real field names once verified against a live capture.
            if hasattr(isakmp, "notify_msgtype"):
                info["notify_msgtype"] = isakmp.notify_msgtype

            results.append(info)
        except AttributeError:
            continue

    cap.close()
    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: extract_ike_features.py <pcap_path>")
        sys.exit(1)

    for row in extract_ike_info(sys.argv[1]):
        print(row)
