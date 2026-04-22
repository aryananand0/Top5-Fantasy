import { type ReactNode } from 'react'
import { cn } from '@/lib/cn'

type MaxWidth = 'sm' | 'md' | 'lg' | 'xl' | 'full'

interface PageShellProps {
  children: ReactNode
  className?: string
  /** Max-width constraint for the content area */
  maxWidth?: MaxWidth
  /** Add bottom padding to clear the mobile nav bar (default true) */
  mobileNavPadding?: boolean
}

const maxWidthStyles: Record<MaxWidth, string> = {
  sm:   'max-w-sm',
  md:   'max-w-2xl',
  lg:   'max-w-4xl',
  xl:   'max-w-6xl',
  full: 'max-w-none',
}

/**
 * Outer layout shell for every page.
 *
 * Provides:
 * - Horizontally centered max-width container
 * - Consistent horizontal padding (mobile: 20px, desktop: 32px)
 * - Bottom padding for the future mobile nav bar
 *
 * Usage:
 *   <PageShell>
 *     <SectionHeader title="My Squad" />
 *     ...
 *   </PageShell>
 */
export function PageShell({
  children,
  className,
  maxWidth = 'lg',
  mobileNavPadding = true,
}: PageShellProps) {
  return (
    <main
      className={cn(
        'mx-auto w-full',
        'px-page md:px-page-md',    // 20px mobile, 32px desktop
        'pt-6 md:pt-10',
        mobileNavPadding && 'pb-24 md:pb-10', // 96px bottom for future mobile nav
        maxWidthStyles[maxWidth],
        className,
      )}
    >
      {children}
    </main>
  )
}
