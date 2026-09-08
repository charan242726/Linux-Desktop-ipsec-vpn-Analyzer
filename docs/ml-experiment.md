# ML Experiment: Encrypted ESP Traffic Classification

This document formally reports the design and results of the Machine Learning experiment evaluating whether encrypted ESP traffic behavior contains sufficient signal to classify application types, without relying on decrypted payloads or VPN configuration metadata.

## 1. Dataset Overview
- **Usable Sessions:** 239 completely independent sessions.
- **Traffic Classes (7):** `icmp` (35), `web` (35), `video` (35), `voip` (35), `email` (35), `chat` (34), `bulk` (30).
- **Configuration Coverage:** 7 different strongSwan IPsec encryption configurations ranging from AES-GCM to weak DH groups and transport modes.

## 2. Feature Set (Primary Model)
The primary model strictly uses **only observable ESP traffic statistics**. No deterministic IKE/VPN configuration properties were provided to the model.
- `esp_packet_count`, `esp_total_bytes`
- `esp_mean_packet_size`, `esp_std_packet_size`, `esp_max_packet_size`, `esp_min_packet_size`
- `esp_duration`, `esp_mean_interarrival`, `esp_std_interarrival`
- `forward_esp_packets`, `reverse_esp_packets`
- `forward_esp_bytes`, `reverse_esp_bytes`

## 3. Evaluation Protocol
- **Method:** 5-Fold Stratified Group K-Fold Cross-Validation.
- **Grouping:** All 5 repetitions of a specific `config` + `traffic_class` experiment were grouped together. This rigorously prevents "repetition leakage" where nearly identical back-to-back runs might bleed across the train/test boundary.
- **Preprocessing:** Missing values (from 0-packet sessions) were imputed strictly using training-fold medians (`SimpleImputer`). No packet-level splits occurred.

## 4. Baselines
The `DummyClassifier` (majority-class predictor) achieved a **macro F1 score of 0.04** and an accuracy of **10.4%**. The dataset is well balanced, so guessing a single class uniformly fails.

## 5. Primary Model Results (ESP-Only)
The primary model selected was a `RandomForestClassifier`.
- **Accuracy:** 99.16%
- **Macro F1:** 0.9918
- **Weighted F1:** 0.9916

**Per-class F1 Scores:**
- `bulk`: 1.00
- `chat`: 1.00
- `email`: 0.97
- `icmp`: 1.00
- `video`: 0.97
- `voip`: 1.00
- `web`: 1.00

### Confusion Matrix Analysis
The model flawlessly separated 5 of the 7 traffic classes across all configurations. The only observed confusion was between `video` and `email` (1 `email` session misclassified as `video`, and 1 `video` session misclassified as `email`). This is highly plausible because both involve sustained, multi-megabyte TCP/UDP transfers that can exhibit similar segmentation and burst characteristics under encryption overhead.

## 6. Feature Importance (Random Forest)
The most determinative ESP features were:
1. `esp_duration` (0.128)
2. `esp_mean_packet_size` (0.103)
3. `esp_std_packet_size` (0.100)
4. `reverse_esp_packets` (0.100)

*Interpretation:* The model successfully keyed in on the structural duration of the flow and the average fragmentation/packet size (which dictates whether traffic is mostly small ACK/VoIP frames or large MTU-capped bulk segments).

## 7. Ablation Experiment (ESP vs ESP + Configuration)
To audit whether IKE configuration metadata artificially inflates the model's confidence, we trained a secondary model supplying both ESP statistics and the raw configuration parameters (`encryption_algorithm`, `dh_group`, etc.).
- **ESP-Only Accuracy:** 99.16%
- **ESP + Configuration Accuracy:** 99.16%
*Conclusion:* The ESP behavioral statistics are so strong and distinguishable that the model completely ignored the configuration metadata. No artificial boost was gained by cheating.

## 8. Configuration-Held-Out Evaluation
To definitively prove the model learned *traffic behavior* and not simply the overhead signature of a specific IPsec configuration, we ran a Leave-One-Group-Out cross-validation (training on 6 VPN configurations, evaluating strictly on the unseen 7th).
- **Held-Out Accuracy:** 99.16%
*Conclusion:* The classifier is **configuration-invariant**. It successfully recognizes a VoIP call whether it is wrapped in `aes128gcm` or `aes256cbc` transport mode.

## 9. Conclusion
Can encrypted ESP traffic statistics provide useful traffic-class inference in this controlled dataset?
**Yes.** The combination of packet counts, directional byte volume, and inter-arrival timing creates a highly robust fingerprint for controlled applications. However, this prototype performance (99%+) reflects the clean, isolated nature of our testbed environment (where only one traffic generator ran per session) and should not be blindly assumed to generalize to noisy, multiplexed real-world enterprise VPN trunks without further real-world data collection.
