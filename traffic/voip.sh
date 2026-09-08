#!/bin/bash
# VoIP: 100Kbps UDP bidirectional for 10s
docker exec vpn1 iperf3 -c 10.10.0.20 -u -b 100K -t 10 --bidir
