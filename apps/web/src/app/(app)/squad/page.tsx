import Link from 'next/link'
import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge, PositionBadge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Button } from '@/components/ui/Button'
import { Divider } from '@/components/ui/Divider'
import { mockSquad, mockGameweek, mockUser } from '@/lib/mock-data'
import { cn } from '@/lib/cn'
import type { MockPlayer } from '@/lib/mock-data'

const starters = mockSquad.filter((p) => p.isStarting)
const bench    = mockSquad.filter((p) => !p.isStarting)
const gk  = starters.filter((p) => p.position === 'GK')
const def = starters.filter((p) => p.position === 'DEF')
const mid = starters.filter((p) => p.position === 'MID')
const fwd = starters.filter((p) => p.position === 'FWD')

const totalGwPts = starters.reduce((sum, p) => {
  const pts = p.isCaptain ? p.gwPts * 2 : p.gwPts
  return sum + pts
}, 0)

// ── Pitch slot ───────────────────────────────────────────────────────────────
function PitchSlot({ player, dark = false }: { player: MockPlayer; dark?: boolean }) {
  const initial = player.name.charAt(0)
  const shortName = player.name.split(' ')[0]
  const pts = player.isCaptain ? player.gwPts * 2 : player.gwPts

  return (
    <div className="flex flex-col items-center gap-1.5 min-w-0">
      <div className="relative">
        <div className="w-10 h-10 rounded-full bg-paper border-2 border-ink shadow-sketch-sm flex items-center justify-center">
          <span className="text-xs font-black text-ink leading-none">{initial}</span>
        </div>
        {player.isCaptain && (
          <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-marker-yellow border border-ink flex items-center justify-center">
            <span className="text-[0.5rem] font-black text-ink leading-none">C</span>
          </div>
        )}
        {player.isVC && (
          <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-ink border border-ink flex items-center justify-center">
            <span className="text-[0.5rem] font-black text-paper leading-none">V</span>
          </div>
        )}
      </div>
      <div className="flex flex-col items-center gap-0.5">
        <span className={cn('text-[0.65rem] font-bold leading-none truncate max-w-[56px] text-center', dark ? 'text-white' : 'text-ink')}>
          {shortName}
        </span>
        <span className={cn('text-[0.6rem] leading-none', dark ? 'text-white/60' : 'text-ink-muted')}>
          {pts}pts
        </span>
      </div>
    </div>
  )
}

// ── Formation row ────────────────────────────────────────────────────────────
function PitchRow({ players, label }: { players: MockPlayer[]; label: string }) {
  return (
    <div className="flex flex-col items-center gap-2">
      <span className="label-text text-white/50 text-center">{label}</span>
      <div className="flex items-center justify-center gap-2 sm:gap-4 w-full">
        {players.map((p) => (
          <PitchSlot key={p.id} player={p} dark />
        ))}
      </div>
    </div>
  )
}

export default function SquadPage() {
  const formation = `${def.length}-${mid.length}-${fwd.length}`
  const budgetUsed = 100 - mockUser.budget
  const budgetPct  = (budgetUsed / 100) * 100

  return (
    <PageShell maxWidth="lg">
      {/* ── Header row ──────────────────────────────────────────────────────── */}
      <SectionHeader
        title="My Squad"
        subtitle={`GW${mockGameweek.number} · Formation ${formation}`}
        action={
          <Link href="/transfers">
            <Button variant="tinted" color="blue" size="sm">Transfers</Button>
          </Link>
        }
        className="mb-4"
      />

      {/* ── Budget bar ──────────────────────────────────────────────────────── */}
      <Card variant="flat" padding="sm" className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="label-text text-ink-muted">Budget used</span>
          <span className="font-display font-bold text-sm text-ink">
            £{budgetUsed.toFixed(1)}M / £100M
          </span>
        </div>
        <div className="h-3 bg-paper-dark border-2 border-ink rounded-full overflow-hidden">
          <div
            className="h-full bg-ink rounded-full transition-all"
            style={{ width: `${budgetPct}%` }}
          />
        </div>
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs text-ink-muted">
            <span className="font-bold text-marker-green">£{mockUser.budget}M</span> remaining
          </span>
          <Badge color="orange" variant="tinted" size="sm">Team Value £{mockUser.teamValue}M</Badge>
        </div>
      </Card>

      {/* ── Pitch ───────────────────────────────────────────────────────────── */}
      <div className="rounded-2xl border-2 border-ink overflow-hidden shadow-sketch-md mb-4">
        {/* Playing surface */}
        <div className="bg-[#2E7D52] p-4 space-y-5">
          {/* Centre line */}
          <div className="w-full border-t border-white/10 pt-2" />
          <PitchRow players={fwd} label="FWD" />
          <PitchRow players={mid} label="MID" />
          <PitchRow players={def} label="DEF" />
          <PitchRow players={gk}  label="GK"  />
        </div>

        {/* Bench */}
        <div className="bg-paper-dark border-t-2 border-ink p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="label-text text-ink-muted">Bench</span>
            <span className="text-xs text-ink-muted">Auto-substitutions active</span>
          </div>
          <div className="flex items-center justify-around">
            {bench.map((p) => (
              <PitchSlot key={p.id} player={p} />
            ))}
          </div>
        </div>
      </div>

      {/* ── GW points summary ───────────────────────────────────────────────── */}
      <Card variant="flat" padding="sm" className="mb-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="label-text text-ink-muted">Gameweek {mockGameweek.number} points</p>
            <p className="num text-3xl text-marker-green mt-1">{totalGwPts}</p>
          </div>
          <div className="text-right">
            <p className="label-text text-ink-muted">Captain bonus</p>
            <p className="num text-2xl text-marker-yellow mt-1">
              +{mockSquad.find(p => p.isCaptain)?.gwPts ?? 0}
            </p>
          </div>
        </div>
      </Card>

      <Divider style="wavy" spacing="sm" />

      {/* ── Player list ─────────────────────────────────────────────────────── */}
      <SectionHeader title="Player Details" className="mb-3 mt-1" />
      <div className="flex flex-col gap-2">
        {starters.map((player) => (
          <Link key={player.id} href={`/players/${player.id}`}>
            <Card variant="flat" padding="sm" className="hover:-translate-y-px transition-transform">
              <div className="flex items-center gap-3">
                <PositionBadge position={player.position} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="font-display font-bold text-sm text-ink truncate">{player.name}</span>
                    {player.isCaptain && <Badge color="yellow" variant="solid" size="sm">C</Badge>}
                    {player.isVC && <Badge color="ink" variant="outline" size="sm">VC</Badge>}
                  </div>
                  <span className="text-xs text-ink-muted">{player.club}</span>
                </div>
                <div className="text-right shrink-0">
                  <span className="num text-lg text-ink">{player.isCaptain ? player.gwPts * 2 : player.gwPts}</span>
                  <span className="text-xs text-ink-muted ml-0.5">pts</span>
                </div>
                <span className="font-bold text-sm text-ink-muted">£{player.price}M</span>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </PageShell>
  )
}
