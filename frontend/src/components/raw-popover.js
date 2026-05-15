import { getSignal } from '../state.js';

let activePopover = null;

export function showRawPopover(canId, signalName, anchorEl) {
  if (activePopover) {
    activePopover.remove();
    activePopover = null;
  }

  const signal = getSignal(canId, signalName);
  if (!signal) return;

  const rect = anchorEl.getBoundingClientRect();
  const popover = document.createElement('div');
  popover.className = 'fixed z-50 bg-gray-950 dark:bg-white border-2 border-blue-500 rounded-xl p-4 shadow-2xl min-w-[260px]';
  popover.style.left = `${Math.min(rect.right + 12, window.innerWidth - 280)}px`;
  popover.style.top = `${Math.min(rect.top, window.innerHeight - 300)}px`;

  popover.innerHTML = `
    <div class="text-sm font-bold text-blue-400 mb-2">${canId} · ${signalName}</div>
    <div class="space-y-2 text-xs font-mono">
      <div>
        <span class="text-gray-500">Value: </span>
        <span class="text-gray-100 dark:text-gray-900 font-bold text-base">${signal.value}</span>
      </div>
      <div>
        <span class="text-gray-500">Raw hex: </span>
        <span class="text-gray-100 dark:text-gray-900">${signal.raw || '—'}</span>
      </div>
      <div>
        <span class="text-gray-500">Updated: </span>
        <span class="text-gray-100 dark:text-gray-900">${new Date(signal.ts * 1000).toLocaleTimeString()}</span>
      </div>
    </div>
    <div class="mt-3 text-[10px] text-gray-600 dark:text-gray-400">Tap elsewhere to dismiss</div>
  `;

  document.body.appendChild(popover);
  activePopover = popover;

  requestAnimationFrame(() => {
    document.addEventListener('pointerdown', dismissPopover, { once: true });
  });
}

function dismissPopover() {
  if (activePopover) {
    activePopover.remove();
    activePopover = null;
  }
}
