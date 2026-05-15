import { SECTIONS } from '../can-definitions.js';

export function createSearchBar({ onSearch, onCategoryChange }) {
  const bar = document.createElement('div');
  bar.className = 'px-4 py-3 space-y-3';
  bar.innerHTML = `
    <div class="relative">
      <svg class="absolute left-3 top-1/2 -translate-y-1/2 text-dim" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input id="signal-search" type="text" placeholder="Search signals, CAN IDs, values..."
        class="w-full pl-10 pr-4 py-2.5 font-mono text-sm bg-base border border-base text-primary placeholder-dim focus:outline-none min-h-touch"
        style="background: var(--bg-base); color: var(--text-primary); border-color: var(--border-color);" />
    </div>
    <div id="category-chips" class="flex gap-2 overflow-x-auto pb-1 scrollbar-hide"></div>
  `;

  const chipsContainer = bar.querySelector('#category-chips');
  let activeCategory = 'All';

  function renderChips() {
    chipsContainer.innerHTML = '';
    const allChip = createChip('ALL', activeCategory === 'All');
    allChip.addEventListener('click', () => {
      activeCategory = 'All';
      onCategoryChange(null);
      renderChips();
    });
    chipsContainer.appendChild(allChip);

    for (const section of SECTIONS) {
      const chip = createChip(section.code, activeCategory === section.name);
      chip.title = section.name;
      chip.addEventListener('click', () => {
        activeCategory = section.name;
        onCategoryChange(section);
        renderChips();
      });
      chipsContainer.appendChild(chip);
    }
  }

  renderChips();

  const input = bar.querySelector('#signal-search');
  input.addEventListener('input', (e) => onSearch(e.target.value.toLowerCase()));

  return bar;
}

function createChip(label, active) {
  const chip = document.createElement('button');
  if (active) {
    chip.className = 'px-3 py-1.5 font-mono text-xs font-medium whitespace-nowrap min-h-touch border';
    chip.style.background = 'var(--accent)';
    chip.style.color = 'var(--bg-base)';
    chip.style.borderColor = 'var(--accent)';
  } else {
    chip.className = 'px-3 py-1.5 font-mono text-xs font-medium whitespace-nowrap min-h-touch border border-base hover:text-primary';
    chip.style.background = 'var(--bg-raised)';
    chip.style.color = 'var(--text-secondary)';
    chip.style.borderColor = 'var(--border-color)';
  }
  chip.textContent = label;
  return chip;
}
