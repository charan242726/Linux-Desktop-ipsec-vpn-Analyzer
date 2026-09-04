# Experiment Matrix Design

## 1. Configurations (9 Variants)
The experiment systematically alters strongSwan IKEv2 configuration to observe the resulting metadata and traffic characteristics.

1. **base**: `aes256-sha256-modp2048` (IKE), `aes256-sha256` (ESP). Mode: `tunnel`. Provides a standard secure baseline.
2. **transport**: Identical to `base`, but Mode is `transport`. Expected to change IP header visibility.
3. **aes128gcm**: `aes128gcm16-prfsha256-modp2048`. Uses AEAD (Galois/Counter Mode) which combines encryption and integrity into one step.
4. **aes256cbc**: Identical to `base` (AES-256-CBC). Explicitly duplicated to satisfy the matrix constraint while maintaining control.
5. **pfsoff**: Identical to `base`. Perfect Forward Secrecy (PFS) in the ESP Child SA is already off by default because `base` omits the DH group in its ESP proposal.
6. **dhweak**: `aes256-sha256-modp1024`. Uses a significantly weaker Diffie-Hellman group (MODP 1024 / Group 2) for the IKE SA.
7. **legacy**: **[UNSUPPORTED]**. Designed for IKEv1 with `3des-sha1-modp1024`. This environment actively rejects the weak proposal (`NO_PROPOSAL_CHOSEN`).
8. **replayoff**: Identical to `base` but with `replay_window = 0` in the Child SA to disable anti-replay protection.
9. **ipv6**: **[UNSUPPORTED]**. Designed for IPv6 endpoints. The underlying Docker bridge `ipsec-net` was initialized without IPv6 enabled.

## 2. Traffic Classes (7 Categories)
Controlled, reproducible traffic generators were built inside `traffic/`.

1. **icmp**: Standard ICMP Echo Requests (`ping`).
2. **web**: Single large HTTP payload fetch (10MB `curl`).
3. **video**: High-bandwidth sustained UDP stream (5Mbps `iperf3`).
4. **voip**: Low-bandwidth bidirectional UDP stream (100Kbps `iperf3`).
5. **email**: Bursty HTTP fetches of medium payloads (1MB `curl` in a loop).
6. **chat**: Paced, low-bandwidth TCP traffic (`iperf3` paced to 10Kbps).
7. **bulk**: Extremely large file transfer (50MB `curl`). *Justification: The initial brief provided 6 examples but explicitly required 7 traffic classes for the final matrix. `bulk` was introduced to represent a sustained, maximal-throughput TCP transfer, which exhibits distinct congestion-control and segmentation behaviors compared to bursty HTTP (`web`) or paced UDP streams (`video`/`voip`).*

## 3. Repetitions
Target: 5 repetitions per supported combination.
Total Supported Configurations: 7
Total Traffic Classes: 7
Total Expected Sessions: 7 * 7 * 5 = 245 sessions.

*(Note: The maximum 315 count includes the unsupported legacy and ipv6 configurations, which are logged and skipped by the driver).*
