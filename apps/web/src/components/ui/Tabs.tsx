'use client'

import { cn } from '@/lib/cn'

export interface Tab {
  id: string
  label: string
  /** Optional count shown as a small badge next to the label */
  count?: number
}

interface TabsProps {
  tabs: Tab[]
  activeTab: string
  onChange: (id: string) => void
  className?: string
}

export function Tabs({ tabs, activeTab, onChange, className }: TabsProps) {
  return (
    <div
      role="tablist"
      className={cn(
        'flex gap-1.5 p-1 bg-paper-dark border-2 border-ink rounded-xl',
        className,
      )}
    >
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(tab.id)}
            className={cn(
              'flex-1 flex items-center justify-center gap-1.5',
              'px-3 py-1.5 rounded-lg text-sm font-semibold leading-none',
              'transition-all duration-100 cursor-pointer',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-1 focus-visible:ring-offset-paper-dark',
              isActive
                ? 'bg-ink text-paper shadow-sketch-sm'
                : 'text-ink-muted hover:text-ink hover:bg-paper',
            )}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span
                className={cn(
                  'inline-flex items-center justify-center min-w-[1.1rem] h-[1.1rem]',
                  'rounded-full text-[0.6rem] font-bold px-1',
                  isActive
                    ? 'bg-paper text-ink'
                    : 'bg-ink-faint text-ink-muted',
                )}
              >
                {tab.count}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
