import { Card } from '@/components/ui/Card'
import { Badge, PositionBadge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import type { CaptainInfo } from '@/lib/api/dashboard'
import type { Position } from '@/lib/design-tokens'

interface SingleCardProps {
  info: CaptainInfo
  role: 'C' | 'VC'
}

function CaptainSlot({ info, role }: SingleCardProps) {
  const isCap = role === 'C'
  return (
    <Card variant={isCap ? 'tinted' : 'flat'} color={isCap ? 'yellow' : undefined}>
      <div className="flex items-start justify-between mb-2">
        <PositionBadge position={info.position as Position} />
        <Badge color="yellow" variant={isCap ? 'solid' : 'outline'} size="sm">{role}</Badge>
      </div>
      <p className="font-display font-bold text-base text-ink leading-tight">
        {info.display_name ?? info.name}
      </p>
      <p className="text-xs text-ink-muted">{info.team_name}</p>
      <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-ink-faint">
        <span className="label-text text-ink-muted">GW pts</span>
        <span className="num text-xl text-marker-green">
          {info.gw_points !== null ? `${info.gw_points}` : '—'}
        </span>
      </div>
    </Card>
  )
}

interface Props {
  captain: CaptainInfo | null
  viceCaptain: CaptainInfo | null
  hasLineup: boolean
}

export function CaptainCard({ captain, viceCaptain, hasLineup }: Props) {
  return (
    <div className="mb-5">
      <SectionHeader title="Your Captain" className="mb-3" />
      {!hasLineup || (!captain && !viceCaptain) ? (
        <Card variant="flat">
          <p className="text-sm text-ink-muted text-center py-2">No lineup selected yet</p>
        </Card>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {captain && <CaptainSlot info={captain} role="C" />}
          {viceCaptain && <CaptainSlot info={viceCaptain} role="VC" />}
        </div>
      )}
    </div>
  )
}
