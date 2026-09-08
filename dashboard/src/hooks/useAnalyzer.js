import { useState, useEffect, useCallback } from 'react';

const API_BASE = 'http://localhost:8000';

export function useAnalyzer() {
  const [engineState, setEngineState] = useState('IDLE');
  const [findings, setFindings] = useState(null);
  const [error, setError] = useState(null);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/status`);
      if (!res.ok) throw new Error('Status endpoint failed');
      const data = await res.json();
      setEngineState(data.state);
    } catch (err) {
      console.error("Failed to fetch status:", err);
      // Don't override state if backend temporarily disconnected
    }
  }, []);

  const fetchFindings = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/sessions/current`);
      if (res.ok) {
        const data = await res.json();
        setFindings(data.findings);
      }
    } catch (err) {
      console.error("Failed to fetch findings:", err);
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    fetchStatus();

    // Poll status every 2 seconds
    const statusInterval = setInterval(fetchStatus, 2000);

    return () => clearInterval(statusInterval);
  }, [fetchStatus]);

  useEffect(() => {
    // Poll findings only when analyzing
    if (engineState === 'ANALYZING') {
      fetchFindings();
      const findingsInterval = setInterval(fetchFindings, 2000);
      return () => clearInterval(findingsInterval);
    }
  }, [engineState, fetchFindings]);

  const startAnalysis = async () => {
    try {
      setError(null);
      const res = await fetch(`${API_BASE}/sessions`, { method: 'POST' });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to start analysis');
      }
      // Force an immediate status update
      fetchStatus();
    } catch (err) {
      setError(err.message);
    }
  };

  return {
    engineState,
    findings,
    startAnalysis,
    error
  };
}
