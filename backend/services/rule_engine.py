WEAK_CIPHERS = {"DES", "3DES", "RC4", "NULL"}
WEAK_DH_GROUPS = {1, 2, 5}  # Groups < 14 are considered weak

def run_rules(ike_meta: dict) -> dict:
    results = {}

    enc = ike_meta.get("encryption_algorithm", "")
    if enc in WEAK_CIPHERS:
        results["weak_cipher"] = {
            "detected": True,
            "severity": "HIGH",
            "detail": f"{enc} is cryptographically broken"
        }

    dh = ike_meta.get("dh_group", 0)
    if dh in WEAK_DH_GROUPS:
        results["weak_dh_group"] = {
            "detected": True,
            "severity": "HIGH",
            "detail": f"DH Group {dh} provides insufficient key strength"
        }

    pfs_status = ike_meta.get("pfs_enabled", "NOT_DETERMINED")
    if pfs_status == "DISABLED":
        results["no_pfs"] = {
            "detected": True,
            "severity": "MEDIUM",
            "detail": "Perfect Forward Secrecy disabled — past sessions vulnerable if key compromised"
        }

    if ike_meta.get("ike_version") == "IKEv1":
        results["ikev1"] = {
            "detected": True,
            "severity": "MEDIUM",
            "detail": "IKEv1 has known vulnerabilities — upgrade to IKEv2"
        }

    sa_lifetime = ike_meta.get("sa_lifetime_seconds", 86400)
    if sa_lifetime > 86400:  # more than 24 hours
        results["long_sa_lifetime"] = {
            "detected": True,
            "severity": "LOW",
            "detail": f"SA lifetime {sa_lifetime}s is too long — reduces forward secrecy"
        }

    return results
