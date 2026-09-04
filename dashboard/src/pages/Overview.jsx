import {
  Activity,
  Brain,
  FileCheck2,
  LockKeyhole,
  Radio,
  Shield,
  Blocks,
} from "lucide-react";

import StatusCard from "../components/StatusCard";
import { useAnalysis } from "../context/AnalysisContext";

export default function Overview() {
  const { analysis, running, mode, error } = useAnalysis();

  const vpnDetected =
    analysis?.ipsec?.ipsec_detected === true;

  const securityScore =
    analysis?.security?.security_score;

  const aiConfidence =
    analysis?.ai?.confidence;

  const risk =
    analysis?.security?.risk_level;

  const status =
    analysis?.status || (running ? "RUNNING" : "IDLE");

  const analysisMode =
    mode || analysis?.mode || "—";

  return (
    <div className="application-page">

      <div className="page-heading-row">

        <div>
          <div className="page-kicker">
            COMMAND CENTER
          </div>

          <h2>System Overview</h2>

          <p className="page-description">
            Real-time operational state of the VPN security analysis engine.
          </p>
        </div>

        <div className="workspace-state">
          <span className="status-dot" />
          {status}
        </div>

      </div>

      {error && (
        <section className="app-panel" style={{ marginBottom: "18px" }}>
          <div className="panel-kicker">
            SYSTEM ALERT
          </div>

          <p style={{ margin: "8px 0 0" }}>
            {error}
          </p>
        </section>
      )}

      <div className="status-grid">

        <StatusCard
          label="VPN STATUS"
          value={vpnDetected ? "DETECTED" : "NOT DETECTED"}
          detail={
            vpnDetected
              ? "IPsec evidence observed"
              : analysis
                ? "No IPsec evidence detected"
                : "Awaiting analysis"
          }
          icon={<Shield size={18} />}
          tone={vpnDetected ? "success" : "warning"}
        />

        <StatusCard
          label="ANALYSIS STATE"
          value={status}
          detail={`${analysisMode} analysis`}
          icon={<Activity size={18} />}
        />

        <StatusCard
          label="AI CONFIDENCE"
          value={
            aiConfidence !== undefined
              ? `${Math.round(aiConfidence * 100)}%`
              : "—"
          }
          detail="Model confidence"
          icon={<Brain size={18} />}
        />

        <StatusCard
          label="SECURITY SCORE"
          value={
            securityScore !== undefined
              ? `${securityScore}/100`
              : "—"
          }
          detail={
            risk
              ? `Risk: ${risk}`
              : "Assessment unavailable"
          }
          icon={<LockKeyhole size={18} />}
        />

      </div>

      <div className="overview-grid">

        <section className="app-panel">

          <div className="panel-header">

            <div>
              <div className="panel-kicker">
                ANALYSIS AGENT
              </div>

              <h3>Current Operation</h3>
            </div>

            <Radio size={18} />

          </div>

          <div className="agent-body">

            <div className="agent-orb">
              <Activity size={30} />
            </div>

            <div className="agent-info">

              <strong>
                {analysis
                  ? "VPN Security Analysis"
                  : "Analysis Agent Ready"}
              </strong>

              <span>
                {analysis?.analysis_id ||
                  "No active analysis"}
              </span>

              <p>
                {analysis
                  ? `Current state: ${analysis.status}`
                  : "The analysis orchestrator is ready to inspect network traffic."}
              </p>

            </div>

          </div>

        </section>

        <section className="app-panel">

          <div className="panel-header">

            <div>
              <div className="panel-kicker">
                OBSERVED EVIDENCE
              </div>

              <h3>Network Signals</h3>
            </div>

            <Radio size={18} />

          </div>

          <div className="evidence-grid">

            <Evidence
              label="IKE / UDP 500"
              value={
                analysis?.ipsec?.evidence?.ike_udp_500 ?? "—"
              }
            />

            <Evidence
              label="NAT-T / UDP 4500"
              value={
                analysis?.ipsec?.evidence?.ike_nat_t_udp_4500 ?? "—"
              }
            />

            <Evidence
              label="ESP"
              value={
                analysis?.ipsec?.evidence?.esp_packets ?? "—"
              }
            />

            <Evidence
              label="AH"
              value={
                analysis?.ipsec?.evidence?.ah_packets ?? "—"
              }
            />

          </div>

        </section>

      </div>

      <section className="app-panel">

        <div className="panel-header">

          <div>
            <div className="panel-kicker">
              ARTIFACT PIPELINE
            </div>

            <h3>Analysis Outputs</h3>
          </div>

          <FileCheck2 size={18} />

        </div>

        <div className="artifact-grid">

          <Artifact
            icon={<FileCheck2 size={17} />}
            title="Security Report"
            value={
              analysis?.report
                ? "GENERATED"
                : "PENDING"
            }
          />

          <Artifact
            icon={<LockKeyhole size={17} />}
            title="SHA-256 Integrity"
            value={
              analysis?.integrity
                ? "AVAILABLE"
                : "PENDING"
            }
          />

          <Artifact
            icon={<Blocks size={17} />}
            title="Blockchain"
            value={
              analysis?.blockchain
                ? analysis.blockchain.status || "REGISTERED"
                : "PENDING"
            }
          />

          <Artifact
            icon={<Shield size={17} />}
            title="Verification"
            value={
              analysis?.blockchain?.verified
                ? "VERIFIED"
                : "PENDING"
            }
          />

        </div>

      </section>

    </div>
  );
}

function Evidence({ label, value }) {
  return (
    <div className="evidence-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Artifact({ icon, title, value }) {
  return (
    <div className="artifact-item">
      <div className="artifact-icon">
        {icon}
      </div>

      <div>
        <span>{title}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}
