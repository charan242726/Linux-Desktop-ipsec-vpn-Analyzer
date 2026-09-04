from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from backend.services.analyzer_service import AnalyzerService

app = FastAPI(
    title="AI-Powered IPsec VPN Analyzer API",
    description="Backend API for predicting IPsec VPN traffic classes and evaluating security risks.",
    version="2.0.0",
)

# Initialize Analyzer Service
analyzer_service = AnalyzerService()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "*" # Broadly allow for Vercel integration
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    session_id: str
    ike_features: Dict[str, Any]
    esp_features: Dict[str, Any]
    xfrm_text: str

@app.post("/api/analyze")
def analyze_session(request: AnalyzeRequest):
    try:
        result = analyzer_service.analyze(
            session_id=request.session_id,
            ike_features=request.ike_features,
            esp_features=request.esp_features,
            xfrm_text=request.xfrm_text
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "name": "AI-Powered IPsec VPN Analyzer",
        "status": "running",
        "version": "2.0.0",
        "model_loaded": analyzer_service.model is not None
    }
    
@app.get("/health")
def health():
    return {"status": "healthy"}
