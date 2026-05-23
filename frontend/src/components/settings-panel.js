const BAUDRATES = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600];

export function createSettingsPanel() {
  const el = document.createElement('div');
  el.className = 'p-6 max-w-lg mx-auto';
  el.innerHTML = `
    <h2 class="text-accent font-mono text-sm uppercase tracking-widest mb-6">Connection Settings</h2>

    <div class="bg-card border border-base rounded p-4 mb-3 flex items-center justify-between">
      <div>
        <div class="text-primary text-xs font-mono uppercase tracking-wider">Simulation Mode</div>
        <div class="text-dim text-[10px] font-mono mt-0.5">Generate fake CAN data (no hardware needed)</div>
      </div>
      <label class="relative inline-flex items-center cursor-pointer ml-4">
        <input type="checkbox" id="sim-toggle" class="sr-only peer" />
        <div class="w-10 h-5 bg-raised rounded-full peer
          peer-checked:after:translate-x-5
          after:content-[''] after:absolute after:top-0.5 after:left-0.5
          after:bg-white after:rounded-full after:h-4 after:w-4
          after:transition-all peer-checked:bg-accent border border-base"></div>
      </label>
    </div>

    <div class="bg-card border border-base rounded p-4 mb-3" id="port-section">
      <div class="text-primary text-xs font-mono uppercase tracking-wider mb-3">Serial Port</div>
      <select id="port-select"
        class="w-full bg-raised border border-base rounded px-3 py-2 text-primary font-mono text-xs focus:outline-none focus:border-accent">
        <option value="">Loading...</option>
      </select>
      <button id="refresh-ports" class="mt-2 text-[10px] font-mono text-dim hover:text-accent transition-colors uppercase tracking-wider">
        Refresh port list
      </button>
    </div>

    <div class="bg-card border border-base rounded p-4 mb-6" id="baud-section">
      <div class="text-primary text-xs font-mono uppercase tracking-wider mb-3">Baud Rate</div>
      <select id="baud-select"
        class="w-full bg-raised border border-base rounded px-3 py-2 text-primary font-mono text-xs focus:outline-none focus:border-accent">
        ${BAUDRATES.map(b => `<option value="${b}"${b === 115200 ? ' selected' : ''}>${b.toLocaleString()}</option>`).join('')}
      </select>
    </div>

    <button id="apply-btn"
      class="w-full py-2.5 bg-raised border border-accent text-accent font-mono text-xs uppercase tracking-widest rounded hover:bg-[var(--accent-dim)] transition-colors">
      Apply
    </button>
    <div id="settings-status" class="mt-3 text-[10px] font-mono text-center h-4"></div>
  `;

  const simToggle = el.querySelector('#sim-toggle');
  const portSelect = el.querySelector('#port-select');
  const baudSelect = el.querySelector('#baud-select');
  const applyBtn = el.querySelector('#apply-btn');
  const statusEl = el.querySelector('#settings-status');
  const portSection = el.querySelector('#port-section');
  const baudSection = el.querySelector('#baud-section');
  const refreshBtn = el.querySelector('#refresh-ports');

  function setHardwareSectionEnabled(enabled) {
    portSelect.disabled = !enabled;
    baudSelect.disabled = !enabled;
    portSection.style.opacity = enabled ? '1' : '0.4';
    baudSection.style.opacity = enabled ? '1' : '0.4';
  }

  simToggle.addEventListener('change', () => {
    setHardwareSectionEnabled(!simToggle.checked);
  });

  async function loadPorts(selectedPort) {
    try {
      const res = await fetch('/api/ports');
      const ports = await res.json();
      portSelect.innerHTML = ports.length
        ? ports.map(p =>
            `<option value="${p.port}"${p.port === selectedPort ? ' selected' : ''}>${p.port} — ${p.description}</option>`
          ).join('')
        : '<option value="">No ports found — enable simulation</option>';
    } catch {
      portSelect.innerHTML = '<option value="">Could not load ports</option>';
    }
  }

  async function loadConfig() {
    try {
      const res = await fetch('/api/config');
      const cfg = await res.json();
      simToggle.checked = cfg.simulation;
      baudSelect.value = String(cfg.baudrate);
      await loadPorts(cfg.port);
      setHardwareSectionEnabled(!cfg.simulation);
      showStatus(cfg);
    } catch {
      showStatusText('Failed to load config', 'text-fault');
    }
  }

  refreshBtn.addEventListener('click', () => loadPorts(portSelect.value));

  applyBtn.addEventListener('click', async () => {
    applyBtn.disabled = true;
    applyBtn.textContent = 'Applying…';
    statusEl.textContent = '';
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          simulation: simToggle.checked,
          port: portSelect.value,
          baudrate: parseInt(baudSelect.value, 10),
        }),
      });
      const result = await res.json();
      showStatus(result);
    } catch {
      showStatusText('Request failed — is the server running?', 'text-fault');
    } finally {
      applyBtn.disabled = false;
      applyBtn.textContent = 'Apply';
    }
  });

  function showStatus(cfg) {
    if (cfg.status === 'error') {
      showStatusText(`Error: ${cfg.error}`, 'text-fault');
    } else if (cfg.status === 'simulation') {
      showStatusText('Simulation active', 'text-warn');
    } else if (cfg.status === 'ok') {
      showStatusText(`Connected to ${cfg.port}`, 'text-ok');
    }
  }

  function showStatusText(msg, cls) {
    statusEl.textContent = msg;
    statusEl.className = `mt-3 text-[10px] font-mono text-center h-4 ${cls}`;
  }

  loadConfig();

  return el;
}
