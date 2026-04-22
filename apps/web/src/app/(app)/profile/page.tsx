import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { StatBox } from '@/components/ui/StatBox'
import { Button } from '@/components/ui/Button'
import { Pill } from '@/components/ui/Pill'
import { Divider } from '@/components/ui/Divider'
import { mockUser, mockGameweek } from '@/lib/mock-data'
import Link from 'next/link'

const settingsRows = [
  { label: 'Display Name',  value: mockUser.displayName, action: 'Edit' },
  { label: 'Team Name',     value: mockUser.teamName,    action: 'Edit' },
  { label: 'Email',         value: mockUser.email,       action: 'Change' },
  { label: 'Password',      value: '••••••••',           action: 'Change' },
]

export default function ProfilePage() {
  return (
    <PageShell maxWidth="lg">
      {/* ── User card ───────────────────────────────────────────────────────── */}
      <Card variant="elevated" className="mb-5">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="w-14 h-14 rounded-2xl bg-tint-purple border-2 border-marker-purple shadow-sketch-sm flex items-center justify-center shrink-0">
            <span className="font-display font-black text-xl text-ink leading-none">
              {mockUser.displayName.charAt(0)}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="font-display font-extrabold text-xl text-ink leading-tight truncate">
              {mockUser.teamName}
            </h1>
            <p className="text-sm text-ink-muted mt-0.5">{mockUser.displayName}</p>
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              <Pill color="purple">GW{mockGameweek.number}</Pill>
              <Badge color="green" variant="tinted" size="sm">{mockUser.globalPercentile}</Badge>
            </div>
          </div>
        </div>
      </Card>

      {/* ── Season stats ────────────────────────────────────────────────────── */}
      <SectionHeader title="Season Stats" className="mb-3" />
      <div className="grid grid-cols-2 gap-3 mb-5">
        <StatBox value={`${mockUser.totalPoints}`}    label="Total Points"  color="green"  />
        <StatBox value={`#${mockUser.rank.toLocaleString()}`} label="Global Rank" color="purple" />
        <StatBox value={`£${mockUser.teamValue}M`}   label="Team Value"    color="orange" />
        <StatBox value={`£${mockUser.budget}M`}      label="In the Bank"   color="blue"   />
      </div>

      <Divider style="wavy" spacing="md" />

      {/* ── Account settings ────────────────────────────────────────────────── */}
      <SectionHeader title="Account" className="mb-3" />
      <Card variant="default" padding="none" className="mb-5 overflow-hidden">
        {settingsRows.map((row, i) => (
          <div
            key={row.label}
            className={`flex items-center justify-between px-4 py-3 gap-3 ${
              i < settingsRows.length - 1 ? 'border-b border-ink-faint' : ''
            }`}
          >
            <div className="min-w-0">
              <p className="label-text text-ink-muted">{row.label}</p>
              <p className="text-sm font-semibold text-ink mt-0.5 truncate">{row.value}</p>
            </div>
            <Button variant="ghost" size="sm" className="shrink-0">{row.action}</Button>
          </div>
        ))}
      </Card>

      <Divider style="dashed" spacing="md" />

      {/* ── Preferences ─────────────────────────────────────────────────────── */}
      <SectionHeader title="Preferences" className="mb-3" />
      <Card variant="default" padding="none" className="mb-5 overflow-hidden">
        {[
          { label: 'Email notifications', value: 'On — Gameweek reminders' },
          { label: 'Favourite league',     value: 'Premier League'          },
          { label: 'Display currency',     value: 'GBP (£)'                 },
        ].map((row, i, arr) => (
          <div
            key={row.label}
            className={`flex items-center justify-between px-4 py-3 gap-3 ${
              i < arr.length - 1 ? 'border-b border-ink-faint' : ''
            }`}
          >
            <div className="min-w-0">
              <p className="label-text text-ink-muted">{row.label}</p>
              <p className="text-sm font-semibold text-ink mt-0.5">{row.value}</p>
            </div>
            <Button variant="ghost" size="sm" className="shrink-0">Edit</Button>
          </div>
        ))}
      </Card>

      <Divider style="dashed" spacing="sm" />

      {/* ── Danger zone ─────────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-3 pb-4">
        <Link href="/">
          <Button variant="secondary" size="md" fullWidth>Sign Out</Button>
        </Link>
        <Button variant="ghost" size="sm" fullWidth className="text-marker-red">
          Delete Account
        </Button>
      </div>
    </PageShell>
  )
}
