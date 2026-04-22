import Link from 'next/link'
import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge, PositionBadge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { StatBox } from '@/components/ui/StatBox'
import { Button } from '@/components/ui/Button'
import { EmptyState } from '@/components/ui/EmptyState'
import { Divider } from '@/components/ui/Divider'
import { mockGameweek, mockUser } from '@/lib/mock-data'

// Placeholder "available to transfer in" suggestions
const suggestions = [
  { id: 'a1', name: 'Mbappé',    club: 'Real Madrid', leagueCode: 'PD', position: 'FWD' as const, price: 13.5, gwPts: 15, form: 8.2 },
  { id: 'a2', name: 'Wirtz',     club: 'Leverkusen',  leagueCode: 'BL1', position: 'MID' as const, price: 8.5,  gwPts: 12, form: 7.9 },
  { id: 'a3', name: 'Osimhen',   club: 'Galatasaray', leagueCode: 'SA',  position: 'FWD' as const, price: 8.0,  gwPts: 10, form: 7.1 },
]

export default function TransfersPage() {
  const penaltyPts = 4

  return (
    <PageShell maxWidth="lg">
      {/* ── Status banner ───────────────────────────────────────────────────── */}
      <Card variant="tinted" color="blue" className="mb-5">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge color="blue" variant="solid" size="sm">GW{mockGameweek.number}</Badge>
              <Badge color="green" variant="tinted" size="sm">Transfers Open</Badge>
            </div>
            <p className="font-display font-bold text-xl text-ink">
              {mockGameweek.freeTransfers} free transfer{mockGameweek.freeTransfers !== 1 ? 's' : ''}
            </p>
            <p className="text-xs text-ink-muted mt-0.5">
              Extra transfers cost <span className="font-bold text-marker-red">−{penaltyPts} pts</span> each
            </p>
          </div>
          <div className="text-right">
            <p className="label-text text-ink-muted">Deadline</p>
            <p className="text-sm font-bold text-ink mt-0.5">{mockGameweek.deadline}</p>
          </div>
        </div>
      </Card>

      {/* ── Budget summary ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <StatBox value={`£${mockUser.budget}M`}       label="In the Bank"    color="green"  />
        <StatBox value={`£${mockUser.teamValue}M`}    label="Team Value"     color="blue"   />
        <StatBox value={`${mockGameweek.freeTransfers}`} label="Free Transfers" color="orange" />
      </div>

      {/* ── Transfer slots (empty — placeholder state) ───────────────────── */}
      <SectionHeader
        title="Pending Transfers"
        subtitle="Select a player from your squad to transfer out"
        className="mb-3"
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        {/* Player OUT slot */}
        <div>
          <p className="label-text text-marker-red mb-2">Player Out</p>
          <Card variant="flat" className="border-dashed border-ink-faint">
            <EmptyState
              icon={<span className="text-3xl" aria-hidden="true">−</span>}
              title="Select a player"
              description="Tap any player in your squad to mark them for transfer"
            />
          </Card>
        </div>

        {/* Player IN slot */}
        <div>
          <p className="label-text text-marker-green mb-2">Player In</p>
          <Card variant="flat" className="border-dashed border-ink-faint">
            <EmptyState
              icon={<span className="text-3xl" aria-hidden="true">+</span>}
              title="Choose replacement"
              description="Available after selecting a player to remove"
            />
          </Card>
        </div>
      </div>

      <Divider style="dashed" spacing="sm" />

      {/* ── Suggested transfers ─────────────────────────────────────────────── */}
      <SectionHeader
        title="Hot This Week"
        subtitle="Players in form worth considering"
        className="mb-3"
      />

      <div className="flex flex-col gap-2 mb-6">
        {suggestions.map((p) => (
          <Card key={p.id} variant="default" padding="sm">
            <div className="flex items-center gap-3">
              <PositionBadge position={p.position} />
              <div className="flex-1 min-w-0">
                <p className="font-display font-bold text-sm text-ink">{p.name}</p>
                <p className="text-xs text-ink-muted">{p.club}</p>
              </div>
              <div className="text-right shrink-0">
                <p className="num text-base text-marker-green">{p.gwPts} pts</p>
                <p className="text-xs text-ink-muted">Form {p.form}</p>
              </div>
              <div className="text-right shrink-0">
                <p className="font-bold text-sm text-ink">£{p.price}M</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* ── Actions ─────────────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-3">
        <Button variant="primary" size="md" fullWidth disabled>
          Confirm Transfers (0 pending)
        </Button>
        <Link href="/squad">
          <Button variant="ghost" size="md" fullWidth>← Back to Squad</Button>
        </Link>
      </div>
    </PageShell>
  )
}
