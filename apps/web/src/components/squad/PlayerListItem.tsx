'use client'

import { cn } from '@/lib/cn'
import { PositionBadge } from '@/components/ui/Badge'
import type { PlayerResponse } from '@/lib/api/players'
import type { Position } from '@/lib/api/squad'

interface PlayerListItemProps {
  player: PlayerResponse
  /** Whether this player is already in the selected squad */
  isSelected: boolean
  /** Whether adding this player would exceed the club limit */
  clubLimitReached: boolean
  /** Whether adding this player would exceed the budget */
  overBudget: boolean
  /** Active slot position — null means no slot selected */
  activePosition: Position | null
  onAdd: (player: PlayerResponse) => void
}

export function PlayerListItem({
  player,
  isSelected,
  clubLimitReached,
  overBudget,
  activePosition,
  onAdd,
}: PlayerListItemProps) {
  const displayName = player.display_name ?? player.name
  const wrongPosition = activePosition !== null && player.position !== activePosition
  const isDisabled = isSelected || clubLimitReached || overBudget || !player.is_available || wrongPosition

  const handleClick = () => {
    if (!isDisabled) onAdd(player)
  }

  let disabledReason = ''
  if (isSelected) disabledReason = 'In squad'
  else if (wrongPosition) disabledReason = 'Wrong position'
  else if (!player.is_available) disabledReason = player.availability_note ?? 'Unavailable'
  else if (clubLimitReached) disabledReason = 'Club limit'
  else if (overBudget) disabledReason = 'Over budget'

  return (
    <button
      onClick={handleClick}
      disabled={isDisabled}
      aria-label={`Add ${displayName} to squad`}
      className={cn(
        'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border-2',
        'text-left transition-all duration-100 cursor-pointer',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-1',
        isSelected
          ? 'bg-tint-green border-marker-green opacity-70 cursor-not-allowed'
          : isDisabled
          ? 'bg-paper border-ink-faint opacity-50 cursor-not-allowed'
          : 'bg-paper border-ink hover:-translate-y-px hover:shadow-sketch-sm active:translate-y-px active:shadow-none shadow-[1px_1px_0px_#1C1917]',
      )}
    >
      {/* Position badge */}
      <PositionBadge position={player.position} size="sm" />

      {/* Name + team */}
      <div className="flex-1 min-w-0">
        <p className="font-display font-bold text-sm text-ink truncate leading-tight">
          {displayName}
        </p>
        <p className="text-[0.7rem] text-ink-muted leading-tight truncate">
          {player.team_short_name}
          {disabledReason ? <span className="ml-1.5 text-marker-red font-medium">· {disabledReason}</span> : null}
        </p>
      </div>

      {/* Form score indicator */}
      <div className="shrink-0 flex flex-col items-end gap-0.5">
        <span className="font-display font-bold text-sm text-ink leading-none">
          £{player.current_price.toFixed(1)}
        </span>
        {player.form_score > 0 && (
          <span className="text-[0.6rem] text-marker-green font-bold leading-none">
            {player.form_score.toFixed(1)} form
          </span>
        )}
      </div>

      {/* Add indicator */}
      {!isDisabled && (
        <div className="shrink-0 w-6 h-6 rounded-full bg-ink flex items-center justify-center">
          <span className="text-paper text-sm font-bold leading-none">+</span>
        </div>
      )}
      {isSelected && (
        <div className="shrink-0 w-6 h-6 rounded-full bg-marker-green flex items-center justify-center">
          <span className="text-paper text-xs font-bold leading-none">✓</span>
        </div>
      )}
    </button>
  )
}
