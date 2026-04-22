'use client'

import { useState } from 'react'
import Link from 'next/link'
import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge, PositionBadge } from '@/components/ui/Badge'
import { StatBox } from '@/components/ui/StatBox'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Tabs } from '@/components/ui/Tabs'
import { Button } from '@/components/ui/Button'
import { Divider } from '@/components/ui/Divider'
import { mockGameweek, mockUser, mockSquad, mockLeagues, mockFixtures } from '@/lib/mock-data'

const captain = mockSquad.find((p) => p.isCaptain)!
const vc      = mockSquad.find((p) => p.isVC)!

const overviewTabs = [
  { id: 'this-gw', label: 'This GW' },
  { id: 'season',  label: 'Season'  },
]

export default function DashboardPage() {
  const [tab, setTab] = useState('this-gw')

  return (
    <PageShell maxWidth="lg">
      {/* ── Gameweek banner ───────────────────────────────────────────────── */}
      <Card variant="tinted" color="yellow" className="mb-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge color="yellow" variant="solid" size="sm">GW{mockGameweek.number}</Badge>
              <Badge color="green" variant="tinted" size="sm">Active</Badge>
            </div>
            <p className="font-display font-extrabold text-4xl text-ink leading-none tabular-nums">
              {mockGameweek.points}
              <span className="text-lg font-semibold text-ink-muted ml-1.5">pts</span>
            </p>
            <p className="text-xs text-ink-muted mt-1">
              Avg this week: {mockGameweek.averagePoints} pts
            </p>
          </div>
          <div className="text-right shrink-0">
            <p className="label-text text-ink-muted">Deadline</p>
            <p className="text-sm font-bold text-ink mt-0.5">{mockGameweek.deadline}</p>
            <Badge color="orange" variant="tinted" size="sm" className="mt-2">
              {mockGameweek.freeTransfers} free transfers
            </Badge>
          </div>
        </div>
      </Card>

      {/* ── Tabs ──────────────────────────────────────────────────────────── */}
      <Tabs tabs={overviewTabs} activeTab={tab} onChange={setTab} className="mb-5" />

      {tab === 'this-gw' && (
        <>
          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3 mb-5">
            <StatBox value={`${mockGameweek.points}`}    label="GW Points"   color="green"  />
            <StatBox value={`#${mockUser.rank.toLocaleString()}`} label="Global Rank" color="purple" />
            <StatBox value={`£${mockUser.budget}M`}      label="In the Bank" color="blue"   />
          </div>
        </>
      )}

      {tab === 'season' && (
        <>
          <div className="grid grid-cols-3 gap-3 mb-5">
            <StatBox value={`${mockUser.totalPoints}`}  label="Total Points"  color="green"  />
            <StatBox value={`£${mockUser.teamValue}M`} label="Team Value"    color="orange" />
            <StatBox value={mockUser.globalPercentile} label="Percentile"    color="purple" />
          </div>
        </>
      )}

      {/* ── Captain card ──────────────────────────────────────────────────── */}
      <SectionHeader title="Your Captain" className="mb-3" />
      <div className="grid grid-cols-2 gap-3 mb-5">
        {[captain, vc].map((player, i) => (
          <Card key={player.id} variant={i === 0 ? 'tinted' : 'flat'} color={i === 0 ? 'yellow' : undefined}>
            <div className="flex items-start justify-between mb-2">
              <PositionBadge position={player.position} />
              <Badge color="yellow" variant={i === 0 ? 'solid' : 'outline'} size="sm">
                {i === 0 ? 'C' : 'VC'}
              </Badge>
            </div>
            <p className="font-display font-bold text-base text-ink leading-tight">{player.name}</p>
            <p className="text-xs text-ink-muted">{player.club}</p>
            <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-ink-faint">
              <span className="label-text text-ink-muted">GW{mockGameweek.number}</span>
              <span className="num text-xl text-marker-green">
                {i === 0 ? player.gwPts * 2 : player.gwPts} pts
              </span>
            </div>
          </Card>
        ))}
      </div>

      {/* ── Quick actions ─────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <Link href="/transfers">
          <Button variant="tinted" color="blue" size="md" fullWidth>
            Make Transfer
          </Button>
        </Link>
        <Link href="/squad">
          <Button variant="secondary" size="md" fullWidth>
            View Squad
          </Button>
        </Link>
      </div>

      <Divider style="wavy" spacing="md" />

      {/* ── Mini-leagues preview ───────────────────────────────────────────── */}
      <SectionHeader
        title="My Leagues"
        action={<Link href="/leagues"><Button variant="ghost" size="sm">See all</Button></Link>}
        className="mb-3"
      />
      <div className="flex flex-col gap-3 mb-6">
        {mockLeagues.map((league) => (
          <Link key={league.id} href={`/leagues/${league.id}`}>
            <Card variant="default" padding="sm" className="hover:-translate-y-px transition-transform">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-display font-bold text-sm text-ink">{league.name}</p>
                  <p className="text-xs text-ink-muted mt-0.5">{league.members} members</p>
                </div>
                <div className="text-right">
                  <Badge color="purple" variant="tinted" size="sm">
                    Rank #{league.userRank}
                  </Badge>
                  <p className="text-xs text-ink-muted mt-1">
                    Leader: {league.leader}
                  </p>
                </div>
              </div>
            </Card>
          </Link>
        ))}
        <Link href="/leagues">
          <Button variant="tinted" color="purple" size="sm" fullWidth>
            + Join or Create a League
          </Button>
        </Link>
      </div>

      <Divider style="dashed" spacing="md" />

      {/* ── Upcoming fixtures ─────────────────────────────────────────────── */}
      <SectionHeader
        title="Upcoming Fixtures"
        subtitle={`GW${mockGameweek.number} · ${mockGameweek.deadline}`}
        action={<Link href="/fixtures"><Button variant="ghost" size="sm">All fixtures</Button></Link>}
        className="mb-3"
      />
      <div className="flex flex-col gap-2">
        {mockFixtures.slice(0, 3).map((f) => (
          <Card key={f.id} variant="flat" padding="sm">
            <div className="flex items-center justify-between text-sm">
              <span className="font-semibold text-ink w-[38%] text-right">{f.home}</span>
              <div className="flex flex-col items-center gap-0.5 px-3">
                <span className="label-text text-ink-muted">vs</span>
                <span className="text-[0.6rem] text-ink-faint">{f.time}</span>
              </div>
              <span className="font-semibold text-ink w-[38%]">{f.away}</span>
            </div>
          </Card>
        ))}
      </div>
    </PageShell>
  )
}
