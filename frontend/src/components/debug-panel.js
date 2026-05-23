const MAX_BUFFER = 500;
const MAX_ROWS = 200;

export function createDebugPanel() {
  const el = document.createElement('div');
  el.className = 'flex flex-col overflow-hidden';
  el.style.height = 'calc(100vh - 40px)';
  el.innerHTML = `
    <div class="flex items-center gap-3 px-4 py-2 bg-card border-b border-base shrink-0">
      <input id="debug-filter" type="text" placeholder="Filter ID (e.g. 0B6)"
        class="bg-raised border border-base rounded px-2 py-1 text-primary font-mono text-[10px] w-36
               focus:outline-none focus:border-accent uppercase tracking-wider" />
      <button id="debug-pause"
        class="px-3 py-1 text-[10px] font-mono uppercase tracking-wider bg-raised border border-base rounded text-primary hover:border-accent transition-colors">
        Pause
      </button>
      <button id="debug-clear"
        class="px-3 py-1 text-[10px] font-mono uppercase tracking-wider bg-raised border border-base rounded text-primary hover:border-accent transition-colors">
        Clear
      </button>
      <span id="debug-count" class="text-dim text-[10px] font-mono ml-auto">0 frames</span>
    </div>
    <div class="flex-1 overflow-auto">
      <table class="w-full border-collapse font-mono text-[10px]">
        <thead class="sticky top-0 bg-card border-b border-base z-10">
          <tr>
            <th class="text-left px-3 py-1.5 text-dim uppercase tracking-wider font-normal w-24">Time</th>
            <th class="text-left px-3 py-1.5 text-dim uppercase tracking-wider font-normal w-20">ID</th>
            <th class="text-left px-3 py-1.5 text-dim uppercase tracking-wider font-normal w-52">Raw (hex)</th>
            <th class="text-left px-3 py-1.5 text-dim uppercase tracking-wider font-normal">Signals</th>
          </tr>
        </thead>
        <tbody id="debug-tbody"></tbody>
      </table>
      <div id="debug-empty" class="text-dim text-center py-16 font-mono text-xs">
        Waiting for CAN frames…
      </div>
    </div>
  `;

  const filterInput = el.querySelector('#debug-filter');
  const pauseBtn = el.querySelector('#debug-pause');
  const clearBtn = el.querySelector('#debug-clear');
  const countEl = el.querySelector('#debug-count');
  const tbody = el.querySelector('#debug-tbody');
  const emptyEl = el.querySelector('#debug-empty');

  let buffer = [];
  let paused = false;
  let filterStr = '';
  let startTime = Date.now();
  let totalFrames = 0;

  filterInput.addEventListener('input', () => {
    filterStr = filterInput.value.trim().toUpperCase();
    render();
  });

  pauseBtn.addEventListener('click', () => {
    paused = !paused;
    pauseBtn.textContent = paused ? 'Resume' : 'Pause';
    pauseBtn.classList.toggle('text-warn', paused);
    if (!paused) render();
  });

  clearBtn.addEventListener('click', () => {
    buffer = [];
    totalFrames = 0;
    startTime = Date.now();
    countEl.textContent = '0 frames';
    render();
  });

  function onFrame(msg) {
    buffer.push(msg);
    totalFrames++;
    if (buffer.length > MAX_BUFFER) buffer.shift();
    countEl.textContent = `${totalFrames.toLocaleString()} frames`;
    if (!paused) render();
  }

  function render() {
    const filtered = filterStr
      ? buffer.filter(f => f.id.toUpperCase().replace('0X', '').includes(filterStr.replace('0X', '')))
      : buffer;

    emptyEl.style.display = filtered.length === 0 ? '' : 'none';

    const rows = filtered.slice(-MAX_ROWS).reverse();
    tbody.innerHTML = rows.map(f => {
      const relMs = Math.round(f.ts * 1000 - startTime);
      const signals = f.data
        ? Object.entries(f.data)
            .filter(([k]) => k !== '_unknown')
            .map(([k, v]) => `${k}=<span class="text-primary">${v}</span>`)
            .join(' <span class="text-dim">·</span> ')
        : '';
      return `<tr class="border-b border-base hover:bg-raised">
        <td class="px-3 py-1 text-dim tabular-nums">${relMs}ms</td>
        <td class="px-3 py-1 text-accent font-semibold">${f.id}</td>
        <td class="px-3 py-1 text-secondary tracking-wider">${f.raw || '—'}</td>
        <td class="px-3 py-1 text-secondary leading-relaxed">${signals}</td>
      </tr>`;
    }).join('');
  }

  return { element: el, onFrame };
}
