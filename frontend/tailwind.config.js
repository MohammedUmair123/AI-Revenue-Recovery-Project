/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#080D16",
          900: "#0B1220",
          800: "#131C2E",
          700: "#1C2740",
        },
        paper: "#EDEFF3",
        slate: {
          400: "#8B93A7",
          500: "#6B7386",
        },
        signal: {
          green: "#34D399",
          amber: "#F2A65A",
          red: "#EF6461",
        },
      },
      fontFamily: {
        mono: ["'IBM Plex Mono'", "monospace"],
        sans: ["'Inter'", "sans-serif"],
      },
    },
  },
  plugins: [],
};
