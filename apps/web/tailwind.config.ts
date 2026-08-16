import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'forge': {
          bg:        '#0a0a0f',
          surface:   '#111118',
          border:    'rgba(255,255,255,0.08)',
          blue:      '#4488FF',
          blueLight: '#6aa3ff',
          text:      '#f0f0f0',
          muted:     '#888899',
          red:       '#FF4444',
          gold:      '#FFD700',
          grey:      '#888888',
        },
        'vex': {
          bg:      '#0c0c0c',
          surface: '#141414',
          border:  '#1a1a1a',
          text:    '#f5f0eb',
          muted:   '#6b6b6b',
          accent:  '#c8b89a',
          dim:     '#8a7d6a',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      animation: {
        'fade-up':   'fadeUp 0.6s ease forwards',
        'fade-in':   'fadeIn 0.4s ease forwards',
        'spin-slow': 'spin 8s linear infinite',
      },
      keyframes: {
        fadeUp: {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

export default config
