from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any

class ObservationStatus(str, Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    UNKNOWN = "unknown"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class Field:
    value: Any
    status: ObservationStatus
    
    @classmethod
    def unknown(cls):
        return cls(value=None, status=ObservationStatus.UNKNOWN)
    
    @classmethod
    def observed(cls, val: Any):
        return cls(value=val, status=ObservationStatus.OBSERVED)
    
    @classmethod
    def inferred(cls, val: Any):
        return cls(value=val, status=ObservationStatus.INFERRED)

@dataclass
class IkeMetadata:
    ike_version: Field = field(default_factory=Field.unknown)
    encryption_algorithm: Field = field(default_factory=Field.unknown)
    encryption_key_length: Field = field(default_factory=Field.unknown)
    integrity_algorithm: Field = field(default_factory=Field.unknown)
    prf_algorithm: Field = field(default_factory=Field.unknown)
    dh_group: Field = field(default_factory=Field.unknown)
    authentication_method: Field = field(default_factory=Field.unknown)

@dataclass
class XfrmMetadata:
    mode: Field = field(default_factory=Field.unknown)
    replay_window: Field = field(default_factory=Field.unknown)

@dataclass
class Finding:
    rule_id: str
    title: str
    severity: Severity
    evidence: str
    explanation: str
    recommendation: str

@dataclass
class MLPrediction:
    predicted_class: str
    confidence: Optional[float] = None

@dataclass
class AnalysisResult:
    session_id: str
    findings: List[Finding] = field(default_factory=list)
    risk_score: int = 100
    risk_category: str = "SECURE"
    ml_prediction: Optional[MLPrediction] = None

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "findings": [f.__dict__ for f in self.findings],
            "risk_score": self.risk_score,
            "risk_category": self.risk_category,
            "ml_prediction": self.ml_prediction.__dict__ if self.ml_prediction else None
        }
