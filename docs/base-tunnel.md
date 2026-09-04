# Base IKEv2/IPsec Tunnel Verification

This document confirms the successful configuration and establishment of a baseline IKEv2 IPsec tunnel between the two Docker testbed endpoints.

## Topology
- **Network**: `ipsec-net` (`10.10.0.0/24`)
- **vpn1**: `10.10.0.10`
- **vpn2**: `10.10.0.20`

## Versions and Capabilities
- **strongSwan Version**: `Linux strongSwan U5.9.13/K7.2.2-arch1-1`
- **Networking**: `XFRM` framework is active and supported within the `NET_ADMIN` privileged containers.

## Configuration Files Created
Two configuration files were written to the hosts using standard `swanctl.conf` syntax.
- `vpn1`: `/etc/swanctl/conf.d/base.conf`
- `vpn2`: `/etc/swanctl/conf.d/base.conf`

**Cryptographic Proposals:**
- **IKE**: `aes256-sha256-modp2048`
- **ESP**: `aes256-sha256`
- **Authentication**: Pre-Shared Key (`psk`)

## Execution Commands
1. Load configurations on both peers:
   ```bash
   docker exec vpn1 swanctl --load-all
   docker exec vpn2 swanctl --load-all
   ```
2. Initiate the IPsec tunnel from `vpn1`:
   ```bash
   docker exec vpn1 swanctl --initiate --child base
   ```

## Verification Results

### 1. IKE and CHILD SA Establishment
The `swanctl --list-sas` command on `vpn1` confirms both the IKE SA (`base[1]`) and the ESP CHILD SA (`base{1}`) are `ESTABLISHED` and `INSTALLED`:
```text
base: #1, ESTABLISHED, IKEv2, 96d867805d478c5b_i* 50a0a40bdfca2f89_r
  local  'vpn1' @ 10.10.0.10[4500]
  remote 'vpn2' @ 10.10.0.20[4500]
  AES_CBC-256/HMAC_SHA2_256_128/PRF_HMAC_SHA2_256/MODP_2048
  base: #1, reqid 1, INSTALLED, TUNNEL, ESP:AES_CBC-256/HMAC_SHA2_256_128
    in  c43ce620,    252 bytes,     3 packets,     0s ago
    out c37c0aac,    252 bytes,     3 packets,     0s ago
    local  10.10.0.10/32
    remote 10.10.0.20/32
```

### 2. XFRM Kernel State and Policy
The kernel successfully mapped the routing rules to the ESP protocol.
`ip xfrm policy` verifies the route intercept:
```text
src 10.10.0.10/32 dst 10.10.0.20/32 
	dir out priority 367231 ptype main 
	tmpl src 10.10.0.10 dst 10.10.0.20
		proto esp spi 0xc37c0aac reqid 1 mode tunnel
```
`ip xfrm state` verifies the encryption keys and SPIs:
```text
src 10.10.0.10 dst 10.10.0.20
	proto esp spi 0xc37c0aac reqid 1 mode tunnel
	replay-window 0 flag af-unspec
	auth-trunc hmac(sha256) 0xe64897b9db5bb5ec19781b90b2fdf626a9d4a0dea7b5a408413b6df365ae0f30 128
	enc cbc(aes) 0x554d9e3118522cb01da5e21ad402da16d6f6535faf2534918cda04bd14ae208f
```

### 3. Traffic Encryption Verification
Executing `ping -c 3 10.10.0.20` resulted in `0% packet loss`.
Crucially, re-running `swanctl --list-sas` confirmed that exactly 3 packets (252 bytes) were encrypted and transmitted over the ESP `out` interface, and exactly 3 response packets were decrypted over the `in` interface. This proves the host-to-host ping traffic was successfully intercepted and wrapped in ESP by the XFRM policies.

## Troubleshooting Notes
- **Plugin Warnings:** `swanctl` printed warnings about missing plugins (e.g., `ldap`, `pkcs11`, `gcrypt`, `curve25519`). These are non-fatal warnings for optional plugins. Standard AES and SHA operations are handled by the default `openssl` plugin, which was successfully loaded. No additional plugins needed to be installed.
