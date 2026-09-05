#!/usr/bin/env python3

from pathlib import Path
import struct

from scapy.all import IP, UDP, Raw, ESP, wrpcap


OUTPUT = Path(__file__).resolve().parents[1] / "captures" / "capture_crypto_vpn.pcap"


def ike_header(
    initiator_spi,
    responder_spi,
    next_payload,
    exchange_type,
    message_id=0,
    flags=0x08,
    payload_length=0,
):
    total_length = 28 + payload_length

    return (
        initiator_spi
        + responder_spi
        + bytes([next_payload])
        + b"\x20"                         # IKEv2
        + bytes([exchange_type])
        + bytes([flags])
        + struct.pack("!I", message_id)
        + struct.pack("!I", total_length)
    )


def transform(transform_type, transform_id, key_length=None):
    attributes = b""

    if key_length is not None:
        # Attribute Type 14 = Key Length.
        # High bit set means TV attribute.
        attributes += struct.pack(
            "!HH",
            0x8000 | 14,
            key_length,
        )

    length = 8 + len(attributes)

    return (
        b"\x00"
        + bytes([transform_type])
        + struct.pack("!H", length)
        + struct.pack("!H", transform_id)
        + b"\x00\x00"
        + attributes
    )


def proposal(
    proposal_number,
    protocol_id,
    transforms,
    spi=b"",
    last=True,
):
    transform_data = b"".join(transforms)

    proposal_length = 8 + len(spi) + len(transform_data)

    return (
        bytes([0 if last else 2])
        + b"\x00"
        + struct.pack("!H", proposal_length)
        + bytes([proposal_number])
        + bytes([protocol_id])
        + bytes([len(spi)])
        + bytes([len(transforms)])
        + spi
        + transform_data
    )


def sa_payload(proposals, next_payload=0):
    body = b"".join(proposals)
    return (
        bytes([next_payload])
        + b"\x00"
        + struct.pack("!H", 4 + len(body))
        + body
    )


def auth_payload(auth_method, next_payload=0):
    # IKEv2 AUTH payload:
    # Auth Method is the first byte of the payload body.
    body = (
        bytes([auth_method])
        + b"\x00\x00\x00"
        + b"\x00" * 32
    )

    return (
        bytes([next_payload])
        + b"\x00"
        + struct.pack("!H", 4 + len(body))
        + body
    )


def make_packet(
    src,
    dst,
    sport,
    dport,
    ike_payload,
    next_payload,
    exchange_type,
    message_id,
    spi_i,
    spi_r,
):
    header = ike_header(
        spi_i,
        spi_r,
        next_payload,
        exchange_type,
        message_id=message_id,
        payload_length=len(ike_payload),
    )

    return (
        IP(src=src, dst=dst)
        / UDP(sport=sport, dport=dport)
        / Raw(load=header + ike_payload)
    )


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    spi_i = bytes.fromhex("1111111111111111")
    spi_r = bytes.fromhex("2222222222222222")

    packets = []

    # ---------------------------------------------------------
    # IKE_SA_INIT
    #
    # AES-256-CBC
    # PRF-HMAC-SHA2-256
    # HMAC-SHA2-256-128
    # DH Group 14
    # ---------------------------------------------------------

    ike_sa_transforms = [
        transform(
            1,      # ENCR
            12,     # AES-CBC
            256,
        ),
        transform(
            2,      # PRF
            5,      # HMAC-SHA2-256
        ),
        transform(
            3,      # INTEG
            12,     # HMAC-SHA2-256-128
        ),
        transform(
            4,      # DH
            14,     # MODP 2048
        ),
    ]

    ike_proposal = proposal(
        1,
        1,          # IKE protocol
        ike_sa_transforms,
    )

    ike_sa = sa_payload(
        [ike_proposal],
        next_payload=0,
    )

    packets.append(
        make_packet(
            "10.10.10.10",
            "10.10.10.20",
            500,
            500,
            ike_sa,
            PAYLOAD_SA := 33,
            34,      # IKE_SA_INIT
            0,
            spi_i,
            spi_r,
        )
    )

    # ---------------------------------------------------------
    # IKE_AUTH
    #
    # Authentication method = Shared Key / PSK
    # ---------------------------------------------------------

    auth = auth_payload(
        2,          # Shared Key / PSK
        next_payload=0,
    )

    packets.append(
        make_packet(
            "10.10.10.10",
            "10.10.10.20",
            500,
            500,
            auth,
            39,       # AUTH payload
            35,       # IKE_AUTH
            1,
            spi_i,
            spi_r,
        )
    )

    # ---------------------------------------------------------
    # CREATE_CHILD_SA
    #
    # ESP
    # AES-256-GCM
    # DH Group 14
    #
    # DH transform in ESP proposal = evidence of PFS.
    # ---------------------------------------------------------

    child_transforms = [
        transform(
            1,      # ENCR
            20,     # AES-GCM
            256,
        ),
        transform(
            4,      # DH
            14,     # MODP 2048
        ),
    ]

    child_proposal = proposal(
        1,
        3,          # ESP protocol
        child_transforms,
    )

    child_sa = sa_payload(
        [child_proposal],
        next_payload=0,
    )

    packets.append(
        make_packet(
            "10.10.10.10",
            "10.10.10.20",
            500,
            500,
            child_sa,
            33,       # SA payload
            36,       # CREATE_CHILD_SA
            2,
            spi_i,
            spi_r,
        )
    )

    # ---------------------------------------------------------
    # ESP DATA
    #
    # The inner IPv4 packet is intentionally visible in this
    # synthetic development capture so the existing mode
    # analyzer can identify Tunnel mode.
    # ---------------------------------------------------------

    for sequence in range(1, 5):
        inner = (
            IP(
                src="192.168.10.10",
                dst="192.168.20.20",
            )
            / UDP(
                sport=40000 + sequence,
                dport=443,
            )
            / Raw(
                load=b"synthetic encrypted VPN payload"
            )
        )

        esp_packet = (
            IP(
                src="10.10.10.10",
                dst="10.10.10.20",
            )
            / ESP(
                spi=0x2001,
                seq=sequence,
            )
            / Raw(
                load=bytes(inner)
            )
        )

        packets.append(esp_packet)

    for sequence in range(5, 9):
        inner = (
            IP(
                src="192.168.20.20",
                dst="192.168.10.10",
            )
            / UDP(
                sport=443,
                dport=40000 + sequence,
            )
            / Raw(
                load=b"synthetic encrypted VPN response"
            )
        )

        esp_packet = (
            IP(
                src="10.10.10.20",
                dst="10.10.10.10",
            )
            / ESP(
                spi=0x2002,
                seq=sequence,
            )
            / Raw(
                load=bytes(inner)
            )
        )

        packets.append(esp_packet)

    # Add reverse-direction packets so the capture resembles
    # a two-way negotiation.
    packets.append(
        make_packet(
            "10.10.10.20",
            "10.10.10.10",
            500,
            500,
            ike_sa,
            33,
            34,
            0,
            spi_i,
            spi_r,
        )
    )

    packets.append(
        make_packet(
            "10.10.10.20",
            "10.10.10.10",
            500,
            500,
            auth,
            39,
            35,
            1,
            spi_i,
            spi_r,
        )
    )

    packets.append(
        make_packet(
            "10.10.10.20",
            "10.10.10.10",
            500,
            500,
            child_sa,
            33,
            36,
            2,
            spi_i,
            spi_r,
        )
    )

    wrpcap(str(OUTPUT), packets)

    print("Crypto test capture created.")
    print(f"Output : {OUTPUT}")
    print(f"Packets: {len(packets)}")


if __name__ == "__main__":
    main()
