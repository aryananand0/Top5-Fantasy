'use client'

import { cn } from '@/lib/cn'
import type { GameweekStatus } from '@/lib/api/lineup'

interface GameweekBannerProps {
  gameweekNumber: number
  gameweekName: string
  deadline: string
  status: GameweekStatus
  isEditable: boolean
  className?: string
}

const STATUS_LABEL: Record<GameweekStatus, string> = {
  UPCOMING: 'Picks open',
  LOCKED: 'Locked',
  ACTIVE: 'In play',
  SCORING: 'Scoring',
  FINISHED: 'Finished',
}

const STATUS_COLOR: Record<GameweekStatus, string> = {
  UPCOMING: 'bg-tint-green border-marker-green text-marker-green',
  LOCKED:   'bg-tint-yellow border-marker-yellow text-ink',
  ACTIVE:   'bg-tint-blue border-marker-blue text-marker-blue',
  SCORING:  'bg-tint-orange border-marker-orange text-marker-orange',
  FINISHED: 'bg-paper-dark border-ink-faint text-ink-muted',
}

function formatDeadline(isoString: string): string {
  try {
    const d = new Date(isoString)
    return d.toLocaleString(undefined, {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return isoString
  }
}

export function GameweekBanner({
  gameweekNumber,
  gameweekName,
  deadline,
  status,
  isEditable,
  className,
}: GameweekBannerProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-between gap-3 px-4 py-3',
        'rounded-2xl border-2 border-ink bg-paper shadow-sketch-sm',
        className,
      )}
    >
      <div className="flex flex-col gap-0.5 min-w-0">
        <span className="font-display font-black text-base text-ink leading-tight">
          {gameweekName}
        </span>
        <span className="text-xs text-ink-muted leading-tight">
          {isEditable
            ? `Deadline: ${formatDeadline(deadline)}`
            : status === 'ACTIVE'
            ? 'Matches in progress'
            : status === 'SCORING'
            ? 'Computing scores…'
            : status === 'FINISHED'
            ? 'Gameweek finished'
            : 'Lineup locked'}
        </span>
      </div>

      <span
        className={cn(
          'flex-none inline-flex items-center px-2 py-1 rounded-lg border-2',
          'text-xs font-bold uppercase tracking-wide',
          STATUS_COLOR[status],
        )}
      >
        {STATUS_LABEL[status]}
      </span>
    </div>
  )
}
