/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.js'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'signal-ok': '#16a34a',
        'signal-warn': '#e07b00',
        'signal-fault': '#dc2626',
        'signal-inactive': '#6b7280',
      },
      minHeight: {
        'touch': '44px',
      },
    },
  },
  plugins: [],
};
