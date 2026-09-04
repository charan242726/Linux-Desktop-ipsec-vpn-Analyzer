# Session-Level Feature Dictionary

This document defines the extracted features derived from the captured PCAP files. Each PCAP corresponds to a single VPN session.

## Group A — Deterministic / Observable VPN Metadata
These features characterize the cryptographic negotiation (IKEv2) and connection identities.

**`ike_version`**
- **Description**: The major version of the IKE protocol observed.
- **Source**: `ike.version` from `IKE_SA_INIT` packets.
- **Unit**: Hexadecimal code (e.g., `0x20` = 2.0).
- **Group**: Deterministic.
- **Missing behavior**: Empty string if no IKE packets found.

**`exchange_types`**
- **Description**: The sequence of exchange types observed in the session.
- **Source**: `ike.exchangetype` sorted and delimited by pipes.
- **Unit**: Integer codes (e.g., `34|35|37` = IKE_SA_INIT, IKE_AUTH, INFORMATIONAL).
- **Group**: Deterministic.
- **Missing behavior**: Empty string.

**`initiator_spi` / `responder_spi`**
- **Description**: The unique Security Parameter Indexes (SPI) assigned by the initiator and responder for the IKE Security Association.
- **Source**: `ike.ispi` and `ike.rspi`.
- **Unit**: Hex string.
- **Group**: Deterministic.
- **Missing behavior**: Empty string.

**`encryption_algorithm`**
- **Description**: The negotiated encryption algorithm for the connection.
- **Source**: `ike.tf.id.encr` from the IKE proposal payload.
- **Unit**: IANA Transform Type 1 ID (e.g., `12` = ENCR_AES_CBC).
- **Group**: Deterministic.
- **Missing behavior**: Empty string.

**`encryption_key_length`**
- **Description**: The bit length of the encryption key.
- **Source**: `ike.ike2.attr.key_length`.
- **Unit**: Bits.
- **Group**: Deterministic.
- **Missing behavior**: Empty string.

**`integrity_algorithm`**
- **Description**: The negotiated integrity protection algorithm.
- **Source**: `ike.tf.id.integ` from the IKE proposal payload.
- **Unit**: IANA Transform Type 3 ID (e.g., `12` = AUTH_HMAC_SHA2_256_128).
- **Group**: Deterministic.
- **Missing behavior**: Empty string.

**`prf_algorithm`**
- **Description**: The negotiated Pseudo-random Function.
- **Source**: `ike.tf.id.prf` from the IKE proposal payload.
- **Unit**: IANA Transform Type 2 ID (e.g., `5` = PRF_HMAC_SHA2_256).
- **Group**: Deterministic.
- **Missing behavior**: Empty string.

**`dh_group`**
- **Description**: The negotiated Diffie-Hellman group for key exchange.
- **Source**: `ike.tf.id.ke` from the IKE proposal payload.
- **Unit**: IANA Transform Type 4 ID (e.g., `14` = 2048-bit MODP).
- **Group**: Deterministic.
- **Missing behavior**: Empty string.


## Group B — Encrypted Traffic Behavior
These features are derived strictly from passive observation of the Encapsulating Security Payload (ESP) stream.

**`esp_packet_count`**
- **Description**: Total number of ESP packets observed in the session.
- **Source**: Counting packets where protocol is ESP.
- **Unit**: Count.
- **Group**: ML Candidate.
- **Missing behavior**: `0`.

**`esp_total_bytes`**
- **Description**: Total bytes transferred across all ESP packets.
- **Source**: Sum of `frame.len`.
- **Unit**: Bytes.
- **Group**: ML Candidate.
- **Missing behavior**: `0`.

**`esp_min_packet_size` / `esp_max_packet_size` / `esp_mean_packet_size` / `esp_std_packet_size`**
- **Description**: Statistical aggregations of the ESP packet sizes in the session.
- **Source**: Calculations over `frame.len`.
- **Unit**: Bytes.
- **Group**: ML Candidate.
- **Missing behavior**: Empty string when `esp_packet_count` is 0. Standard deviation is `0.0` when count is 1.

**`esp_duration`**
- **Description**: The time elapsed between the first and last observed ESP packet in the session.
- **Source**: Max `frame.time_epoch` minus min `frame.time_epoch` for ESP packets.
- **Unit**: Seconds (float).
- **Group**: ML Candidate.
- **Missing behavior**: Empty string.

**`esp_mean_interarrival` / `esp_std_interarrival`**
- **Description**: The mean and standard deviation of time intervals between consecutive ESP packets.
- **Source**: Differences between consecutive `frame.time_epoch` values.
- **Unit**: Seconds (float).
- **Group**: ML Candidate.
- **Missing behavior**: Empty string when `esp_packet_count` < 2.

**`forward_esp_packets` / `reverse_esp_packets`**
- **Description**: Directional counts of ESP packets. Forward is defined as traffic originating from the source IP of the first observed ESP packet.
- **Source**: Grouping by `ip.src` and `ip.dst`.
- **Unit**: Count.
- **Group**: ML Candidate.
- **Missing behavior**: `0`.

**`forward_esp_bytes` / `reverse_esp_bytes`**
- **Description**: Directional total bytes of ESP packets.
- **Source**: Sum of `frame.len` grouped by direction.
- **Unit**: Bytes.
- **Group**: ML Candidate.
- **Missing behavior**: `0`.
