/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f5f6ff",
          100: "#ebeeff",
          500: "#3d5af1",
          700: "#2639a7",
          900: "#131f59"
        }
      }
    },
  },
  plugins: [],
};
