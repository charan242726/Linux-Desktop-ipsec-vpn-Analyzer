#!/bin/bash
set -e
mkdir -p testbed/metadata testbed/captures

echo "Starting r1..."
tshark -i br-0b6dd8ac7a51 -w testbed/captures/base_icmp_r1.pcapng >/dev/null 2>&1 &
TSHARK_PID=$!
sleep 2

docker exec vpn1 swanctl --initiate --child base
sleep 2
docker exec vpn1 ping -c 20 10.10.0.20
sleep 2

docker exec vpn1 ip xfrm state > testbed/metadata/base_icmp_r1.xfrm.txt
docker exec vpn1 ip xfrm policy > testbed/metadata/base_icmp_r1.xfrm-policy.txt

docker exec vpn1 swanctl --terminate --ike base
sleep 2
kill $TSHARK_PID || true
sleep 2

echo "Starting r2..."
tshark -i br-0b6dd8ac7a51 -w testbed/captures/base_icmp_r2.pcapng >/dev/null 2>&1 &
TSHARK_PID=$!
sleep 2

docker exec vpn1 swanctl --initiate --child base
sleep 2
docker exec vpn1 ping -c 20 10.10.0.20
sleep 2

docker exec vpn1 ip xfrm state > testbed/metadata/base_icmp_r2.xfrm.txt
docker exec vpn1 ip xfrm policy > testbed/metadata/base_icmp_r2.xfrm-policy.txt

docker exec vpn1 swanctl --terminate --ike base
sleep 2
kill $TSHARK_PID || true

echo "Done"
