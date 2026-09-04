import {
  Database,
  FileArchive,
  Radio,
  RefreshCw,
  Play,
  Square,
  CheckCircle2,
  AlertTriangle,
  Loader2,
} from "lucide-react";

import { useAnalysis } from "../context/AnalysisContext";


const DEFAULT_CAPTURE =
  "testbed/captures/capture_combined_vpn.pcap";


export default function Captures() {
  const {
    analysis,
    events,
    running,
    error,
    mode,
    startReplay,
    stopAnalysis,
  } = useAnalysis();


  const isReplayRunning =
    running && mode === "REPLAY";


  const replayCompleted =
    analysis?.mode === "REPLAY" &&
    analysis?.status === "COMPLETED";


  const replayResult =
    replayCompleted ? analysis : null;


  async function handleReplay() {
    if (isReplayRunning) {
      stopAnalysis();
      return;
    }

    await startReplay(DEFAULT_CAPTURE);
  }


  function refreshPage() {
    window.location.reload();
  }


  return (
    <div className="application-page">

      {/* =====================================================
          PAGE HEADER
          ===================================================== */}

      <div className="page-heading-row">

        <div>

          <div className="page-kicker">
            TRAFFIC ARTIFACTS
          </div>

          <h2>
            Captures
          </h2>

          <p className="page-description">
            Live traffic and deterministic replay analysis
            sources.
          </p>

        </div>


        <div className="capture-mode">
          <Radio size={14} />
          ANALYSIS ENGINE
        </div>

      </div>


      {/* =====================================================
          CAPTURE SOURCE CARDS
          ===================================================== */}

      <div className="capture-grid">

        {/* LIVE CAPTURE */}

        <CaptureCard
          icon={<Radio size={20} />}
          title="Live Capture"
          status={
            analysis?.mode === "LIVE"
              ? analysis?.status || "ACTIVE"
              : "READY"
          }
          description={
            analysis?.mode === "LIVE"
              ? "Connected to the live analysis engine."
              : "Automatically captured from the active network interface."
          }
        />


        {/* REPLAY CAPTURE */}

        <div className="capture-card replay-card">

          <div className="capture-icon">
            <FileArchive size={20} />
          </div>


          <div className="capture-card-content">

            <div className="capture-card-title-row">

              <strong>
                Replay Capture
              </strong>

              <span className="capture-status">
                {isReplayRunning
                  ? "RUNNING"
                  : replayCompleted
                    ? "COMPLETED"
                    : "AVAILABLE"}
              </span>

            </div>


            <p>
              Run the deterministic SIH test capture
              through the complete analysis pipeline.
            </p>


            <div className="replay-file">

              <FileArchive size={14} />

              <span>
                capture_combined_vpn.pcap
              </span>

            </div>


            <button
              type="button"
              className={
                isReplayRunning
                  ? "app-button danger"
                  : "app-button primary"
              }
              onClick={handleReplay}
              disabled={
                running && !isReplayRunning
              }
            >

              {isReplayRunning ? (
                <>
                  <Square size={15} />
                  STOP REPLAY
                </>
              ) : (
                <>
                  <Play size={15} />
                  RUN REPLAY ANALYSIS
                </>
              )}

            </button>

          </div>

        </div>


        {/* CAPTURE STORE */}

        <CaptureCard
          icon={<Database size={20} />}
          title="Capture Store"
          status="LOCAL"
          description="Analysis artifacts are stored under the backend results directory."
        />

      </div>


      {/* =====================================================
          REPLAY PIPELINE
          ===================================================== */}

      {(isReplayRunning || replayCompleted) && (

        <section className="app-panel">

          <div className="panel-header">

            <div>

              <div className="panel-kicker">
                REPLAY PIPELINE
              </div>

              <h3>
                Analysis Execution
              </h3>

            </div>


            {isReplayRunning ? (
              <Loader2
                size={17}
                className="spin"
              />
            ) : (
              <CheckCircle2 size={17} />
            )}

          </div>


          <div className="pipeline-list">

            <PipelineStage
              label="Capture Validation"
              completed={hasEvent(
                events,
                "CAPTURE_VALID"
              )}
              running={
                isReplayRunning &&
                !hasEvent(
                  events,
                  "CAPTURE_VALID"
                )
              }
            />


            <PipelineStage
              label="AI Protocol Analysis"
              completed={hasEvent(
                events,
                "AI_ANALYSIS_COMPLETED"
              )}
              running={
                isReplayRunning &&
                hasEvent(
                  events,
                  "CAPTURE_VALID"
                ) &&
                !hasEvent(
                  events,
                  "AI_ANALYSIS_COMPLETED"
                )
              }
            />


            <PipelineStage
              label="Security Assessment"
              completed={hasEvent(
                events,
                "SECURITY_ASSESSMENT_COMPLETED"
              )}
              running={
                isReplayRunning &&
                hasEvent(
                  events,
                  "AI_ANALYSIS_COMPLETED"
                ) &&
                !hasEvent(
                  events,
                  "SECURITY_ASSESSMENT_COMPLETED"
                )
              }
            />


            <PipelineStage
              label="Security Report"
              completed={hasEvent(
                events,
                "REPORT_GENERATED"
              )}
              running={
                isReplayRunning &&
                hasEvent(
                  events,
                  "SECURITY_ASSESSMENT_COMPLETED"
                ) &&
                !hasEvent(
                  events,
                  "REPORT_GENERATED"
                )
              }
            />


            <PipelineStage
              label="SHA-256 Integrity"
              completed={hasEvent(
                events,
                "HASH_GENERATED"
              )}
              running={
                isReplayRunning &&
                hasEvent(
                  events,
                  "REPORT_GENERATED"
                ) &&
                !hasEvent(
                  events,
                  "HASH_GENERATED"
                )
              }
            />


            <PipelineStage
              label="Blockchain Verification"
              completed={hasEvent(
                events,
                "BLOCKCHAIN_VERIFIED"
              )}
              running={
                isReplayRunning &&
                hasEvent(
                  events,
                  "HASH_GENERATED"
                ) &&
                !hasEvent(
                  events,
                  "BLOCKCHAIN_VERIFIED"
                )
              }
            />


            <PipelineStage
              label="Analysis Completed"
              completed={hasEvent(
                events,
                "COMPLETED"
              )}
              running={false}
            />

          </div>

        </section>

      )}


      {/* =====================================================
          CURRENT CAPTURE
          ===================================================== */}

      <section className="app-panel">

        <div className="panel-header">

          <div>

            <div className="panel-kicker">
              CURRENT CAPTURE
            </div>

            <h3>
              Traffic Evidence
            </h3>

          </div>


          <button
            type="button"
            className="icon-button"
            title="Refresh capture state"
            onClick={refreshPage}
          >
            <RefreshCw size={17} />
          </button>

        </div>


        <div className="capture-stats">

          <CaptureStat
            label="CAPTURE"
            value={
              replayResult?.capture?.file
                ? "PCAP LOADED"
                : "—"
            }
          />


          <CaptureStat
            label="MODE"
            value={
              replayResult?.mode ||
              analysis?.mode ||
              "—"
            }
          />


          <CaptureStat
            label="IPSEC"
            value={
              replayResult?.ai?.ipsec_detected === true
                ? "DETECTED"
                : replayResult?.ai?.ipsec_detected === false
                  ? "NOT DETECTED"
                  : "—"
            }
          />


          <CaptureStat
            label="STATUS"
            value={
              replayResult?.status ||
              analysis?.status ||
              "—"
            }
          />

        </div>

      </section>


      {/* =====================================================
          FINAL ANALYSIS RESULT
          ===================================================== */}

      {replayResult && (

        <section className="app-panel">

          <div className="panel-header">

            <div>

              <div className="panel-kicker">
                ANALYSIS RESULT
              </div>

              <h3>
                VPN Security Assessment
              </h3>

            </div>


            <CheckCircle2 size={17} />

          </div>


          <div className="result-grid">

            <ResultItem
              label="IPsec"
              value={
                replayResult.ai?.ipsec_detected
                  ? "Detected"
                  : "Not Detected"
              }
            />


            <ResultItem
              label="IKE Version"
              value={
                replayResult.ai?.ike_version ||
                "Unknown"
              }
            />


            <ResultItem
              label="VPN Mode"
              value={
                replayResult.ai?.mode ||
                "Unknown"
              }
            />


            <ResultItem
              label="Traffic Type"
              value={
                replayResult.ai?.traffic_type ||
                "Unknown"
              }
            />


            <ResultItem
              label="AI Confidence"
              value={
                replayResult.ai?.confidence != null
                  ? `${Math.round(
                      replayResult.ai.confidence * 100
                    )}%`
                  : "—"
              }
            />


            <ResultItem
              label="Security Score"
              value={
                replayResult.security?.security_score != null
                  ? `${replayResult.security.security_score}/100`
                  : "—"
              }
            />


            <ResultItem
              label="Risk Level"
              value={
                replayResult.security?.risk_level ||
                "—"
              }
            />


            <ResultItem
              label="Findings"
              value={
                replayResult.security?.findings?.length ??
                0
              }
            />

          </div>


          {/* =================================================
              CRYPTOGRAPHIC INFORMATION
              ================================================= */}

          <div className="result-grid">

            <ResultItem
              label="Encryption"
              value={
                replayResult.ai?.encryption_algorithm ||
                "Unknown"
              }
            />


            <ResultItem
              label="Authentication"
              value={
                replayResult.ai?.authentication_algorithm ||
                "Unknown"
              }
            />


            <ResultItem
              label="Key Exchange"
              value={
                replayResult.ai?.key_exchange_method ||
                "Unknown"
              }
            />

          </div>


          {/* =================================================
              INTEGRITY + BLOCKCHAIN
              ================================================= */}

          <div className="integrity-result">

            <div>

              <span>
                SHA-256
              </span>

              <strong>
                {replayResult.integrity?.report_hash ||
                  "—"}
              </strong>

            </div>


            <div>

              <span>
                BLOCKCHAIN
              </span>

              <strong>
                {replayResult.blockchain?.verified
                  ? "VERIFIED"
                  : replayResult.blockchain?.status ||
                    "—"}
              </strong>

            </div>

          </div>

        </section>

      )}


      {/* =====================================================
          SECURITY FINDINGS
          ===================================================== */}

      {replayResult?.security?.findings?.length > 0 && (

        <section className="app-panel">

          <div className="panel-header">

            <div>

              <div className="panel-kicker">
                SECURITY FINDINGS
              </div>

              <h3>
                Detected Issues
              </h3>

            </div>

            <AlertTriangle size={17} />

          </div>


          <div className="finding-list">

            {replayResult.security.findings.map(
              (finding) => (

                <div
                  className="finding-item"
                  key={finding.rule_id}
                >

                  <div className="finding-header">

                    <strong>
                      {finding.title}
                    </strong>

                    <span>
                      {finding.severity}
                    </span>

                  </div>


                  <p>
                    {finding.description}
                  </p>


                  <small>
                    Rule: {finding.rule_id}
                    {" • "}
                    Impact: {finding.score_impact}
                  </small>

                </div>

              )
            )}

          </div>

        </section>

      )}


      {/* =====================================================
          RECOMMENDATIONS
          ===================================================== */}

      {replayResult?.security?.recommendations?.length > 0 && (

        <section className="app-panel">

          <div className="panel-header">

            <div>

              <div className="panel-kicker">
                RECOMMENDATIONS
              </div>

              <h3>
                Security Improvements
              </h3>

            </div>

          </div>


          <div className="recommendation-list">

            {replayResult.security.recommendations.map(
              (item) => (

                <div
                  className="recommendation-item"
                  key={item.rule_id}
                >

                  <CheckCircle2 size={16} />

                  <div>

                    <strong>
                      {item.rule_id}
                    </strong>

                    <p>
                      {item.recommendation}
                    </p>

                  </div>

                </div>

              )
            )}

          </div>

        </section>

      )}


      {/* =====================================================
          ERROR
          ===================================================== */}

      {error && (

        <section className="error-panel">

          <AlertTriangle size={18} />

          <div>

            <strong>
              Analysis Error
            </strong>

            <p>
              {error}
            </p>

          </div>

        </section>

      )}

    </div>
  );
}


/* ============================================================
   CAPTURE CARD
   ============================================================ */

function CaptureCard({
  icon,
  title,
  status,
  description,
}) {

  return (

    <div className="capture-card">

      <div className="capture-icon">
        {icon}
      </div>


      <div>

        <div className="capture-card-title-row">

          <strong>
            {title}
          </strong>

          <span className="capture-status">
            {status}
          </span>

        </div>


        <p>
          {description}
        </p>

      </div>

    </div>
  );
}


/* ============================================================
   CAPTURE STAT
   ============================================================ */

function CaptureStat({
  label,
  value,
}) {

  return (

    <div className="capture-stat">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


/* ============================================================
   RESULT ITEM
   ============================================================ */

function ResultItem({
  label,
  value,
}) {

  return (

    <div className="result-item">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


/* ============================================================
   PIPELINE STAGE
   ============================================================ */

function PipelineStage({
  label,
  completed,
  running,
}) {

  return (

    <div className="pipeline-stage">

      <div className="pipeline-stage-indicator">

        {completed ? (

          <CheckCircle2 size={16} />

        ) : running ? (

          <Loader2
            size={16}
            className="spin"
          />

        ) : (

          <span className="pipeline-dot" />

        )}

      </div>


      <span>
        {label}
      </span>


      <small>
        {completed
          ? "COMPLETED"
          : running
            ? "RUNNING"
            : "WAITING"}
      </small>

    </div>
  );
}


/* ============================================================
   EVENT HELPER
   ============================================================ */

function hasEvent(
  events,
  eventName,
) {

  return Boolean(
    events?.some(
      (event) =>
        event.event === eventName
    )
  );
}
