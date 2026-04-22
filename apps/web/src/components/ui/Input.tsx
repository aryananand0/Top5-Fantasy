'use client'

import { type InputHTMLAttributes, forwardRef, useId } from 'react'
import { cn } from '@/lib/cn'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  containerClassName?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, containerClassName, className, id, ...props }, ref) => {
    const generatedId = useId()
    const inputId = id ?? generatedId
    const hintId = hint ? `${inputId}-hint` : undefined
    const errorId = error ? `${inputId}-error` : undefined

    return (
      <div className={cn('flex flex-col gap-1.5', containerClassName)}>
        {label && (
          <label
            htmlFor={inputId}
            className="font-sans font-semibold text-sm text-ink leading-none"
          >
            {label}
          </label>
        )}

        <input
          ref={ref}
          id={inputId}
          aria-describedby={[hintId, errorId].filter(Boolean).join(' ') || undefined}
          aria-invalid={!!error}
          className={cn(
            'w-full px-3.5 py-2.5 min-h-[44px]',
            'font-sans text-sm text-ink placeholder:text-ink-faint',
            'bg-paper border-2 rounded-xl',
            'transition-colors duration-100',
            error
              ? 'border-marker-red focus:border-marker-red focus:outline-none'
              : 'border-ink-faint focus:border-ink focus:outline-none',
            'focus:ring-0',      // use border color change instead of ring
            'disabled:opacity-40 disabled:cursor-not-allowed',
            className,
          )}
          {...props}
        />

        {hint && !error && (
          <p id={hintId} className="text-xs text-ink-muted leading-snug">
            {hint}
          </p>
        )}
        {error && (
          <p id={errorId} className="text-xs text-marker-red font-semibold leading-snug">
            {error}
          </p>
        )}
      </div>
    )
  },
)

Input.displayName = 'Input'
