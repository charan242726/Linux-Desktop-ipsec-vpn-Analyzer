# Deterministic IPsec Security Rule Engine

This document details the deterministic rule engine built to evaluate IPsec VPN security based solely on passive PCAP observations and XFRM metadata, ensuring strict separation from the ML-based traffic classification.

## 1. Core Architecture
The engine is driven by `rules/risk_engine.py` and `analyzer/session_analyzer.py`.
- **Evidence collection:** IKE configurations (algorithms, DH groups) are collected from `IKE_SA_INIT`, while actual ESP configurations (Replay Window, Transport mode) are extracted from Linux XFRM state logs.
- **Observation Status:** The engine explicitly tracks whether a field is `OBSERVED`, `INFERRED`, or `UNKNOWN`. It refuses to guess unobservable fields like the authentication method (PSK vs RSA/Certificates).
- **ML Separation:** The ML traffic prediction is attached at the very end of the `AnalysisResult` object, but it *does not* alter the deterministic VPN security score.

## 2. Implemented Rules & Evidence
| Rule ID | Severity | Condition | Evidence Source |
|---------|----------|-----------|-----------------|
| `IKE_VERSION_DEPRECATED` | HIGH | Version < 2.0 | `ike_version` (IKE PCAP) |
| `WEAK_ENCRYPTION_CRITICAL` | CRITICAL | DES, 3DES, or NULL ciphers | `encryption_algorithm` (IKE PCAP) |
| `WEAK_ENCRYPTION_KEYLEN` | HIGH | AES with key < 128 bit | `encryption_key_length` (IKE PCAP) |
| `MISSING_INTEGRITY` | CRITICAL | Missing integrity HMAC & Non-AEAD cipher | `integrity_algorithm` + `encryption_algorithm` (IKE PCAP) |
| `WEAK_INTEGRITY` | HIGH | MD5 or SHA-1 | `integrity_algorithm` (IKE PCAP) |
| `WEAK_DH_GROUP` | HIGH | DH Group 1 or 2 (768/1024-bit MODP) | `dh_group` (IKE PCAP) |
| `SUBOPTIMAL_DH_GROUP` | MEDIUM | DH Group 5 (1536-bit MODP) | `dh_group` (IKE PCAP) |
| `REPLAY_PROTECTION_DISABLED` | HIGH | Receiver replay-window size == 0 | `replay-window` (XFRM state) |
| `UNKNOWN_AUTHENTICATION` | INFO | Unobservable authentication payload | (Intentional Lack of Evidence) |
| `TRANSPORT_MODE` | INFO | Tunnel mode bypassed | `mode` (XFRM state) |

### Negative Rule Testing (Edge Cases Avoided)
- **AEAD Integrity (AES-GCM):** The engine specifically checks if the cipher is an AEAD (e.g., IANA 20 for GCM). If so, it disables the `MISSING_INTEGRITY` rule to prevent false positives.
- **Outbound Replay Window:** The engine only searches for the *maximum* replay window in the XFRM state. This prevents false positives because IPsec only enforces the replay window on the *inbound/receiver* SA (the outbound transmitter always shows a 0 window).

## 3. Risk Scoring Methodology
The scoring system is entirely deterministic and reproducible.
- **Base Score:** 100
- **Penalties:** 
  - CRITICAL (-40)
  - HIGH (-20)
  - MEDIUM (-10)
  - LOW (-5)
  - INFO (0)
- **Category Matrix:**
  - 100: `SECURE`
  - 90 - 99: `LOW RISK`
  - 70 - 89: `MEDIUM RISK`
  - 40 - 69: `HIGH RISK`
  - < 40: `CRITICAL RISK`

## 4. Regression Validation on Real Sessions
We executed the engine against the actual generated testbed sessions. Results correctly aligned with the expected configuration flaws:
- **`base` / `aes128gcm` / `aes256cbc`**: Scored `100` (`SECURE`). The only finding triggered was `UNKNOWN_AUTHENTICATION` (INFO) because passive capture cannot decrypt the `IKE_AUTH` payload.
- **`dhweak`**: Triggered `WEAK_DH_GROUP` (Group 2). Scored `80` (`MEDIUM RISK`).
- **`replayoff`**: Triggered `REPLAY_PROTECTION_DISABLED` (Replay window = 0). Scored `80` (`MEDIUM RISK`).

## 5. Unobservable Fields & Limitations
- **Perfect Forward Secrecy (PFS):** While we can observe phase 1 DH groups, verifying if PFS is enabled requires capturing Phase 2 (CREATE_CHILD_SA) DH groups or tracking XFRM state refreshes. We left this out of the strict deterministic rule engine until stronger active evidence is gathered.
- **Authentication Method:** Entirely unobservable from passive PCAP. Firing the `UNKNOWN_AUTHENTICATION` rule ensures users know to check for PSK usage out-of-band.
