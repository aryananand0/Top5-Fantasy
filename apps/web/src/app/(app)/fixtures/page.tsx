'use client'

import { useState } from 'react'
import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Tabs } from '@/components/ui/Tabs'
import { Pill } from '@/components/ui/Pill'
import { Divider } from '@/components/ui/Divider'
import { mockFixtures, mockGameweek } from '@/lib/mock-data'

const gwTabs = [
  { id: 'prev', label: `GW${mockGameweek.number - 1}` },
  { id: 'curr', label: `GW${mockGameweek.number}`, count: mockFixtures.length },
  { id: 'next', label: `GW${mockGameweek.number + 1}` },
]

// Group fixtures by date
function groupByDate(fixtures: typeof mockFixtures) {
  return fixtures.reduce<Record<string, typeof mockFixtures>>((acc, f) => {
    if (!acc[f.date]) acc[f.date] = []
    acc[f.date].push(f)
    return acc
  }, {})
}

export default function FixturesPage() {
  const [tab, setTab] = useState('curr')

  const grouped = groupByDate(mockFixtures)
  const dates   = Object.keys(grouped)

  return (
    <PageShell maxWidth="lg">
      <SectionHeader
        title="Fixtures"
        subtitle={`GW${mockGameweek.number} · Deadline ${mockGameweek.deadline}`}
        className="mb-5"
      />

      <Tabs tabs={gwTabs} activeTab={tab} onChange={setTab} className="mb-5" />

      {/* League filter pills */}
      <div className="flex gap-2 flex-wrap mb-5">
        <Pill color="ink">All Leagues</Pill>
        <Pill color="purple">Premier League</Pill>
        <Pill color="orange">La Liga</Pill>
        <Pill color="red">Bundesliga</Pill>
      </div>

      {/* ── Previous GW placeholder ─────────────────────────────────────── */}
      {tab === 'prev' && (
        <Card variant="flat" className="border-dashed">
          <div className="py-8 text-center">
            <p className="font-display font-bold text-ink mb-1">GW{mockGameweek.number - 1} Complete</p>
            <p className="text-sm text-ink-muted">All results are final. Scores were processed.</p>
          </div>
        </Card>
      )}

      {/* ── Current GW fixtures ─────────────────────────────────────────── */}
      {tab === 'curr' && (
        <div className="space-y-5">
          {dates.map((date) => (
            <div key={date}>
              <div className="flex items-center gap-3 mb-2">
                <span className="label-text text-ink-muted">{date}</span>
                <div className="flex-1 border-t border-dashed border-ink-faint" />
              </div>

              <div className="flex flex-col gap-2">
                {grouped[date].map((fixture) => (
                  <Card key={fixture.id} variant="default" padding="sm">
                    <div className="flex items-center justify-between gap-2">
                      {/* Home */}
                      <div className="flex-1 text-right min-w-0">
                        <span className="font-display font-bold text-sm text-ink truncate block">
                          {fixture.home}
                        </span>
                      </div>

                      {/* Score / time */}
                      <div className="shrink-0 flex flex-col items-center gap-0.5 px-3">
                        {fixture.homeScore !== null ? (
                          <span className="num text-base text-ink">
                            {fixture.homeScore} – {fixture.awayScore}
                          </span>
                        ) : (
                          <>
                            <span className="font-bold text-xs text-ink-muted">vs</span>
                            <span className="text-[0.6rem] text-ink-faint">{fixture.time}</span>
                          </>
                        )}
                        <Badge color="green" variant="tinted" size="sm">upcoming</Badge>
                      </div>

                      {/* Away */}
                      <div className="flex-1 min-w-0">
                        <span className="font-display font-bold text-sm text-ink truncate block">
                          {fixture.away}
                        </span>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              <Divider style="solid" spacing="sm" />
            </div>
          ))}
        </div>
      )}

      {/* ── Next GW placeholder ─────────────────────────────────────────── */}
      {tab === 'next' && (
        <Card variant="flat" className="border-dashed">
          <div className="py-8 text-center">
            <p className="font-display font-bold text-ink mb-1">GW{mockGameweek.number + 1}</p>
            <p className="text-sm text-ink-muted">Fixtures not yet announced. Check back soon.</p>
          </div>
        </Card>
      )}
    </PageShell>
  )
}
