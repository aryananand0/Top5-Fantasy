import { type ReactNode } from 'react'
import { cn } from '@/lib/cn'

type PillColor = 'green' | 'blue' | 'red' | 'yellow' | 'purple' | 'orange' | 'ink'

interface PillProps {
  children: ReactNode
  color?: PillColor
  className?: string
}

// Pills are softer than Badges: rounded-full, tint fill, thinner border.
// Use for hashtag-style tags, filter chips, and league labels.
const colorStyles: Record<PillColor, string> = {
  green:  'bg-tint-green  text-ink border-marker-green',
  blue:   'bg-tint-blue   text-ink border-marker-blue',
  red:    'bg-tint-red    text-ink border-marker-red',
  yellow: 'bg-tint-yellow text-ink border-marker-yellow',
  purple: 'bg-tint-purple text-ink border-marker-purple',
  orange: 'bg-tint-orange text-ink border-marker-orange',
  ink:    'bg-paper-dark  text-ink border-ink-faint',
}

export function Pill({ children, color = 'ink', className }: PillProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 border px-2.5 py-0.5 rounded-full',
        'text-xs font-semibold',
        colorStyles[color],
        className,
      )}
    >
      {children}
    </span>
  )
}
