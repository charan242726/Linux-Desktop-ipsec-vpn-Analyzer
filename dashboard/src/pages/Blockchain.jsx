import {
  Blocks,
  CheckCircle2,
  Fingerprint,
  ShieldCheck,
} from "lucide-react";

import { useAnalysis } from "../context/AnalysisContext";

export default function Blockchain() {
  const {
    analysis,
    running,
    mode,
    error,
  } = useAnalysis();

  const blockchain =
    analysis?.blockchain;

  const verified =
    blockchain?.verified === true;

  const status =
    analysis?.status ||
    (running ? "RUNNING" : "IDLE");

  return (
    <div className="application-page">

      <div className="page-kicker">
        INTEGRITY LAYER
      </div>

      <h2>Blockchain Verification</h2>

      <p className="page-description">
        Independent verification of report integrity using the registry contract.
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

      <div className="blockchain-hero">

        <div className="chain-icon">
          <Blocks size={30} />
        </div>

        <div>

          <span>VERIFICATION STATUS</span>

          <strong>
            {verified
              ? "VERIFIED"
              : blockchain
                ? "REGISTERED"
                : running
                  ? "PROCESSING"
                  : "PENDING"}
          </strong>

          <p>
            {verified
              ? "The locally generated report hash matches the blockchain record."
              : blockchain
                ? "A blockchain record exists, but completed verification is not available."
                : running
                  ? "The current analysis is still processing its integrity record."
                  : "No completed blockchain verification is available for the current analysis."}
          </p>

        </div>

      </div>

      <section className="app-panel">

        <div className="panel-header">

          <div>
            <div className="panel-kicker">
              REGISTRY RECORD
            </div>

            <h3>Integrity Evidence</h3>
          </div>

          <ShieldCheck size={18} />

        </div>

        <div className="chain-details">

          <ChainField
            label="REPORT ID"
            value={
              blockchain?.report_id ||
              analysis?.report?.report_id ||
              "—"
            }
          />

          <ChainField
            label="LOCAL HASH"
            value={
              blockchain?.local_hash ||
              analysis?.integrity?.sha256 ||
              analysis?.sha256 ||
              "—"
            }
            mono
          />

          <ChainField
            label="BLOCKCHAIN HASH"
            value={
              blockchain?.blockchain_hash ||
              "—"
            }
            mono
          />

          <ChainField
            label="CONTRACT"
            value={
              blockchain?.contract_address ||
              "—"
            }
            mono
          />

          <ChainField
            label="REGISTERED BY"
            value={
              blockchain?.registered_by ||
              "—"
            }
            mono
          />

          <ChainField
            label="VERIFICATION"
            value={
              verified
                ? "HASH MATCH"
                : blockchain
                  ? "REGISTERED"
                  : "—"
            }
          />

        </div>

      </section>

      <section className="app-panel">

        <div className="panel-header">

          <div>
            <div className="panel-kicker">
              ANALYSIS CONTEXT
            </div>

            <h3>Current Record</h3>
          </div>

          <Fingerprint size={18} />

        </div>

        <div className="chain-details">

          <ChainField
            label="ANALYSIS ID"
            value={
              analysis?.analysis_id ||
              "—"
            }
          />

          <ChainField
            label="MODE"
            value={
              mode ||
              analysis?.mode ||
              "—"
            }
          />

          <ChainField
            label="STATUS"
            value={status}
          />

          <ChainField
            label="INTEGRITY"
            value={
              analysis?.integrity
                ? "AVAILABLE"
                : "PENDING"
            }
          />

        </div>

      </section>

    </div>
  );
}

function ChainField({ label, value, mono }) {
  return (
    <div className="chain-field">

      <span>{label}</span>

      <strong className={mono ? "mono" : ""}>
        {value}
      </strong>

      {label === "VERIFICATION" &&
        value === "HASH MATCH" && (
          <CheckCircle2 size={16} />
        )}

      {label === "REPORT ID" && (
        <Fingerprint size={15} />
      )}

    </div>
  );
}
