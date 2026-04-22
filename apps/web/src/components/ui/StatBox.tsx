import { cn } from '@/lib/cn'
import { type MarkerColor } from '@/lib/design-tokens'

type StatBoxColor = MarkerColor | 'ink'
type StatBoxSize = 'sm' | 'md' | 'lg'

interface StatBoxProps {
  /** The headline number or value — shown large */
  value: string | number
  /** Short descriptive label shown below the value */
  label: string
  /** Accent color for the value text */
  color?: StatBoxColor
  size?: StatBoxSize
  className?: string
}

const valueColorStyles: Record<StatBoxColor, string> = {
  green:  'text-marker-green',
  blue:   'text-marker-blue',
  red:    'text-marker-red',
  yellow: 'text-ink',          // yellow is hard to read; use ink instead
  purple: 'text-marker-purple',
  orange: 'text-marker-orange',
  ink:    'text-ink',
}

const valueSizeStyles: Record<StatBoxSize, string> = {
  sm: 'text-3xl',
  md: 'text-4xl',
  lg: 'text-5xl',
}

const labelSizeStyles: Record<StatBoxSize, string> = {
  sm: 'text-xs',
  md: 'text-xs',
  lg: 'text-sm',
}

export function StatBox({ value, label, color = 'ink', size = 'md', className }: StatBoxProps) {
  return (
    <div
      className={cn(
        'border-2 border-ink bg-paper rounded-2xl shadow-sketch',
        'p-4 flex flex-col gap-1.5',
        className,
      )}
    >
      <span
        className={cn(
          'num leading-none',            // num utility: display font + tabular nums
          valueSizeStyles[size],
          valueColorStyles[color],
        )}
      >
        {value}
      </span>
      <span
        className={cn(
          'label-text text-ink-muted leading-none',   // label-text utility: uppercase tracking
          labelSizeStyles[size],
        )}
      >
        {label}
      </span>
    </div>
  )
}
