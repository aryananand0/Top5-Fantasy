'use client'

import { cn } from '@/lib/cn'
import type { SlotKey, SelectedMap, Slot, Mode } from '@/hooks/useSquadBuilder'
import { SLOTS } from '@/hooks/useSquadBuilder'
import { EmptySlot, FilledChip } from './SquadPlayerChip'
import type { Position, SquadPlayerResponse } from '@/lib/api/squad'

// ── Formation row ─────────────────────────────────────────────────────────────

interface FormationRowProps {
  label: Position
  slots: Slot[]
  selectedMap: SelectedMap
  activeSlot: SlotKey | null
  onSlotClick: (key: SlotKey) => void
  onRemove: (key: SlotKey) => void
  mode: Mode
}

function FormationRow({
  label,
  slots,
  selectedMap,
  activeSlot,
  onSlotClick,
  onRemove,
  mode,
}: FormationRowProps) {
  const isEditing = mode === 'build' || mode === 'saving'

  return (
    <div className="flex flex-col items-center gap-2">
      <span className="text-[0.6rem] font-bold uppercase tracking-widest text-white/40 text-center">
        {label}
      </span>
      <div className="flex items-center justify-center gap-3 sm:gap-5 w-full">
        {slots.map((slot) => {
          const player = selectedMap[slot.key]
          if (player) {
            return (
              <FilledChip
                key={slot.key}
                playerName={player.name}
                teamShortName={player.team_short_name}
                slotKey={slot.key}
                onRemove={onRemove}
                dark
                readOnly={!isEditing}
                price={isEditing ? player.current_price : undefined}
              />
            )
          }
          return (
            <EmptySlot
              key={slot.key}
              position={slot.position}
              slotKey={slot.key}
              isActive={activeSlot === slot.key}
              onClick={onSlotClick}
              dark
            />
          )
        })}
      </div>
    </div>
  )
}

// ── View-only row (existing squad, no edit) ───────────────────────────────────

interface ViewRowProps {
  label: Position
  players: SquadPlayerResponse[]
}

function ViewRow({ label, players }: ViewRowProps) {
  return (
    <div className="flex flex-col items-center gap-2">
      <span className="text-[0.6rem] font-bold uppercase tracking-widest text-white/40 text-center">
        {label}
      </span>
      <div className="flex items-center justify-center gap-3 sm:gap-5 w-full">
        {players.map((p) => {
          const initial = p.name.charAt(0).toUpperCase()
          const parts = p.name.trim().split(' ')
          const shortName = parts.length > 1 ? parts[parts.length - 1] : parts[0]

          return (
            <div key={p.player_id} className="flex flex-col items-center gap-1.5 min-w-0">
              <div className="w-10 h-10 rounded-full bg-white/20 border-2 border-white shadow-[2px_2px_0px_rgba(0,0,0,0.3)] flex items-center justify-center">
                <span className="text-xs font-black text-white leading-none">{initial}</span>
              </div>
              <div className="flex flex-col items-center gap-0.5">
                <span className="text-[0.65rem] font-bold leading-none truncate max-w-[56px] text-center text-white">
                  {shortName}
                </span>
                <span className="text-[0.55rem] leading-none text-white/50">
                  £{p.current_price.toFixed(1)}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

interface SquadFormationBoardProps {
  mode: Mode
  selectedMap: SelectedMap
  activeSlot: SlotKey | null
  onSlotClick: (key: SlotKey) => void
  onRemoveSlot: (key: SlotKey) => void
  /** Provide for view mode — bypasses slot system */
  viewPlayers?: SquadPlayerResponse[]
}

export function SquadFormationBoard({
  mode,
  selectedMap,
  activeSlot,
  onSlotClick,
  onRemoveSlot,
  viewPlayers,
}: SquadFormationBoardProps) {
  const isViewMode = mode === 'view' && viewPlayers != null

  const slotsByPosition = (pos: Position) =>
    SLOTS.filter((s) => s.position === pos)

  const viewByPosition = (pos: Position) =>
    (viewPlayers ?? []).filter((p) => p.position === pos)

  return (
    <div className="rounded-2xl border-2 border-ink overflow-hidden shadow-sketch-md">
      <div className="bg-[#2E7D52] p-4 space-y-5">
        {/* Subtle centre line */}
        <div className="w-full border-t border-white/10" />

        {isViewMode ? (
          <>
            <ViewRow label="FWD" players={viewByPosition('FWD')} />
            <ViewRow label="MID" players={viewByPosition('MID')} />
            <ViewRow label="DEF" players={viewByPosition('DEF')} />
            <ViewRow label="GK"  players={viewByPosition('GK')}  />
          </>
        ) : (
          <>
            <FormationRow
              label="FWD"
              slots={slotsByPosition('FWD')}
              selectedMap={selectedMap}
              activeSlot={activeSlot}
              onSlotClick={onSlotClick}
              onRemove={onRemoveSlot}
              mode={mode}
            />
            <FormationRow
              label="MID"
              slots={slotsByPosition('MID')}
              selectedMap={selectedMap}
              activeSlot={activeSlot}
              onSlotClick={onSlotClick}
              onRemove={onRemoveSlot}
              mode={mode}
            />
            <FormationRow
              label="DEF"
              slots={slotsByPosition('DEF')}
              selectedMap={selectedMap}
              activeSlot={activeSlot}
              onSlotClick={onSlotClick}
              onRemove={onRemoveSlot}
              mode={mode}
            />
            <FormationRow
              label="GK"
              slots={slotsByPosition('GK')}
              selectedMap={selectedMap}
              activeSlot={activeSlot}
              onSlotClick={onSlotClick}
              onRemove={onRemoveSlot}
              mode={mode}
            />
          </>
        )}
      </div>

      {/* Pitch bottom strip */}
      <div className="bg-paper-dark border-t-2 border-ink px-4 py-2">
        <p className="text-center text-[0.6rem] text-ink-muted font-medium tracking-wide uppercase">
          {isViewMode ? '1 · 3 · 4 · 3' : 'Tap a slot to add a player'}
        </p>
      </div>
    </div>
  )
}
