/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.js'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        display: ['"Rajdhani"', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Cascadia Code"', 'monospace'],
      },
      minHeight: {
        touch: '44px',
      },
      boxShadow: {
        popover: '0 0 0 1px rgba(230,168,23,0.3), 0 8px 32px rgba(0,0,0,0.6)',
      },
    },
  },
  plugins: [],
};
