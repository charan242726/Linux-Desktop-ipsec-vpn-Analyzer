#!/bin/bash
# Video: 5Mbps UDP stream for 10s
docker exec vpn1 iperf3 -c 10.10.0.20 -u -b 5M -t 10
