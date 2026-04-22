'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Tabs } from '@/components/ui/Tabs'
import { Button } from '@/components/ui/Button'
import { StatBox } from '@/components/ui/StatBox'
import { Divider } from '@/components/ui/Divider'
import { mockLeagues, mockLeagueStandings, mockGameweek } from '@/lib/mock-data'
import { cn } from '@/lib/cn'

const detailTabs = [
  { id: 'standings', label: 'Standings' },
  { id: 'gameweek',  label: 'This GW'   },
  { id: 'members',   label: 'Members'   },
]

export default function LeagueDetailPage() {
  const params = useParams<{ id: string }>()
  const [tab, setTab] = useState('standings')

  // Find the league or fall back to first
  const league = mockLeagues.find((l) => l.id === params.id) ?? mockLeagues[0]
  const myEntry = mockLeagueStandings.find((e) => e.isMe)!

  // GW standings (sort by gwPts)
  const gwStandings = [...mockLeagueStandings].sort((a, b) => b.gwPts - a.gwPts)

  return (
    <PageShell maxWidth="lg">
      {/* ── League header ───────────────────────────────────────────────────── */}
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-2">
          <Link href="/leagues">
            <Button variant="ghost" size="sm" className="text-ink-muted">← Leagues</Button>
          </Link>
        </div>
        <div className="flex items-start justify-between gap-3">
          <div>
            <h1 className="font-display font-extrabold text-2xl text-ink leading-tight">{league.name}</h1>
            <p className="text-sm text-ink-muted mt-0.5">{league.members} members · Private league</p>
          </div>
          <Badge color="purple" variant="solid" size="md">Rank #{league.userRank}</Badge>
        </div>
      </div>

      {/* ── My position strip ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-3 gap-3 mb-5">
        <StatBox value={`#${league.userRank}`}  label="My Rank"      color="purple" />
        <StatBox value={`${myEntry.totalPts}`}  label="My Total"     color="green"  />
        <StatBox value={`${myEntry.gwPts}`}     label="This GW"      color="blue"   />
      </div>

      {/* ── Share code ──────────────────────────────────────────────────────── */}
      <Card variant="tinted" color="yellow" className="mb-5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="label-text text-ink-muted mb-1">Invite code</p>
            <p className="font-mono font-black text-xl text-ink tracking-[0.2em]">X4K9PQ</p>
          </div>
          <Button variant="secondary" size="sm">Copy Link</Button>
        </div>
      </Card>

      <Tabs tabs={detailTabs} activeTab={tab} onChange={setTab} className="mb-5" />

      {/* ── Standings tab ─────────────────────────────────────────────────── */}
      {tab === 'standings' && (
        <div className="flex flex-col gap-2">
          {/* Header row */}
          <div className="flex items-center gap-3 px-2 pb-1">
            <span className="w-6 label-text text-ink-muted text-center">#</span>
            <span className="flex-1 label-text text-ink-muted">Team</span>
            <span className="w-16 label-text text-ink-muted text-right">GW</span>
            <span className="w-16 label-text text-ink-muted text-right">Total</span>
          </div>
          {mockLeagueStandings.map((entry) => (
            <Card
              key={entry.rank}
              variant={entry.isMe ? 'tinted' : 'flat'}
              color={entry.isMe ? 'yellow' : undefined}
              padding="sm"
            >
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    'num text-xl w-6 text-center shrink-0',
                    entry.rank === 1 ? 'text-marker-yellow' : 'text-ink-muted',
                  )}
                >
                  {entry.rank}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <p className="font-display font-bold text-sm text-ink truncate">{entry.teamName}</p>
                    {entry.isMe && <Badge color="yellow" variant="solid" size="sm">You</Badge>}
                  </div>
                  <p className="text-xs text-ink-muted">{entry.displayName}</p>
                </div>
                <span className="num text-base text-marker-green w-16 text-right">{entry.gwPts}</span>
                <span className="num text-base text-ink w-16 text-right">{entry.totalPts}</span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* ── Gameweek tab ──────────────────────────────────────────────────── */}
      {tab === 'gameweek' && (
        <>
          <Card variant="tinted" color="blue" className="mb-4">
            <p className="label-text text-ink-muted mb-1">GW{mockGameweek.number} winner</p>
            <p className="font-display font-bold text-lg text-ink">{league.gwWinner}</p>
            <p className="num text-3xl text-marker-green mt-1">{league.gwWinnerPts} pts</p>
          </Card>
          <Divider style="dashed" spacing="sm" />
          <div className="flex flex-col gap-2">
            {gwStandings.map((entry, i) => (
              <Card key={entry.rank} variant="flat" padding="sm">
                <div className="flex items-center gap-3">
                  <span className="num text-xl text-ink-muted w-6 text-center">{i + 1}</span>
                  <div className="flex-1 min-w-0">
                    <p className="font-display font-bold text-sm text-ink">{entry.teamName}</p>
                    <p className="text-xs text-ink-muted">{entry.displayName}</p>
                  </div>
                  <span className="num text-xl text-marker-green">{entry.gwPts}</span>
                </div>
              </Card>
            ))}
          </div>
        </>
      )}

      {/* ── Members tab ───────────────────────────────────────────────────── */}
      {tab === 'members' && (
        <div className="flex flex-col gap-2">
          {mockLeagueStandings.map((entry) => (
            <Card key={entry.rank} variant="flat" padding="sm">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-tint-purple border-2 border-marker-purple flex items-center justify-center shrink-0">
                  <span className="text-xs font-black text-ink">{entry.displayName[0]}</span>
                </div>
                <div className="flex-1">
                  <p className="font-display font-bold text-sm text-ink">{entry.displayName}</p>
                  <p className="text-xs text-ink-muted">{entry.teamName}</p>
                </div>
                {entry.isMe && <Badge color="yellow" variant="solid" size="sm">You</Badge>}
              </div>
            </Card>
          ))}
        </div>
      )}
    </PageShell>
  )
}
