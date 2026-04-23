'use client'

import { cn } from '@/lib/cn'
import { positionMeta } from '@/lib/design-tokens'
import type { Position } from '@/lib/api/squad'
import type { SlotKey } from '@/hooks/useSquadBuilder'

// ── Empty slot ────────────────────────────────────────────────────────────────

interface EmptySlotProps {
  position: Position
  slotKey: SlotKey
  isActive: boolean
  onClick: (key: SlotKey) => void
  dark?: boolean
}

export function EmptySlot({ position, slotKey, isActive, onClick, dark = false }: EmptySlotProps) {
  const { color } = positionMeta[position]

  const ringColor: Record<string, string> = {
    yellow: 'border-marker-yellow',
    blue: 'border-marker-blue',
    green: 'border-marker-green',
    red: 'border-marker-red',
  }

  return (
    <button
      onClick={() => onClick(slotKey)}
      aria-label={`Add ${position} player`}
      className={cn(
        'flex flex-col items-center gap-1.5 min-w-0 group cursor-pointer',
      )}
    >
      <div
        className={cn(
          'w-10 h-10 rounded-full border-2 border-dashed flex items-center justify-center',
          'transition-all duration-100',
          isActive
            ? `${ringColor[color] ?? 'border-white'} bg-white/20 scale-110`
            : dark
            ? 'border-white/40 hover:border-white/80'
            : 'border-ink-faint hover:border-ink',
        )}
      >
        <span
          className={cn(
            'text-lg font-bold leading-none',
            isActive
              ? dark ? 'text-white' : 'text-ink'
              : dark ? 'text-white/40 group-hover:text-white/70' : 'text-ink-faint group-hover:text-ink',
          )}
        >
          +
        </span>
      </div>
      <div className="flex flex-col items-center gap-0.5">
        <span
          className={cn(
            'text-[0.6rem] font-bold leading-none uppercase',
            dark ? 'text-white/50' : 'text-ink-muted',
          )}
        >
          {position}
        </span>
      </div>
    </button>
  )
}

// ── Filled chip ───────────────────────────────────────────────────────────────

interface FilledChipProps {
  playerName: string
  teamShortName: string
  slotKey: SlotKey
  onRemove: (key: SlotKey) => void
  dark?: boolean
  /** View-only mode — no remove button */
  readOnly?: boolean
  pts?: number
  price?: number
}

export function FilledChip({
  playerName,
  teamShortName,
  slotKey,
  onRemove,
  dark = false,
  readOnly = false,
  pts,
  price,
}: FilledChipProps) {
  const initial = playerName.charAt(0).toUpperCase()
  // First name or surname (whichever is shorter)
  const parts = playerName.trim().split(' ')
  const shortName = parts.length > 1 ? parts[parts.length - 1] : parts[0]

  return (
    <div className="flex flex-col items-center gap-1.5 min-w-0">
      <div className="relative">
        <button
          onClick={() => !readOnly && onRemove(slotKey)}
          aria-label={readOnly ? playerName : `Remove ${playerName}`}
          disabled={readOnly}
          className={cn(
            'w-10 h-10 rounded-full border-2 flex items-center justify-center',
            'transition-all duration-100',
            readOnly
              ? 'cursor-default'
              : 'cursor-pointer hover:-translate-y-px active:translate-y-px',
            dark
              ? 'bg-white/20 border-white shadow-[2px_2px_0px_rgba(0,0,0,0.3)]'
              : 'bg-paper border-ink shadow-sketch-sm',
          )}
        >
          <span
            className={cn(
              'text-xs font-black leading-none',
              dark ? 'text-white' : 'text-ink',
            )}
          >
            {initial}
          </span>
        </button>
        {!readOnly && (
          <div
            className={cn(
              'absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center',
              'border border-white/60 bg-marker-red',
            )}
            aria-hidden="true"
          >
            <span className="text-[0.5rem] font-black text-white leading-none">✕</span>
          </div>
        )}
      </div>

      <div className="flex flex-col items-center gap-0.5">
        <span
          className={cn(
            'text-[0.65rem] font-bold leading-none truncate max-w-[56px] text-center',
            dark ? 'text-white' : 'text-ink',
          )}
        >
          {shortName}
        </span>
        <span
          className={cn(
            'text-[0.55rem] leading-none',
            dark ? 'text-white/50' : 'text-ink-muted',
          )}
        >
          {readOnly && pts !== undefined
            ? `${pts}pts`
            : price !== undefined
            ? `£${price.toFixed(1)}`
            : teamShortName}
        </span>
      </div>
    </div>
  )
}
