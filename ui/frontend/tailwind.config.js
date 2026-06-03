/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      colors: {
        base:    '#080c18',
        panel:   '#0c1120',
        surface: '#101827',
        hover:   '#162036',
        active:  '#1a2540',
        accent:  '#00e5b3',
        border:  '#1e2d45',
      },
      animation: {
        'spin-custom': 'spin 1s linear infinite',
        'fadeIn': 'fadeIn 0.25s ease forwards',
      },
    },
  },
  plugins: [],
}
