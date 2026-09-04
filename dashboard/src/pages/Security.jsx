import {
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
} from "lucide-react";

import { useAnalysis } from "../context/AnalysisContext";

export default function Security() {
  const {
    analysis,
    running,
    mode,
    error,
  } = useAnalysis();

  const security = analysis?.security;

  const score =
    security?.security_score;

  const findings =
    Array.isArray(security?.findings)
      ? security.findings
      : [];

  const recommendations =
    Array.isArray(security?.recommendations)
      ? security.recommendations
      : [];

  const riskLevel =
    security?.risk_level || "—";

  const status =
    analysis?.status ||
    (running ? "RUNNING" : "IDLE");

  return (
    <div className="application-page">

      <div className="page-kicker">
        RISK ENGINE
      </div>

      <h2>Security Assessment</h2>

      <p className="page-description">
        Evidence-based security posture derived from the analysis engine.
      </p>

      {error && (
        <section
          className="app-panel"
          style={{ marginBottom: "18px" }}
        >
          <div className="panel-kicker">
            ANALYSIS ERROR
          </div>

          <p style={{ margin: "8px 0 0" }}>
            {error}
          </p>
        </section>
      )}

      <div className="security-summary">

        <div className="score-card">

          <span>SECURITY SCORE</span>

          <strong>
            {score !== undefined
              ? score
              : "—"}
          </strong>

          <small>/ 100</small>

        </div>

        <div className="risk-card">

          <ShieldAlert size={22} />

          <div>
            <span>RISK LEVEL</span>

            <strong>
              {riskLevel}
            </strong>
          </div>

        </div>

        <div className="risk-card">

          <AlertTriangle size={22} />

          <div>
            <span>FINDINGS</span>

            <strong>
              {findings.length}
            </strong>
          </div>

        </div>

      </div>

      <section className="app-panel">

        <div className="panel-header">

          <div>
            <div className="panel-kicker">
              SECURITY FINDINGS
            </div>

            <h3>Detected Risks</h3>
          </div>

          <ShieldAlert size={18} />

        </div>

        <div className="finding-list">

          {findings.length === 0 ? (

            <div className="empty-result">

              {running
                ? `Security assessment is still running (${mode || "ANALYSIS"} mode).`
                : analysis
                  ? "No security findings were returned by the assessment engine."
                  : "No analysis available yet. Start a live or replay analysis to generate a security assessment."}

            </div>

          ) : (

            findings.map((finding, index) => (

              <div
                className="finding"
                key={
                  finding.rule_id ||
                  finding.id ||
                  index
                }
              >

                <div className="finding-icon">
                  <AlertTriangle size={17} />
                </div>

                <div>
                  <strong>
                    {finding.rule_id ||
                      finding.id ||
                      "Security Finding"}
                  </strong>

                  <span>
                    {finding.description ||
                      finding.message ||
                      "Security condition identified by the assessment engine."}
                  </span>
                </div>

                <em>
                  {finding.severity || "UNKNOWN"}
                </em>

              </div>

            ))

          )}

        </div>

      </section>

      <section className="app-panel">

        <div className="panel-header">

          <div>
            <div className="panel-kicker">
              REMEDIATION
            </div>

            <h3>Recommendations</h3>
          </div>

          <CheckCircle2 size={18} />

        </div>

        <div className="recommendation-list">

          {recommendations.length === 0 ? (

            <div className="empty-result">

              {analysis
                ? "No recommendations were returned by the assessment engine."
                : "Recommendations will appear after assessment."}

            </div>

          ) : (

            recommendations.map((item, index) => (

              <div
                className="recommendation"
                key={index}
              >

                <span>
                  {index + 1}
                </span>

                <p>
                  {typeof item === "string"
                    ? item
                    : item?.description ||
                      item?.recommendation ||
                      item?.message ||
                      JSON.stringify(item)}
                </p>

              </div>

            ))

          )}

        </div>

      </section>

      <section className="app-panel">

        <div className="panel-header">

          <div>
            <div className="panel-kicker">
              ANALYSIS CONTEXT
            </div>

            <h3>Assessment Metadata</h3>
          </div>

          <CheckCircle2 size={18} />

        </div>

        <div className="evidence-grid">

          <div className="evidence-item">
            <span>MODE</span>
            <strong>
              {mode || analysis?.mode || "—"}
            </strong>
          </div>

          <div className="evidence-item">
            <span>STATUS</span>
            <strong>
              {status}
            </strong>
          </div>

          <div className="evidence-item">
            <span>ANALYSIS ID</span>
            <strong>
              {analysis?.analysis_id || "—"}
            </strong>
          </div>

          <div className="evidence-item">
            <span>RISK</span>
            <strong>
              {riskLevel}
            </strong>
          </div>

        </div>

      </section>

    </div>
  );
}
