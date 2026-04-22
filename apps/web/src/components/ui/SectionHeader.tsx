import { type ReactNode } from 'react'
import { cn } from '@/lib/cn'

interface SectionHeaderProps {
  title: string
  subtitle?: string
  /** Optional right-aligned action (button, link, count, etc.) */
  action?: ReactNode
  className?: string
}

export function SectionHeader({ title, subtitle, action, className }: SectionHeaderProps) {
  return (
    <div className={cn('flex items-start justify-between gap-4', className)}>
      <div className="min-w-0">
        <h2 className="font-display font-bold text-xl leading-tight text-ink tracking-tight truncate">
          {title}
        </h2>
        {subtitle && (
          <p className="text-sm text-ink-muted mt-0.5 leading-snug">{subtitle}</p>
        )}
      </div>
      {action && <div className="shrink-0 self-center">{action}</div>}
    </div>
  )
}
