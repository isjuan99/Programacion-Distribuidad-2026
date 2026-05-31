/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        gold: {
          DEFAULT: '#C9A84C',
          light:   '#DEC068',
          dark:    '#A8882E',
          muted:   '#9B7E3A',
        },
        aroma: {
          dark:    '#0A0A0A',
          darker:  '#050505',
          surface: '#141414',
          card:    '#1A1A1A',
          border:  '#2A2A2A',
          muted:   '#6B6B6B',
          text:    '#F5F0E8',
          cream:   '#EDE8DF',
        },
      },
      fontFamily: {
        serif:  ['Georgia', 'Cambria', '"Times New Roman"', 'serif'],
        sans:   ['"Helvetica Neue"', 'Helvetica', 'Arial', 'sans-serif'],
        display:['Georgia', 'serif'],
      },
      letterSpacing: {
        widest: '0.3em',
        ultra:  '0.5em',
      },
      backgroundImage: {
        'gold-gradient': 'linear-gradient(135deg, #C9A84C 0%, #DEC068 50%, #A8882E 100%)',
      },
    },
  },
  plugins: [],
}
