#!/usr/bin/env python3

import json
import struct
import sys
from pathlib import Path

from scapy.all import IP, IPv6, UDP, rdpcap


# IKEv2 payload types
PAYLOAD_SA = 33
PAYLOAD_AUTH = 39

# IKEv2 transform types
TRANSFORM_ENCR = 1
TRANSFORM_PRF = 2
TRANSFORM_INTEG = 3
TRANSFORM_DH = 4

# Encryption algorithms
ENCR_ALGORITHMS = {
    12: "AES-CBC",
    20: "AES-GCM",
}

# PRF algorithms
PRF_ALGORITHMS = {
    2: "PRF-HMAC-SHA1",
    4: "PRF-AES128-XCBC",
    5: "PRF-HMAC-SHA2-256",
    6: "PRF-HMAC-SHA2-384",
    7: "PRF-HMAC-SHA2-512",
}

# Integrity algorithms
INTEGRITY_ALGORITHMS = {
    2: "HMAC-SHA1-96",
    5: "AES-XCBC-96",
    12: "HMAC-SHA2-256-128",
    13: "HMAC-SHA2-384-192",
    14: "HMAC-SHA2-512-256",
}

# Diffie-Hellman groups
DH_GROUPS = {
    14: "DH Group 14 (MODP 2048)",
    15: "DH Group 15 (MODP 3072)",
    16: "DH Group 16 (MODP 4096)",
    17: "DH Group 17 (MODP 6144)",
    18: "DH Group 18 (MODP 8192)",
    19: "DH Group 19 (ECP 256)",
    20: "DH Group 20 (ECP 384)",
    21: "DH Group 21 (ECP 521)",
    31: "DH Group 31 (Curve25519)",
}

# IKEv2 AUTH methods
AUTH_METHODS = {
    1: "RSA Digital Signature",
    2: "Shared Key / PSK",
    3: "DSS Digital Signature",
    9: "ECDSA SHA-256",
    10: "ECDSA SHA-384",
    11: "ECDSA SHA-512",
}


def read_u16(data, offset):
    if offset + 2 > len(data):
        return None
    return struct.unpack("!H", data[offset:offset + 2])[0]


def read_u32(data, offset):
    if offset + 4 > len(data):
        return None
    return struct.unpack("!I", data[offset:offset + 4])[0]


def get_udp_payload(packet):
    """
    Return raw UDP payload bytes.

    This deliberately uses UDP.payload instead of requiring Scapy's
    Raw layer because Scapy may represent payloads differently depending
    on packet construction/dissection.
    """
    if not packet.haslayer(UDP):
        return b""

    try:
        return bytes(packet[UDP].payload)
    except Exception:
        return b""


def is_ike_packet(packet):
    if not packet.haslayer(UDP):
        return False

    udp = packet[UDP]

    return (
        (udp.sport in (500, 4500))
        or (udp.dport in (500, 4500))
    )


def detect_ike_version(payload):
    """
    IKE header:

    0-7   Initiator SPI
    8-15  Responder SPI
    16    Next Payload
    17    Version
    18    Exchange Type
    19    Flags
    20-23 Message ID
    24-27 Length
    """

    if len(payload) < 28:
        return None

    version = payload[17]

    major = version >> 4
    minor = version & 0x0F

    if major == 2:
        return "IKEv2"

    if major == 1:
        return "IKEv1"

    return "Unknown"


def parse_transform_attributes(data):
    """
    Parse IKEv2 transform attributes.

    Key Length uses attribute type 14.
    """

    attributes = []
    offset = 0

    while offset + 4 <= len(data):
        attr_type_raw = read_u16(data, offset)
        attr_value_raw = read_u16(data, offset + 2)

        if attr_type_raw is None or attr_value_raw is None:
            break

        # High bit = TV format.
        is_tv = bool(attr_type_raw & 0x8000)
        attr_type = attr_type_raw & 0x7FFF

        if is_tv:
            attributes.append({
                "type": attr_type,
                "format": "TV",
                "value": attr_value_raw,
            })
            offset += 4
        else:
            attr_length = attr_value_raw

            if offset + 4 + attr_length > len(data):
                break

            value = data[offset + 4:offset + 4 + attr_length]

            attributes.append({
                "type": attr_type,
                "format": "TLV",
                "value": value.hex(),
                "length": attr_length,
            })

            offset += 4 + attr_length

    return attributes


def get_key_length(attributes):
    """
    IKEv2 attribute type 14 = Key Length.

    Return the key length in bits when present.
    """

    for attribute in attributes:
        if attribute.get("type") != 14:
            continue

        if attribute.get("format") == "TV":
            return attribute.get("value")

        value = attribute.get("value")

        if isinstance(value, str):
            try:
                raw = bytes.fromhex(value)
                if len(raw) == 2:
                    return struct.unpack("!H", raw)[0]
            except ValueError:
                pass

    return None


def parse_transform(data, offset):
    """
    Parse one IKEv2 Transform substructure.

    Transform header:

    0       Reserved
    1       Transform Type
    2-3     Transform Length
    4-5     Transform ID
    6-7     Reserved
    """

    if offset + 8 > len(data):
        return None, offset

    transform_type = data[offset + 1]
    transform_length = read_u16(data, offset + 2)
    transform_id = read_u16(data, offset + 4)

    if transform_length is None or transform_length < 8:
        return None, offset

    end = offset + transform_length

    if end > len(data):
        return None, offset

    attributes = parse_transform_attributes(
        data[offset + 8:end]
    )

    key_length = get_key_length(attributes)

    transform = {
        "type": transform_type,
        "id": transform_id,
        "length": transform_length,
        "attributes": attributes,
    }

    if key_length is not None:
        transform["key_length_bits"] = key_length

    return transform, end


def transform_name(transform):
    transform_type = transform["type"]
    transform_id = transform["id"]

    if transform_type == TRANSFORM_ENCR:
        name = ENCR_ALGORITHMS.get(
            transform_id,
            f"Encryption ID {transform_id}"
        )

        key_length = transform.get("key_length_bits")

        if key_length:
            return f"{name}-{key_length}" if name != "AES-CBC" else f"AES-CBC-{key_length}"

        return name

    if transform_type == TRANSFORM_PRF:
        return PRF_ALGORITHMS.get(
            transform_id,
            f"PRF ID {transform_id}"
        )

    if transform_type == TRANSFORM_INTEG:
        return INTEGRITY_ALGORITHMS.get(
            transform_id,
            f"Integrity ID {transform_id}"
        )

    if transform_type == TRANSFORM_DH:
        return DH_GROUPS.get(
            transform_id,
            f"DH Group {transform_id}"
        )

    return f"Transform Type {transform_type} ID {transform_id}"


def parse_proposal(data, offset):
    """
    Parse an IKEv2 Proposal substructure.

    Proposal header:

    0       Last/More
    1       Reserved
    2-3     Proposal Length
    4       Proposal Number
    5       Protocol ID
    6       SPI Size
    7       Number of Transforms
    8...    SPI
    """

    if offset + 8 > len(data):
        return None, offset

    more = data[offset]
    proposal_length = read_u16(data, offset + 2)
    proposal_number = data[offset + 4]
    protocol_id = data[offset + 5]
    spi_size = data[offset + 6]
    transform_count = data[offset + 7]

    if proposal_length is None or proposal_length < 8:
        return None, offset

    end = offset + proposal_length

    if end > len(data):
        return None, offset

    transform_offset = offset + 8 + spi_size

    if transform_offset > end:
        return None, offset

    transforms = []

    for _ in range(transform_count):
        if transform_offset >= end:
            break

        transform, next_offset = parse_transform(
            data,
            transform_offset
        )

        if transform is None or next_offset <= transform_offset:
            break

        transforms.append(transform)
        transform_offset = next_offset

    proposal = {
        "proposal_number": proposal_number,
        "protocol_id": protocol_id,
        "spi_size": spi_size,
        "transform_count": len(transforms),
        "transforms": transforms,
        "more": more,
    }

    return proposal, end


def parse_sa_payload(body):
    """
    Parse IKEv2 Security Association payload.

    Unlike IKEv1 ISAKMP SA payloads, IKEv2 proposals begin
    immediately after the generic 4-byte payload header.
    """

    proposals = []
    offset = 0

    while offset + 8 <= len(body):
        proposal, next_offset = parse_proposal(
            body,
            offset
        )

        if proposal is None or next_offset <= offset:
            break

        proposals.append(proposal)
        offset = next_offset

        # Last proposal has the Last flag.
        if proposal["more"] == 0:
            break

    return proposals


def parse_ikev2_payloads(payload):
    """
    Walk the IKEv2 payload chain.

    Returns all discovered SA proposals and AUTH methods.
    """

    if len(payload) < 28:
        return {
            "sa_payloads": [],
            "auth_methods": [],
            "payload_types": [],
        }

    next_payload = payload[16]
    total_length = read_u32(payload, 24)

    if total_length is None:
        return {
            "sa_payloads": [],
            "auth_methods": [],
            "payload_types": [],
        }

    # Do not trust malformed lengths beyond the actual packet.
    end_of_message = min(total_length, len(payload))

    offset = 28

    sa_payloads = []
    auth_methods = []
    payload_types = []

    while (
        next_payload != 0
        and offset + 4 <= end_of_message
    ):
        current_payload = next_payload

        generic_next = payload[offset]
        critical = payload[offset + 1]
        payload_length = read_u16(payload, offset + 2)

        if payload_length is None or payload_length < 4:
            break

        payload_end = offset + payload_length

        if payload_end > end_of_message:
            break

        body = payload[offset + 4:payload_end]

        payload_types.append(current_payload)

        if current_payload == PAYLOAD_SA:
            proposals = parse_sa_payload(body)

            if proposals:
                sa_payloads.append({
                    "proposals": proposals
                })

        elif current_payload == PAYLOAD_AUTH:
            # AUTH payload:
            # Auth Method is first byte of payload body.
            if len(body) >= 1:
                auth_method_id = body[0]

                auth_methods.append({
                    "id": auth_method_id,
                    "name": AUTH_METHODS.get(
                        auth_method_id,
                        f"AUTH Method {auth_method_id}"
                    ),
                })

        offset = payload_end
        next_payload = generic_next

    return {
        "sa_payloads": sa_payloads,
        "auth_methods": auth_methods,
        "payload_types": payload_types,
    }


def analyze_pcap(capture_file):
    packets = rdpcap(str(capture_file))

    ike_packets = 0
    ikev1_packets = 0
    ikev2_packets = 0
    unknown_packets = 0

    encryption = []
    integrity = []
    prf = []
    dh = []
    auth_methods = []

    all_proposals = []
    payload_types = []

    for packet in packets:
        if not is_ike_packet(packet):
            continue

        payload = get_udp_payload(packet)

        version = detect_ike_version(payload)

        if version is None:
            continue

        ike_packets += 1

        if version == "IKEv1":
            ikev1_packets += 1
            continue

        if version != "IKEv2":
            unknown_packets += 1
            continue

        ikev2_packets += 1

        parsed = parse_ikev2_payloads(payload)

        payload_types.extend(parsed["payload_types"])
        auth_methods.extend(parsed["auth_methods"])

        for sa in parsed["sa_payloads"]:
            all_proposals.extend(sa["proposals"])

            for proposal in sa["proposals"]:
                for transform in proposal["transforms"]:
                    name = transform_name(transform)
                    transform_type = transform["type"]

                    if transform_type == TRANSFORM_ENCR:
                        encryption.append({
                            "value": name,
                            "id": transform["id"],
                            "key_length_bits": transform.get(
                                "key_length_bits"
                            ),
                        })

                    elif transform_type == TRANSFORM_INTEG:
                        integrity.append({
                            "value": name,
                            "id": transform["id"],
                        })

                    elif transform_type == TRANSFORM_PRF:
                        prf.append({
                            "value": name,
                            "id": transform["id"],
                        })

                    elif transform_type == TRANSFORM_DH:
                        dh.append({
                            "value": name,
                            "id": transform["id"],
                        })

    def unique_values(items):
        seen = []
        for item in items:
            value = item.get("value", item.get("name"))
            if value is not None and value not in seen:
                seen.append(value)
        return seen

    encryption_values = unique_values(encryption)
    integrity_values = unique_values(integrity)
    prf_values = unique_values(prf)
    dh_values = unique_values(dh)
    auth_method_values = unique_values(auth_methods)

    def parameter(
        value_list,
        unknown_source,
        known_source,
    ):
        if not value_list:
            return {
                "value": "Unknown",
                "status": "INSUFFICIENT_EVIDENCE",
                "source": unknown_source,
                "confidence": 0.0,
                "transforms": [],
            }

        if len(value_list) == 1:
            value = value_list[0]
        else:
            value = " / ".join(value_list)

        return {
            "value": value,
            "status": "OBSERVED",
            "source": known_source,
            "confidence": 0.95,
            "transforms": value_list,
        }

    encryption_parameter = parameter(
        encryption_values,
        "No IKEv2 SA proposal/transform evidence",
        "Observed in IKEv2 SA proposal transform(s)",
    )

    integrity_parameter = parameter(
        integrity_values,
        "No IKEv2 integrity transform evidence",
        "Observed in IKEv2 SA proposal transform(s)",
    )

    prf_parameter = parameter(
        prf_values,
        "No IKEv2 PRF transform evidence",
        "Observed in IKEv2 SA proposal transform(s)",
    )

    dh_parameter = parameter(
        dh_values,
        "No IKEv2 DH transform evidence",
        "Observed in IKEv2 SA proposal transform(s)",
    )

    auth_parameter = parameter(
        auth_method_values,
        "No IKEv2 AUTH payload evidence",
        "Observed in IKEv2 AUTH payload",
    )

    # Determine PFS from ESP/CHILD_SA proposals.
    #
    # Protocol ID 3 = ESP.
    # A DH transform in an ESP proposal is evidence of PFS.
    esp_proposals = [
        proposal
        for proposal in all_proposals
        if proposal.get("protocol_id") == 3
    ]

    esp_dh = []

    for proposal in esp_proposals:
        for transform in proposal.get("transforms", []):
            if transform.get("type") == TRANSFORM_DH:
                esp_dh.append(
                    DH_GROUPS.get(
                        transform.get("id"),
                        f"DH Group {transform.get('id')}"
                    )
                )

    esp_dh = list(dict.fromkeys(esp_dh))

    if esp_dh:
        pfs = {
            "value": "Enabled",
            "status": "OBSERVED",
            "source": "DH transform observed in ESP proposal",
            "confidence": 0.95,
            "dh_groups": esp_dh,
        }
    elif esp_proposals:
        pfs = {
            "value": "Not observed",
            "status": "OBSERVED",
            "source": "ESP proposal observed without a DH transform",
            "confidence": 0.85,
            "dh_groups": [],
        }
    else:
        pfs = {
            "value": "Unknown",
            "status": "INSUFFICIENT_EVIDENCE",
            "source": "No ESP CHILD_SA proposal evidence",
            "confidence": 0.0,
            "dh_groups": [],
        }

    if ike_packets == 0:
        ike_detected = False
        ike_version = "Unknown"
        confidence = 0.0
    elif ikev2_packets > 0 and ikev1_packets == 0:
        ike_detected = True
        ike_version = "IKEv2"
        confidence = 1.0
    elif ikev1_packets > 0 and ikev2_packets == 0:
        ike_detected = True
        ike_version = "IKEv1"
        confidence = 1.0
    else:
        ike_detected = True
        ike_version = "Mixed"
        confidence = 0.9

    result = {
        "ike_detected": ike_detected,
        "ike_version": ike_version,
        "confidence": confidence,
        "statistics": {
            "ike_packets": ike_packets,
            "ikev1_packets": ikev1_packets,
            "ikev2_packets": ikev2_packets,
            "unknown_packets": unknown_packets,
        },
        "cryptographic_parameters": {
            "encryption_algorithm": encryption_parameter,
            "authentication_algorithm": integrity_parameter,
            "integrity_algorithm": integrity_parameter,
            "authentication_method": auth_parameter,
            "key_exchange_method": dh_parameter,
            "prf": prf_parameter,
            "pfs": pfs,
        },
        "sa_characteristics": {
            "proposal_count": len(all_proposals),
            "esp_proposal_count": len(esp_proposals),
            "payload_types": sorted(set(payload_types)),
        },
        "observed_proposals": all_proposals,
    }

    return result


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python ai/src/ike_analyzer.py "
            "<input.pcap> <output.json>"
        )
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Input capture not found: {input_file}")
        sys.exit(1)

    try:
        result = analyze_pcap(input_file)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.write_text(
            json.dumps(
                result,
                indent=2
            )
        )

        print("IKE analysis complete.")
        print(f"Input : {input_file}")
        print(f"Output: {output_file}")

    except Exception as exc:
        print(f"IKE analysis failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
