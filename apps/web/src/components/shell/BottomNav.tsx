'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/cn'

// ── Icons ────────────────────────────────────────────────────────────────────
// Inline SVGs — no icon library needed for 5 icons

function HomeIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  )
}

function SquadIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
    </svg>
  )
}

function TransfersIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <polyline points="17 1 21 5 17 9" />
      <path d="M3 11V9a4 4 0 014-4h14" />
      <polyline points="7 23 3 19 7 15" />
      <path d="M21 13v2a4 4 0 01-4 4H3" />
    </svg>
  )
}

function LeaguesIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <polyline points="8 21 12 17 16 21" />
      <line x1="12" y1="17" x2="12" y2="11" />
      <path d="M5 4h14M7 4c0 5.5 2.5 9.5 5 10.5 2.5-1 5-5 5-10.5" />
      <line x1="4" y1="7" x2="7" y2="7" />
      <line x1="17" y1="7" x2="20" y2="7" />
    </svg>
  )
}

function ProfileIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  )
}

const navItems = [
  { href: '/dashboard', label: 'Home',      Icon: HomeIcon      },
  { href: '/squad',     label: 'Squad',     Icon: SquadIcon     },
  { href: '/transfers', label: 'Transfers', Icon: TransfersIcon },
  { href: '/leagues',   label: 'Leagues',   Icon: LeaguesIcon   },
  { href: '/profile',   label: 'Profile',   Icon: ProfileIcon   },
]

function isActive(pathname: string, href: string): boolean {
  if (href === '/dashboard') return pathname === '/dashboard'
  return pathname.startsWith(href)
}

export function BottomNav() {
  const pathname = usePathname()

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 md:hidden"
      aria-label="Mobile navigation"
    >
      {/* The bar itself */}
      <div className="bg-paper border-t-2 border-ink">
        <div className="flex items-stretch h-16">
          {navItems.map(({ href, label, Icon }) => {
            const active = isActive(pathname, href)
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  'flex-1 flex flex-col items-center justify-center gap-1 px-1',
                  'transition-all duration-100 active:scale-95',
                  'focus-visible:outline-none focus-visible:bg-paper-dark',
                  active ? 'text-ink' : 'text-ink-faint',
                )}
                aria-current={active ? 'page' : undefined}
                aria-label={label}
              >
                {/* Active pill indicator */}
                <div
                  className={cn(
                    'relative flex flex-col items-center gap-1 px-3 py-1.5 rounded-xl',
                    'transition-all duration-100',
                    active && 'bg-ink',
                  )}
                >
                  <Icon
                    className={cn(
                      'w-5 h-5 transition-colors',
                      active ? 'stroke-paper' : 'stroke-ink-faint',
                    )}
                  />
                  <span
                    className={cn(
                      'text-[0.6rem] font-bold leading-none tracking-wide',
                      active ? 'text-paper' : 'text-ink-faint',
                    )}
                  >
                    {label}
                  </span>
                </div>
              </Link>
            )
          })}
        </div>
        {/* Safe area for iOS home indicator */}
        <div className="h-safe-area-inset-bottom bg-paper" style={{ height: 'env(safe-area-inset-bottom, 0px)' }} />
      </div>
    </nav>
  )
}
