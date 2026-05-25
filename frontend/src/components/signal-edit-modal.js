import { getEnumOptions } from '../can-enum-maps.js';
import { getSignal } from '../state.js';
import { sendCanWrite } from '../can-send.js';

function esc(s) {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

let activeModal = null;
let activeBackdrop = null;

export function showSignalEditModal(canId, signalName) {
  const options = getEnumOptions(canId, signalName);
  if (!options) return;

  dismiss();

  const signal = getSignal(canId, signalName);
  const currentValue = signal?.value ?? null;

  const backdrop = document.createElement('div');
  backdrop.className = 'fixed inset-0 z-40';
  backdrop.style.background = 'rgba(0,0,0,0.6)';
  backdrop.addEventListener('pointerdown', dismiss);
  document.body.appendChild(backdrop);
  activeBackdrop = backdrop;

  const modal = document.createElement('div');
  modal.className = 'fixed z-50 p-4 font-mono min-w-[260px] max-w-[90vw]';
  modal.style.background = 'var(--bg-base)';
  modal.style.border = '1px solid rgba(230,168,23,0.3)';
  modal.style.top = '50%';
  modal.style.left = '50%';
  modal.style.transform = 'translate(-50%, -50%)';

  const cols = options.length <= 4 ? options.length : Math.ceil(Math.sqrt(options.length));

  modal.innerHTML = `
    <div class="flex items-start justify-between mb-3 pb-2 border-b border-base">
      <div>
        <div class="text-xs font-bold text-accent tracking-wide uppercase">${esc(signalName)}</div>
        <div class="text-[10px] text-dim">${esc(canId)}</div>
      </div>
      <button class="dismiss-btn text-dim text-xl leading-none ml-4 hover:text-primary" style="line-height:1">×</button>
    </div>
    <div class="text-[10px] text-dim uppercase tracking-wider mb-1">Current</div>
    <div class="text-lg font-bold mb-4 ${valueColor(currentValue)}">${currentValue != null ? esc(currentValue) : '—'}</div>
    <div class="text-[10px] text-dim uppercase tracking-wider mb-2">Set value</div>
    <div class="grid gap-2" style="grid-template-columns: repeat(${cols}, 1fr)">
      ${options.map(o => `
        <button
          class="option-btn py-2 px-3 text-xs font-mono border transition-colors ${String(o.label) === String(currentValue) ? 'border-accent text-accent' : 'border-base text-dim hover:text-primary hover:border-primary'}"
          data-raw="${esc(o.rawValue)}"
        >${esc(o.label)}</button>
      `).join('')}
    </div>
  `;

  modal.querySelector('.dismiss-btn').addEventListener('click', dismiss);

  modal.querySelectorAll('.option-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      sendCanWrite(canId, signalName, Number(btn.dataset.raw));
      dismiss();
    });
  });

  document.body.appendChild(modal);
  activeModal = modal;
}

function dismiss() {
  activeModal?.remove(); activeModal = null;
  activeBackdrop?.remove(); activeBackdrop = null;
}

function valueColor(v) {
  if (typeof v === 'string') {
    const lower = v.toLowerCase();
    if (['open','fault','error','low','warning','active','on','alert','faulty','punctured',
         'clogged','worn','max','water!','stop!','due','applied','warning!'].includes(lower))
      return 'text-fault';
    if (['blinking','elevated','check','in progress','wait','deactivated','disabled'].includes(lower))
      return 'text-warn';
    if (['ok','closed','off','valid','normal','running','stopped','inactive','linked','enabled'].includes(lower))
      return 'text-ok';
  }
  if (v === true) return 'text-ok';
  if (v === false) return 'text-mute';
  return 'text-primary';
}
