'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Pill } from '@/components/ui/Pill'
import { apiSignup, apiLogin, apiMe, saveSession, ApiError } from '@/lib/api/auth'

const perks = [
  { color: 'green' as const, label: 'Free to play' },
  { color: 'purple' as const, label: '5 leagues' },
  { color: 'blue' as const, label: 'Private leagues' },
]

export default function SignupPage() {
  const router = useRouter()
  const [displayName, setDisplayName] = useState('')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await apiSignup({
        email,
        username,
        password,
        display_name: displayName || undefined,
      })
      const { access_token } = await apiLogin({ login: email, password })
      const user = await apiMe(access_token)
      saveSession(access_token, user)
      router.push('/squad')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Sign up failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-page py-12">
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

      <div className="w-full max-w-sm border-2 border-ink bg-paper rounded-2xl shadow-sketch p-6 md:p-7">
        <h1 className="font-display font-bold text-xl text-ink mb-6">Create your account</h1>

        <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
          <Input
            label="Display Name"
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="e.g. Alex Freeman"
            autoComplete="name"
            hint="Shown in leagues and standings"
          />
          <Input
            label="Username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. alexf99"
            hint="Letters, numbers, underscores only"
            required
          />
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            autoComplete="email"
            required
          />
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
            autoComplete="new-password"
            hint="Minimum 8 characters"
            required
          />

          {error && (
            <p className="text-xs text-red-600 font-medium -mt-1">{error}</p>
          )}

          <Button variant="primary" size="md" fullWidth type="submit" disabled={loading} className="mt-1">
            {loading ? 'Creating account…' : 'Create Account'}
          </Button>
        </form>

        <p className="text-center text-xs text-ink-muted mt-4 leading-relaxed">
          By signing up you agree to our{' '}
          <a href="#" className="underline underline-offset-2 hover:text-ink">Terms</a>
          {' '}and{' '}
          <a href="#" className="underline underline-offset-2 hover:text-ink">Privacy Policy</a>.
        </p>

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
