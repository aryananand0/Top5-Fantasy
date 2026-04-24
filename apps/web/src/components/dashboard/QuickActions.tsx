import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import type { DashboardSummary } from '@/lib/api/dashboard'

interface Props {
  data: DashboardSummary
}

export function QuickActions({ data }: Props) {
  const showTransfer = data.can_transfer
  const showLineup = data.is_editable && data.has_squad

  if (!showTransfer && !showLineup && data.has_squad) {
    // GW locked / active / finished — just show squad view
    return (
      <div className="mb-6">
        <Link href="/squad">
          <Button variant="secondary" size="md" fullWidth>View Squad</Button>
        </Link>
      </div>
    )
  }

  if (!data.has_squad) {
    return (
      <div className="mb-6">
        <Link href="/squad">
          <Button variant="tinted" color="green" size="md" fullWidth>
            Build Your Squad
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 gap-3 mb-6">
      {showTransfer && (
        <Link href="/transfers">
          <Button variant="tinted" color="blue" size="md" fullWidth>
            Make Transfer
          </Button>
        </Link>
      )}
      <Link href={showLineup ? '/lineup' : '/squad'}>
        <Button variant="secondary" size="md" fullWidth>
          {showLineup ? 'Set Lineup' : 'View Squad'}
        </Button>
      </Link>
    </div>
  )
}
