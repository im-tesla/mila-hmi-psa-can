const WS_URL = `ws://${window.location.hostname}:8765/ws`;

export function createWsClient({ onMessage, onStatusChange }) {
  let ws = null;
  let reconnectTimer = null;
  let backoff = 1000;

  function connect() {
    if (ws) { ws.close(); }
    onStatusChange('connecting');
    try {
      ws = new WebSocket(WS_URL);
    } catch (e) {
      scheduleReconnect();
      return;
    }

    ws.onopen = () => {
      backoff = 1000;
      onStatusChange('connected');
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        onMessage(msg);
      } catch (e) {
        console.warn('Failed to parse WebSocket message:', e);
      }
    };

    ws.onclose = () => {
      ws = null;
      onStatusChange('disconnected');
      scheduleReconnect();
    };

    ws.onerror = () => { ws?.close(); };
  }

  function scheduleReconnect() {
    if (reconnectTimer) return;
    onStatusChange('reconnecting');
    reconnectTimer = setTimeout(() => {
      reconnectTimer = null;
      connect();
    }, backoff);
    backoff = Math.min(backoff * 2, 30000);
  }

  function disconnect() {
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
    if (ws) { ws.close(); ws = null; }
  }

  return { connect, disconnect };
}
