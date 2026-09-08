#!/bin/bash
# Chat: simulated typing with iperf3 sending low-bandwidth paced TCP packets over 15 seconds
docker exec vpn1 iperf3 -c 10.10.0.20 -t 15 --pacing-timer 1000 -b 10K
