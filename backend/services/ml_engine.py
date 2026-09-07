import logging
import joblib
from backend.config import MODEL_PATH

logger = logging.getLogger(__name__)
ML_AVAILABLE = False
_model = None

def load_model():
    global _model, ML_AVAILABLE
    try:
        _model = joblib.load(MODEL_PATH)
        ML_AVAILABLE = True
        logger.info(f"ML model loaded from {MODEL_PATH}")
    except FileNotFoundError:
        logger.warning(f"Model not found at {MODEL_PATH} — running Rules-Only mode")
        ML_AVAILABLE = False
    except Exception as e:
        logger.error(f"Model load failed: {e} — running Rules-Only mode")
        ML_AVAILABLE = False

def classify_traffic(features: dict) -> dict:
    if not ML_AVAILABLE or _model is None:
        return {
            "traffic_type": "unknown",
            "confidence": 0.0,
            "ml_available": False,
            "note": "ML model not loaded — rules-only mode active"
        }
    try:
        import pandas as pd
        df = pd.DataFrame([features])
        prediction = _model.predict(df)[0]
        confidence = float(max(_model.predict_proba(df)[0]))
        return {
            "traffic_type": prediction,
            "confidence": confidence,
            "ml_available": True
        }
    except Exception as e:
        logger.error(f"ML inference failed: {e}")
        return {
            "traffic_type": "error",
            "confidence": 0.0,
            "ml_available": False,
            "note": str(e)
        }
