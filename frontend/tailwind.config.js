/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'climate-blue': '#0ea5e9',
        'climate-green': '#10b981',
        'climate-red': '#ef4444',
        'climate-yellow': '#f59e0b',
        'climate-dark': '#0f172a',
        'climate-card': '#1e293b',
      },
    },
  },
  plugins: [],
}
