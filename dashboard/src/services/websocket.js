import { getWebSocketUrl } from "./api";

export function connectAnalysisStream(
  analysisId,
  {
    onEvent,
    onStatus,
    onCompleted,
    onError,
  } = {}
) {
  const socket = new WebSocket(
    getWebSocketUrl(analysisId)
  );

  socket.onmessage = (message) => {
    try {
      const payload = JSON.parse(message.data);

      switch (payload.type) {
        case "event":
          onEvent?.(payload.event);
          break;

        case "status":
          onStatus?.(payload.status);
          break;

        case "completed":
          onCompleted?.(payload);
          socket.close();
          break;

        case "error":
          onError?.(payload.message);
          break;

        default:
          break;
      }
    } catch (error) {
      onError?.("Invalid WebSocket message received.");
    }
  };

  socket.onerror = () => {
    onError?.("Unable to connect to analysis stream.");
  };

  return {
    socket,
    close: () => socket.close(),
  };
}
