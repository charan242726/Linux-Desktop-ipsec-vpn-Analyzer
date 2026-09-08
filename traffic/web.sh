#!/bin/bash
# Web: fetch a 10MB file from vpn2's HTTP server
docker exec vpn1 curl -s -o /dev/null http://10.10.0.20/10M.bin
