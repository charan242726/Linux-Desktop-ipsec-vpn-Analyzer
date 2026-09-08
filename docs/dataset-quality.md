# Dataset Quality Analysis

This document reports the quality metrics of the generated IPsec VPN corpus.

## 1. Corpus Coverage
- **Intended Sessions:** 245 (7 Supported Configs × 7 Traffic Classes × 5 Repetitions)
- **Successful Sessions:** 239
- **Failed Sessions:** 6 (Missing `replayoff` bulk/chat sessions due to traffic generation timeouts)
- **Unsupported Configurations:** 2 (`legacy`, `ipv6`)
- **Usable Feature Rows:** 239 (One row per successful PCAP, rigorously verified)

**Coverage Matrix (Success/Repetitions):**
| Configuration | icmp | web | video | voip | email | chat | bulk |
|---------------|------|-----|-------|------|-------|------|------|
| base | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| transport | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| aes128gcm | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| aes256cbc | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| pfsoff | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| dhweak | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| replayoff | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 4/5 | 0/5 |

## 2. Missing Values Analysis
Across the 239 usable rows, missing values were strictly tracked:
- **`integrity_algorithm`**: Missing in 37 rows. Justification: Configurations utilizing AEAD ciphers (e.g., `aes128gcm`) intrinsically combine encryption and integrity. StrongSwan does not explicitly negotiate a separate integrity algorithm in these cases.
- **IKE Metadata (`ike_version`, etc.)**: Missing in 3 rows due to edge-case truncated IKE payload captures in `tshark` before daemon handshake completion.
- **ESP Size/Timing features**: Missing in 2 rows. Justification: Two sessions successfully established the tunnel but captured 0 ESP packets during their duration.

## 3. Constant Features Analysis
- `ike_version` (Unique Values: 1)
- `prf_algorithm` (Unique Values: 1)
- `integrity_algorithm` (Unique Values: 1, excluding nulls)

*Conclusion:* These are deterministic metadata values representing the fixed structure of our environment. They provide zero predictive variance for ML but are valid for rules-engine mapping.

## 4. Duplicates & Near-Duplicates
- **Exact Feature Duplicates:** 0
- Every single successful session generated a mathematically unique vector of packet timings and sizes. None were duplicated from file-system caching or driver overlapping.

## 5. ESP Feature Distributions by Traffic Class
Measurements grouped by traffic class empirically prove they are distinguishable:
- **`icmp`**: Exactly 40 packets, 100% symmetrical (20 fwd / 20 rev), zero variance in packet size (`std_packet_size` = 0).
- **`bulk`**: Massive throughput. Averaging ~57,000 packets per session and ~59MB payload. Highly asymmetrical (19,000 fwd / 38,000 rev).
- **`video`**: Heavily unidirectional UDP stream. Averaging 4393 forward packets and only 13 reverse packets.
- **`voip`**: Symmetrical low-bandwidth UDP stream. Averaging 108 forward / 105 reverse packets.
- **`chat` / `email` / `web`**: Differing TCP patterns displaying bursty variance and distinct maximum/minimum segmentation thresholds.

## 6. IKE Sanity Checks
The extracted metadata maps correctly to the intended VPN configuration parameters:
- `aes128gcm` correctly reflects `ENCR_AES_GCM_16` encryption and drops integrity.
- `dhweak` correctly reflects `MODP_1024` instead of the baseline `MODP_2048`.

## 7. Leakage Risks & Feature Groups
Features have been definitively grouped to prevent data leakage in future ML models:

**Group C (Leakage / Identifiers) - EXCLUDED FROM ML:**
- `sample_id`, `config`, `traffic_class`, `rep` (These encode the target and represent extreme leakage).

**Group B (Behavioral Features) - ML CANDIDATES:**
- Encrypted traffic statistics (`esp_packet_count`, `esp_mean_packet_size`, `forward_esp_packets`, etc.)

**Group A (Deterministic Metadata) - ML CANDIDATES:**
- IKE negotiation metadata (`encryption_algorithm`, `dh_group`, `exchange_types`).

*Action:* `Group C` features have been removed from the primary dataset and saved strictly to `dataset/ml_metadata_mapping.csv`. Only Group A + B features exist in `dataset/ml_candidate_features.csv`.
