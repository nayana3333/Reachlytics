import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111111",
        muted: "#737373",
        line: "#E5E5E5",
        canvas: "#FFFCF7",
        accent: "#111111",
        warning: "#737373",
        target: "#2563EB",
        outside: "#F97316",
        skipped: "#D4D4D4"
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"]
      },
      boxShadow: {
        instrument: "0 1px 3px rgba(0,0,0,0.06)"
      }
    }
  },
  plugins: []
};

export default config;
