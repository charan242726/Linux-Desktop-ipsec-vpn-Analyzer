import pytest
from analyzer.models import IkeMetadata, XfrmMetadata, Field, ObservationStatus, Severity
from rules.security_rules import (
    IkeVersionRule, WeakEncryptionRule, MissingIntegrityRule,
    WeakDhGroupRule, ReplayProtectionRule, UnknownAuthenticationRule, XfrmModeRule
)

def test_ike_version_rule():
    rule = IkeVersionRule()
    
    # Secure
    ike = IkeMetadata(ike_version=Field.observed("2.0"))
    assert rule.evaluate(ike, XfrmMetadata()) is None
    
    # Weak
    ike_weak = IkeMetadata(ike_version=Field.observed("1.0"))
    finding = rule.evaluate(ike_weak, XfrmMetadata())
    assert finding is not None
    assert finding.severity == Severity.HIGH
    assert finding.rule_id == "IKE_VERSION_DEPRECATED"
    
    # Unknown
    ike_unk = IkeMetadata()
    assert rule.evaluate(ike_unk, XfrmMetadata()) is None

def test_weak_encryption_rule():
    rule = WeakEncryptionRule()
    
    # Secure
    ike = IkeMetadata(encryption_algorithm=Field.observed("AES"), encryption_key_length=Field.observed("256"))
    assert rule.evaluate(ike, XfrmMetadata()) is None
    
    # Critical (DES)
    ike_des = IkeMetadata(encryption_algorithm=Field.observed("DES"))
    finding = rule.evaluate(ike_des, XfrmMetadata())
    assert finding is not None
    assert finding.severity == Severity.CRITICAL
    
    # High (AES 64-bit)
    ike_aes_weak = IkeMetadata(encryption_algorithm=Field.observed("AES"), encryption_key_length=Field.observed("64"))
    finding = rule.evaluate(ike_aes_weak, XfrmMetadata())
    assert finding is not None
    assert finding.severity == Severity.HIGH

def test_missing_integrity_aead_rule():
    rule = MissingIntegrityRule()
    
    # Non-AEAD missing integrity
    ike_cbc = IkeMetadata(
        encryption_algorithm=Field.observed("AES-CBC"),
        integrity_algorithm=Field.unknown()
    )
    finding = rule.evaluate(ike_cbc, XfrmMetadata())
    assert finding is not None
    assert finding.severity == Severity.CRITICAL
    assert finding.rule_id == "MISSING_INTEGRITY"
    
    # AEAD missing integrity
    ike_gcm = IkeMetadata(
        encryption_algorithm=Field.observed("ENCR_AES_GCM_16"),
        integrity_algorithm=Field.unknown()
    )
    assert rule.evaluate(ike_gcm, XfrmMetadata()) is None
    
    # Weak Integrity (MD5)
    ike_md5 = IkeMetadata(
        encryption_algorithm=Field.observed("AES-CBC"),
        integrity_algorithm=Field.observed("MD5")
    )
    finding = rule.evaluate(ike_md5, XfrmMetadata())
    assert finding is not None
    assert finding.severity == Severity.HIGH
    assert finding.rule_id == "WEAK_INTEGRITY"

def test_replay_protection():
    rule = ReplayProtectionRule()
    
    # Disabled
    xfrm_off = XfrmMetadata(replay_window=Field.observed("0"))
    finding = rule.evaluate(IkeMetadata(), xfrm_off)
    assert finding is not None
    assert finding.severity == Severity.HIGH
    
    # Enabled
    xfrm_on = XfrmMetadata(replay_window=Field.observed("32"))
    assert rule.evaluate(IkeMetadata(), xfrm_on) is None

def test_weak_dh_group():
    rule = WeakDhGroupRule()
    
    # Group 14 (Secure)
    ike_secure = IkeMetadata(dh_group=Field.observed("14"))
    assert rule.evaluate(ike_secure, XfrmMetadata()) is None
    
    # Group 2 (Weak)
    ike_weak = IkeMetadata(dh_group=Field.observed("2"))
    finding = rule.evaluate(ike_weak, XfrmMetadata())
    assert finding is not None
    assert finding.severity == Severity.HIGH
    
    # Group 5 (Suboptimal)
    ike_sub = IkeMetadata(dh_group=Field.observed("5"))
    finding = rule.evaluate(ike_sub, XfrmMetadata())
    assert finding is not None
    assert finding.severity == Severity.MEDIUM

def test_unknown_auth():
    rule = UnknownAuthenticationRule()
    finding = rule.evaluate(IkeMetadata(), XfrmMetadata())
    assert finding is not None
    assert finding.severity == Severity.INFO
    assert finding.rule_id == "UNKNOWN_AUTHENTICATION"

def test_xfrm_mode():
    rule = XfrmModeRule()
    xfrm_trans = XfrmMetadata(mode=Field.observed("transport"))
    finding = rule.evaluate(IkeMetadata(), xfrm_trans)
    assert finding is not None
    assert finding.severity == Severity.INFO
    
    xfrm_tunnel = XfrmMetadata(mode=Field.observed("tunnel"))
    assert rule.evaluate(IkeMetadata(), xfrm_tunnel) is None
