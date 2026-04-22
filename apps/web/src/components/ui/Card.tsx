import { type ReactNode, type ElementType } from 'react'
import { cn } from '@/lib/cn'

export type CardVariant = 'default' | 'elevated' | 'flat' | 'tinted'
export type CardPadding = 'none' | 'sm' | 'md' | 'lg'
export type CardColor = 'green' | 'blue' | 'red' | 'yellow' | 'purple' | 'orange'

interface CardProps {
  children: ReactNode
  className?: string
  variant?: CardVariant
  padding?: CardPadding
  /** Only applies when variant="tinted" */
  color?: CardColor
  /** Render as a different HTML element for semantics */
  as?: ElementType
}

const variantStyles: Record<CardVariant, string> = {
  default:  'border-2 border-ink bg-paper shadow-sketch',
  elevated: 'border-2 border-ink bg-paper shadow-sketch-md',
  flat:     'border-2 border-ink bg-paper',
  tinted:   'border-2 border-ink',
}

const paddingStyles: Record<CardPadding, string> = {
  none: '',
  sm:   'p-3',
  md:   'p-4 md:p-5',
  lg:   'p-5 md:p-6',
}

const tintedColorStyles: Record<CardColor, string> = {
  green:  'bg-tint-green',
  blue:   'bg-tint-blue',
  red:    'bg-tint-red',
  yellow: 'bg-tint-yellow',
  purple: 'bg-tint-purple',
  orange: 'bg-tint-orange',
}

export function Card({
  children,
  className,
  variant = 'default',
  padding = 'md',
  color = 'green',
  as: Component = 'div',
}: CardProps) {
  return (
    <Component
      className={cn(
        'rounded-2xl',
        variantStyles[variant],
        paddingStyles[padding],
        variant === 'tinted' && tintedColorStyles[color],
        className,
      )}
    >
      {children}
    </Component>
  )
}
