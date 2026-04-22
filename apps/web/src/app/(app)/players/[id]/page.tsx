import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge, PositionBadge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Button } from '@/components/ui/Button'
import { StatBox } from '@/components/ui/StatBox'
import { Divider } from '@/components/ui/Divider'
import { mockSquad, mockPlayerHistory, mockFixtures, mockGameweek } from '@/lib/mock-data'
import { leagueMeta } from '@/lib/design-tokens'
import { cn } from '@/lib/cn'
import Link from 'next/link'

export default async function PlayerDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const player  = mockSquad.find((p) => p.id === id) ?? mockSquad[6] // Salah as default
  const league  = leagueMeta[player.leagueCode]

  const totalGwPts = mockPlayerHistory.reduce((s, h) => s + h.pts, 0)
  const avgPts     = (totalGwPts / mockPlayerHistory.length).toFixed(1)
  const bestGw     = Math.max(...mockPlayerHistory.map((h) => h.pts))

  return (
    <PageShell maxWidth="lg">
      {/* ── Back link ───────────────────────────────────────────────────────── */}
      <div className="mb-4">
        <Link href="/squad">
          <Button variant="ghost" size="sm" className="text-ink-muted">← Back to Squad</Button>
        </Link>
      </div>

      {/* ── Player header ───────────────────────────────────────────────────── */}
      <Card variant="elevated" className="mb-5">
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-center gap-2 flex-wrap">
            <PositionBadge position={player.position} />
            <Badge color={league.color} variant="tinted" size="md">{league.short}</Badge>
            {player.isCaptain && <Badge color="yellow" variant="solid" size="md">Captain</Badge>}
          </div>
          <span className="font-display font-bold text-xl text-ink shrink-0">£{player.price}M</span>
        </div>

        <div className="mb-4">
          <h1 className="font-display font-extrabold text-3xl text-ink leading-tight">{player.name}</h1>
          <p className="text-ink-muted text-sm mt-1">{player.club} · {league.name}</p>
        </div>

        {/* Quick stats */}
        <div className="grid grid-cols-3 gap-3">
          <StatBox value={`${player.gwPts}`}  label={`GW${mockGameweek.number}`} color="green"  size="sm" />
          <StatBox value={`${player.totalPts}`} label="Season"                   color="blue"   size="sm" />
          <StatBox value={avgPts}             label="Avg / GW"                  color="ink"    size="sm" />
        </div>
      </Card>

      {/* ── Action buttons ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <Link href="/transfers">
          <Button variant="destructive" size="md" fullWidth>Transfer Out</Button>
        </Link>
        <Button variant="tinted" color="yellow" size="md" fullWidth>
          {player.isCaptain ? 'Remove Captain' : 'Make Captain'}
        </Button>
      </div>

      <Divider style="wavy" spacing="md" />

      {/* ── Recent scores ───────────────────────────────────────────────────── */}
      <SectionHeader title="Recent Scores" subtitle="Last 5 gameweeks" className="mb-3" />
      <div className="flex flex-col gap-2 mb-6">
        {mockPlayerHistory.map((h) => (
          <Card key={h.gw} variant="flat" padding="sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Badge color="ink" variant="outline" size="sm">GW{h.gw}</Badge>
                <div>
                  <p className="text-sm font-semibold text-ink">{h.opponent}</p>
                  <p className="text-xs text-ink-muted">{h.minutes} min</p>
                </div>
              </div>
              <span
                className={cn(
                  'num text-2xl',
                  h.pts >= 10 ? 'text-marker-green' : h.pts >= 6 ? 'text-marker-blue' : 'text-ink-muted',
                )}
              >
                {h.pts}
              </span>
            </div>
          </Card>
        ))}
      </div>

      {/* Best GW highlight */}
      <Card variant="tinted" color="green" className="mb-6">
        <p className="label-text text-ink-muted mb-1">Best gameweek (last 5)</p>
        <p className="num text-4xl text-marker-green">{bestGw} pts</p>
      </Card>

      <Divider style="dashed" spacing="md" />

      {/* ── Upcoming fixtures ───────────────────────────────────────────────── */}
      <SectionHeader title="Upcoming Fixtures" subtitle={player.club} className="mb-3" />
      <div className="flex flex-col gap-2">
        {mockFixtures.slice(0, 3).map((f) => {
          const isHome = f.home === player.club
          const opponent = isHome ? f.away : f.home
          return (
            <Card key={f.id} variant="flat" padding="sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge color={isHome ? 'green' : 'orange'} variant="tinted" size="sm">
                    {isHome ? 'H' : 'A'}
                  </Badge>
                  <span className="font-semibold text-sm text-ink">vs {opponent}</span>
                </div>
                <div className="text-right">
                  <p className="text-xs text-ink-muted">{f.date}</p>
                  <p className="text-xs text-ink-faint">{f.time}</p>
                </div>
              </div>
            </Card>
          )
        })}
      </div>
    </PageShell>
  )
}
