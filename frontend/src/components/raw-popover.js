import { getSignal } from '../state.js';

let activePopover = null;
let activeBackdrop = null;

export function showRawPopover(canId, signalName, anchorEl) {
  dismissPopover();

  const signal = getSignal(canId, signalName);
  if (!signal) return;

  const backdrop = document.createElement('div');
  backdrop.className = 'popover-backdrop';
  backdrop.addEventListener('pointerdown', dismissPopover);
  document.body.appendChild(backdrop);
  activeBackdrop = backdrop;

  const rect = anchorEl.getBoundingClientRect();
  const popover = document.createElement('div');
  popover.className = 'fixed z-50 shadow-popover p-4 min-w-[280px] font-mono';
  popover.style.background = 'var(--bg-base)';
  popover.style.border = '1px solid rgba(230,168,23,0.3)';
  popover.style.left = `${Math.min(rect.right + 8, window.innerWidth - 296)}px`;
  popover.style.top = `${Math.max(8, Math.min(rect.top, window.innerHeight - 320))}px`;

  popover.innerHTML = `
    <div class="flex items-center gap-2 mb-3 pb-2 border-b border-base">
      <span class="led-dot ok"></span>
      <span class="text-xs font-bold text-accent tracking-wide">${canId}</span>
      <span class="text-xs text-dim">${signalName}</span>
    </div>
    <div class="space-y-2 text-xs">
      <div class="flex justify-between">
        <span class="text-dim uppercase tracking-wider text-[10px]">Value</span>
        <span class="text-primary font-bold">${signal.value}</span>
      </div>
      <div class="flex justify-between">
        <span class="text-dim uppercase tracking-wider text-[10px]">Raw</span>
        <span class="text-primary">${signal.raw || '—'}</span>
      </div>
      <div class="flex justify-between">
        <span class="text-dim uppercase tracking-wider text-[10px]">Updated</span>
        <span class="text-primary">${new Date(signal.ts * 1000).toLocaleTimeString()}</span>
      </div>
    </div>
    <div class="mt-3 text-[9px] text-dim uppercase tracking-wider">Tap to dismiss</div>
  `;

  document.body.appendChild(popover);
  activePopover = popover;
}

function dismissPopover() {
  if (activePopover) { activePopover.remove(); activePopover = null; }
  if (activeBackdrop) { activeBackdrop.remove(); activeBackdrop = null; }
}
