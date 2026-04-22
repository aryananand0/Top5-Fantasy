import type { Metadata } from 'next'
import Link from 'next/link'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Pill } from '@/components/ui/Pill'

export const metadata: Metadata = { title: 'Create Account' }

const perks = [
  { color: 'green' as const, label: 'Free to play' },
  { color: 'purple' as const, label: '5 leagues' },
  { color: 'blue' as const, label: 'Private leagues' },
]

export default function SignupPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-page py-12">
      {/* Brand */}
      <div className="text-center mb-8">
        <Link href="/" className="inline-flex flex-col items-center gap-3 group">
          <div className="w-14 h-14 rounded-2xl bg-ink border-2 border-ink shadow-sketch flex items-center justify-center group-hover:-translate-y-px transition-transform">
            <span className="font-display font-black text-paper text-xl leading-none">T5</span>
          </div>
          <span className="font-display font-black text-ink text-2xl tracking-tight">Top5 Fantasy</span>
        </Link>
        <div className="flex items-center justify-center gap-2 mt-3 flex-wrap">
          {perks.map((p) => (
            <Pill key={p.label} color={p.color}>{p.label}</Pill>
          ))}
        </div>
      </div>

      {/* Card */}
      <div className="w-full max-w-sm border-2 border-ink bg-paper rounded-2xl shadow-sketch p-6 md:p-7">
        <h1 className="font-display font-bold text-xl text-ink mb-6">Create your account</h1>

        {/* Form — wired up to a server action in a later step */}
        <form className="flex flex-col gap-4" action="#" method="POST">
          <Input
            label="Display Name"
            type="text"
            name="displayName"
            placeholder="e.g. Alex Freeman"
            autoComplete="name"
            hint="Shown in leagues and standings"
            required
          />
          <Input
            label="Team Name"
            type="text"
            name="teamName"
            placeholder="e.g. Red Devils United"
            hint="Your fantasy team's name"
            required
          />
          <Input
            label="Email"
            type="email"
            name="email"
            placeholder="you@example.com"
            autoComplete="email"
            required
          />
          <Input
            label="Password"
            type="password"
            name="password"
            placeholder="At least 8 characters"
            autoComplete="new-password"
            hint="Minimum 8 characters"
            required
          />

          <Link href="/onboarding" className="mt-1">
            <Button variant="primary" size="md" fullWidth type="button">
              Create Account
            </Button>
          </Link>
        </form>

        <p className="text-center text-xs text-ink-muted mt-4 leading-relaxed">
          By signing up you agree to our{' '}
          <a href="#" className="underline underline-offset-2 hover:text-ink">Terms</a>
          {' '}and{' '}
          <a href="#" className="underline underline-offset-2 hover:text-ink">Privacy Policy</a>.
        </p>

        {/* Divider */}
        <div className="flex items-center gap-3 my-5">
          <div className="flex-1 border-t border-dashed border-ink-faint" />
          <span className="text-xs text-ink-faint font-medium">already playing?</span>
          <div className="flex-1 border-t border-dashed border-ink-faint" />
        </div>

        <Link href="/login">
          <Button variant="secondary" size="md" fullWidth>Log In Instead</Button>
        </Link>
      </div>

      <Link href="/" className="mt-6 text-xs text-ink-faint hover:text-ink transition-colors">
        ← Back to homepage
      </Link>
    </div>
  )
}
