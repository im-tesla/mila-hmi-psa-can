import { createSignalCard } from './signal-card.js';
import { SIGNAL_META } from '../can-definitions.js';

export function createSection(sectionDef) {
  const section = document.createElement('div');
  section.className = 'bg-card border border-base mb-2';
  section.id = `section-${sectionDef.name.replace(/\s+/g, '-')}`;

  const header = document.createElement('div');
  header.className = 'section-header flex items-center justify-between px-4 py-3 cursor-pointer min-h-touch select-none';
  const badgeId = `badge-${sectionDef.name.replace(/\s+/g, '-')}`;
  header.innerHTML = `
    <div class="flex items-center gap-3">
      <span class="section-code">${sectionDef.code}</span>
      <span class="font-display font-semibold text-base text-primary tracking-wide">${sectionDef.name.toUpperCase()}</span>
      <span id="${badgeId}" class="text-[10px] font-mono px-2 py-0.5 bg-raised text-dim"></span>
    </div>
    <span class="chevron-icon">&#9654;</span>
  `;

  const grid = document.createElement('div');
  grid.className = 'grid grid-cols-3 gap-px';
  grid.style.background = 'var(--border-color)';
  grid.style.display = 'none';

  header.addEventListener('click', () => {
    const isOpen = grid.style.display !== 'none';
    grid.style.display = isOpen ? 'none' : 'grid';
    const chevron = header.querySelector('.chevron-icon');
    chevron.classList.toggle('open', !isOpen);
  });

  section.appendChild(header);
  section.appendChild(grid);

  for (const [key, meta] of Object.entries(SIGNAL_META)) {
    for (const canId of sectionDef.canIds) {
      if (meta.canId === canId) {
        const signalName = key.slice(canId.length + 1);
        const card = createSignalCard(canId, signalName, meta.unit);
        grid.appendChild(card);
        break;
      }
    }
  }

  return { element: section, grid, header, badgeId };
}
