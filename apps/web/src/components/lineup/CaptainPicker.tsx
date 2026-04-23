'use client'

import { cn } from '@/lib/cn'
import { Button } from '@/components/ui/Button'
import { PositionBadge } from '@/components/ui/Badge'
import type { LineupPlayer } from '@/lib/api/lineup'
import type { SaveState } from '@/hooks/useCurrentLineup'

// ── Single player row ─────────────────────────────────────────────────────────

interface PlayerRowProps {
  player: LineupPlayer
  isCaptain: boolean
  isVC: boolean
  isEditable: boolean
  onSetCaptain: (id: number) => void
  onSetVC: (id: number) => void
}

function PlayerRow({
  player,
  isCaptain,
  isVC,
  isEditable,
  onSetCaptain,
  onSetVC,
}: PlayerRowProps) {
  const displayName = player.display_name ?? player.name

  return (
    <div
      className={cn(
        'flex items-center gap-2 px-3 py-2.5 rounded-xl border-2 transition-colors',
        isCaptain
          ? 'bg-tint-yellow border-marker-yellow'
          : isVC
          ? 'bg-tint-blue border-marker-blue'
          : 'bg-paper border-ink',
      )}
    >
      {/* C / VC buttons */}
      <div className="flex gap-1 shrink-0">
        <button
          onClick={() => isEditable && onSetCaptain(player.player_id)}
          disabled={!isEditable}
          aria-label={`Set ${displayName} as captain`}
          aria-pressed={isCaptain}
          className={cn(
            'w-7 h-7 rounded-full border-2 flex items-center justify-center',
            'text-[0.65rem] font-black leading-none transition-all duration-100',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-1',
            isEditable ? 'cursor-pointer' : 'cursor-not-allowed opacity-60',
            isCaptain
              ? 'bg-marker-yellow border-marker-yellow text-ink shadow-[1px_1px_0px_#1C1917]'
              : 'bg-paper border-ink text-ink-muted hover:border-marker-yellow hover:bg-tint-yellow',
          )}
        >
          C
        </button>
        <button
          onClick={() => isEditable && onSetVC(player.player_id)}
          disabled={!isEditable}
          aria-label={`Set ${displayName} as vice-captain`}
          aria-pressed={isVC}
          className={cn(
            'w-7 h-7 rounded-full border-2 flex items-center justify-center',
            'text-[0.65rem] font-black leading-none transition-all duration-100',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-1',
            isEditable ? 'cursor-pointer' : 'cursor-not-allowed opacity-60',
            isVC
              ? 'bg-marker-blue border-marker-blue text-paper shadow-[1px_1px_0px_#1C1917]'
              : 'bg-paper border-ink text-ink-muted hover:border-marker-blue hover:bg-tint-blue',
          )}
        >
          VC
        </button>
      </div>

      {/* Position badge */}
      <PositionBadge position={player.position} size="sm" />

      {/* Name + team */}
      <div className="flex-1 min-w-0">
        <p className="font-display font-bold text-sm text-ink truncate leading-tight">
          {displayName}
        </p>
        <p className="text-[0.7rem] text-ink-muted leading-tight truncate">
          {player.team_short_name}
          {!player.is_available && (
            <span className="ml-1.5 text-marker-red font-medium">· Unavailable</span>
          )}
        </p>
      </div>

      {/* Price / points */}
      <div className="shrink-0 text-right">
        {player.points_scored !== null ? (
          <span className="font-display font-black text-base text-marker-green leading-none">
            {isCaptain ? player.points_scored * 2 : player.points_scored}
            <span className="text-[0.6rem] font-bold text-ink-muted ml-0.5">pts</span>
          </span>
        ) : (
          <span className="text-xs text-ink-muted font-bold">
            £{player.current_price.toFixed(1)}
          </span>
        )}
      </div>
    </div>
  )
}

// ── Validation hints ──────────────────────────────────────────────────────────

interface ValidationHintProps {
  captainId: number | null
  vcId: number | null
  isLocked: boolean
}

function ValidationHint({ captainId, vcId, isLocked }: ValidationHintProps) {
  if (isLocked) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-tint-yellow border-2 border-marker-yellow">
        <span className="text-xs font-bold text-ink">
          🔒 Lineup is locked. No further changes allowed.
        </span>
      </div>
    )
  }

  if (!captainId) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-paper border-2 border-ink-faint">
        <span className="text-xs text-ink-muted">
          Tap <strong className="text-ink">C</strong> to select your captain. Their points are doubled.
        </span>
      </div>
    )
  }

  if (!vcId) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-paper border-2 border-ink-faint">
        <span className="text-xs text-ink-muted">
          Tap <strong className="text-ink">VC</strong> to select your vice-captain.
        </span>
      </div>
    )
  }

  return null
}

// ── Main component ────────────────────────────────────────────────────────────

interface CaptainPickerProps {
  players: LineupPlayer[]
  captainId: number | null
  vcId: number | null
  isEditable: boolean
  isLocked: boolean
  hasUnsavedChanges: boolean
  selectionIsValid: boolean
  saveState: SaveState
  saveError: string | null
  onSetCaptain: (id: number) => void
  onSetVC: (id: number) => void
  onSave: () => void
}

export function CaptainPicker({
  players,
  captainId,
  vcId,
  isEditable,
  isLocked,
  hasUnsavedChanges,
  selectionIsValid,
  saveState,
  saveError,
  onSetCaptain,
  onSetVC,
  onSave,
}: CaptainPickerProps) {
  const sortOrder = { GK: 0, DEF: 1, MID: 2, FWD: 3 } as const
  const sorted = [...players].sort(
    (a, b) => sortOrder[a.position] - sortOrder[b.position],
  )

  return (
    <div className="flex flex-col gap-3">
      {/* Hint / lock notice */}
      <ValidationHint captainId={captainId} vcId={vcId} isLocked={isLocked} />

      {/* Player rows */}
      <div className="flex flex-col gap-1.5">
        {sorted.map((player) => (
          <PlayerRow
            key={player.player_id}
            player={player}
            isCaptain={player.player_id === captainId}
            isVC={player.player_id === vcId}
            isEditable={isEditable}
            onSetCaptain={onSetCaptain}
            onSetVC={onSetVC}
          />
        ))}
      </div>

      {/* Save error */}
      {saveError && (
        <div className="px-3 py-2 rounded-xl bg-tint-red border-2 border-marker-red">
          <p className="text-xs text-ink">{saveError}</p>
        </div>
      )}

      {/* Save success */}
      {saveState === 'saved' && !hasUnsavedChanges && (
        <div className="px-3 py-2 rounded-xl bg-tint-green border-2 border-marker-green">
          <p className="text-xs font-bold text-marker-green">Captain selection saved.</p>
        </div>
      )}

      {/* Save button */}
      {isEditable && (
        <Button
          variant="primary"
          size="md"
          fullWidth
          onClick={onSave}
          disabled={!selectionIsValid || saveState === 'saving'}
        >
          {saveState === 'saving'
            ? 'Saving…'
            : hasUnsavedChanges
            ? 'Save Captain & VC'
            : 'Selection saved ✓'}
        </Button>
      )}
    </div>
  )
}
