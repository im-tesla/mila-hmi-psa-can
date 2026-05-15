const store = new Map();
const listeners = new Map();

export function updateSignal(canId, signalName, value, ts, raw) {
  const key = `${canId}.${signalName}`;
  const prev = store.get(key);
  store.set(key, { value, ts, raw });
  if (!prev || prev.value !== value) {
    const sigListeners = listeners.get(key);
    if (sigListeners) {
      sigListeners.forEach(fn => fn(value, ts));
    }
  }
}

export function getSignal(canId, signalName) {
  return store.get(`${canId}.${signalName}`);
}

export function getAllSignalsForCanId(canId) {
  const prefix = `${canId}.`;
  const result = [];
  for (const [key, data] of store) {
    if (key.startsWith(prefix)) {
      result.push({ name: key.slice(prefix.length), ...data });
    }
  }
  return result;
}

export function onSignalChange(canId, signalName, callback) {
  const key = `${canId}.${signalName}`;
  if (!listeners.has(key)) listeners.set(key, new Set());
  listeners.get(key).add(callback);
}
