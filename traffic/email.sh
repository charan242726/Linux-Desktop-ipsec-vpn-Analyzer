#!/bin/bash
# Email: bursty request/response pattern fetching 1MB payloads
docker exec vpn1 bash -c 'for i in {1..5}; do curl -s -o /dev/null http://10.10.0.20/1M.bin; sleep 1; done'
