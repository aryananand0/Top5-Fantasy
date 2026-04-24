'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { apiLogin, apiMe, saveSession, ApiError } from '@/lib/api/auth'

export default function LoginPage() {
  const router = useRouter()
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const { access_token } = await apiLogin({ login, password })
      const user = await apiMe(access_token)
      saveSession(access_token, user)
      router.push('/dashboard')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Login failed. Please try again.')
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
        <p className="text-sm text-ink-muted mt-1">Welcome back. Your squad awaits.</p>
      </div>

      <div className="w-full max-w-sm border-2 border-ink bg-paper rounded-2xl shadow-sketch p-6 md:p-7">
        <h1 className="font-display font-bold text-xl text-ink mb-6">Log in to your account</h1>

        <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
          <Input
            label="Email or Username"
            type="text"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            placeholder="you@example.com"
            autoComplete="email"
            required
          />
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete="current-password"
            required
          />

          {error && (
            <p className="text-xs text-red-600 font-medium -mt-1">{error}</p>
          )}

          <Button variant="primary" size="md" fullWidth type="submit" disabled={loading} className="mt-1">
            {loading ? 'Logging in…' : 'Log In'}
          </Button>
        </form>

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

      <Link href="/" className="mt-6 text-xs text-ink-faint hover:text-ink transition-colors">
        ← Back to homepage
      </Link>
    </div>
  )
}
