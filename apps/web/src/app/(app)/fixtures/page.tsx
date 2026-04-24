'use client'

import { useState, useEffect } from 'react'
import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Divider } from '@/components/ui/Divider'
import { fetchFixtures, type FixtureResponse } from '@/lib/api/fixtures'

// ── Competition filter config ──────────────────────────────────────────────────

const LEAGUES = [
  { code: '',    label: 'All',         color: 'ink'    },
  { code: 'PL',  label: 'Premier League', color: 'purple' },
  { code: 'PD',  label: 'La Liga',     color: 'orange' },
  { code: 'BL1', label: 'Bundesliga',  color: 'red'    },
  { code: 'SA',  label: 'Serie A',     color: 'blue'   },
  { code: 'FL1', label: 'Ligue 1',     color: 'green'  },
] as const

type LeagueCode = '' | 'PL' | 'PD' | 'BL1' | 'SA' | 'FL1'

// ── Date view tabs ─────────────────────────────────────────────────────────────

const DATE_WINDOWS = [
  { id: 'recent',   label: 'Recent',   daysBack: 3,  daysForward: 0 },
  { id: 'this',     label: 'This Week',daysBack: 1,  daysForward: 7 },
  { id: 'upcoming', label: 'Upcoming', daysBack: 0,  daysForward: 14 },
] as const

type WindowId = typeof DATE_WINDOWS[number]['id']

// ── Helpers ────────────────────────────────────────────────────────────────────

function formatKickoff(iso: string | null): { date: string; time: string } {
  if (!iso) return { date: 'TBC', time: '' }
  const d = new Date(iso)
  return {
    date: d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' }),
    time: d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }),
  }
}

function groupByDate(fixtures: FixtureResponse[]): Map<string, FixtureResponse[]> {
  const map = new Map<string, FixtureResponse[]>()
  for (const f of fixtures) {
    const { date } = formatKickoff(f.kickoff_at)
    if (!map.has(date)) map.set(date, [])
    map.get(date)!.push(f)
  }
  return map
}

function statusBadge(status: FixtureResponse['status'], score: boolean) {
  if (status === 'LIVE')      return <Badge color="red"    variant="tinted" size="sm">Live</Badge>
  if (status === 'FINISHED')  return <Badge color="ink"    variant="tinted" size="sm">FT</Badge>
  if (status === 'POSTPONED') return <Badge color="orange" variant="tinted" size="sm">PPD</Badge>
  if (score)                  return <Badge color="green"  variant="tinted" size="sm">Soon</Badge>
  return null
}

function leagueColor(code: string): string {
  const map: Record<string, string> = {
    PL: 'bg-tint-purple border-marker-purple',
    PD: 'bg-tint-orange border-marker-orange',
    BL1: 'bg-tint-red border-marker-red',
    SA: 'bg-tint-blue border-marker-blue',
    FL1: 'bg-tint-green border-marker-green',
  }
  return map[code] ?? 'bg-paper-dark border-ink-faint'
}

// ── Skeleton ───────────────────────────────────────────────────────────────────

function Skeleton() {
  return (
    <div className="space-y-3 animate-pulse">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="h-14 rounded-2xl bg-paper-darker border-2 border-ink-faint" />
      ))}
    </div>
  )
}

// ── Fixture row ────────────────────────────────────────────────────────────────

function FixtureCard({ fixture }: { fixture: FixtureResponse }) {
  const { time } = formatKickoff(fixture.kickoff_at)
  const hasScore = fixture.home_score !== null && fixture.away_score !== null

  return (
    <Card variant="default" padding="sm">
      <div className="flex items-center gap-2">
        {/* League dot */}
        <span
          className={`w-2 h-2 rounded-full border shrink-0 ${leagueColor(fixture.competition_code)}`}
          title={fixture.competition_name}
        />

        {/* Home team */}
        <span className="flex-1 text-right font-display font-bold text-sm text-ink truncate">
          {fixture.home_team_short}
        </span>

        {/* Score / time block */}
        <div className="shrink-0 w-24 flex flex-col items-center gap-0.5">
          {hasScore ? (
            <span className="font-display font-black text-base text-ink tabular-nums">
              {fixture.home_score} – {fixture.away_score}
            </span>
          ) : (
            <span className="text-xs font-bold text-ink-muted">{time || 'TBC'}</span>
          )}
          {statusBadge(fixture.status, !hasScore)}
        </div>

        {/* Away team */}
        <span className="flex-1 font-display font-bold text-sm text-ink truncate">
          {fixture.away_team_short}
        </span>
      </div>
    </Card>
  )
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function FixturesPage() {
  const [window, setWindow] = useState<WindowId>('this')
  const [league, setLeague] = useState<LeagueCode>('')
  const [fixtures, setFixtures] = useState<FixtureResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const cfg = DATE_WINDOWS.find((w) => w.id === window)!
    setLoading(true)
    setError(null)
    fetchFixtures({
      competition_code: league || undefined,
      days_back: cfg.daysBack,
      days_forward: cfg.daysForward,
    })
      .then((res) => setFixtures(res.fixtures))
      .catch(() => setError('Could not load fixtures.'))
      .finally(() => setLoading(false))
  }, [window, league])

  const grouped = groupByDate(fixtures)

  return (
    <PageShell maxWidth="lg">
      <SectionHeader title="Fixtures" subtitle="2025–26 season · All 5 leagues" className="mb-4" />

      {/* Date window tabs */}
      <div className="flex gap-2 mb-4">
        {DATE_WINDOWS.map((w) => (
          <button
            key={w.id}
            onClick={() => setWindow(w.id)}
            className={`px-3.5 py-1.5 rounded-lg text-sm font-semibold transition-all ${
              window === w.id
                ? 'bg-ink text-paper shadow-sketch-sm'
                : 'text-ink-muted hover:text-ink hover:bg-paper-dark'
            }`}
          >
            {w.label}
          </button>
        ))}
      </div>

      {/* League filter pills */}
      <div className="flex gap-2 flex-wrap mb-5 overflow-x-auto pb-1">
        {LEAGUES.map((l) => (
          <button
            key={l.code}
            onClick={() => setLeague(l.code as LeagueCode)}
            className={`px-3 py-1 rounded-full text-xs font-bold border-2 transition-all whitespace-nowrap ${
              league === l.code
                ? 'bg-ink text-paper border-ink'
                : 'bg-paper text-ink-muted border-ink-faint hover:border-ink hover:text-ink'
            }`}
          >
            {l.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading && <Skeleton />}

      {!loading && error && (
        <Card variant="flat" className="border-dashed py-8 text-center">
          <p className="text-sm text-ink-muted">{error}</p>
        </Card>
      )}

      {!loading && !error && fixtures.length === 0 && (
        <Card variant="flat" className="border-dashed py-8 text-center">
          <p className="font-display font-bold text-ink mb-1">No fixtures found</p>
          <p className="text-sm text-ink-muted">Try a different date range or league.</p>
        </Card>
      )}

      {!loading && !error && fixtures.length > 0 && (
        <div className="space-y-5">
          {Array.from(grouped.entries()).map(([date, dayFixtures], i) => (
            <div key={date}>
              {i > 0 && <Divider style="dashed" spacing="sm" />}
              <div className="flex items-center gap-3 mb-2">
                <span className="label-text text-ink-muted font-bold">{date}</span>
                <div className="flex-1 border-t border-dashed border-ink-faint" />
                <span className="text-xs text-ink-faint">{dayFixtures.length} matches</span>
              </div>
              <div className="flex flex-col gap-2">
                {dayFixtures.map((f) => (
                  <FixtureCard key={f.id} fixture={f} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </PageShell>
  )
}
