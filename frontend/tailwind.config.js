/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        champagne: {
          50:  '#FDFBF7',
          100: '#F7F3EC',
          200: '#EEE6D8',
          300: '#E0D0B8',
        },
      },
    },
  },
  plugins: [],
}
