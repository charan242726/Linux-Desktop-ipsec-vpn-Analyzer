import os
import re
from typing import Dict, Any, Optional
import pandas as pd

from analyzer.models import IkeMetadata, XfrmMetadata, Field, AnalysisResult, MLPrediction, ObservationStatus
from rules.risk_engine import RiskEngine

class SessionAnalyzer:
    def __init__(self):
        self.risk_engine = RiskEngine()

    def parse_xfrm_metadata(self, xfrm_txt_path: str) -> XfrmMetadata:
        metadata = XfrmMetadata()
        if not os.path.exists(xfrm_txt_path):
            return metadata
            
        with open(xfrm_txt_path, 'r') as f:
            content = f.read()
            
        # Extract mode (tunnel or transport)
        mode_match = re.search(r'mode (\w+)', content)
        if mode_match:
            metadata.mode = Field.observed(mode_match.group(1))
            
        # Extract maximum inbound replay-window (outbound is normally 0)
        replay_matches = re.findall(r'replay-window (\d+)', content)
        if replay_matches:
            max_window = max(int(w) for w in replay_matches)
            metadata.replay_window = Field.observed(str(max_window))
            
        return metadata

    def parse_ike_metadata(self, row: pd.Series) -> IkeMetadata:
        metadata = IkeMetadata()
        
        def get_val(key):
            if key not in row:
                return None
            val = row.get(key)
            if pd.isna(val) or val == 'MISSING' or str(val).strip() == '':
                return None
            # Standardize numeric strings ending in .0
            if isinstance(val, float) and val.is_integer():
                val = int(val)
            return str(val).replace('.0', '')
            
        if (v := get_val('ike_version')) is not None:
            metadata.ike_version = Field.observed(v)
        if (v := get_val('encryption_algorithm')) is not None:
            metadata.encryption_algorithm = Field.observed(v)
        if (v := get_val('encryption_key_length')) is not None:
            metadata.encryption_key_length = Field.observed(v)
        if (v := get_val('integrity_algorithm')) is not None:
            metadata.integrity_algorithm = Field.observed(v)
        if (v := get_val('prf_algorithm')) is not None:
            metadata.prf_algorithm = Field.observed(v)
        if (v := get_val('dh_group')) is not None:
            metadata.dh_group = Field.observed(v)
            
        return metadata

    def analyze_session(
        self, 
        session_id: str, 
        ike_features: pd.Series, 
        xfrm_txt_path: str, 
        ml_prediction: Optional[MLPrediction] = None
    ) -> AnalysisResult:
        ike_meta = self.parse_ike_metadata(ike_features)
        xfrm_meta = self.parse_xfrm_metadata(xfrm_txt_path)
        
        findings, score, category = self.risk_engine.evaluate(ike_meta, xfrm_meta)
        
        return AnalysisResult(
            session_id=session_id,
            findings=findings,
            risk_score=score,
            risk_category=category,
            ml_prediction=ml_prediction
        )
