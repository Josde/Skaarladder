/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./tracker/templates/**/*.{html,js}',
    './tracker/**/*.py',
  ],
  theme: {
    extend: {
      'fontFamily': {
        'bebas': ['"Bebas Neue"']
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
