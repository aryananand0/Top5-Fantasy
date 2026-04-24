import { StatBox } from '@/components/ui/StatBox'
import type { DashboardSummary } from '@/lib/api/dashboard'

interface Props {
  data: DashboardSummary
}

export function ScoreStatsRow({ data }: Props) {
  const gwPts = data.gw_points !== null ? String(data.gw_points) : '—'
  const rank = data.gw_rank !== null ? `#${data.gw_rank.toLocaleString()}` : '—'
  const budget = `£${data.budget_remaining.toFixed(1)}M`

  return (
    <div className="grid grid-cols-3 gap-3 mb-5">
      <StatBox value={gwPts}   label="GW Points"   color="green"  />
      <StatBox value={rank}    label="Global Rank" color="purple" />
      <StatBox value={budget}  label="In the Bank" color="blue"   />
    </div>
  )
}
