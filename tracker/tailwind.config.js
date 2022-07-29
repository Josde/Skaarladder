/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/**/*.{html,js}',
            './**/*.py',
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
