import { type ReactNode } from 'react'
import { cn } from '@/lib/cn'
import { type Position, positionMeta, type MarkerColor } from '@/lib/design-tokens'

export type BadgeVariant = 'solid' | 'tinted' | 'outline'
export type BadgeSize = 'sm' | 'md'
export { type MarkerColor as BadgeColor }

interface BadgeProps {
  children: ReactNode
  color?: MarkerColor | 'ink'
  variant?: BadgeVariant
  size?: BadgeSize
  className?: string
}

// Solid: vivid marker color fill — for position tags, key labels
const solidStyles: Record<MarkerColor | 'ink', string> = {
  green:  'bg-marker-green  text-paper border-marker-green',
  blue:   'bg-marker-blue   text-paper border-marker-blue',
  red:    'bg-marker-red    text-paper border-marker-red',
  yellow: 'bg-marker-yellow text-ink   border-marker-yellow', // yellow bg needs dark text
  purple: 'bg-marker-purple text-paper border-marker-purple',
  orange: 'bg-marker-orange text-paper border-marker-orange',
  ink:    'bg-ink           text-paper border-ink',
}

// Tinted: soft fill — for secondary labels, league tags
const tintedStyles: Record<MarkerColor | 'ink', string> = {
  green:  'bg-tint-green  text-ink border-marker-green',
  blue:   'bg-tint-blue   text-ink border-marker-blue',
  red:    'bg-tint-red    text-ink border-marker-red',
  yellow: 'bg-tint-yellow text-ink border-marker-yellow',
  purple: 'bg-tint-purple text-ink border-marker-purple',
  orange: 'bg-tint-orange text-ink border-marker-orange',
  ink:    'bg-paper-dark  text-ink border-ink-faint',
}

// Outline: transparent fill — for subtle tags, filters
const outlineStyles: Record<MarkerColor | 'ink', string> = {
  green:  'bg-transparent text-marker-green  border-marker-green',
  blue:   'bg-transparent text-marker-blue   border-marker-blue',
  red:    'bg-transparent text-marker-red    border-marker-red',
  yellow: 'bg-transparent text-ink           border-marker-yellow',
  purple: 'bg-transparent text-marker-purple border-marker-purple',
  orange: 'bg-transparent text-marker-orange border-marker-orange',
  ink:    'bg-transparent text-ink           border-ink',
}

const variantMap = { solid: solidStyles, tinted: tintedStyles, outline: outlineStyles }

const sizeStyles: Record<BadgeSize, string> = {
  sm: 'px-1.5 py-0.5 text-[0.65rem]',
  md: 'px-2   py-0.5 text-[0.7rem]',
}

export function Badge({
  children,
  color = 'ink',
  variant = 'solid',
  size = 'md',
  className,
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center border-2 rounded-md font-bold uppercase tracking-wide',
        variantMap[variant][color],
        sizeStyles[size],
        className,
      )}
    >
      {children}
    </span>
  )
}

/**
 * Convenience wrapper — automatically maps GK/DEF/MID/FWD to the right color.
 * Use this everywhere you render a player position.
 */
export function PositionBadge({
  position,
  size = 'md',
  variant = 'solid',
  className,
}: {
  position: Position
  size?: BadgeSize
  variant?: BadgeVariant
  className?: string
}) {
  const { label, color } = positionMeta[position]
  return (
    <Badge color={color} variant={variant} size={size} className={className}>
      {label}
    </Badge>
  )
}
