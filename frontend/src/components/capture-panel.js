const BASELINE_MS = 3000;
const CAPTURE_MS = 2000;
const NUM_ROUNDS = 3;

export function createCapturePanel() {
  let phase = 'idle';
  let baselineRaw = new Map();
  let noisyIds = new Set();
  let currentRoundSnap = new Map();
  let currentRoundDiffs = new Map();
  let roundResults = [];
  let phaseTimer = null;
  let countdownTimer = null;
  let progressTimer = null;

  const el = document.createElement('div');
  el.className = 'flex flex-col overflow-auto';
  el.style.height = 'calc(100vh - 40px)';

  function esc(s) {
    return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function render() {
    el.innerHTML = buildHTML();
    attachHandlers();
  }

  function buildHTML() {
    if (phase === 'idle')        return buildIdle();
    if (phase === 'baseline')    return buildBaseline();
    if (phase === 'ready' || phase === 'round-done') return buildReady();
    if (phase === 'countdown')   return buildCountdown();
    if (phase === 'capturing')   return buildCapturing();
    if (phase === 'complete')    return buildComplete();
    return '';
  }

  function buildIdle() {
    return `
      <div class="max-w-lg mx-auto mt-8 px-4">
        <div class="text-accent font-bold uppercase tracking-widest text-xs mb-1">CAN Reverse Engineering</div>
        <div class="text-dim text-xs mb-6">Identify which CAN frame is sent when you press a button or trigger an action in the car.</div>
        <div class="border border-base p-4 mb-4 bg-card">
          <div class="text-[10px] uppercase tracking-wider text-dim mb-2">Step 1 of 3 — Capture Baseline</div>
          <div class="text-xs text-primary mb-4">Keep everything idle. Don't press any buttons or touch anything in the car.</div>
          <button id="btn-start-baseline" class="px-4 py-2 text-[10px] font-mono uppercase tracking-wider border border-accent text-accent hover:bg-accent hover:text-black transition-colors">
            Start 3s Baseline
          </button>
        </div>
      </div>
    `;
  }

  function buildBaseline() {
    return `
      <div class="max-w-lg mx-auto mt-8 px-4">
        <div class="text-accent font-bold text-xs uppercase tracking-widest mb-4">Capturing Baseline…</div>
        <div class="text-dim text-xs mb-4">Stay idle — don't touch anything.</div>
        <div class="w-full bg-raised rounded overflow-hidden" style="height:4px">
          <div id="baseline-bar" class="h-full bg-accent" style="width:0%;transition:none"></div>
        </div>
        <button id="btn-reset" class="mt-4 text-[10px] text-dim hover:text-primary transition-colors uppercase tracking-wider">✕ Cancel</button>
      </div>
    `;
  }

  function buildReady() {
    const roundIdx = roundResults.length;
    const prevRounds = roundResults.map((r, i) =>
      `<div class="text-ok text-[10px] mb-1">✓ Round ${i + 1}: ${r.size} candidate ID(s)</div>`
    ).join('');
    return `
      <div class="max-w-lg mx-auto mt-8 px-4">
        <div class="text-ok text-[10px] mb-1">✓ Baseline: ${baselineRaw.size} IDs seen, ${noisyIds.size} filtered (noisy)</div>
        ${prevRounds}
        <div class="border border-base p-4 mt-4 bg-card">
          <div class="text-[10px] uppercase tracking-wider text-dim mb-2">Step 2 of 3 — Round ${roundIdx + 1} of ${NUM_ROUNDS}</div>
          <div class="text-xs text-primary mb-4">Click Start, then press your button when the countdown reaches zero.</div>
          <button id="btn-start-round" class="px-4 py-2 text-[10px] font-mono uppercase tracking-wider border border-accent text-accent hover:bg-accent hover:text-black transition-colors">
            Start Round ${roundIdx + 1}
          </button>
        </div>
        <button id="btn-reset" class="mt-4 text-[10px] text-dim hover:text-primary transition-colors uppercase tracking-wider">↩ Reset</button>
      </div>
    `;
  }

  function buildCountdown() {
    return `
      <div class="max-w-lg mx-auto mt-8 px-4 text-center">
        <div class="text-dim text-[10px] uppercase tracking-wider mb-6">Press the button in…</div>
        <div id="countdown-num" class="font-bold text-accent" style="font-size:6rem;line-height:1">3</div>
        <button id="btn-reset" class="mt-8 text-[10px] text-dim hover:text-primary transition-colors uppercase tracking-wider">✕ Cancel</button>
      </div>
    `;
  }

  function buildCapturing() {
    const roundNum = roundResults.length + 1;
    return `
      <div class="max-w-lg mx-auto mt-8 px-4">
        <div class="text-warn text-[10px] uppercase tracking-wider mb-4">Round ${roundNum} — Capturing…</div>
        <div class="w-full bg-raised rounded overflow-hidden" style="height:4px">
          <div id="capture-bar" class="h-full bg-warn" style="width:0%;transition:none"></div>
        </div>
        <button id="btn-reset" class="mt-4 text-[10px] text-dim hover:text-primary transition-colors uppercase tracking-wider">✕ Cancel</button>
      </div>
    `;
  }

  function buildComplete() {
    const candidates = computeCandidates();
    const rows = candidates.length === 0
      ? `<div class="border border-fault p-4 text-fault text-xs">No consistent candidates found. Try again — ensure the car is fully idle during baseline and you pressed the same button each round.</div>`
      : candidates.map(buildCandidateRow).join('');
    return `
      <div class="max-w-lg mx-auto mt-8 px-4">
        <div class="text-accent font-bold text-xs uppercase tracking-widest mb-4">Step 3 of 3 — Results</div>
        ${rows}
        <button id="btn-reset" class="mt-4 px-4 py-2 text-[10px] font-mono uppercase tracking-wider border border-base text-dim hover:text-primary hover:border-primary transition-colors">
          ↩ Try Another Button
        </button>
      </div>
    `;
  }

  function buildCandidateRow({ id, before, after }) {
    const isNew = before === null;
    const diffLines = isNew ? '' : byteDiff(before, after).map(d =>
      `<div class="text-[10px] mb-0.5">
        <span class="text-dim">Byte ${d.idx}:</span>
        <span class="text-fault ml-1">${esc(d.before)}</span>
        <span class="text-dim"> → </span>
        <span class="text-ok">${esc(d.after)}</span>
      </div>`
    ).join('');
    return `
      <div class="border border-base p-3 mb-3 bg-card">
        <div class="text-accent font-bold text-sm mb-2">${esc(id)}</div>
        ${isNew ? '<div class="text-[10px] text-warn mb-1">New frame — not seen during baseline</div>' : diffLines}
        <div class="text-[10px] text-dim mt-2">Before: <span class="text-secondary">${isNew ? '—' : esc(before)}</span></div>
        <div class="text-[10px] text-dim">After:  <span class="text-primary">${esc(after)}</span></div>
      </div>
    `;
  }

  function attachHandlers() {
    el.querySelector('#btn-start-baseline')?.addEventListener('click', startBaseline);
    el.querySelector('#btn-start-round')?.addEventListener('click', startCountdown);
    el.querySelector('#btn-reset')?.addEventListener('click', reset);
  }

  function startBaseline() {
    clearTimeout(phaseTimer);
    clearInterval(progressTimer);
    baselineRaw.clear();
    noisyIds.clear();
    roundResults = [];
    currentRoundSnap.clear();
    currentRoundDiffs.clear();
    phase = 'baseline';
    render();
    startProgress(BASELINE_MS, '#baseline-bar');
    phaseTimer = setTimeout(() => {
      phase = 'ready';
      render();
    }, BASELINE_MS);
  }

  function startCountdown() {
    clearInterval(countdownTimer);
    currentRoundDiffs = new Map();
    phase = 'countdown';
    render();
    let secs = 3;
    updateCountdownNum(secs);
    countdownTimer = setInterval(() => {
      secs--;
      updateCountdownNum(secs);
      if (secs <= 0) {
        clearInterval(countdownTimer);
        countdownTimer = null;
        setTimeout(startCapture, 400);
      }
    }, 1000);
  }

  function updateCountdownNum(n) {
    const numEl = el.querySelector('#countdown-num');
    if (numEl) numEl.textContent = n;
  }

  function startCapture() {
    currentRoundSnap = new Map(baselineRaw);
    phase = 'capturing';
    render();
    startProgress(CAPTURE_MS, '#capture-bar');
    phaseTimer = setTimeout(() => {
      roundResults.push(new Map(currentRoundDiffs));
      phase = roundResults.length >= NUM_ROUNDS ? 'complete' : 'round-done';
      render();
    }, CAPTURE_MS);
  }

  function startProgress(durationMs, selector) {
    clearInterval(progressTimer);
    const t0 = Date.now();
    progressTimer = setInterval(() => {
      const pct = Math.min(100, ((Date.now() - t0) / durationMs) * 100);
      const bar = el.querySelector(selector);
      if (bar) bar.style.width = pct + '%';
      if (pct >= 100) { clearInterval(progressTimer); progressTimer = null; }
    }, 50);
  }

  function reset() {
    clearTimeout(phaseTimer);
    clearInterval(countdownTimer);
    clearInterval(progressTimer);
    phaseTimer = null; countdownTimer = null; progressTimer = null;
    baselineRaw.clear();
    noisyIds.clear();
    roundResults = [];
    currentRoundSnap.clear();
    currentRoundDiffs.clear();
    phase = 'idle';
    render();
  }

  function onFrame(msg) {
    const { id, raw } = msg;
    if (!id || !raw) return;
    if (phase === 'baseline') {
      if (baselineRaw.has(id) && baselineRaw.get(id) !== raw) noisyIds.add(id);
      baselineRaw.set(id, raw);
    } else if (phase === 'capturing') {
      const before = currentRoundSnap.get(id);
      if (before === undefined && !noisyIds.has(id)) {
        currentRoundDiffs.set(id, { before: null, after: raw });
      } else if (before !== undefined && before !== raw && !noisyIds.has(id)) {
        currentRoundDiffs.set(id, { before, after: raw });
      }
    }
  }

  function computeCandidates() {
    if (roundResults.length === 0) return [];
    let common = new Set(roundResults[0].keys());
    for (let i = 1; i < roundResults.length; i++) {
      common = new Set([...common].filter(id => roundResults[i].has(id)));
    }
    return [...common].map(id => {
      const last = roundResults[roundResults.length - 1].get(id);
      return { id, before: last.before, after: last.after };
    });
  }

  function byteDiff(hexA, hexB) {
    const a = hexA.split(' ');
    const b = hexB.split(' ');
    const diffs = [];
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      const av = a[i] || '--', bv = b[i] || '--';
      if (av !== bv) diffs.push({ idx: i, before: av, after: bv });
    }
    return diffs;
  }

  render();
  return { element: el, onFrame };
}
