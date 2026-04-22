/**
 * Design tokens in JS/TS form.
 *
 * These mirror tailwind.config.ts. Use them when you need the values in
 * TypeScript (e.g. dynamic inline styles, runtime color lookups, tests).
 * For styling components, always prefer Tailwind classes.
 */

export const colors = {
  paper: {
    DEFAULT: '#F7F4EE',
    dark: '#EDE9DF',
    darker: '#E2DDD5',
  },
  ink: {
    DEFAULT: '#1C1917',
    muted: '#78716C',
    faint: '#C4BDB3',
  },
  marker: {
    green: '#2DB87A',
    blue: '#3B82F6',
    red: '#DC4040',
    yellow: '#F5C228',
    purple: '#8B5CF6',
    orange: '#F07530',
  },
  tint: {
    green: '#D4F5E4',
    blue: '#DBEAFE',
    red: '#FCE4E4',
    yellow: '#FEF3C7',
    purple: '#EDE9FE',
    orange: '#FDEBD6',
  },
} as const

// ── Domain-specific token maps ──────────────────────────────────────────────

export type Position = 'GK' | 'DEF' | 'MID' | 'FWD'
export type MarkerColor = 'green' | 'blue' | 'red' | 'yellow' | 'purple' | 'orange'
export type LeagueCode = 'PL' | 'PD' | 'BL1' | 'SA' | 'FL1'

export const positionMeta: Record<Position, { label: string; color: MarkerColor }> = {
  GK:  { label: 'GK',  color: 'yellow' },
  DEF: { label: 'DEF', color: 'blue'   },
  MID: { label: 'MID', color: 'green'  },
  FWD: { label: 'FWD', color: 'red'    },
}

export const leagueMeta: Record<LeagueCode, { name: string; short: string; color: MarkerColor }> = {
  PL:  { name: 'Premier League', short: 'PL',  color: 'purple' },
  PD:  { name: 'La Liga',        short: 'LAL', color: 'orange' },
  BL1: { name: 'Bundesliga',     short: 'BUN', color: 'red'    },
  SA:  { name: 'Serie A',        short: 'SA',  color: 'blue'   },
  FL1: { name: 'Ligue 1',        short: 'L1',  color: 'green'  },
}

// Salary cap in millions
export const SALARY_CAP_M = 100

// Max players from one club
export const MAX_PER_CLUB = 3

// Free transfers per gameweek
export const FREE_TRANSFERS = 2

// Transfer penalty (points per extra transfer)
export const TRANSFER_PENALTY = -4
