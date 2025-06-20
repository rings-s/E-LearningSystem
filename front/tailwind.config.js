import forms from '@tailwindcss/forms';
import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    darkMode: 'class',
    theme: {
      extend: {
        animation: {
          'drawLine': 'drawLine 2s ease-out forwards',
          'expandWidth': 'expandWidth 1s ease-out forwards',
        },
        keyframes: {
          drawLine: {
            'to': {
              'stroke-dashoffset': '0',
              'opacity': '1'
            }
          },
          expandWidth: {
            'to': {
              'width': '100%'
            }
          }
        }
      },
    },
    plugins: [
      forms,
      typography,
    ],
};