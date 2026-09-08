import pytest
from unittest.mock import patch
from backend.worker.worker_thread import _analyze_batch
from scapy.all import IP, UDP, Raw
import json

def test_model_failure_degrades_gracefully():
    # Mock packets
    ike_pkt = IP(dst="1.1.1.1")/UDP(sport=500, dport=500)/Raw(b"IKEv2_SA_INIT")
    esp_pkt = IP(dst="1.1.1.1", proto=50)/Raw(b"encrypted_data" * 10)
    
    # Mock ML Engine to raise an exception or simulate unavailable
    with patch('backend.services.ml_engine.ML_AVAILABLE', False):
        with patch('backend.services.ml_engine._model', None):
            # Run batch analysis
            findings = _analyze_batch([ike_pkt], [esp_pkt])
            
            # Should still return IKE and ESP features
            assert "ike" in findings
            assert "esp_features" in findings
            
            # Rules should still operate
            assert "security_rules" in findings
            
            # ML should degrade to UNKNOWN/RULES ONLY
            assert "ml" in findings
            assert findings["ml"]["traffic_type"] == "unknown"
            assert findings["ml"]["confidence"] == 0.0
            assert "ML model not loaded" in findings["ml"]["note"]
