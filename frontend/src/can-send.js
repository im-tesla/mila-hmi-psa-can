let _sendFn = null;

export function initSend(sendFn) {
  _sendFn = sendFn;
}

export function sendCanWrite(canId, signalName, rawValue) {
  if (!_sendFn) return;
  _sendFn(JSON.stringify({ type: 'write', canId, signal: signalName, rawValue }));
}
