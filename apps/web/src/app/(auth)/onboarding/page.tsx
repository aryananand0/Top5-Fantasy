'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Pill } from '@/components/ui/Pill'
import { cn } from '@/lib/cn'

const steps = [
  {
    number: 1,
    title: 'Welcome to Top5 Fantasy',
    body: "You're about to build a 15-player dream squad from the Premier League, La Liga, Bundesliga, Serie A, and Ligue 1 — all in one team.",
    detail: 'Pick players from across Europe and score points based on their real-life performances each gameweek.',
    visual: (
      <div className="flex flex-wrap gap-2 justify-center">
        {[
          { code: 'PL',  color: 'purple' as const },
          { code: 'LAL', color: 'orange' as const },
          { code: 'BUN', color: 'red'    as const },
          { code: 'SA',  color: 'blue'   as const },
          { code: 'L1',  color: 'green'  as const },
        ].map((l) => (
          <Badge key={l.code} color={l.color} variant="solid" size="md">{l.code}</Badge>
        ))}
      </div>
    ),
  },
  {
    number: 2,
    title: 'Build your squad',
    body: "You have a £100M budget to pick 15 players: 1 GK, 4–5 DEF, 3–5 MID, and 1–3 FWD. Max 3 players from the same club.",
    detail: 'Pick a captain (2× points) and vice-captain (2× if captain doesn\'t play). Your bench covers your starting XI if players don\'t feature.',
    visual: (
      <div className="flex items-center justify-center gap-2 flex-wrap">
        {[
          { pos: 'GK',  color: 'yellow' as const },
          { pos: 'DEF', color: 'blue'   as const },
          { pos: 'MID', color: 'green'  as const },
          { pos: 'FWD', color: 'red'    as const },
        ].map((p) => (
          <div key={p.pos} className="flex flex-col items-center gap-1">
            <Badge color={p.color} variant="solid" size="md">{p.pos}</Badge>
          </div>
        ))}
      </div>
    ),
  },
  {
    number: 3,
    title: 'Score and compete',
    body: 'Points are calculated from goals, assists, clean sheets, minutes played, and more. Each gameweek your score updates after matches finish.',
    detail: 'You get 2 free transfers each week. Create or join a private league to compete with friends. Global standings track everyone.',
    visual: (
      <div className="flex items-center justify-center gap-3">
        <div className="text-center">
          <div className="num text-4xl text-marker-green">+4</div>
          <Pill color="green" className="mt-1">Goal (FWD)</Pill>
        </div>
        <div className="text-center">
          <div className="num text-4xl text-marker-blue">+3</div>
          <Pill color="blue" className="mt-1">Assist</Pill>
        </div>
        <div className="text-center">
          <div className="num text-4xl text-marker-red">−1</div>
          <Pill color="red" className="mt-1">Yellow</Pill>
        </div>
      </div>
    ),
  },
]

export default function OnboardingPage() {
  const [current, setCurrent] = useState(0)
  const step = steps[current]
  const isLast = current === steps.length - 1

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-page py-12">
      {/* Progress indicators */}
      <div className="flex items-center gap-2 mb-8">
        {steps.map((s, i) => (
          <button
            key={s.number}
            onClick={() => setCurrent(i)}
            aria-label={`Step ${s.number}`}
            className={cn(
              'transition-all duration-150',
              i === current
                ? 'w-8 h-2.5 bg-ink rounded-full'
                : i < current
                  ? 'w-2.5 h-2.5 bg-ink-muted rounded-full'
                  : 'w-2.5 h-2.5 bg-ink-faint rounded-full',
            )}
          />
        ))}
      </div>

      {/* Card */}
      <div className="w-full max-w-sm border-2 border-ink bg-paper rounded-2xl shadow-sketch-md p-6 md:p-8">
        {/* Step number */}
        <div className="flex items-center gap-2 mb-5">
          <Badge color="ink" variant="solid" size="sm">Step {step.number} of {steps.length}</Badge>
        </div>

        {/* Visual */}
        <div className="border-2 border-ink-faint bg-paper-dark rounded-xl p-5 mb-5 min-h-[80px] flex items-center justify-center">
          {step.visual}
        </div>

        {/* Content */}
        <h2 className="font-display font-bold text-xl text-ink mb-3 leading-tight">
          {step.title}
        </h2>
        <p className="text-sm text-ink leading-relaxed mb-3">{step.body}</p>
        <p className="text-sm text-ink-muted leading-relaxed">{step.detail}</p>
      </div>

      {/* Navigation */}
      <div className="flex items-center gap-3 mt-6 w-full max-w-sm">
        {current > 0 && (
          <Button variant="ghost" size="md" onClick={() => setCurrent(current - 1)}>
            ← Back
          </Button>
        )}
        <div className="flex-1">
          {isLast ? (
            <Link href="/squad">
              <Button variant="primary" size="md" fullWidth>
                Build My Squad →
              </Button>
            </Link>
          ) : (
            <Button variant="primary" size="md" fullWidth onClick={() => setCurrent(current + 1)}>
              Next →
            </Button>
          )}
        </div>
      </div>

      {/* Skip */}
      <Link href="/dashboard" className="mt-4 text-xs text-ink-faint hover:text-ink transition-colors">
        Skip for now
      </Link>
    </div>
  )
}
