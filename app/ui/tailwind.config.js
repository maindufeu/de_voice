/** @type {import('tailwindcss').Config} */
import daisyui from 'daisyui';
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'softtek': {
          'primary': '#004254',
          'primary-dark': '#002532', 
          'accent': '#FF0054',
          'neutral': '#646459',
          'neutral-light': '#AAAA9F',
        }
      }
    },
  },
  daisyui: {
    themes: [
      {
        softtek: {
          "primary": "#004254",
          "primary-content": "#ffffff",
          "secondary": "#FF0054", 
          "secondary-content": "#ffffff",
          "accent": "#FF0054",
          "accent-content": "#ffffff",
          "neutral": "#646459",
          "neutral-content": "#000000",
          "base-100": "#ffffff",
          "base-200": "#F5F5F5",
          "base-300": "#E3E2DA",
          "base-content": "#1f2937",
          "info": "#3ABFF8",
          "success": "#36D399", 
          "warning": "#FBBD23",
          "error": "#F87272",
        }
      },
      // 'light', 
      //'dark', 
      //'cupcake'
    ],
  },
  plugins: [daisyui],
};
