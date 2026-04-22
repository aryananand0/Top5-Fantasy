'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/cn'

const desktopNavItems = [
  { href: '/dashboard', label: 'Home'      },
  { href: '/squad',     label: 'My Squad'  },
  { href: '/transfers', label: 'Transfers' },
  { href: '/leagues',   label: 'Leagues'   },
  { href: '/fixtures',  label: 'Fixtures'  },
]

const pageTitles: Record<string, string> = {
  '/dashboard': 'Top5 Fantasy',
  '/squad':     'My Squad',
  '/transfers': 'Transfers',
  '/leagues':   'Leagues',
  '/fixtures':  'Fixtures',
  '/profile':   'Profile',
}

function getPageTitle(pathname: string): string {
  if (pageTitles[pathname]) return pageTitles[pathname]
  if (pathname.startsWith('/leagues/')) return 'League'
  if (pathname.startsWith('/players/')) return 'Player'
  return 'Top5 Fantasy'
}

function isNavActive(pathname: string, href: string): boolean {
  if (href === '/dashboard') return pathname === '/dashboard'
  return pathname.startsWith(href)
}

// ── Logo mark ───────────────────────────────────────────────────────────────
function LogoMark({ size = 'sm' }: { size?: 'sm' | 'md' }) {
  const dim = size === 'md' ? 'w-9 h-9' : 'w-8 h-8'
  const text = size === 'md' ? 'text-base' : 'text-sm'
  return (
    <div
      className={cn(
        dim,
        'rounded-xl bg-ink border-2 border-ink shadow-sketch-sm',
        'flex items-center justify-center shrink-0',
      )}
    >
      <span className={cn('font-display font-black text-paper leading-none', text)}>
        T5
      </span>
    </div>
  )
}

// ── Notification bell ────────────────────────────────────────────────────────
function BellIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="w-5 h-5"
      aria-hidden="true"
    >
      <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 01-3.46 0" />
    </svg>
  )
}

export function TopBar() {
  const pathname = usePathname()
  const title = getPageTitle(pathname)

  return (
    <header className="sticky top-0 z-40 bg-paper border-b-2 border-ink">
      {/* ── Mobile ─────────────────────────────────────────────────────────── */}
      <div className="md:hidden flex items-center justify-between h-14 px-4 gap-3">
        <Link href="/dashboard" aria-label="Top5 Fantasy home">
          <LogoMark />
        </Link>

        <span className="font-display font-bold text-base text-ink tracking-tight flex-1 text-center">
          {title}
        </span>

        <Link
          href="/profile"
          className={cn(
            'w-8 h-8 rounded-lg border-2 border-ink',
            'flex items-center justify-center',
            'text-ink hover:bg-paper-dark transition-colors',
            pathname === '/profile' && 'bg-ink text-paper',
          )}
          aria-label="Profile"
        >
          <BellIcon />
        </Link>
      </div>

      {/* ── Desktop ────────────────────────────────────────────────────────── */}
      <div className="hidden md:flex items-center justify-between h-16 px-page-md max-w-6xl mx-auto gap-6">
        {/* Logo */}
        <Link
          href="/dashboard"
          className="flex items-center gap-2.5 shrink-0 group"
          aria-label="Top5 Fantasy home"
        >
          <LogoMark size="md" />
          <span className="font-display font-black text-lg text-ink tracking-tight leading-none">
            Top5 Fantasy
          </span>
        </Link>

        {/* Nav links */}
        <nav className="flex items-center gap-1" aria-label="Main navigation">
          {desktopNavItems.map((item) => {
            const active = isNavActive(pathname, item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'px-3.5 py-2 rounded-lg text-sm font-semibold leading-none',
                  'transition-all duration-100',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-1',
                  active
                    ? 'bg-ink text-paper shadow-sketch-sm'
                    : 'text-ink-muted hover:text-ink hover:bg-paper-dark',
                )}
                aria-current={active ? 'page' : undefined}
              >
                {item.label}
              </Link>
            )
          })}
        </nav>

        {/* Right side */}
        <Link
          href="/profile"
          className={cn(
            'flex items-center gap-2 px-3 py-1.5 rounded-xl border-2',
            'text-sm font-semibold transition-all duration-100',
            pathname === '/profile'
              ? 'bg-ink text-paper border-ink shadow-sketch-sm'
              : 'bg-paper text-ink border-ink-faint hover:border-ink hover:bg-paper-dark',
          )}
          aria-label="Profile"
        >
          <div className="w-6 h-6 rounded-full bg-tint-purple border-2 border-marker-purple flex items-center justify-center">
            <span className="text-[0.6rem] font-black text-ink leading-none">AF</span>
          </div>
          <span className="hidden lg:inline">Alex F.</span>
        </Link>
      </div>
    </header>
  )
}
