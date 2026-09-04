# Task 2 Validation: Base × ICMP × 2

This document validates the two independently captured IPsec sessions generated on the testbed.

## 1. Environment
- **Docker Containers**: `vpn1` (10.10.0.10) and `vpn2` (10.10.0.20)
- **strongSwan Version**: 5.9.13 (Linux U5.9.13/K7.2.2-arch1-1)
- **tshark Version**: 4.2.2
- **Capture Interface**: `br-0b6dd8ac7a51` (Host bridge corresponding to the Docker `ipsec-net` network)

## 2. Experiment
- **Configuration**: The `base` IKEv2 connection using PSK and `aes256-sha256-modp2048`.
- **Traffic Generator**: `ping -c 20 10.10.0.20` running on `vpn1` targeting `vpn2`.
- **Repetitions**: 2 independent runs (`r1` and `r2`).

## 3. Artifacts
- **PCAPs**: 
  - `testbed/captures/base_icmp_r1.pcapng`
  - `testbed/captures/base_icmp_r2.pcapng`
- **XFRM State & Policy Metadata**:
  - `testbed/metadata/base_icmp_r1.xfrm.txt`
  - `testbed/metadata/base_icmp_r1.xfrm-policy.txt`
  - `testbed/metadata/base_icmp_r2.xfrm.txt`
  - `testbed/metadata/base_icmp_r2.xfrm-policy.txt`
- **Manifest**: `testbed/manifest.csv`

## 4. Validation
- **IKEv2 Observed**: Yes, both captures contain exactly the 4 required IKEv2 handshake packets (`IKE_SA_INIT` and `IKE_AUTH`), plus the tear-down `INFORMATIONAL` packets.
- **ESP Observed**: Yes, both captures contain 40 ESP packets (20 encrypted ICMP requests and 20 encrypted ICMP replies).
- **Expected Traffic Observed**: 
  - *Before Encryption*: Inside the containers, the traffic is plain ICMP (verifiable by the ping output returning 0% packet loss).
  - *After Encryption*: On the bridge interface, the payload is completely opaque. We only observe `ESP` protocol packets with lengths corresponding to the ping padding. ICMP is **not** observable in the PCAP, which confirms successful encryption.
- **XFRM State Observed**: Yes, the extracted state files show the negotiated AES and SHA keys for the two unidirectional ESP tunnels.
- **XFRM Policy Observed**: Yes, the policy intercepting `10.10.0.10/32` to `10.10.0.20/32` was successfully recorded.
- **PCAP Readability**: Both PCAPs load successfully in `tshark` without corruption.
- **Manifest Integrity**: The manifest accurately lists 2 valid rows pointing to existing files.

## 5. Repetition Comparison

| Metric                    | base_icmp_r1 | base_icmp_r2 |
|---------------------------|--------------|--------------|
| **PCAP size**             | 11K          | 12K          |
| **Total Packet Count**    | 48           | 54           |
| **IKE Packet Count**      | 6            | 6            |
| **ESP Packet Count**      | 40           | 40           |
| **ICMP Packet Count**     | 0 (Encrypted)| 0 (Encrypted)|
| **VPN Established**       | Yes          | Yes          |
| **XFRM State Present**    | Yes          | Yes          |
| **XFRM Policy Present**   | Yes          | Yes          |

*Note: Total packet count variations are typical in bridge captures due to background network noise like ARP, but the cryptographic (IKE/ESP) counts match exactly.*

## 6. Extraction Feasibility
We verified that our version of `tshark` natively parses the modern `ike` protocol fields (not just legacy `isakmp`). We successfully extracted the following critical IKEv2 negotiation parameters required for the future ML parser pipeline:

- `ike.version`: (Value `0x20` for IKEv2)
- `ike.exchangetype`: (`34` for INIT, `35` for AUTH)
- `ike.ispi`: The Initiator SPI (e.g., `5dc000903277c08c`)
- `ike.rspi`: The Responder SPI

*Note: Deprecated fields like `isakmp.icookie` and `isakmp.rcookie` are unsupported in this `tshark` version. Our extraction scripts must rely on `ike.ispi` and `ike.rspi`.*
