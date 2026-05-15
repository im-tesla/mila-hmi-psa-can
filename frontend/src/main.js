import './style.css';
import { initTheme, toggleTheme } from './theme.js';
import { createWsClient } from './ws-client.js';
import { updateSignal } from './state.js';
import { createConnectionBar, updateConnectionBar } from './components/connection-bar.js';
import { createSearchBar } from './components/search-bar.js';
import { createSectionList } from './components/section-list.js';
import { SECTIONS } from './can-definitions.js';

initTheme();

const app = document.getElementById('app');
app.innerHTML = '';

// Connection bar
const connBar = createConnectionBar();
app.appendChild(connBar);

// Theme toggle
document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

// Search bar
let currentSearch = '';
let currentCategory = null;

const searchBar = createSearchBar({
  onSearch: (query) => {
    currentSearch = query;
    applyFilters();
  },
  onCategoryChange: (section) => {
    currentCategory = section;
    applyFilters();
  },
});
app.appendChild(searchBar);

// Section list
const { container: sectionList, sections } = createSectionList();
app.appendChild(sectionList);

// WebSocket
const wsClient = createWsClient({
  onStatusChange: (status) => updateConnectionBar(status),
  onMessage: (msg) => {
    const canId = msg.id;
    const ts = msg.ts;
    const raw = msg.raw;
    if (msg.data) {
      for (const [name, value] of Object.entries(msg.data)) {
        updateSignal(canId, name, value, ts, raw);
      }
    }
  },
});

wsClient.connect();

// Filter logic
function applyFilters() {
  for (const { def, element } of sections) {
    const matchesCategory = !currentCategory || def.name === currentCategory.name;
    const hasSearchMatch = !currentSearch || sectionMatchesSearch(def, currentSearch);
    element.style.display = (matchesCategory && hasSearchMatch) ? '' : 'none';
  }
}

function sectionMatchesSearch(sectionDef, query) {
  if (sectionDef.name.toLowerCase().includes(query)) return true;
  for (const canId of sectionDef.canIds) {
    if (canId.toLowerCase().includes(query)) return true;
  }
  return false;
}
