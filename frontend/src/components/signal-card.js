import { onSignalChange, getSignal } from '../state.js';
import { showRawPopover } from './raw-popover.js';
import { getEnumOptions } from '../can-enum-maps.js';
import { showSignalEditModal } from './signal-edit-modal.js';

export function createSignalCard(canId, signalName, unit) {
  const card = document.createElement('div');
  card.className = 'signal-card p-2.5 min-h-touch cursor-pointer select-none';
  card.style.WebkitTapHighlightColor = 'transparent';
  card.innerHTML = `
    <div class="flex items-center justify-between mb-1">
      <span class="text-[10px] font-mono text-dim uppercase tracking-wider truncate mr-1">${signalName}</span>
      <span class="text-[9px] font-mono text-dim/50 shrink-0" style="opacity:0.4">${canId}</span>
    </div>
    <div class="text-xl font-mono font-bold signal-value text-dim">--</div>
    <div class="text-[10px] font-mono text-dim/60 mt-0.5" style="opacity:0.4">${unit || ''}</div>
  `;

  const valueEl = card.querySelector('.signal-value');

  onSignalChange(canId, signalName, (value) => {
    valueEl.textContent = formatValue(value);
    valueEl.className = `text-xl font-mono font-bold signal-value ${valueColor(value)}`;
  });

  const existing = getSignal(canId, signalName);
  if (existing) {
    valueEl.textContent = formatValue(existing.value);
    valueEl.className = `text-xl font-mono font-bold signal-value ${valueColor(existing.value)}`;
  }

  let pressTimer;
  let longPressTriggered = false;

  card.addEventListener('pointerdown', () => {
    longPressTriggered = false;
    pressTimer = setTimeout(() => {
      longPressTriggered = true;
      showRawPopover(canId, signalName, card);
    }, 500);
  });
  card.addEventListener('pointerup', () => clearTimeout(pressTimer));
  card.addEventListener('pointercancel', () => clearTimeout(pressTimer));

  card.addEventListener('click', () => {
    if (longPressTriggered) return;
    if (getEnumOptions(canId, signalName)) {
      showSignalEditModal(canId, signalName);
    } else {
      showRawPopover(canId, signalName, card);
    }
  });

  return card;
}

function formatValue(v) {
  if (typeof v === 'boolean') return v ? 'ON' : 'OFF';
  if (typeof v === 'number' && !Number.isInteger(v)) return v.toFixed(1);
  return String(v);
}

function valueColor(v) {
  if (typeof v === 'string') {
    const lower = v.toLowerCase();
    if (['open', 'fault', 'error', 'low', 'warning', 'active', 'on', 'alert', 'faulty', 'punctured',
         'clogged', 'worn', 'max', 'water!', 'stop!', 'due', 'applied', 'warning!'].includes(lower))
      return 'text-fault';
    if (['blinking', 'elevated', 'check', 'in progress', 'wait', 'deactivated', 'disabled'].includes(lower))
      return 'text-warn';
    if (['ok', 'closed', 'off', 'valid', 'normal', 'running', 'stopped', 'inactive', 'linked', 'enabled'].includes(lower))
      return 'text-ok';
  }
  if (v === true) return 'text-ok';
  if (v === false) return 'text-mute';
  return 'text-primary';
}
