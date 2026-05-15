import { initTheme } from './theme.js';

initTheme();

document.getElementById('app').innerHTML = `
  <div class="flex items-center justify-center min-h-screen text-gray-500">
    <p>Connecting to CAN bridge...</p>
  </div>
`;
