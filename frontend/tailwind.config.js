/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#07080f',
        panel: '#12131f',
        glass: 'rgba(255,255,255,0.06)',
        spotify: '#1DB954',
        apple: '#FA243C',
        glow: '#7c5cff',
      },
      boxShadow: {
        glass: '0 8px 32px rgba(0,0,0,0.45)',
        neon: '0 0 40px rgba(124,92,255,0.35)',
      },
      backgroundImage: {
        'mesh':
          'radial-gradient(ellipse at 20% 20%, rgba(29,185,84,0.18), transparent 50%), radial-gradient(ellipse at 80% 0%, rgba(250,36,60,0.16), transparent 45%), radial-gradient(ellipse at 50% 80%, rgba(124,92,255,0.2), transparent 50%)',
      },
      fontFamily: {
        display: ['"Segoe UI"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
