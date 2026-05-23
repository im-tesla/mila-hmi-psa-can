import './style.css';
import { initTheme, toggleTheme } from './theme.js';
import { createWsClient } from './ws-client.js';
import { updateSignal } from './state.js';
import { createTabBar, updateTabBarConnection } from './components/tab-bar.js';
import { createSearchBar } from './components/search-bar.js';
import { createSectionList } from './components/section-list.js';
import { createSettingsPanel } from './components/settings-panel.js';
import { createDebugPanel } from './components/debug-panel.js';

initTheme();

const app = document.getElementById('app');
app.innerHTML = '';
app.style.display = 'flex';
app.style.flexDirection = 'column';
app.style.height = '100vh';
app.style.overflow = 'hidden';

// Tab bar
const tabBar = createTabBar({ onTabChange: switchTab });
app.appendChild(tabBar);
document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

// --- Dashboard panel ---
const dashboardPanel = document.createElement('div');
dashboardPanel.id = 'panel-dashboard';
dashboardPanel.className = 'flex-1 overflow-auto';

let currentSearch = '';
let currentCategory = null;

const searchBar = createSearchBar({
  onSearch: (query) => { currentSearch = query; applyFilters(); },
  onCategoryChange: (section) => { currentCategory = section; applyFilters(); },
});
dashboardPanel.appendChild(searchBar);

const { container: sectionList, sections } = createSectionList();
dashboardPanel.appendChild(sectionList);
app.appendChild(dashboardPanel);

// --- Debug panel ---
const { element: debugEl, onFrame } = createDebugPanel();
debugEl.id = 'panel-debug';
debugEl.style.display = 'none';
app.appendChild(debugEl);

// --- Settings panel ---
const settingsEl = createSettingsPanel();
settingsEl.id = 'panel-settings';
settingsEl.style.display = 'none';
settingsEl.style.flex = '1';
settingsEl.style.overflowY = 'auto';
app.appendChild(settingsEl);

// --- Tab switching ---
function switchTab(tab) {
  dashboardPanel.style.display = tab === 'dashboard' ? '' : 'none';
  debugEl.style.display = tab === 'debug' ? '' : 'none';
  settingsEl.style.display = tab === 'settings' ? '' : 'none';
}

// --- WebSocket ---
const wsClient = createWsClient({
  onStatusChange: (status) => updateTabBarConnection(status),
  onMessage: (msg) => {
    onFrame(msg);
    if (msg.data) {
      const { id: canId, ts, raw } = msg;
      for (const [name, value] of Object.entries(msg.data)) {
        updateSignal(canId, name, value, ts, raw);
      }
    }
  },
});

wsClient.connect();

// --- Filter logic ---
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
