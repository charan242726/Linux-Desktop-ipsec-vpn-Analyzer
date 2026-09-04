from typing import List, Tuple
from analyzer.models import IkeMetadata, XfrmMetadata, Finding, Severity
from rules.security_rules import get_all_rules

class RiskEngine:
    def __init__(self):
        self.rules = get_all_rules()
        self.severity_penalties = {
            Severity.CRITICAL: 40,
            Severity.HIGH: 20,
            Severity.MEDIUM: 10,
            Severity.LOW: 5,
            Severity.INFO: 0
        }

    def evaluate(self, ike: IkeMetadata, xfrm: XfrmMetadata) -> Tuple[List[Finding], int, str]:
        findings = []
        for rule in self.rules:
            finding = rule.evaluate(ike, xfrm)
            if finding:
                findings.append(finding)
        
        # Calculate risk score deterministically
        score = 100
        for f in findings:
            score -= self.severity_penalties.get(f.severity, 0)
            
        # Floor at 0
        score = max(0, score)
        
        # Map to explicit category
        if score == 100:
            category = "SECURE"
        elif score >= 90:
            category = "LOW RISK"
        elif score >= 70:
            category = "MEDIUM RISK"
        elif score >= 40:
            category = "HIGH RISK"
        else:
            category = "CRITICAL RISK"
            
        return findings, score, category
