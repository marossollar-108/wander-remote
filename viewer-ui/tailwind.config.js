/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#EB002F',
          hover: '#C50028',
          light: '#FBCCD6',
          ring: '#F799AD',
        },
        tk: {
          black: '#1A1A1A',
          'black-80': '#484848',
          'black-60': '#777777',
          'black-40': '#A5A5A5',
          'black-20': '#D2D2D2',
          border: '#D2D2D2',
        },
        surface: '#F5F5F5',
      },
      fontFamily: {
        sans: ['Montserrat', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        btn: '8px',
        card: '12px',
        input: '6px',
      },
    },
  },
  plugins: [],
};
