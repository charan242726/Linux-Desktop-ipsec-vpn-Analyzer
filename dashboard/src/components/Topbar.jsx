import { Activity } from "lucide-react";

export default function Topbar({ analysis }) {
  return (
    <header className="topbar">

      <div>
        <div className="eyebrow">
          AUTONOMOUS SECURITY ANALYSIS
        </div>

        <h1>
          VPN IPsec Command Center
        </h1>

        <p>
          Detect → Analyze → Assess → Verify
        </p>
      </div>

      <div className="topbar-right">

        {analysis?.analysis_id && (
          <div className="analysis-id">
            <span>ANALYSIS</span>
            <strong>{analysis.analysis_id}</strong>
          </div>
        )}

        <div className="top-status">
          <span className="live-dot" />
          <Activity size={13} />
          SYSTEM ONLINE
        </div>

      </div>

    </header>
  );
}
