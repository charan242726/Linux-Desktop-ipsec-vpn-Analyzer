#!/bin/bash
# Bulk: sustained large file transfer (50MB)
docker exec vpn1 curl -s -o /dev/null http://10.10.0.20/50M.bin
