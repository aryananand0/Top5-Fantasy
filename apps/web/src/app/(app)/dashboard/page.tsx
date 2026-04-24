'use client'

import { PageShell } from '@/components/ui/PageShell'
import { Divider } from '@/components/ui/Divider'
import { useDashboard } from '@/hooks/useDashboard'
import { GWBannerCard } from '@/components/dashboard/GWBannerCard'
import { ScoreStatsRow } from '@/components/dashboard/ScoreStatsRow'
import { CaptainCard } from '@/components/dashboard/CaptainCard'
import { TransferStatusCard } from '@/components/dashboard/TransferStatusCard'
import { FixturesCard } from '@/components/dashboard/FixturesCard'
import { QuickActions } from '@/components/dashboard/QuickActions'
import { DashboardSkeleton } from '@/components/dashboard/DashboardSkeleton'

export default function DashboardPage() {
  const { loadState, data, error } = useDashboard()

  if (loadState === 'loading') {
    return (
      <PageShell maxWidth="lg">
        <DashboardSkeleton />
      </PageShell>
    )
  }

  if (loadState === 'error' || !data) {
    return (
      <PageShell maxWidth="lg">
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <p className="text-ink-muted text-sm">{error ?? 'Something went wrong.'}</p>
        </div>
      </PageShell>
    )
  }

  return (
    <PageShell maxWidth="lg">
      <GWBannerCard data={data} />

      <ScoreStatsRow data={data} />

      <CaptainCard
        captain={data.captain}
        viceCaptain={data.vice_captain}
        hasLineup={data.has_lineup}
      />

      <QuickActions data={data} />

      <Divider style="wavy" spacing="md" />

      {data.has_squad && (
        <>
          <TransferStatusCard data={data} />
          <Divider style="dashed" spacing="md" />
        </>
      )}

      <FixturesCard
        fixtures={data.fixtures}
        gameweekName={data.gameweek_name}
      />
    </PageShell>
  )
}
