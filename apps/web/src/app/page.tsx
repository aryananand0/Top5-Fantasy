'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Badge, PositionBadge } from '@/components/ui/Badge'
import { Pill } from '@/components/ui/Pill'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { StatBox } from '@/components/ui/StatBox'
import { Tabs } from '@/components/ui/Tabs'
import { Input } from '@/components/ui/Input'
import { SearchInput } from '@/components/ui/SearchInput'
import { EmptyState } from '@/components/ui/EmptyState'
import { Divider } from '@/components/ui/Divider'
import { PageShell } from '@/components/ui/PageShell'

const squadTabs = [
  { id: 'squad',     label: 'My Squad',  count: 15 },
  { id: 'transfers', label: 'Transfers', count: 2  },
  { id: 'fixtures',  label: 'Fixtures'             },
]

export default function DesignSystemPage() {
  const [activeTab, setActiveTab] = useState('squad')

  return (
    <PageShell maxWidth="lg">
      {/* ── Header ──────────────────────────────────────────────────────────── */}
      <div className="mb-10">
        <div className="inline-flex items-center gap-2 mb-3">
          <Badge color="yellow" variant="solid" size="md">Design System</Badge>
          <Badge color="ink" variant="outline" size="md">v0.1</Badge>
        </div>
        <h1 className="font-display font-extrabold text-4xl md:text-5xl text-ink tracking-tight leading-none">
          Top5 Fantasy
        </h1>
        <p className="text-ink-muted mt-2 text-base">
          Component library — the visual building blocks for every screen.
        </p>
      </div>

      <Divider style="wavy" spacing="lg" />

      {/* ── Colors ──────────────────────────────────────────────────────────── */}
      <section className="mb-12">
        <SectionHeader
          title="Color Palette"
          subtitle="Marker pen on cream paper — accent sparingly"
          className="mb-5"
        />

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {[
            { name: 'Paper',       hex: '#F7F4EE', cls: 'bg-paper     border-ink' },
            { name: 'Paper Dark',  hex: '#EDE9DF', cls: 'bg-paper-dark border-ink' },
            { name: 'Ink',         hex: '#1C1917', cls: 'bg-ink        border-ink' },
            { name: 'Ink Muted',   hex: '#78716C', cls: 'bg-ink-muted  border-ink' },
            { name: 'Green',       hex: '#2DB87A', cls: 'bg-marker-green border-marker-green' },
            { name: 'Blue',        hex: '#3B82F6', cls: 'bg-marker-blue  border-marker-blue'  },
            { name: 'Red',         hex: '#DC4040', cls: 'bg-marker-red   border-marker-red'   },
            { name: 'Yellow',      hex: '#F5C228', cls: 'bg-marker-yellow border-marker-yellow' },
            { name: 'Purple',      hex: '#8B5CF6', cls: 'bg-marker-purple border-marker-purple' },
            { name: 'Orange',      hex: '#F07530', cls: 'bg-marker-orange border-marker-orange' },
            { name: 'Tint Green',  hex: '#D4F5E4', cls: 'bg-tint-green  border-marker-green'  },
            { name: 'Tint Blue',   hex: '#DBEAFE', cls: 'bg-tint-blue   border-marker-blue'   },
          ].map((swatch) => (
            <div key={swatch.name} className="flex flex-col gap-2">
              <div className={`h-12 rounded-xl border-2 ${swatch.cls}`} />
              <div>
                <p className="text-xs font-bold text-ink leading-none">{swatch.name}</p>
                <p className="text-xs text-ink-muted font-mono">{swatch.hex}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <Divider style="dashed" />

      {/* ── Typography ──────────────────────────────────────────────────────── */}
      <section className="mb-12">
        <SectionHeader title="Typography" subtitle="Syne (display) · Nunito (body)" className="mb-5" />

        <div className="space-y-4">
          <div>
            <p className="label-text text-ink-muted mb-1">Display — Syne</p>
            <p className="font-display font-extrabold text-5xl text-ink leading-none tracking-tight">124 pts</p>
          </div>
          <div>
            <p className="label-text text-ink-muted mb-1">Heading — Syne Bold</p>
            <h2 className="font-display font-bold text-2xl text-ink">Erling Haaland</h2>
          </div>
          <div>
            <p className="label-text text-ink-muted mb-1">Subheading</p>
            <h3 className="font-display font-semibold text-lg text-ink">Manchester City · FWD</h3>
          </div>
          <div>
            <p className="label-text text-ink-muted mb-1">Body — Nunito</p>
            <p className="font-sans text-base text-ink">
              Build your 15-player squad from players across the top 5 European leagues.
              Stay within your £100M budget, pick your captain, and score points each gameweek.
            </p>
          </div>
          <div>
            <p className="label-text text-ink-muted mb-1">Small / Muted</p>
            <p className="font-sans text-sm text-ink-muted">Gameweek 28 · Deadline: Sat 2 Mar, 11:30</p>
          </div>
          <div>
            <p className="label-text text-ink-muted mb-1">Label (uppercase)</p>
            <p className="label-text text-ink-muted">Total Points · Global Rank · Team Value</p>
          </div>
        </div>
      </section>

      <Divider style="wavy" />

      {/* ── Buttons ─────────────────────────────────────────────────────────── */}
      <section className="mb-12">
        <SectionHeader title="Buttons" subtitle="Stamp-press effect on click" className="mb-5" />

        <div className="space-y-6">
          <div>
            <p className="label-text text-ink-muted mb-3">Variants</p>
            <div className="flex flex-wrap gap-3 items-center">
              <Button variant="primary">Save Squad</Button>
              <Button variant="secondary">Make Transfer</Button>
              <Button variant="ghost">Cancel</Button>
              <Button variant="tinted" color="green">Join League</Button>
              <Button variant="tinted" color="purple">View Standings</Button>
              <Button variant="destructive">Remove Player</Button>
            </div>
          </div>

          <div>
            <p className="label-text text-ink-muted mb-3">Sizes</p>
            <div className="flex flex-wrap gap-3 items-center">
              <Button variant="primary" size="sm">Small</Button>
              <Button variant="primary" size="md">Medium</Button>
              <Button variant="primary" size="lg">Large</Button>
            </div>
          </div>

          <div>
            <p className="label-text text-ink-muted mb-3">States</p>
            <div className="flex flex-wrap gap-3 items-center">
              <Button variant="secondary" disabled>Disabled</Button>
              <Button variant="primary" fullWidth>Full Width (mobile CTA)</Button>
            </div>
          </div>
        </div>
      </section>

      <Divider style="dashed" />

      {/* ── Cards ───────────────────────────────────────────────────────────── */}
      <section className="mb-12">
        <SectionHeader title="Cards" subtitle="Thick border · offset shadow · rounded" className="mb-5" />

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {/* Player card mockup */}
          <Card variant="default">
            <div className="flex items-start justify-between mb-3">
              <PositionBadge position="FWD" />
              <span className="font-display font-bold text-lg text-ink">£12.5M</span>
            </div>
            <div className="mb-1">
              <p className="font-display font-bold text-base text-ink">Haaland</p>
              <p className="text-xs text-ink-muted">Man City · Premier League</p>
            </div>
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-ink-faint">
              <span className="label-text text-ink-muted">GW28</span>
              <span className="num text-xl text-marker-green">12 pts</span>
            </div>
          </Card>

          {/* Elevated variant */}
          <Card variant="elevated">
            <div className="flex items-start justify-between mb-3">
              <PositionBadge position="DEF" />
              <span className="font-display font-bold text-lg text-ink">£7.5M</span>
            </div>
            <div className="mb-1">
              <p className="font-display font-bold text-base text-ink">Trent A-A</p>
              <p className="text-xs text-ink-muted">Liverpool · Premier League</p>
            </div>
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-ink-faint">
              <span className="label-text text-ink-muted">GW28</span>
              <span className="num text-xl text-marker-green">9 pts</span>
            </div>
          </Card>

          {/* Tinted variant */}
          <Card variant="tinted" color="yellow">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-1.5">
                <PositionBadge position="MID" />
                <Badge color="yellow" variant="solid" size="sm">C</Badge>
              </div>
              <span className="font-display font-bold text-lg text-ink">£8.0M</span>
            </div>
            <div className="mb-1">
              <p className="font-display font-bold text-base text-ink">Salah</p>
              <p className="text-xs text-ink-muted">Liverpool · Premier League</p>
            </div>
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-ink">
              <span className="label-text text-ink-muted">Captain · 2×</span>
              <span className="num text-xl text-ink">18 pts</span>
            </div>
          </Card>
        </div>
      </section>

      <Divider style="wavy" />

      {/* ── Badges & Pills ──────────────────────────────────────────────────── */}
      <section className="mb-12">
        <SectionHeader title="Badges & Pills" subtitle="Sticker-like labels · position tags · league chips" className="mb-5" />

        <div className="space-y-5">
          <div>
            <p className="label-text text-ink-muted mb-3">Positions (solid)</p>
            <div className="flex flex-wrap gap-2">
              <PositionBadge position="GK" />
              <PositionBadge position="DEF" />
              <PositionBadge position="MID" />
              <PositionBadge position="FWD" />
            </div>
          </div>

          <div>
            <p className="label-text text-ink-muted mb-3">Badges — all colors</p>
            <div className="flex flex-wrap gap-2">
              {(['green', 'blue', 'red', 'yellow', 'purple', 'orange', 'ink'] as const).map((c) => (
                <Badge key={c} color={c} variant="solid">{c}</Badge>
              ))}
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {(['green', 'blue', 'red', 'yellow', 'purple', 'orange', 'ink'] as const).map((c) => (
                <Badge key={c} color={c} variant="tinted">{c}</Badge>
              ))}
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {(['green', 'blue', 'red', 'yellow', 'purple', 'orange', 'ink'] as const).map((c) => (
                <Badge key={c} color={c} variant="outline">{c}</Badge>
              ))}
            </div>
          </div>

          <div>
            <p className="label-text text-ink-muted mb-3">Pills — league & filter chips</p>
            <div className="flex flex-wrap gap-2">
              <Pill color="purple">Premier League</Pill>
              <Pill color="orange">La Liga</Pill>
              <Pill color="red">Bundesliga</Pill>
              <Pill color="blue">Serie A</Pill>
              <Pill color="green">Ligue 1</Pill>
              <Pill color="ink">All Leagues</Pill>
              <Pill color="yellow">Clean Sheet</Pill>
              <Pill color="green">Goal Scorer</Pill>
            </div>
          </div>
        </div>
      </section>

      <Divider style="dashed" />

      {/* ── Stat Boxes ──────────────────────────────────────────────────────── */}
      <section className="mb-12">
        <SectionHeader title="Stat Boxes" subtitle="Big numbers · bold display font · color accent" className="mb-5" />

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <StatBox value="247"    label="Total Points" color="green"  />
          <StatBox value="#15"    label="Global Rank"  color="purple" />
          <StatBox value="£4.2M" label="In the Bank"  color="blue"   />
          <StatBox value="2"      label="Free Transfers" color="orange" />
          <StatBox value="124"   label="GW Points"    color="ink" size="lg" />
          <StatBox value="68%"   label="Haaland Owned" color="red" />
        </div>
      </section>

      <Divider style="wavy" />

      {/* ── Tabs ────────────────────────────────────────────────────────────── */}
      <section className="mb-12">
        <SectionHeader title="Tabs" subtitle="Pill-style navigation" className="mb-5" />

        <div className="space-y-4">
          <Tabs tabs={squadTabs} activeTab={activeTab} onChange={setActiveTab} />
          <Card variant="flat" className="border-dashed">
            <p className="text-sm text-ink-muted text-center py-2">
              Active tab: <strong className="text-ink font-bold">{activeTab}</strong>
            </p>
          </Card>
        </div>
      </section>

      <Divider style="dashed" />

      {/* ── Form Elements ───────────────────────────────────────────────────── */}
      <section className="mb-12">
        <SectionHeader title="Form Elements" subtitle="Thick borders · clear focus states · accessible labels" className="mb-5" />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 max-w-xl">
          <Input
            label="Display Name"
            placeholder="e.g. GaretH Bale fan"
            hint="Shown in public leagues"
          />
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
          />
          <Input
            label="With Error"
            placeholder="Enter value..."
            defaultValue="bad input"
            error="This field is required"
          />
          <SearchInput
            label="Find a Player"
            placeholder="Search by name or club..."
          />
        </div>
      </section>

      <Divider style="wavy" />

      {/* ── Empty State ─────────────────────────────────────────────────────── */}
      <section className="mb-12">
        <SectionHeader title="Empty State" subtitle="Used when a list or section has no content yet" className="mb-5" />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Card variant="flat">
            <EmptyState
              title="No squad yet"
              description="Build your 15-player squad from across the top 5 European leagues."
              action={<Button variant="primary" size="sm">Build Squad</Button>}
            />
          </Card>

          <Card variant="flat">
            <EmptyState
              icon={<span className="text-5xl" aria-hidden="true">🏆</span>}
              title="No leagues joined"
              description="Create a private league or join one with an invite code."
              action={<Button variant="tinted" color="purple" size="sm">Join League</Button>}
            />
          </Card>
        </div>
      </section>

      <Divider style="dashed" />

      {/* ── Dividers ────────────────────────────────────────────────────────── */}
      <section className="mb-16">
        <SectionHeader title="Dividers" className="mb-5" />
        <div className="space-y-2">
          <p className="label-text text-ink-muted">Wavy</p>
          <Divider style="wavy" spacing="sm" />
          <p className="label-text text-ink-muted">Dashed</p>
          <Divider style="dashed" spacing="sm" />
          <p className="label-text text-ink-muted">Solid</p>
          <Divider style="solid" spacing="sm" />
        </div>
      </section>

      {/* ── Footer note ─────────────────────────────────────────────────────── */}
      <div className="text-center pb-8">
        <p className="text-xs text-ink-faint font-mono">
          Top5 Fantasy Design System · Step 2 of build
        </p>
      </div>
    </PageShell>
  )
}
