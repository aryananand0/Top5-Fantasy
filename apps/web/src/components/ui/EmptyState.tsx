import { type ReactNode } from 'react'
import { cn } from '@/lib/cn'

interface EmptyStateProps {
  /** SVG or emoji icon. Defaults to a hand-drawn football doodle. */
  icon?: ReactNode
  title: string
  description?: string
  /** Optional CTA button or link */
  action?: ReactNode
  className?: string
}

function DefaultIcon() {
  return (
    <svg
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="w-16 h-16"
      aria-hidden="true"
    >
      {/* Doodle-style football (soccer ball) */}
      <circle cx="32" cy="32" r="26" stroke="var(--color-ink-faint)" strokeWidth="3" />
      <polygon
        points="32,12 37,22 32,30 27,22"
        stroke="var(--color-ink-faint)"
        strokeWidth="2"
        fill="none"
        strokeLinejoin="round"
      />
      <line x1="32" y1="30" x2="24" y2="40" stroke="var(--color-ink-faint)" strokeWidth="2" strokeLinecap="round" />
      <line x1="32" y1="30" x2="40" y2="40" stroke="var(--color-ink-faint)" strokeWidth="2" strokeLinecap="round" />
      <line x1="24" y1="40" x2="32" y2="52" stroke="var(--color-ink-faint)" strokeWidth="2" strokeLinecap="round" />
      <line x1="40" y1="40" x2="32" y2="52" stroke="var(--color-ink-faint)" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center text-center',
        'gap-3 py-12 px-6',
        className,
      )}
    >
      <div className="mb-1 opacity-60">{icon ?? <DefaultIcon />}</div>

      <h3 className="font-display font-bold text-lg text-ink leading-tight">
        {title}
      </h3>

      {description && (
        <p className="text-sm text-ink-muted max-w-xs leading-relaxed">
          {description}
        </p>
      )}

      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}
