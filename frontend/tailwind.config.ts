import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Orange asosiy palitra (sutli krem fon bilan birga)
        primary: {
          50: "#fff3e6",
          100: "#ffe1c2",
          200: "#ffc894",
          300: "#ffaa5c",
          400: "#ff8f33",
          500: "#ff7a00",
          600: "#e66a00",
          700: "#c25600",
          800: "#9c4500",
          900: "#7a3600",
          DEFAULT: "#ff7a00",
        },
        // Sutli krem fon palitra
        cream: {
          DEFAULT: "#fff8f0",
          100: "#fffaf4",
          200: "#fff3e6",
          300: "#ffead2",
        },
        success: "#16a34a",
        danger: "#e11d48",
        warning: "#f59e0b",
      },
      fontFamily: {
        sans: ["var(--font-manrope)", "system-ui", "sans-serif"],
      },
      borderRadius: {
        xl: "0.875rem",
        "2xl": "1.25rem",
        "3xl": "1.75rem",
      },
      boxShadow: {
        card: "0 1px 3px rgba(120,60,0,0.06), 0 1px 2px rgba(120,60,0,0.04)",
        hover: "0 10px 30px rgba(255,122,0,0.18)",
        glow: "0 0 0 4px rgba(255,122,0,0.12)",
      },
      keyframes: {
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.96)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        float: {
          "0%,100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "float-slow": {
          "0%,100%": { transform: "translateY(0) scale(1)" },
          "50%": { transform: "translateY(-16px) scale(1.05)" },
        },
        "pulse-ring": {
          "0%": { transform: "scale(0.9)", opacity: "0.7" },
          "70%,100%": { transform: "scale(1.6)", opacity: "0" },
        },
        "gradient-shift": {
          "0%,100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
      },
      animation: {
        shimmer: "shimmer 1.5s infinite",
        "fade-up": "fade-up 0.4s ease-out both",
        "fade-in": "fade-in 0.5s ease-out both",
        "scale-in": "scale-in 0.3s ease-out both",
        float: "float 5s ease-in-out infinite",
        "float-slow": "float-slow 7s ease-in-out infinite",
        "pulse-ring": "pulse-ring 1.8s cubic-bezier(0.4,0,0.6,1) infinite",
        "gradient-shift": "gradient-shift 6s ease infinite",
      },
    },
  },
  plugins: [],
};

export default config;
