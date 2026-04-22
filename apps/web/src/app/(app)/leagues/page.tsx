'use client'

import { useState } from 'react'
import Link from 'next/link'
import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Tabs } from '@/components/ui/Tabs'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { EmptyState } from '@/components/ui/EmptyState'
import { Divider } from '@/components/ui/Divider'
import { StatBox } from '@/components/ui/StatBox'
import { mockLeagues, mockUser } from '@/lib/mock-data'

const leagueTabs = [
  { id: 'my',     label: 'My Leagues', count: mockLeagues.length },
  { id: 'global', label: 'Global'                                },
]

export default function LeaguesPage() {
  const [tab, setTab] = useState('my')
  const [showJoin, setShowJoin] = useState(false)

  return (
    <PageShell maxWidth="lg">
      <SectionHeader
        title="Leagues"
        subtitle="Compete with friends and the world"
        className="mb-5"
      />

      <Tabs tabs={leagueTabs} activeTab={tab} onChange={setTab} className="mb-5" />

      {/* ── My Leagues tab ────────────────────────────────────────────────── */}
      {tab === 'my' && (
        <>
          {/* Action buttons */}
          <div className="grid grid-cols-2 gap-3 mb-5">
            <Button variant="tinted" color="purple" size="md" fullWidth onClick={() => setShowJoin(false)}>
              + Create League
            </Button>
            <Button variant="secondary" size="md" fullWidth onClick={() => setShowJoin((v) => !v)}>
              Join with Code
            </Button>
          </div>

          {/* Join by code panel */}
          {showJoin && (
            <Card variant="tinted" color="blue" className="mb-5">
              <p className="font-display font-bold text-sm text-ink mb-3">Enter invite code</p>
              <div className="flex gap-2">
                <Input
                  placeholder="e.g. X4K9PQ"
                  containerClassName="flex-1"
                  className="font-mono uppercase tracking-widest"
                />
                <Button variant="primary" size="md">Join</Button>
              </div>
            </Card>
          )}

          {/* League cards */}
          {mockLeagues.length === 0 ? (
            <EmptyState
              icon={<span className="text-5xl" aria-hidden="true">🏆</span>}
              title="No leagues yet"
              description="Create a private league or join one with an invite code."
              action={<Button variant="primary" size="sm">Create League</Button>}
            />
          ) : (
            <div className="flex flex-col gap-3 mb-5">
              {mockLeagues.map((league) => (
                <Link key={league.id} href={`/leagues/${league.id}`}>
                  <Card variant="default" className="hover:-translate-y-px transition-transform">
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div>
                        <p className="font-display font-bold text-base text-ink">{league.name}</p>
                        <p className="text-xs text-ink-muted mt-0.5">{league.members} members</p>
                      </div>
                      <Badge color="purple" variant="tinted" size="md">
                        Rank #{league.userRank}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between pt-3 border-t border-ink-faint">
                      <div>
                        <p className="label-text text-ink-muted">Leader</p>
                        <p className="text-sm font-bold text-ink mt-0.5">{league.leader}</p>
                      </div>
                      <div className="text-right">
                        <p className="label-text text-ink-muted">Top score</p>
                        <p className="num text-xl text-marker-green mt-0.5">{league.leaderPts}</p>
                      </div>
                    </div>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Global tab ────────────────────────────────────────────────────── */}
      {tab === 'global' && (
        <>
          <div className="grid grid-cols-2 gap-3 mb-5">
            <StatBox value={`#${mockUser.rank.toLocaleString()}`} label="Global Rank"   color="purple" />
            <StatBox value={mockUser.globalPercentile}            label="Percentile"    color="green"  />
          </div>

          <Card variant="tinted" color="purple" className="mb-5">
            <p className="font-display font-bold text-sm text-ink mb-1">Overall Standings</p>
            <p className="text-xs text-ink-muted leading-relaxed">
              You are ranked <span className="font-bold text-ink">#{mockUser.rank.toLocaleString()}</span> globally
              out of all managers this season. Keep climbing!
            </p>
          </Card>

          <Divider style="dashed" spacing="sm" />

          <SectionHeader title="Top Managers This Week" className="mb-3" />
          <div className="flex flex-col gap-2">
            {[
              { rank: 1, name: 'Anonymous',  teamName: 'World Beaters', pts: 2401, gw: 118 },
              { rank: 2, name: 'Anonymous',  teamName: 'Top Drawer',    pts: 2387, gw: 114 },
              { rank: 3, name: 'Anonymous',  teamName: 'Form FC',       pts: 2361, gw: 101 },
            ].map((entry) => (
              <Card key={entry.rank} variant="flat" padding="sm">
                <div className="flex items-center gap-3">
                  <span className="num text-xl text-ink-muted w-6 text-center">{entry.rank}</span>
                  <div className="flex-1">
                    <p className="font-display font-bold text-sm text-ink">{entry.teamName}</p>
                    <p className="text-xs text-ink-muted">{entry.name}</p>
                  </div>
                  <div className="text-right">
                    <p className="num text-base text-ink">{entry.pts}</p>
                    <p className="text-xs text-marker-green">+{entry.gw} pts</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </>
      )}
    </PageShell>
  )
}
