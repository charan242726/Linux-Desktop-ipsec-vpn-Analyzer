import {
  Activity,
  Brain,
  Play,
  Radio,
  Square,
} from "lucide-react";

import { useAnalysis } from "../context/AnalysisContext";

const pipeline = [
  "DETECTING_NETWORK",
  "DETECTING_VPN",
  "CAPTURING",
  "ANALYZING",
  "ASSESSING",
  "GENERATING_REPORT",
  "HASHING",
  "BLOCKCHAIN_REGISTERING",
  "BLOCKCHAIN_VERIFIED",
  "COMPLETED",
];

export default function LiveAnalysis() {
  const {
    analysis,
    events,
    running,
    error,
    startAnalysis,
    stopAnalysis,
    mode,
  } = useAnalysis();

  const currentStatus =
    analysis?.status || "IDLE";

  const currentIndex =
    pipeline.indexOf(currentStatus);

  const isLive =
    mode === "LIVE" || !mode;

  function handleAction() {
    if (running) {
      stopAnalysis();
    } else {
      startAnalysis();
    }
  }

  return (
    <div className="application-page">

      <div className="page-heading-row">

        <div>
          <div className="page-kicker">
            ANALYSIS AGENT
          </div>

          <h2>Live Analysis</h2>

          <p className="page-description">
            Autonomous network inspection and IPsec security analysis.
          </p>
        </div>

        <button
          className={`agent-action ${
            running ? "stop" : ""
          }`}
          onClick={handleAction}
          disabled={!isLive && !running}
        >
          {running ? (
            <>
              <Square size={15} />
              STOP ANALYSIS
            </>
          ) : (
            <>
              <Play size={15} />
              START LIVE ANALYSIS
            </>
          )}
        </button>

      </div>

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

      <div className="live-layout">

        <section className="app-panel">

          <div className="panel-header">

            <div>
              <div className="panel-kicker">
                AUTONOMOUS PIPELINE
              </div>

              <h3>Agent Execution</h3>
            </div>

            <div className="agent-state">
              <span
                className={
                  running
                    ? "pulse-dot"
                    : "status-dot"
                }
              />

              {currentStatus}
            </div>

          </div>

          <div className="agent-pipeline">

            {pipeline.map((stage, index) => {

              let state = "pending";

              if (
                currentIndex > index ||
                currentStatus === "COMPLETED"
              ) {
                state = "complete";
              }

              if (currentIndex === index) {
                state = "active";
              }

              return (
                <div
                  className={`agent-stage ${state}`}
                  key={stage}
                >

                  <div className="stage-marker">
                    {state === "complete"
                      ? "✓"
                      : index + 1}
                  </div>

                  <div>
                    <strong>
                      {formatStage(stage)}
                    </strong>

                    <span>
                      {stage}
                    </span>
                  </div>

                  {state === "active" && (
                    <small>
                      PROCESSING
                    </small>
                  )}

                </div>
              );
            })}

          </div>

        </section>

        <section className="app-panel">

          <div className="panel-header">

            <div>
              <div className="panel-kicker">
                LIVE EVIDENCE
              </div>

              <h3>Network Signals</h3>
            </div>

            <Radio size={18} />

          </div>

          <div className="signal-list">

            <Signal
              label="Interface"
              value={
                analysis?.network?.routes?.[0]
                  ?.match(/dev (\S+)/)?.[1] ||
                "—"
              }
            />

            <Signal
              label="IKE / UDP 500"
              value={
                analysis?.ipsec?.evidence?.ike_udp_500 ??
                "—"
              }
            />

            <Signal
              label="NAT-T / UDP 4500"
              value={
                analysis?.ipsec?.evidence?.ike_nat_t_udp_4500 ??
                "—"
              }
            />

            <Signal
              label="ESP"
              value={
                analysis?.ipsec?.evidence?.esp_packets ??
                "—"
              }
            />

            <Signal
              label="AH"
              value={
                analysis?.ipsec?.evidence?.ah_packets ??
                "—"
              }
            />

            <Signal
              label="Confidence"
              value={
                analysis?.ipsec?.confidence !== undefined
                  ? `${Math.round(
                      analysis.ipsec.confidence * 100
                    )}%`
                  : "—"
              }
            />

          </div>

        </section>

      </div>

      <section className="app-panel activity-console">

        <div className="panel-header">

          <div>
            <div className="panel-kicker">
              AGENT ACTIVITY
            </div>

            <h3>Execution Stream</h3>
          </div>

          <Brain size={18} />

        </div>

        <div className="console">

          {events.length === 0 ? (

            <div className="console-empty">
              <Activity size={22} />

              <span>
                {running
                  ? "Connecting to analysis agent..."
                  : "Agent waiting for command."}
              </span>
            </div>

          ) : (

            events.map((event, index) => (

              <div
                className="console-event"
                key={`${event.timestamp || "event"}-${index}`}
              >

                <span className="console-time">
                  {event.timestamp
                    ? new Date(
                        event.timestamp
                      ).toLocaleTimeString()
                    : "--:--:--"}
                </span>

                <strong>
                  {event.event}
                </strong>

                <span>
                  {event.message}
                </span>

              </div>

            ))

          )}

        </div>

      </section>

    </div>
  );
}

function Signal({ label, value }) {
  return (
    <div className="signal">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function formatStage(stage) {
  return stage
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
