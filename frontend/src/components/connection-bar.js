export function createConnectionBar() {
  const el = document.createElement('div');
  el.id = 'connection-bar';
  el.className = 'flex items-center justify-between h-10 px-4 text-sm font-medium transition-colors duration-300 bg-gray-900 dark:bg-white border-b border-gray-800 dark:border-gray-200';
  el.innerHTML = `
    <div class="flex items-center gap-2">
      <span id="conn-dot" class="w-2.5 h-2.5 rounded-full bg-gray-500"></span>
      <span id="conn-text" class="text-gray-400">Disconnected</span>
    </div>
    <button id="theme-toggle" class="min-h-touch px-3 py-1 rounded-lg bg-gray-800 dark:bg-gray-200 dark:text-gray-800 hover:opacity-80 text-sm">
      🌓
    </button>
  `;
  return el;
}

export function updateConnectionBar(status) {
  const dot = document.getElementById('conn-dot');
  const text = document.getElementById('conn-text');
  if (!dot || !text) return;
  const states = {
    connected:    { color: 'bg-green-500', text: 'Connected', textColor: 'text-green-400' },
    connecting:   { color: 'bg-yellow-500', text: 'Connecting...', textColor: 'text-yellow-400' },
    reconnecting: { color: 'bg-yellow-500', text: 'Reconnecting...', textColor: 'text-yellow-400', pulse: true },
    disconnected: { color: 'bg-red-500', text: 'Disconnected', textColor: 'text-red-400' },
  };
  const s = states[status] || states.disconnected;
  dot.className = `w-2.5 h-2.5 rounded-full ${s.color} ${s.pulse ? 'animate-pulse' : ''}`;
  text.className = s.textColor;
  text.textContent = s.text;
}
