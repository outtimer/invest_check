module.exports = {
  content: [
    './src/views/*.ejs',
    './src/public/**/*.js'
  ],
  theme: {
    extend: {
      colors: {
        'brand-blue': '#0ea5ff',
        'brand-green': '#10b981',
        'brand-red': '#ef4444',
        'bg-main': '#0b0e11',
        'card': '#151921'
      }
    }
  },
  plugins: []
};
