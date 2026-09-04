import {
  Download,
  ExternalLink,
  FileCheck2,
  FileJson,
  Lock,
  RefreshCw,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";

import { useEffect, useState } from "react";

import {
  getReport,
  getReportDownloadUrl,
  getReportPdfDownloadUrl,
  getReports,
} from "../services/api";

import { useAnalysis } from "../context/AnalysisContext";

export default function Reports() {
  const { analysis } = useAnalysis();

  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedReport, setSelectedReport] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  async function loadReports(showRefresh = false) {
    try {
      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const data = await getReports();

      setReports(
        Array.isArray(data?.reports)
          ? data.reports
          : []
      );
    } catch (err) {
      setError(
        err?.message ||
          "Unable to load saved reports."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadReports();
  }, []);

  async function handleView(analysisId) {
    try {
      setError("");

      const data = await getReport(analysisId);

      setSelectedReport(data);
    } catch (err) {
      setError(
        err?.message ||
          "Unable to open report."
      );
    }
  }

  function handleDownload(analysisId) {
    const url =
      getReportDownloadUrl(analysisId);

    window.open(
      url,
      "_blank",
      "noopener,noreferrer"
    );
  }

  function handlePdfDownload(analysisId) {
    const url =
      getReportPdfDownloadUrl(analysisId);

    window.open(
      url,
      "_blank",
      "noopener,noreferrer"
    );
  }

  const totalReports = reports.length;

  const verifiedReports =
    reports.filter(
      (report) =>
        report.blockchain_verified
    ).length;

  const averageScore =
    totalReports > 0
      ? Math.round(
          reports.reduce(
            (sum, report) =>
              sum +
              Number(
                report.security_score || 0
              ),
            0
          ) / totalReports
        )
      : 0;

  return (
    <div className="application-page">
      <div className="page-kicker">
        REPORT REPOSITORY
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: "20px",
          flexWrap: "wrap",
        }}
      >
        <div>
          <h2>Reports</h2>

          <p className="page-description">
            Persistent security assessment reports,
            integrity records, and verification history.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => loadReports(true)}
          disabled={refreshing}
          type="button"
        >
          <RefreshCw
            size={16}
            className={
              refreshing ? "spin" : ""
            }
          />

          {refreshing
            ? "Refreshing..."
            : "Refresh"}
        </button>
      </div>

      {error && (
        <section
          className="app-panel"
          style={{
            marginBottom: "18px",
          }}
        >
          <div className="panel-kicker">
            REPORT ERROR
          </div>

          <p
            style={{
              margin: "8px 0 0",
            }}
          >
            {error}
          </p>
        </section>
      )}

      <div className="status-grid">
        <SummaryCard
          icon={<FileCheck2 size={19} />}
          label="TOTAL REPORTS"
          value={totalReports}
          detail="Saved on disk"
        />

        <SummaryCard
          icon={<ShieldCheck size={19} />}
          label="BLOCKCHAIN VERIFIED"
          value={verifiedReports}
          detail={
            totalReports
              ? `${Math.round(
                  (verifiedReports /
                    totalReports) *
                    100
                )}% verified`
              : "No reports"
          }
        />

        <SummaryCard
          icon={<Lock size={19} />}
          label="AVERAGE SCORE"
          value={
            totalReports
              ? `${averageScore}/100`
              : "—"
          }
          detail="Across saved reports"
        />
      </div>

      <section className="app-panel">
        <div className="panel-header">
          <div>
            <div className="panel-kicker">
              SAVED REPORT HISTORY
            </div>

            <h3>
              Security Assessments
            </h3>
          </div>

          <FileJson size={18} />
        </div>

        {loading ? (
          <div className="empty-state">
            Loading saved reports...
          </div>
        ) : reports.length === 0 ? (
          <div className="empty-state">
            No completed reports have been saved yet.
          </div>
        ) : (
          <div className="report-history">
            {reports.map((report) => (
              <ReportRow
                key={report.analysis_id}
                report={report}
                onView={handleView}
                onDownload={handleDownload}
                onPdfDownload={handlePdfDownload}
              />
            ))}
          </div>
        )}
      </section>

      {analysis?.status === "COMPLETED" && (
        <section
          className="app-panel"
          style={{
            marginTop: "18px",
          }}
        >
          <div className="panel-kicker">
            CURRENT ANALYSIS
          </div>

          <p
            style={{
              margin: "8px 0 0",
            }}
          >
            The current analysis is complete.
            Refresh the repository to see the
            newly generated report.
          </p>
        </section>
      )}

      {selectedReport && (
        <ReportViewer
          report={selectedReport}
          onClose={() =>
            setSelectedReport(null)
          }
          onDownload={handleDownload}
        />
      )}
    </div>
  );
}

function SummaryCard({
  icon,
  label,
  value,
  detail,
}) {
  return (
    <div className="status-card">
      <div className="status-card-icon">
        {icon}
      </div>

      <div>
        <span>{label}</span>

        <strong>{value}</strong>

        <small>{detail}</small>
      </div>
    </div>
  );
}

function ReportRow({
  report,
  onView,
  onDownload,
  onPdfDownload,
}) {
  const risk =
    String(
      report.risk_level ||
        "UNKNOWN"
    ).toUpperCase();

  const verified =
    Boolean(
      report.blockchain_verified
    );

  const score =
    report.security_score ?? "—";

  return (
    <div className="report-history-row">
      <div className="report-history-main">
        <div className="report-history-icon">
          <FileCheck2 size={18} />
        </div>

        <div
          style={{
            minWidth: 0,
          }}
        >
          <strong
            style={{
              display: "block",
              overflowWrap: "anywhere",
            }}
          >
            {report.report_id ||
              report.analysis_id}
          </strong>

          <span
            style={{
              display: "block",
              marginTop: "4px",
              overflowWrap: "anywhere",
            }}
          >
            {formatDate(
              report.generated_at
            )}
          </span>
        </div>
      </div>

      <div className="report-history-score">
        <strong>{score}</strong>

        <span>SCORE</span>
      </div>

      <div
        className={`report-risk report-risk-${risk.toLowerCase()}`}
      >
        {risk === "HIGH" ||
        risk === "CRITICAL" ? (
          <AlertTriangle size={14} />
        ) : (
          <ShieldCheck size={14} />
        )}

        {risk}
      </div>

      <div className="report-blockchain">
        <span
          className={
            verified
              ? "verified"
              : "unverified"
          }
        >
          {verified
            ? "VERIFIED"
            : "NOT VERIFIED"}
        </span>
      </div>

      <div className="report-actions">
        <button
          type="button"
          className="icon-button"
          title="View report"
          onClick={() =>
            onView(report.analysis_id)
          }
        >
          <ExternalLink size={16} />
        </button>

        <button
          type="button"
          className="icon-button"
          title="Download JSON report"
          onClick={() =>
            onDownload(report.analysis_id)
          }
        >
          <FileJson size={16} />
        </button>

        <button
          type="button"
          className="icon-button"
          title="Download PDF report"
          onClick={() =>
            onPdfDownload(report.analysis_id)
          }
        >
          <Download size={16} />
        </button>
      </div>
    </div>
  );
}

function ReportViewer({
  report,
  onClose,
  onDownload,
  onPdfDownload,
}) {
  const security =
    report.security || {};

  const ai =
    report.ai || {};

  const integrity =
    report.integrity || {};

  const blockchain =
    report.blockchain || {};

  const reportData =
    report.report || {};

  return (
    <div
      className="report-modal-backdrop"
      onClick={onClose}
    >
      <div
        className="report-modal"
        onClick={(event) =>
          event.stopPropagation()
        }
      >
        <div className="panel-header">
          <div>
            <div className="panel-kicker">
              REPORT DETAILS
            </div>

            <h3>
              {reportData.report_id ||
                report.analysis_id}
            </h3>
          </div>

          <button
            type="button"
            className="icon-button"
            onClick={onClose}
            title="Close"
          >
            ×
          </button>
        </div>

        <div className="report-details">
          <ReportField
            label="STATUS"
            value={
              report.status ||
              "COMPLETED"
            }
          />

          <ReportField
            label="SECURITY SCORE"
            value={
              security.security_score ??
              "—"
            }
          />

          <ReportField
            label="RISK LEVEL"
            value={
              security.risk_level ||
              "—"
            }
          />

          <ReportField
            label="IPSEC DETECTED"
            value={
              ai.ipsec_detected
                ? "YES"
                : "NO"
            }
          />

          <ReportField
            label="IKE VERSION"
            value={
              ai.ike_version ||
              "Unknown"
            }
          />

          <ReportField
            label="VPN MODE"
            value={
              ai.mode ||
              "Unknown"
            }
          />

          <ReportField
            label="TRAFFIC TYPE"
            value={
              ai.traffic_type ||
              "Unknown"
            }
          />

          <ReportField
            label="SHA-256"
            value={
              integrity.report_hash ||
              "Not available"
            }
          />

          <ReportField
            label="BLOCKCHAIN"
            value={
              blockchain.verified
                ? "VERIFIED"
                : "NOT VERIFIED"
            }
          />
        </div>

        {security.findings?.length > 0 && (
          <div
            style={{
              marginTop: "20px",
            }}
          >
            <div className="panel-kicker">
              FINDINGS
            </div>

            <div className="report-findings">
              {security.findings.map(
                (finding, index) => (
                  <div
                    className="report-finding"
                    key={
                      finding.rule_id ||
                      finding.id ||
                      index
                    }
                  >
                    <strong>
                      {finding.title ||
                        finding.rule_id ||
                        finding.id ||
                        `Finding ${index + 1}`}
                    </strong>

                    <span>
                      {typeof finding.description ===
                      "string"
                        ? finding.description
                        : typeof finding.message ===
                          "string"
                        ? finding.message
                        : "No description available."}
                    </span>
                  </div>
                )
              )}
            </div>
          </div>
        )}

        {security.recommendations?.length > 0 && (
          <div
            style={{
              marginTop: "20px",
            }}
          >
            <div className="panel-kicker">
              RECOMMENDATIONS
            </div>

            <div className="report-findings">
              {security.recommendations.map(
                (recommendation, index) => {
                  const text =
                    typeof recommendation ===
                    "string"
                      ? recommendation
                      : recommendation?.recommendation ||
                        recommendation?.description ||
                        recommendation?.message ||
                        "No recommendation available.";

                  const ruleId =
                    typeof recommendation ===
                    "object"
                      ? recommendation?.rule_id
                      : null;

                  return (
                    <div
                      className="report-finding"
                      key={
                        ruleId ||
                        index
                      }
                    >
                      <strong>
                        {ruleId ||
                          `Recommendation ${index + 1}`}
                      </strong>

                      <span>
                        {text}
                      </span>
                    </div>
                  );
                }
              )}
            </div>
          </div>
        )}

        <div
          style={{
            display: "flex",
            gap: "10px",
            marginTop: "22px",
            flexWrap: "wrap",
          }}
        >
          <button
            type="button"
            className="primary-button"
            onClick={() =>
              onPdfDownload(
                report.analysis_id
              )
            }
          >
            <Download size={16} />
            Download PDF
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={() =>
              onDownload(
                report.analysis_id
              )
            }
          >
            <FileJson size={16} />
            Download JSON
          </button>

          <button
            type="button"
            className="secondary-button"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function ReportField({
  label,
  value,
}) {
  return (
    <div className="report-field">
      <span>{label}</span>

      <strong
        style={{
          overflowWrap: "anywhere",
          wordBreak: "break-word",
        }}
      >
        {renderSafeValue(value)}
      </strong>
    </div>
  );
}

function renderSafeValue(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }

  if (
    typeof value === "string" ||
    typeof value === "number"
  ) {
    return value;
  }

  if (typeof value === "boolean") {
    return value ? "YES" : "NO";
  }

  if (Array.isArray(value)) {
    return value
      .map((item) =>
        typeof item === "string"
          ? item
          : JSON.stringify(item)
      )
      .join(", ");
  }

  return JSON.stringify(value);
}

function formatDate(value) {
  if (!value) {
    return "Date unavailable";
  }

  try {
    return new Date(
      value
    ).toLocaleString();
  } catch {
    return value;
  }
}
