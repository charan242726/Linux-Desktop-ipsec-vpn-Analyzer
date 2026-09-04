import os
import tempfile
import joblib
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from analyzer.session_analyzer import SessionAnalyzer
from analyzer.models import MLPrediction

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "ml" / "model" / "primary_rf_pipeline.pkl"

class AnalyzerService:
    def __init__(self):
        # Load the ML Model Pipeline (Imputer + RandomForest)
        if MODEL_PATH.exists():
            self.model = joblib.load(MODEL_PATH)
        else:
            self.model = None
            
        # Initialize the Deterministic Rule Engine Analyzer
        self.session_analyzer = SessionAnalyzer()
        
    def analyze(self, session_id: str, ike_features: Dict[str, Any], esp_features: Dict[str, Any], xfrm_text: str) -> Dict[str, Any]:
        """
        Runs the full analysis pipeline:
        1. Predict traffic class using the ML model.
        2. Evaluate security risks using the deterministic rule engine.
        """
        
        # 1. Run ML Prediction
        ml_prediction = None
        if self.model and esp_features:
            try:
                # The model expects a DataFrame with the exact features
                df_features = pd.DataFrame([esp_features])
                predicted_class = self.model.predict(df_features)[0]
                
                # Get probabilities
                probs = self.model.predict_proba(df_features)[0]
                classes = self.model.classes_
                confidence_dict = {str(c): float(p) for c, p in zip(classes, probs)}
                
                # Confidence score of the winning class
                confidence = float(max(probs))
                
                ml_prediction = MLPrediction(
                    predicted_class=str(predicted_class),
                    confidence=confidence
                )
            except Exception as e:
                print(f"ML Prediction failed: {e}")
                pass
                
        # 2. Run Deterministic Rule Engine
        # We need to temporarily write xfrm_text to a file because SessionAnalyzer expects a path
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_xfrm:
            temp_xfrm.write(xfrm_text)
            temp_path = temp_xfrm.name
            
        try:
            # Parse features (pandas-like dictionary access)
            analysis_result = self.session_analyzer.analyze_session(
                session_id=session_id,
                ike_features=ike_features,
                xfrm_txt_path=temp_path,
                ml_prediction=ml_prediction
            )
            
            # Serialize the result to dict
            return analysis_result.to_dict()
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
