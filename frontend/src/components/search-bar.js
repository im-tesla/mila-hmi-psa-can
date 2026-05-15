import { SECTIONS } from '../can-definitions.js';

export function createSearchBar({ onSearch, onCategoryChange }) {
  const bar = document.createElement('div');
  bar.className = 'px-4 py-3 space-y-3';
  bar.innerHTML = `
    <div class="relative">
      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-lg">🔍</span>
      <input id="signal-search" type="text" placeholder="Search signals, CAN IDs, values..."
        class="w-full pl-10 pr-4 py-2.5 bg-gray-900 dark:bg-white border border-gray-700 dark:border-gray-300 rounded-xl text-base text-gray-100 dark:text-gray-900 placeholder-gray-600 dark:placeholder-gray-400 focus:outline-none focus:border-blue-500 min-h-touch" />
    </div>
    <div id="category-chips" class="flex gap-2 overflow-x-auto pb-1 scrollbar-hide"></div>
  `;

  const chipsContainer = bar.querySelector('#category-chips');
  let activeCategory = 'All';

  function renderChips() {
    chipsContainer.innerHTML = '';
    const allChip = createChip('All', activeCategory === 'All');
    allChip.addEventListener('click', () => {
      activeCategory = 'All';
      onCategoryChange(null);
      renderChips();
    });
    chipsContainer.appendChild(allChip);

    for (const section of SECTIONS) {
      const chip = createChip(section.name, activeCategory === section.name);
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
  input.addEventListener('input', (e) => {
    onSearch(e.target.value.toLowerCase());
  });

  return bar;
}

function createChip(label, active) {
  const chip = document.createElement('button');
  chip.className = active
    ? 'px-4 py-2 rounded-full text-sm font-medium bg-blue-600 text-white whitespace-nowrap min-h-touch'
    : 'px-4 py-2 rounded-full text-sm font-medium bg-gray-800 dark:bg-gray-200 text-gray-400 dark:text-gray-600 whitespace-nowrap min-h-touch hover:bg-gray-700 dark:hover:bg-gray-300';
  chip.textContent = label;
  return chip;
}
