import pytest
from analyzer.models import IkeMetadata, XfrmMetadata, Field
from rules.risk_engine import RiskEngine

def test_risk_engine_secure():
    engine = RiskEngine()
    ike = IkeMetadata(
        ike_version=Field.observed("2.0"),
        encryption_algorithm=Field.observed("AES-GCM"),
        encryption_key_length=Field.observed("256"),
        dh_group=Field.observed("14")
    )
    xfrm = XfrmMetadata(
        replay_window=Field.observed("32"),
        mode=Field.observed("tunnel")
    )
    
    findings, score, category = engine.evaluate(ike, xfrm)
    
    # We should get UNKNOWN_AUTHENTICATION (INFO) -> penalty 0
    assert score == 100
    assert category == "SECURE"
    assert len(findings) == 1
    assert findings[0].rule_id == "UNKNOWN_AUTHENTICATION"

def test_risk_engine_critical():
    engine = RiskEngine()
    ike = IkeMetadata(
        ike_version=Field.observed("1.0"),          # HIGH (-20)
        encryption_algorithm=Field.observed("DES"), # CRITICAL (-40)
        dh_group=Field.observed("2")                # HIGH (-20)
    )
    xfrm = XfrmMetadata(
        replay_window=Field.observed("0")           # HIGH (-20)
    )
    
    findings, score, category = engine.evaluate(ike, xfrm)
    
    assert score == 0 # 100 - 20 - 40 - 20 - 20 = 0
    assert category == "CRITICAL RISK"
    
    rule_ids = [f.rule_id for f in findings]
    assert "IKE_VERSION_DEPRECATED" in rule_ids
    assert "WEAK_ENCRYPTION_CRITICAL" in rule_ids
    assert "WEAK_DH_GROUP" in rule_ids
    assert "REPLAY_PROTECTION_DISABLED" in rule_ids
