from scapy.all import Ether, IP, UDP, ESP, TCP, Raw, wrpcap


packets = []

# ============================================================
# IKEv2 TEST TRAFFIC
# ============================================================

for i in range(10):

    initiator_spi = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    responder_spi = b"\x00" * 8

    # IKEv2 header
    # Next Payload = 0
    # Version = 0x20
    # Exchange Type = 34 (IKE_SA_INIT)
    # Flags = 0x08
    # Message ID = 0
    # Length = 28 bytes

    ike_header = (
        initiator_spi
        + responder_spi
        + b"\x00"
        + b"\x20"
        + b"\x22"
        + b"\x08"
        + b"\x00\x00\x00\x00"
        + b"\x00\x00\x00\x1c"
    )

    packet = (
        Ether()
        / IP(src="10.0.0.1", dst="10.0.0.2")
        / UDP(sport=500, dport=500)
        / Raw(load=ike_header)
    )

    packets.append(packet)


# ============================================================
# ESP TUNNEL TRAFFIC
# ============================================================

for i in range(20):

    # Inner IP packet
    inner_packet = (
        IP(
            src="192.168.100.10",
            dst="192.168.100.20"
        )
        / TCP(
            sport=5000 + i,
            dport=443
        )
        / Raw(load=b"web-test-data")
    )

    # Outer IP -> ESP -> Inner IP
    packet = (
        Ether()
        / IP(
            src="10.0.0.1",
            dst="10.0.0.2"
        )
        / ESP(
            spi=0x2001,
            seq=i + 1
        )
        / inner_packet
    )

    packets.append(packet)


output = "testbed/captures/capture_combined_vpn.pcap"

wrpcap(output, packets)

print(f"Created combined VPN test PCAP: {output}")
print(f"Packets: {len(packets)}")
print("IKEv2 packets: 10")
print("ESP packets: 20")
