import type { Metadata } from 'next'
import Link from 'next/link'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

export const metadata: Metadata = { title: 'Log In' }

export default function LoginPage() {
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
        <p className="text-sm text-ink-muted mt-1">Welcome back. Your squad awaits.</p>
      </div>

      {/* Card */}
      <div className="w-full max-w-sm border-2 border-ink bg-paper rounded-2xl shadow-sketch p-6 md:p-7">
        <h1 className="font-display font-bold text-xl text-ink mb-6">Log in to your account</h1>

        {/* Form — wired up to a server action in a later step */}
        <form className="flex flex-col gap-4" action="#" method="POST">
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
            placeholder="••••••••"
            autoComplete="current-password"
            required
          />

          <div className="flex items-center justify-end">
            <a href="#" className="text-xs text-ink-muted hover:text-ink underline underline-offset-2 transition-colors">
              Forgot password?
            </a>
          </div>

          <Link href="/dashboard" className="mt-1">
            <Button variant="primary" size="md" fullWidth type="button">
              Log In
            </Button>
          </Link>
        </form>

        {/* Divider */}
        <div className="flex items-center gap-3 my-5">
          <div className="flex-1 border-t border-dashed border-ink-faint" />
          <span className="text-xs text-ink-faint font-medium">or</span>
          <div className="flex-1 border-t border-dashed border-ink-faint" />
        </div>

        <p className="text-center text-sm text-ink-muted">
          No account?{' '}
          <Link href="/signup" className="font-bold text-ink hover:underline underline-offset-2">
            Sign up free
          </Link>
        </p>
      </div>

      {/* Back */}
      <Link href="/" className="mt-6 text-xs text-ink-faint hover:text-ink transition-colors">
        ← Back to homepage
      </Link>
    </div>
  )
}
