# Dataset Generation Driver

## Overview
The dataset generation pipeline is fully automated and resumable via `scripts/generate_dataset.sh`.
It operates on the principle that:
`1 config × 1 traffic class × 1 repetition = 1 independent VPN session (1 PCAP)`

## Usage
Run the preflight (base × icmp × 2) to validate the capture environment:
```bash
./scripts/generate_dataset.sh --preflight
```

Run the full matrix:
```bash
./scripts/generate_dataset.sh
```

## Resumability & Failure Handling
- **Resumable**: If a session fails (e.g., VPN initiation failure, empty PCAP, or traffic generator crash), it logs the error to `run.log` and marks the sample as failed. Rerunning the script will skip any sample already marked as `success` in `manifest.csv` that has a valid PCAP file on disk.
- **Validation**: After every run, `tshark` is executed against the generated PCAP. If IKE packets are not found or the file is 0 bytes, the capture is marked as a failure.
- **Isolation**: Between every repetition, `swanctl --terminate` is called, and background `tshark` processes are killed to prevent cross-contamination of sessions.

## Artifacts Generated
For each successful session `sample_id` (e.g., `aes128gcm_video_r3`), the following are produced:
1. `captures/<sample_id>.pcapng` (The raw packet capture of the bridge)
2. `metadata/<sample_id>.xfrm.txt` (Kernel IPsec state)
3. `metadata/<sample_id>.xfrm-policy.txt` (Kernel IPsec policy)
4. A single row in `testbed/manifest.csv` recording the outcome.

## Known Limitations
- `legacy` and `ipv6` configurations are hard-coded to skip and report as unsupported due to kernel/docker environment constraints. They will not produce PCAPs.
