// front/tailwind.config.js
import forms from '@tailwindcss/forms';
import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    darkMode: 'class',
    theme: {
      extend: {
        fontFamily: {
          'sans': ['Inter', 'system-ui', 'sans-serif'],
          'display': ['Clash Display', 'Inter', 'sans-serif'],
          'arabic': ['Cairo', 'Noto Sans Arabic', 'system-ui', 'sans-serif'],
          'arabic-display': ['Readex Pro', 'Cairo', 'sans-serif'],
        },
        colors: {
          // Trendy 2024 Color Palette - "Aurora Dreams"
          'aurora': {
            50: '#fef3ff',
            100: '#fce7ff',
            200: '#facfff',
            300: '#f7a8ff',
            400: '#f370ff',
            500: '#e638ff',
            600: '#c61aed',
            700: '#a70fc4',
            800: '#8a109f',
            900: '#721481',
            950: '#4d0056',
          },
          'nebula': {
            50: '#f0f9ff',
            100: '#e0f2fe',
            200: '#bae6fd',
            300: '#7dd3fc',
            400: '#38bdf8',
            500: '#0ea5e9',
            600: '#0284c7',
            700: '#0369a1',
            800: '#075985',
            900: '#0c4a6e',
            950: '#082f49',
          },
          'cosmic': {
            50: '#fefce8',
            100: '#fef9c3',
            200: '#fef08a',
            300: '#fde047',
            400: '#facc15',
            500: '#eab308',
            600: '#ca8a04',
            700: '#a16207',
            800: '#854d0e',
            900: '#713f12',
            950: '#422006',
          },
          'stellar': {
            50: '#f0fdf4',
            100: '#dcfce7',
            200: '#bbf7d0',
            300: '#86efac',
            400: '#4ade80',
            500: '#22c55e',
            600: '#16a34a',
            700: '#15803d',
            800: '#166534',
            900: '#14532d',
            950: '#052e16',
          },
        },
        backdropBlur: {
          xs: '2px',
        },
        animation: {
          'float': 'float 6s ease-in-out infinite',
          'glow': 'glow 2s ease-in-out infinite alternate',
          'slide-in': 'slideIn 0.3s ease-out',
          'slide-out': 'slideOut 0.3s ease-out',
          'icon-bounce': 'iconBounce 0.5s ease-out',
          'pulse-glow': 'pulseGlow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        },
        keyframes: {
          float: {
            '0%, 100%': { transform: 'translateY(0)' },
            '50%': { transform: 'translateY(-10px)' },
          },
          glow: {
            'from': { 'box-shadow': '0 0 10px rgba(230, 56, 255, 0.5), 0 0 20px rgba(230, 56, 255, 0.3)' },
            'to': { 'box-shadow': '0 0 20px rgba(230, 56, 255, 0.8), 0 0 30px rgba(230, 56, 255, 0.5)' },
          },
          slideIn: {
            'from': { transform: 'translateX(-100%)' },
            'to': { transform: 'translateX(0)' },
          },
          slideOut: {
            'from': { transform: 'translateX(0)' },
            'to': { transform: 'translateX(-100%)' },
          },
          iconBounce: {
            '0%, 100%': { transform: 'scale(1)' },
            '50%': { transform: 'scale(1.2)' },
          },
          pulseGlow: {
            '0%, 100%': { opacity: 1, transform: 'scale(1)' },
            '50%': { opacity: 0.8, transform: 'scale(1.05)' },
          },
        },
        fontSize: {
          'xs': ['0.75rem', { lineHeight: '1rem' }],
          'sm': ['0.875rem', { lineHeight: '1.25rem' }],
          'base': ['1rem', { lineHeight: '1.5rem' }],
          'lg': ['1.125rem', { lineHeight: '1.75rem' }],
          'xl': ['1.25rem', { lineHeight: '1.75rem' }],
          '2xl': ['1.5rem', { lineHeight: '2rem' }],
          '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
          '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
          '5xl': ['3rem', { lineHeight: '1' }],
          '6xl': ['3.75rem', { lineHeight: '1' }],
          '7xl': ['4.5rem', { lineHeight: '1' }],
          '8xl': ['6rem', { lineHeight: '1' }],
          '9xl': ['8rem', { lineHeight: '1' }],
        },
      },
    },
    plugins: [
      forms,
      typography,
    ],
};