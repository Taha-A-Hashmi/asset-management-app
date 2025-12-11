/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#0d6efd',
        success: '#198754',
        warning: '#ffc107',
      },
    },
  },
  plugins: [],
};
