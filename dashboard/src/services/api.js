const API_BASE = "http://127.0.0.1:8002";


async function request(url, options = {}) {
  const response = await fetch(url, options);

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;

    try {
      const data = await response.json();

      message =
        data.detail ||
        data.message ||
        message;
    } catch {
      // Keep default message
    }

    throw new Error(message);
  }

  return response.json();
}


// ============================================================
// LIVE ANALYSIS
// ============================================================

export async function startLiveAnalysis() {
  return request(
    `${API_BASE}/api/analysis/start`,
    {
      method: "POST",
    }
  );
}


export async function getAnalysis(analysisId) {
  return request(
    `${API_BASE}/api/analysis/${analysisId}`
  );
}


// ============================================================
// REPLAY ANALYSIS
// ============================================================

export async function startReplayAnalysis(
  captureFile = null
) {
  let url =
    `${API_BASE}/api/replay/start`;

  if (captureFile) {
    url +=
      `?capture_file=${encodeURIComponent(captureFile)}`;
  }

  return request(url, {
    method: "POST",
  });
}


export async function getReplayAnalysis(
  replayId
) {
  return request(
    `${API_BASE}/api/replay/${replayId}`
  );
}


// ============================================================
// REPORTS
// ============================================================

export async function getReports() {
  return request(
    `${API_BASE}/api/reports`
  );
}


export async function getReport(
  analysisId
) {
  return request(
    `${API_BASE}/api/reports/${encodeURIComponent(
      analysisId
    )}`
  );
}


export async function getReportJson(
  analysisId
) {
  return request(
    `${API_BASE}/api/reports/${encodeURIComponent(
      analysisId
    )}/json`
  );
}


export function getReportDownloadUrl(
  analysisId
) {
  return (
    `${API_BASE}/api/reports/` +
    `${encodeURIComponent(analysisId)}/download`
  );
}


export function getReportPdfDownloadUrl(
  analysisId
) {
  return (
    `${API_BASE}/api/reports/` +
    `${encodeURIComponent(analysisId)}/download/pdf`
  );
}


// ============================================================
// WEBSOCKET
// ============================================================

export function getWebSocketUrl(
  analysisId
) {
  return (
    `ws://127.0.0.1:8002/ws/analysis/` +
    `${encodeURIComponent(analysisId)}`
  );
}


export { API_BASE };
