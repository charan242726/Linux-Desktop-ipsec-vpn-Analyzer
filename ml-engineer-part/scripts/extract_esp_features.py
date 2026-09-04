#!/usr/bin/env python3
"""
Groups ESP packets by SPI (= one flow per tunnel/traffic-type run) and
computes the size/timing/direction statistics the ML classifier trains
on. ESP payload itself is encrypted — everything here comes from what
survives encryption unchanged: packet sizes, timestamps, and direction.

Requires: pip install scapy

Run per-pcap, then concatenate the resulting rows (one per flow) across
your whole dataset into a single CSV/DataFrame for training. The
conn_name/traffic_type labels come from the pcap filename (which
run_experiment.py names as <conn_name>_<traffic_type>.pcap) and the
manifest.json ground truth — join on conn_name to pull in cipher/mode/etc.
if you want those as features too.
"""

import sys
import statistics
from collections import defaultdict
from pathlib import Path
from scapy.all import rdpcap, IP, ESP


def extract_flow_features(pcap_path):
    packets = rdpcap(pcap_path)

    # spi -> list of (timestamp, size, direction)
    flows = defaultdict(list)

    for pkt in packets:
        if IP in pkt and ESP in pkt:
            spi = pkt[ESP].spi
            size = len(pkt)
            ts = float(pkt.time)
            direction = "fwd" if pkt[IP].src < pkt[IP].dst else "bwd"  # arbitrary but consistent
            flows[spi].append((ts, size, direction))

    rows = []
    for spi, pkts in flows.items():
        pkts.sort(key=lambda p: p[0])
        sizes = [p[1] for p in pkts]
        timestamps = [p[0] for p in pkts]
        iats = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])]

        fwd_bytes = sum(p[1] for p in pkts if p[2] == "fwd")
        bwd_bytes = sum(p[1] for p in pkts if p[2] == "bwd")

        row = {
            "spi": hex(spi),
            "packet_count": len(pkts),
            "duration_sec": timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0.0,
            "size_mean": statistics.mean(sizes),
            "size_std": statistics.pstdev(sizes) if len(sizes) > 1 else 0.0,
            "size_min": min(sizes),
            "size_max": max(sizes),
            "iat_mean": statistics.mean(iats) if iats else 0.0,
            "iat_std": statistics.pstdev(iats) if len(iats) > 1 else 0.0,
            "fwd_bwd_byte_ratio": (fwd_bytes / bwd_bytes) if bwd_bytes else float("inf"),
            "source_pcap": Path(pcap_path).name,
        }
        rows.append(row)

    return rows


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: extract_esp_features.py <pcap_path>")
        sys.exit(1)

    for row in extract_flow_features(sys.argv[1]):
        print(row)
