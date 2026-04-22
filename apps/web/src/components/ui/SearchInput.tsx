'use client'

import { type InputHTMLAttributes, forwardRef, useId } from 'react'
import { cn } from '@/lib/cn'

interface SearchInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  containerClassName?: string
}

function SearchIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="w-4 h-4 text-ink-muted shrink-0"
      aria-hidden="true"
    >
      <circle cx="8.5" cy="8.5" r="5.5" />
      <path d="M15 15l-3-3" />
    </svg>
  )
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  ({ label, containerClassName, className, id, ...props }, ref) => {
    const generatedId = useId()
    const inputId = id ?? generatedId

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
        <div className="relative">
          <span className="absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none">
            <SearchIcon />
          </span>
          <input
            ref={ref}
            id={inputId}
            type="search"
            role="searchbox"
            className={cn(
              'w-full pl-10 pr-3.5 py-2.5 min-h-[44px]',
              'font-sans text-sm text-ink placeholder:text-ink-faint',
              'bg-paper border-2 border-ink-faint rounded-xl',
              'focus:border-ink focus:outline-none',
              'transition-colors duration-100',
              'disabled:opacity-40 disabled:cursor-not-allowed',
              // Remove browser default search UI
              '[&::-webkit-search-decoration]:hidden [&::-webkit-search-cancel-button]:hidden',
              className,
            )}
            {...props}
          />
        </div>
      </div>
    )
  },
)

SearchInput.displayName = 'SearchInput'
