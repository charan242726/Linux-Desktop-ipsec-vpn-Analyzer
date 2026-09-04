import {
  createContext,
  useContext,
  useRef,
  useState,
} from "react";

import {
  startLiveAnalysis,
  startReplayAnalysis,
  getReplayAnalysis,
} from "../services/api";

import {
  connectAnalysisStream,
} from "../services/websocket";

const AnalysisContext = createContext(null);

export function AnalysisProvider({ children }) {
  const [analysis, setAnalysis] = useState(null);
  const [events, setEvents] = useState([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState(null);

  const streamRef = useRef(null);
  const replayTimerRef = useRef(null);
  const operationRef = useRef(0);

  function cleanupStream() {
    streamRef.current?.close();
    streamRef.current = null;
  }

  function cleanupReplayTimer() {
    if (replayTimerRef.current) {
      clearInterval(replayTimerRef.current);
      replayTimerRef.current = null;
    }
  }

  function cleanupActiveOperation() {
    cleanupStream();
    cleanupReplayTimer();
  }

  // ==========================================================
  // LIVE ANALYSIS
  // ==========================================================

  async function startAnalysis() {
    if (running) return;

    cleanupActiveOperation();

    const operationId = ++operationRef.current;

    setRunning(true);
    setError(null);
    setEvents([]);
    setMode("LIVE");

    try {
      const response = await startLiveAnalysis();

      if (operationId !== operationRef.current) {
        return;
      }

      setAnalysis({
        analysis_id: response.analysis_id,
        status: response.status || "STARTING",
        mode: "LIVE",
      });

      streamRef.current = connectAnalysisStream(
        response.analysis_id,
        {
          onEvent(event) {
            if (operationId !== operationRef.current) {
              return;
            }

            setEvents((previous) => [
              ...previous,
              event,
            ]);

            setAnalysis((previous) => ({
              ...(previous || {}),
              status: event.event,
              mode: "LIVE",
            }));
          },

          onStatus(status) {
            if (operationId !== operationRef.current) {
              return;
            }

            setAnalysis((previous) => ({
              ...(previous || {}),
              status,
              mode: "LIVE",
            }));
          },

          onCompleted(payload) {
            if (operationId !== operationRef.current) {
              return;
            }

            cleanupStream();

            const finalResult =
              payload?.result || payload || {};

            setAnalysis({
              ...finalResult,
              mode: "LIVE",
            });

            if (Array.isArray(finalResult.events)) {
              setEvents(finalResult.events);
            }

            setRunning(false);
          },

          onError(message) {
            if (operationId !== operationRef.current) {
              return;
            }

            cleanupStream();

            setError(
              message ||
              "Live analysis failed."
            );

            setAnalysis((previous) => ({
              ...(previous || {}),
              status: "FAILED",
              mode: "LIVE",
            }));

            setRunning(false);
          },
        }
      );
    } catch (error) {
      if (operationId !== operationRef.current) {
        return;
      }

      cleanupStream();

      setError(
        error?.message ||
        "Unable to start live analysis."
      );

      setAnalysis((previous) => ({
        ...(previous || {}),
        status: "FAILED",
        mode: "LIVE",
      }));

      setRunning(false);
    }
  }

  // ==========================================================
  // REPLAY ANALYSIS
  // ==========================================================

  async function startReplay(captureFile = null) {
    if (running) return;

    cleanupActiveOperation();

    const operationId = ++operationRef.current;

    setRunning(true);
    setError(null);
    setEvents([]);
    setMode("REPLAY");

    try {
      const response =
        await startReplayAnalysis(captureFile);

      if (operationId !== operationRef.current) {
        return;
      }

      const replayId =
        response.replay_id;

      setAnalysis({
        analysis_id: replayId,
        replay_id: replayId,
        status: response.status || "RUNNING",
        mode: "REPLAY",
        capture_file: response.capture_file,
      });

      let finished = false;

      const pollReplay = async () => {
        if (
          finished ||
          operationId !== operationRef.current
        ) {
          cleanupReplayTimer();
          return;
        }

        try {
          const result =
            await getReplayAnalysis(replayId);

          if (
            operationId !== operationRef.current
          ) {
            cleanupReplayTimer();
            return;
          }

          if (result.status === "COMPLETED") {
            finished = true;
            cleanupReplayTimer();

            const finalResult =
              result.result || {};

            setAnalysis({
              ...finalResult,
              analysis_id:
                finalResult.analysis_id ||
                replayId,
              mode: "REPLAY",
              status: "COMPLETED",
            });

            if (Array.isArray(finalResult.events)) {
              setEvents(finalResult.events);
            }

            setRunning(false);
            return;
          }

          if (result.status === "FAILED") {
            finished = true;
            cleanupReplayTimer();

            setError(
              result.error ||
              "Replay analysis failed."
            );

            setAnalysis((previous) => ({
              ...(previous || {}),
              analysis_id: replayId,
              mode: "REPLAY",
              status: "FAILED",
            }));

            setRunning(false);
            return;
          }

          setAnalysis((previous) => ({
            ...(previous || {}),
            analysis_id: replayId,
            mode: "REPLAY",
            status: result.status || "RUNNING",
          }));
        } catch (error) {
          if (
            operationId !== operationRef.current
          ) {
            return;
          }

          finished = true;
          cleanupReplayTimer();

          setError(
            error?.message ||
            "Unable to retrieve replay analysis."
          );

          setAnalysis((previous) => ({
            ...(previous || {}),
            analysis_id: replayId,
            mode: "REPLAY",
            status: "FAILED",
          }));

          setRunning(false);
        }
      };

      await pollReplay();

      if (
        !finished &&
        operationId === operationRef.current
      ) {
        replayTimerRef.current =
          setInterval(pollReplay, 1000);
      }
    } catch (error) {
      if (operationId !== operationRef.current) {
        return;
      }

      cleanupReplayTimer();

      setError(
        error?.message ||
        "Unable to start replay analysis."
      );

      setAnalysis((previous) => ({
        ...(previous || {}),
        status: "FAILED",
        mode: "REPLAY",
      }));

      setRunning(false);
    }
  }

  // ==========================================================
  // STOP
  // ==========================================================

  function stopAnalysis() {
    ++operationRef.current;

    cleanupActiveOperation();

    setRunning(false);

    setAnalysis((previous) => {
      if (!previous) {
        return {
          status: "STOPPED",
          mode: mode || null,
        };
      }

      return {
        ...previous,
        status: "STOPPED",
      };
    });
  }

  // ==========================================================
  // CLEAR
  // ==========================================================

  function clearAnalysis() {
    ++operationRef.current;

    cleanupActiveOperation();

    setAnalysis(null);
    setEvents([]);
    setError(null);
    setRunning(false);
    setMode(null);
  }

  return (
    <AnalysisContext.Provider
      value={{
        analysis,
        setAnalysis,
        events,
        running,
        error,
        mode,
        startAnalysis,
        startReplay,
        stopAnalysis,
        clearAnalysis,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  const context =
    useContext(AnalysisContext);

  if (!context) {
    throw new Error(
      "useAnalysis must be used inside AnalysisProvider"
    );
  }

  return context;
}
