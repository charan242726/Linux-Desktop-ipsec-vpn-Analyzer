from abc import ABC, abstractmethod
from typing import Optional, List
from analyzer.models import IkeMetadata, XfrmMetadata, Finding, Severity, ObservationStatus

class BaseRule(ABC):
    @abstractmethod
    def evaluate(self, ike: IkeMetadata, xfrm: XfrmMetadata) -> Optional[Finding]:
        pass

class IkeVersionRule(BaseRule):
    def evaluate(self, ike: IkeMetadata, xfrm: XfrmMetadata) -> Optional[Finding]:
        if ike.ike_version.status == ObservationStatus.OBSERVED:
            try:
                ver = float(ike.ike_version.value)
                if ver < 2.0:
                    return Finding(
                        rule_id="IKE_VERSION_DEPRECATED",
                        title="Deprecated IKE Version",
                        severity=Severity.HIGH,
                        evidence=f"Observed IKE version {ike.ike_version.value}",
                        explanation="IKEv1 is deprecated (RFC 4306/7296) and vulnerable to aggressive mode PSK cracking and DoS.",
                        recommendation="Upgrade to IKEv2."
                    )
            except (ValueError, TypeError):
                pass
        return None

class WeakEncryptionRule(BaseRule):
    def evaluate(self, ike: IkeMetadata, xfrm: XfrmMetadata) -> Optional[Finding]:
        if ike.encryption_algorithm.status == ObservationStatus.OBSERVED:
            alg = str(ike.encryption_algorithm.value).upper()
            
            # Identify purely by IANA code if it's purely numeric
            if alg in ["2", "3"]: # DES, 3DES
                is_critical = True
            elif "DES" in alg or "NULL" in alg or alg == "11": # NULL
                is_critical = True
            else:
                is_critical = False

            if is_critical:
                return Finding(
                    rule_id="WEAK_ENCRYPTION_CRITICAL",
                    title="Critically Weak Encryption Algorithm",
                    severity=Severity.CRITICAL,
                    evidence=f"Observed encryption: {alg}",
                    explanation="DES, 3DES, or NULL ciphers are broken and provide no meaningful confidentiality.",
                    recommendation="Upgrade to AES-GCM (>=128 bit) or AES-CBC (>=256 bit)."
                )
                
            # Check key length if AES (ID 12 is AES-CBC, ID 20 is AES-GCM)
            if "AES" in alg or alg in ["12", "13", "14", "18", "19", "20"]:
                if ike.encryption_key_length.status == ObservationStatus.OBSERVED:
                    try:
                        key_len = int(float(ike.encryption_key_length.value))
                        if key_len < 128:
                            return Finding(
                                rule_id="WEAK_ENCRYPTION_KEYLEN",
                                title="Insecure Encryption Key Length",
                                severity=Severity.HIGH,
                                evidence=f"Observed algorithm {alg} with key length {key_len} bits",
                                explanation="Encryption keys under 128 bits are susceptible to brute force attacks.",
                                recommendation="Increase key length to at least 128 bits, preferably 256 bits."
                            )
                    except (ValueError, TypeError):
                        pass
        return None

class MissingIntegrityRule(BaseRule):
    def evaluate(self, ike: IkeMetadata, xfrm: XfrmMetadata) -> Optional[Finding]:
        if ike.encryption_algorithm.status == ObservationStatus.OBSERVED:
            alg = str(ike.encryption_algorithm.value).upper()
            
            # AEAD IANA codes: 20=AES_GCM_16, 18=AES_CCM_8, 19=AES_CCM_12, 28=CHACHA20_POLY1305
            is_aead = "GCM" in alg or "CCM" in alg or "CHACHA20" in alg or alg in ["18", "19", "20", "28"]
            
            if not is_aead and ike.integrity_algorithm.status != ObservationStatus.OBSERVED:
                return Finding(
                    rule_id="MISSING_INTEGRITY",
                    title="Missing Integrity Protection",
                    severity=Severity.CRITICAL,
                    evidence=f"Encryption is {alg} (non-AEAD), but no integrity algorithm observed.",
                    explanation="Without integrity (HMAC) or an AEAD cipher, IPsec is vulnerable to active tampering and padding oracle attacks.",
                    recommendation="Enable an HMAC (e.g., SHA-256) or switch to an AEAD cipher like AES-GCM."
                )
            
            if ike.integrity_algorithm.status == ObservationStatus.OBSERVED:
                integ = str(ike.integrity_algorithm.value).upper()
                # IANA 1=MD5, 2=SHA1
                if "MD5" in integ or "SHA1" in integ or integ in ["1", "2"]:
                    return Finding(
                        rule_id="WEAK_INTEGRITY",
                        title="Weak Integrity Algorithm",
                        severity=Severity.HIGH,
                        evidence=f"Observed integrity: {integ}",
                        explanation="MD5 and SHA-1 are cryptographically weak and vulnerable to collision attacks.",
                        recommendation="Upgrade to SHA-256 or better."
                    )
        return None

class WeakDhGroupRule(BaseRule):
    def evaluate(self, ike: IkeMetadata, xfrm: XfrmMetadata) -> Optional[Finding]:
        if ike.dh_group.status == ObservationStatus.OBSERVED:
            dh = str(ike.dh_group.value).upper()
            
            try:
                group_num = int("".join(filter(str.isdigit, dh)))
                if group_num <= 2:
                    return Finding(
                        rule_id="WEAK_DH_GROUP",
                        title="Logjam-Vulnerable DH Group",
                        severity=Severity.HIGH,
                        evidence=f"Observed DH Group {group_num}",
                        explanation="DH Groups 1 and 2 (768/1024-bit) are vulnerable to the Logjam attack and provide insufficient forward secrecy.",
                        recommendation="Upgrade to DH Group 14 (2048-bit) or ECP groups (e.g., 19 or 20)."
                    )
                if group_num == 5:
                    return Finding(
                        rule_id="SUBOPTIMAL_DH_GROUP",
                        title="Suboptimal DH Group",
                        severity=Severity.MEDIUM,
                        evidence=f"Observed DH Group {group_num}",
                        explanation="DH Group 5 (1536-bit) is considered borderline and may be crackable by well-resourced adversaries.",
                        recommendation="Upgrade to DH Group 14 or higher."
                    )
            except ValueError:
                pass
        return None

class ReplayProtectionRule(BaseRule):
    def evaluate(self, ike: IkeMetadata, xfrm: XfrmMetadata) -> Optional[Finding]:
        if xfrm.replay_window.status == ObservationStatus.OBSERVED:
            try:
                window = int(xfrm.replay_window.value)
                if window == 0:
                    return Finding(
                        rule_id="REPLAY_PROTECTION_DISABLED",
                        title="Anti-Replay Protection Disabled",
                        severity=Severity.HIGH,
                        evidence=f"XFRM state shows inbound replay-window size of {window}",
                        explanation="When the replay window is 0, the receiver accepts replayed ESP packets, allowing attackers to inject old traffic.",
                        recommendation="Enable anti-replay protection (replay-window >= 32)."
                    )
            except (ValueError, TypeError):
                pass
        return None

class UnknownAuthenticationRule(BaseRule):
    def evaluate(self, ike: IkeMetadata, xfrm: XfrmMetadata) -> Optional[Finding]:
        if ike.authentication_method.status == ObservationStatus.UNKNOWN:
            return Finding(
                rule_id="UNKNOWN_AUTHENTICATION",
                title="Unknown Authentication Method",
                severity=Severity.INFO,
                evidence="Passive capture cannot decrypt the IKE_AUTH payload.",
                explanation="The authentication method (PSK vs Certificates) could not be observed from the evidence.",
                recommendation="Verify configuration out-of-band to ensure PSKs are not being used in enterprise environments."
            )
        return None

class XfrmModeRule(BaseRule):
    def evaluate(self, ike: IkeMetadata, xfrm: XfrmMetadata) -> Optional[Finding]:
        if xfrm.mode.status == ObservationStatus.OBSERVED:
            if "transport" in str(xfrm.mode.value).lower():
                return Finding(
                    rule_id="TRANSPORT_MODE",
                    title="Transport Mode Used",
                    severity=Severity.INFO,
                    evidence="XFRM state indicates transport mode.",
                    explanation="Transport mode encrypts only the payload, leaving IP headers visible. It is usually safe if wrapped in another tunnel, but exposes internal IP structures otherwise.",
                    recommendation="Ensure this is intended. Use Tunnel mode for site-to-site WAN connections."
                )
        return None

def get_all_rules() -> List[BaseRule]:
    return [
        IkeVersionRule(),
        WeakEncryptionRule(),
        MissingIntegrityRule(),
        WeakDhGroupRule(),
        ReplayProtectionRule(),
        UnknownAuthenticationRule(),
        XfrmModeRule()
    ]
