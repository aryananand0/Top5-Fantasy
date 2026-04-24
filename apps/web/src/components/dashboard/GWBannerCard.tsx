import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import type { DashboardSummary } from '@/lib/api/dashboard'

function formatDeadline(isoString: string | null): string {
  if (!isoString) return '—'
  const d = new Date(isoString)
  return d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function statusColor(status: string | null): 'green' | 'orange' | 'red' | 'yellow' {
  switch (status) {
    case 'ACTIVE':   return 'green'
    case 'SCORING':  return 'orange'
    case 'FINISHED': return 'red'
    default:         return 'yellow'
  }
}

function statusLabel(status: string | null): string {
  switch (status) {
    case 'UPCOMING':  return 'Upcoming'
    case 'LOCKED':    return 'Locked'
    case 'ACTIVE':    return 'Active'
    case 'SCORING':   return 'Scoring'
    case 'FINISHED':  return 'Final'
    default:          return 'Unknown'
  }
}

interface Props {
  data: DashboardSummary
}

export function GWBannerCard({ data }: Props) {
  const scored = data.gw_points !== null

  return (
    <Card variant="tinted" color="yellow" className="mb-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge color="yellow" variant="solid" size="sm">
              {data.gameweek_name ?? 'No gameweek'}
            </Badge>
            {data.gameweek_status && (
              <Badge color={statusColor(data.gameweek_status)} variant="tinted" size="sm">
                {statusLabel(data.gameweek_status)}
              </Badge>
            )}
          </div>

          {scored ? (
            <>
              <p className="font-display font-extrabold text-4xl text-ink leading-none tabular-nums">
                {data.gw_points}
                <span className="text-lg font-semibold text-ink-muted ml-1.5">pts</span>
              </p>
              {data.gw_transfer_cost > 0 && (
                <p className="text-xs text-ink-muted mt-1">
                  −{data.gw_transfer_cost} pts transfer hit · {data.gw_raw_points} raw
                </p>
              )}
            </>
          ) : (
            <p className="font-display font-bold text-2xl text-ink-muted leading-none mt-1">
              {data.has_lineup ? 'Score pending' : 'No lineup set'}
            </p>
          )}
        </div>

        <div className="text-right shrink-0">
          <p className="label-text text-ink-muted">Deadline</p>
          <p className="text-sm font-bold text-ink mt-0.5">{formatDeadline(data.deadline_at)}</p>
          {data.can_transfer && (
            <Badge color="orange" variant="tinted" size="sm" className="mt-2">
              {data.free_transfers} free transfer{data.free_transfers !== 1 ? 's' : ''}
            </Badge>
          )}
        </div>
      </div>
    </Card>
  )
}
