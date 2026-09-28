/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'google-blue': '#4285F4',
        'google-red': '#EA4335',
        'google-yellow': '#FBBC05',
        'google-green': '#34A853',
        // same palette as the talk deck
        canvas: '#F8FAFD',
        ink: '#202124',
        muted: '#5F6368',
        line: '#DADCE0',
        faint: '#E8EAED',
        stage: {
          upload: '#4285F4',
          gemini: '#A142F4',
          banana: '#F9AB00',
          veo: '#34A853',
          share: '#EA4335',
        },
      },
      fontFamily: {
        sans: ['"Google Sans"', '"Google Sans Text"', '"DM Sans"', 'system-ui', 'sans-serif'],
        mono: ['"Roboto Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(60,64,67,0.08), 0 4px 16px rgba(60,64,67,0.06)',
        lift: '0 2px 6px rgba(60,64,67,0.10), 0 12px 32px rgba(60,64,67,0.10)',
      },
    },
  },
  plugins: [],
}
