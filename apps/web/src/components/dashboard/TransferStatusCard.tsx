import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import type { DashboardSummary } from '@/lib/api/dashboard'

interface Props {
  data: DashboardSummary
}

export function TransferStatusCard({ data }: Props) {
  const extraTransfers = Math.max(0, data.transfers_made - data.free_transfers)

  return (
    <div className="mb-5">
      <SectionHeader title="Transfers" className="mb-3" />
      <Card variant="flat" padding="sm">
        <div className="grid grid-cols-3 divide-x divide-ink-faint">
          <div className="flex flex-col items-center px-3 py-1">
            <span className="num text-2xl text-ink">{data.free_transfers}</span>
            <span className="label-text text-ink-muted mt-0.5">Free</span>
          </div>
          <div className="flex flex-col items-center px-3 py-1">
            <span className="num text-2xl text-ink">{data.transfers_made}</span>
            <span className="label-text text-ink-muted mt-0.5">Made</span>
          </div>
          <div className="flex flex-col items-center px-3 py-1">
            {data.transfer_hit > 0 ? (
              <Badge color="red" variant="tinted" size="sm" className="mt-1">
                −{data.transfer_hit} pts
              </Badge>
            ) : extraTransfers > 0 ? (
              <Badge color="orange" variant="tinted" size="sm" className="mt-1">
                −{extraTransfers * 4} pts
              </Badge>
            ) : (
              <span className="num text-2xl text-marker-green">0</span>
            )}
            <span className="label-text text-ink-muted mt-0.5">Hit</span>
          </div>
        </div>
      </Card>
    </div>
  )
}
