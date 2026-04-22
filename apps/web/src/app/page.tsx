import Link from 'next/link'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Pill } from '@/components/ui/Pill'

const features = [
  {
    title: 'Five leagues, one squad',
    body:  'Pick from players across the PL, La Liga, Bundesliga, Serie A, and Ligue 1. No league boundaries.',
    accent: 'bg-tint-purple border-marker-purple',
    label: 'purple' as const,
  },
  {
    title: 'Score every gameweek',
    body:  'Points from goals, assists, clean sheets, and minutes played. Captain your best player for 2× points.',
    accent: 'bg-tint-green border-marker-green',
    label: 'green' as const,
  },
  {
    title: 'Compete with your mates',
    body:  'Create private leagues, share an invite code, and see where you rank at the end of every week.',
    accent: 'bg-tint-blue border-marker-blue',
    label: 'blue' as const,
  },
]

const leagues = [
  { code: 'PL',  label: 'Premier League', color: 'purple' as const },
  { code: 'LAL', label: 'La Liga',        color: 'orange' as const },
  { code: 'BUN', label: 'Bundesliga',     color: 'red'    as const },
  { code: 'SA',  label: 'Serie A',        color: 'blue'   as const },
  { code: 'L1',  label: 'Ligue 1',        color: 'green'  as const },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Top bar ─────────────────────────────────────────────────────────── */}
      <header className="border-b-2 border-ink bg-paper sticky top-0 z-40">
        <div className="flex items-center justify-between h-14 px-page md:px-page-md max-w-6xl mx-auto">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-ink shadow-sketch-sm flex items-center justify-center">
              <span className="font-display font-black text-paper text-sm leading-none">T5</span>
            </div>
            <span className="font-display font-black text-ink text-base hidden sm:inline">Top5 Fantasy</span>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/login">
              <Button variant="ghost" size="sm">Log In</Button>
            </Link>
            <Link href="/signup">
              <Button variant="primary" size="sm">Play Free</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* ── Hero ────────────────────────────────────────────────────────────── */}
      <main className="flex-1">
        <section className="px-page md:px-page-md max-w-4xl mx-auto pt-14 pb-12 md:pt-20 md:pb-16">
          {/* Season badge */}
          <div className="mb-6 flex items-center gap-2">
            <Badge color="yellow" variant="solid">2024/25 Season</Badge>
            <Badge color="ink" variant="outline">Now Open</Badge>
          </div>

          {/* Headline */}
          <h1 className="font-display font-extrabold text-4xl md:text-6xl text-ink leading-tight tracking-tight mb-5">
            Fantasy Football.<br />
            <span className="relative inline-block">
              Five Leagues.
              {/* Hand-drawn underline feel */}
              <svg viewBox="0 0 320 12" className="absolute -bottom-1 left-0 w-full h-3" preserveAspectRatio="none" aria-hidden="true">
                <path d="M0,8 Q80,2 160,8 Q240,14 320,8" stroke="var(--color-marker-yellow)" strokeWidth="4" fill="none" strokeLinecap="round"/>
              </svg>
            </span>
            <br />One Squad.
          </h1>

          <p className="font-sans text-base md:text-lg text-ink-muted max-w-xl mb-8 leading-relaxed">
            Build a 15-player squad under a £100M budget. Score points from real
            matches across Europe&apos;s top 5 leagues. Beat your mates all season.
          </p>

          {/* CTAs */}
          <div className="flex flex-wrap gap-3 mb-10">
            <Link href="/signup">
              <Button variant="primary" size="lg">Start Playing Free</Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="secondary" size="lg">Preview the App</Button>
            </Link>
          </div>

          {/* League pills */}
          <div className="flex flex-wrap gap-2">
            {leagues.map((l) => (
              <Pill key={l.code} color={l.color}>{l.label}</Pill>
            ))}
          </div>
        </section>

        {/* ── Feature cards ───────────────────────────────────────────────── */}
        <section className="px-page md:px-page-md max-w-4xl mx-auto pb-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {features.map((f) => (
              <div
                key={f.title}
                className={`border-2 ${f.accent} rounded-2xl p-5 shadow-sketch`}
              >
                <Badge color={f.label} variant="solid" size="sm" className="mb-3">
                  {f.label}
                </Badge>
                <h3 className="font-display font-bold text-base text-ink mb-2 leading-tight">
                  {f.title}
                </h3>
                <p className="text-sm text-ink-muted leading-relaxed">{f.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Stats strip ─────────────────────────────────────────────────── */}
        <section className="border-t-2 border-b-2 border-ink bg-paper-dark">
          <div className="px-page md:px-page-md max-w-4xl mx-auto py-6">
            <div className="grid grid-cols-3 gap-4 text-center">
              {[
                { value: '5', label: 'Leagues'   },
                { value: '100+', label: 'Clubs'  },
                { value: '2000+', label: 'Players' },
              ].map((s) => (
                <div key={s.label}>
                  <p className="num text-3xl md:text-4xl text-ink">{s.value}</p>
                  <p className="label-text text-ink-muted mt-1">{s.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Footer CTA ──────────────────────────────────────────────────── */}
        <section className="px-page md:px-page-md max-w-4xl mx-auto py-16 text-center">
          <p className="font-display font-bold text-2xl text-ink mb-4">
            Ready to build your dream squad?
          </p>
          <Link href="/signup">
            <Button variant="primary" size="lg">Create Free Account</Button>
          </Link>
        </section>
      </main>

      {/* ── Footer ──────────────────────────────────────────────────────────── */}
      <footer className="border-t-2 border-ink py-6 px-page md:px-page-md">
        <div className="max-w-4xl mx-auto flex items-center justify-between gap-4">
          <span className="text-xs text-ink-muted">
            Top5 Fantasy · Not affiliated with any league or club
          </span>
          <div className="flex gap-4">
            <Link href="/login" className="text-xs text-ink-muted hover:text-ink transition-colors">Log In</Link>
            <Link href="/signup" className="text-xs text-ink-muted hover:text-ink transition-colors">Sign Up</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
