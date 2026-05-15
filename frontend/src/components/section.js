import { createSignalCard } from './signal-card.js';
import { SIGNAL_META } from '../can-definitions.js';

export function createSection(sectionDef) {
  const section = document.createElement('div');
  section.className = 'bg-gray-900/50 dark:bg-white border border-gray-800 dark:border-gray-200 rounded-xl overflow-hidden mb-3';
  section.id = `section-${sectionDef.name.replace(/\s+/g, '-')}`;

  const header = document.createElement('div');
  header.className = 'flex items-center justify-between p-4 cursor-pointer min-h-touch select-none hover:bg-gray-800/50 dark:hover:bg-gray-100 active:bg-gray-800 dark:active:bg-gray-200';
  const badgeId = `badge-${sectionDef.name.replace(/\s+/g, '-')}`;
  header.innerHTML = `
    <div class="flex items-center gap-3">
      <span class="text-lg">${sectionDef.icon}</span>
      <span class="font-semibold text-base text-gray-100 dark:text-gray-900">${sectionDef.name}</span>
      <span id="${badgeId}" class="text-xs px-2 py-0.5 rounded-full bg-gray-800 dark:bg-gray-200 text-gray-400"></span>
    </div>
    <span class="text-gray-500 text-sm chevron">▶</span>
  `;

  const grid = document.createElement('div');
  grid.className = 'grid grid-cols-3 gap-2 p-4 pt-0';
  grid.style.display = 'none';

  header.addEventListener('click', () => {
    const isOpen = grid.style.display !== 'none';
    grid.style.display = isOpen ? 'none' : 'grid';
    header.querySelector('.chevron').textContent = isOpen ? '▶' : '▼';
  });

  section.appendChild(header);
  section.appendChild(grid);

  // Populate grid with signal cards
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
