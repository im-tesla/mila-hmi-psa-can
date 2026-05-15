import { onSignalChange, getSignal } from '../state.js';
import { showRawPopover } from './raw-popover.js';

export function createSignalCard(canId, signalName, unit) {
  const card = document.createElement('div');
  card.className = 'bg-gray-900 dark:bg-white border border-gray-800 dark:border-gray-200 rounded-lg p-3 min-h-touch cursor-pointer select-none';
  card.style.WebkitTapHighlightColor = 'transparent';
  card.innerHTML = `
    <div class="flex items-center justify-between mb-1">
      <span class="text-xs text-gray-500 dark:text-gray-400">${signalName}</span>
      <span class="text-[10px] text-gray-600 dark:text-gray-300 font-mono">${canId}</span>
    </div>
    <div class="text-2xl font-bold signal-value text-gray-400">—</div>
    <div class="text-[11px] text-gray-600 dark:text-gray-400 mt-0.5">${unit || ''}</div>
  `;

  const valueEl = card.querySelector('.signal-value');

  onSignalChange(canId, signalName, (value) => {
    valueEl.textContent = formatValue(value);
    valueEl.className = `text-2xl font-bold signal-value ${valueColor(value)}`;
  });

  const existing = getSignal(canId, signalName);
  if (existing) {
    valueEl.textContent = formatValue(existing.value);
    valueEl.className = `text-2xl font-bold signal-value ${valueColor(existing.value)}`;
  }

  // Long-press for raw data
  let pressTimer;
  card.addEventListener('pointerdown', () => {
    pressTimer = setTimeout(() => showRawPopover(canId, signalName, card), 500);
  });
  card.addEventListener('pointerup', () => clearTimeout(pressTimer));
  card.addEventListener('pointerleave', () => clearTimeout(pressTimer));
  card.addEventListener('pointercancel', () => clearTimeout(pressTimer));

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
      return 'text-signal-fault';
    if (['blinking', 'elevated', 'check', 'in progress', 'wait', 'deactivated', 'disabled'].includes(lower))
      return 'text-signal-warn';
    if (['ok', 'closed', 'off', 'valid', 'normal', 'running', 'stopped', 'inactive', 'linked', 'enabled'].includes(lower))
      return 'text-signal-ok';
  }
  if (v === true) return 'text-signal-ok';
  if (v === false) return 'text-signal-inactive';
  return 'text-gray-100 dark:text-gray-900';
}
