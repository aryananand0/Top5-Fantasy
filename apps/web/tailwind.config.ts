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
        // ── Surface ──────────────────────────────────────────────
        paper: {
          DEFAULT: '#F7F4EE', // warm cream — main background
          dark: '#EDE9DF',    // secondary surfaces, pressed states
          darker: '#E2DDD5',  // tertiary surfaces, deep hover
        },
        // ── Ink ──────────────────────────────────────────────────
        ink: {
          DEFAULT: '#1C1917', // near-black (warm, not cold)
          muted: '#78716C',   // secondary text
          faint: '#C4BDB3',   // borders, dividers, placeholders
        },
        // ── Marker accents (pen-on-paper feel) ───────────────────
        marker: {
          green: '#2DB87A',   // goals, positive, success
          blue: '#3B82F6',    // assists, info
          red: '#DC4040',     // cards, negative, danger
          yellow: '#F5C228',  // captain, highlight, gold
          purple: '#8B5CF6',  // leagues, premium
          orange: '#F07530',  // price, transfer cost
        },
        // ── Tints (light fills for badges, cards) ────────────────
        tint: {
          green: '#D4F5E4',
          blue: '#DBEAFE',
          red: '#FCE4E4',
          yellow: '#FEF3C7',
          purple: '#EDE9FE',
          orange: '#FDEBD6',
        },
      },

      fontFamily: {
        display: ['var(--font-syne)', 'sans-serif'],
        sans: ['var(--font-nunito)', 'sans-serif'],
      },

      fontSize: {
        // Stat numbers — big, bold, tabular
        'stat-sm': ['2rem', { lineHeight: '1', fontWeight: '800' }],
        'stat-md': ['3rem', { lineHeight: '1', fontWeight: '800' }],
        'stat-lg': ['4rem', { lineHeight: '1', fontWeight: '800' }],
      },

      borderWidth: {
        '3': '3px',
      },

      // Sketch shadows: offset with zero blur — the core visual signature
      boxShadow: {
        'sketch-sm': '2px 2px 0px #1C1917',
        'sketch':    '3px 3px 0px #1C1917',
        'sketch-md': '4px 4px 0px #1C1917',
        'sketch-lg': '6px 6px 0px #1C1917',
      },

      borderRadius: {
        '2xl': '1.25rem', // 20px — default card radius
        '3xl': '1.75rem', // 28px — large surfaces
      },

      spacing: {
        'page': '1.25rem',    // 20px — mobile horizontal padding
        'page-md': '2rem',    // 32px — desktop horizontal padding
      },
    },
  },
  plugins: [],
}

export default config
