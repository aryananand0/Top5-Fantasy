'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Button } from '@/components/ui/Button'
import { Pill } from '@/components/ui/Pill'
import { Divider } from '@/components/ui/Divider'
import { getStoredUser, clearSession } from '@/lib/api/auth'
import type { UserInfo } from '@/lib/api/auth'

function initials(user: UserInfo): string {
  const name = user.display_name || user.username
  const parts = name.split(/[\s_]+/)
  return parts.length >= 2
    ? (parts[0][0] + parts[1][0]).toUpperCase()
    : name.slice(0, 2).toUpperCase()
}

export default function ProfilePage() {
  const router = useRouter()
  const [user, setUser] = useState<UserInfo | null>(null)

  useEffect(() => {
    const u = getStoredUser()
    if (!u) {
      router.replace('/login')
      return
    }
    setUser(u)
  }, [router])

  function handleSignOut() {
    clearSession()
    router.push('/')
  }

  if (!user) return null

  const displayName = user.display_name || user.username

  const accountRows = [
    { label: 'Display Name', value: displayName },
    { label: 'Username',     value: `@${user.username}` },
    { label: 'Email',        value: user.email },
    { label: 'Password',     value: '••••••••' },
  ]

  return (
    <PageShell maxWidth="lg">
      {/* ── User card ─────────────────────────────────────────────────────── */}
      <Card variant="elevated" className="mb-5">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-2xl bg-tint-purple border-2 border-marker-purple shadow-sketch-sm flex items-center justify-center shrink-0">
            <span className="font-display font-black text-xl text-ink leading-none">
              {initials(user)}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="font-display font-extrabold text-xl text-ink leading-tight truncate">
              {displayName}
            </h1>
            <p className="text-sm text-ink-muted mt-0.5">@{user.username}</p>
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              <Pill color="purple">Member</Pill>
              <Badge color="green" variant="tinted" size="sm">Active</Badge>
            </div>
          </div>
        </div>
      </Card>

      <Divider style="wavy" spacing="md" />

      {/* ── Account settings ──────────────────────────────────────────────── */}
      <SectionHeader title="Account" className="mb-3" />
      <Card variant="default" padding="none" className="mb-5 overflow-hidden">
        {accountRows.map((row, i) => (
          <div
            key={row.label}
            className={`flex items-center justify-between px-4 py-3 gap-3 ${
              i < accountRows.length - 1 ? 'border-b border-ink-faint' : ''
            }`}
          >
            <div className="min-w-0">
              <p className="label-text text-ink-muted">{row.label}</p>
              <p className="text-sm font-semibold text-ink mt-0.5 truncate">{row.value}</p>
            </div>
          </div>
        ))}
      </Card>

      <Divider style="dashed" spacing="sm" />

      {/* ── Danger zone ───────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-3 pb-4">
        <Button variant="secondary" size="md" fullWidth onClick={handleSignOut}>
          Sign Out
        </Button>
      </div>
    </PageShell>
  )
}
