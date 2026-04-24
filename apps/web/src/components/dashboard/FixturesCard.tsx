import Link from 'next/link'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Button } from '@/components/ui/Button'
import type { FixtureInfo } from '@/lib/api/dashboard'

function formatKickoff(isoString: string | null): string {
  if (!isoString) return 'TBC'
  const d = new Date(isoString)
  return d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' })
    + ' · '
    + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

function fixtureResult(f: FixtureInfo): string {
  if (f.home_score !== null && f.away_score !== null) {
    return `${f.home_score}–${f.away_score}`
  }
  return 'vs'
}

interface Props {
  fixtures: FixtureInfo[]
  gameweekName: string | null
}

export function FixturesCard({ fixtures, gameweekName }: Props) {
  return (
    <div>
      <SectionHeader
        title="Upcoming Fixtures"
        subtitle={gameweekName ?? undefined}
        action={
          <Link href="/fixtures">
            <Button variant="ghost" size="sm">All fixtures</Button>
          </Link>
        }
        className="mb-3"
      />
      {fixtures.length === 0 ? (
        <Card variant="flat">
          <p className="text-sm text-ink-muted text-center py-2">No fixtures yet</p>
        </Card>
      ) : (
        <div className="flex flex-col gap-2">
          {fixtures.map((f) => (
            <Card
              key={f.fixture_id}
              variant={f.has_squad_players ? 'tinted' : 'flat'}
              color={f.has_squad_players ? 'green' : undefined}
              padding="sm"
            >
              <div className="flex items-center justify-between text-sm">
                <span className="font-semibold text-ink w-[38%] text-right">
                  {f.home_team_short || f.home_team}
                </span>
                <div className="flex flex-col items-center gap-0.5 px-3 min-w-[60px]">
                  <span className="label-text text-ink-muted font-bold tabular-nums">
                    {fixtureResult(f)}
                  </span>
                  <span className="text-[0.6rem] text-ink-faint text-center leading-tight">
                    {formatKickoff(f.kickoff_at)}
                  </span>
                </div>
                <span className="font-semibold text-ink w-[38%]">
                  {f.away_team_short || f.away_team}
                </span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
