'use client'

import { type ButtonHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/cn'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'tinted' | 'destructive'
export type ButtonSize = 'sm' | 'md' | 'lg'
export type ButtonColor = 'green' | 'blue' | 'red' | 'yellow' | 'purple' | 'orange'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  /** Only applies when variant="tinted" */
  color?: ButtonColor
  fullWidth?: boolean
}

// Base classes shared across all variants
const base = [
  'inline-flex items-center justify-center gap-2',
  'font-sans font-semibold leading-none',
  'border-2 cursor-pointer select-none',
  'transition-all duration-75',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-2 focus-visible:ring-offset-paper',
  'disabled:opacity-40 disabled:pointer-events-none',
].join(' ')

// The stamp-press effect: hover lifts, active presses down into shadow
const pressBase = [
  'hover:-translate-x-px hover:-translate-y-px hover:shadow-sketch-md',
  'active:translate-x-px  active:translate-y-px  active:shadow-none',
].join(' ')

const variantStyles: Record<ButtonVariant, string> = {
  primary:     `bg-ink text-paper border-ink shadow-sketch ${pressBase}`,
  secondary:   `bg-paper text-ink border-ink shadow-sketch ${pressBase}`,
  ghost:       'bg-transparent text-ink border-transparent hover:bg-paper-dark hover:border-ink-faint active:bg-paper-darker',
  tinted:      `text-ink border-2 shadow-sketch ${pressBase}`,   // color applied separately
  destructive: `bg-tint-red text-ink border-marker-red shadow-sketch ${pressBase}`,
}

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-3   py-1.5 text-sm  rounded-lg  min-h-[36px]',
  md: 'px-5   py-2.5 text-sm  rounded-xl  min-h-[44px]',
  lg: 'px-7   py-3   text-base rounded-xl  min-h-[52px]',
}

const tintedColorStyles: Record<ButtonColor, string> = {
  green:  'bg-tint-green  border-marker-green',
  blue:   'bg-tint-blue   border-marker-blue',
  red:    'bg-tint-red    border-marker-red',
  yellow: 'bg-tint-yellow border-marker-yellow',
  purple: 'bg-tint-purple border-marker-purple',
  orange: 'bg-tint-orange border-marker-orange',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'secondary',
      size = 'md',
      color = 'green',
      fullWidth = false,
      children,
      ...props
    },
    ref,
  ) => (
    <button
      ref={ref}
      className={cn(
        base,
        variantStyles[variant],
        sizeStyles[size],
        variant === 'tinted' && tintedColorStyles[color],
        fullWidth && 'w-full',
        className,
      )}
      {...props}
    >
      {children}
    </button>
  ),
)

Button.displayName = 'Button'
