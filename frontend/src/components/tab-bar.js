export function createTabBar({ onTabChange }) {
  const el = document.createElement('div');
  el.id = 'tab-bar';
  el.className = 'flex items-center justify-between h-10 px-4 text-xs font-mono bg-card border-b border-base select-none shrink-0';
  el.innerHTML = `
    <div class="flex items-center gap-2 w-32">
      <span id="conn-dot" class="led-dot mute"></span>
      <span id="conn-text" class="text-dim uppercase tracking-wider text-[10px]">OFFLINE</span>
    </div>
    <div class="flex items-center gap-1">
      <button data-tab="dashboard" class="tab-btn active-tab px-3 py-1 text-[10px] uppercase tracking-wider rounded transition-colors">Dashboard</button>
      <button data-tab="debug" class="tab-btn px-3 py-1 text-[10px] uppercase tracking-wider rounded transition-colors">Debug</button>
      <button data-tab="settings" class="tab-btn px-3 py-1 text-[10px] uppercase tracking-wider rounded transition-colors">Settings</button>
    </div>
    <div class="w-32 flex justify-end">
      <button id="theme-toggle" class="min-h-touch px-3 text-dim hover:text-accent transition-colors">
        <svg id="theme-sun" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg id="theme-moon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="hidden">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
    </div>
  `;

  const tabs = el.querySelectorAll('.tab-btn');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active-tab'));
      btn.classList.add('active-tab');
      onTabChange(btn.dataset.tab);
    });
  });

  return el;
}

export function updateTabBarConnection(status) {
  const dot = document.getElementById('conn-dot');
  const text = document.getElementById('conn-text');
  if (!dot || !text) return;
  const states = {
    connected:    { cls: 'ok',         label: 'CONNECTED',    textCls: 'text-ok' },
    connecting:   { cls: 'warn',        label: 'CONNECTING',   textCls: 'text-warn' },
    reconnecting: { cls: 'warn pulse',  label: 'RECONNECTING', textCls: 'text-warn' },
    disconnected: { cls: 'fault',       label: 'OFFLINE',      textCls: 'text-fault' },
  };
  const s = states[status] || states.disconnected;
  dot.className = `led-dot ${s.cls}`;
  text.className = `uppercase tracking-wider text-[10px] ${s.textCls}`;
  text.textContent = s.label;
}
