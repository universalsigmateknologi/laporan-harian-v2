/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  theme: {
    extend: {
          colors: {
            navy: {
              50:  '#f0f3f9',
              100: '#dce3f0',
              200: '#b8c7e1',
              300: '#8da3cc',
              400: '#637fb5',
              500: '#3d5a8a',
              600: '#2e4770',
              700: '#1e3355',
              800: '#152540',
              900: '#0d1a2d',
              950: '#070e1a',
            }
            // navy: {
            //   50:  '#fdf2f4',
            //   100: '#fbe4e8',
            //   200: '#f7ccd5',
            //   300: '#f1a8b8',
            //   400: '#e67c93',
            //   500: '#d14d6c',
            //   600: '#b33251',
            //   700: '#801a31', // Warna Maroon Klasik
            //   800: '#5c1022',
            //   900: '#410b18',
            //   950: '#26040b',
            // }
          },
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
          }
        },
  },
  plugins: [],
}

