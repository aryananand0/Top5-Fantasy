'use client'

import { cn } from '@/lib/cn'
import { SearchInput } from '@/components/ui/SearchInput'
import { Button } from '@/components/ui/Button'
import { PlayerListItem } from './PlayerListItem'
import type { PlayerResponse } from '@/lib/api/players'
import type { Position } from '@/lib/api/squad'
import type { SelectedMap } from '@/hooks/useSquadBuilder'

const POSITIONS: (Position | null)[] = [null, 'GK', 'DEF', 'MID', 'FWD']
const POSITION_LABELS: Record<string, string> = {
  '': 'All',
  GK: 'GK',
  DEF: 'DEF',
  MID: 'MID',
  FWD: 'FWD',
}

const MAX_PER_CLUB = 2

interface PlayerSearchPanelProps {
  players: PlayerResponse[]
  loading: boolean
  page: number
  totalPages: number
  onLoadMore: () => void

  searchQuery: string
  onSearchChange: (q: string) => void
  positionFilter: Position | null
  onPositionChange: (p: Position | null) => void

  selectedMap: SelectedMap
  clubCounts: Record<number, number>
  budgetRemaining: number
  activePosition: Position | null

  onAddPlayer: (player: PlayerResponse) => void
}

export function PlayerSearchPanel({
  players,
  loading,
  page,
  totalPages,
  onLoadMore,
  searchQuery,
  onSearchChange,
  positionFilter,
  onPositionChange,
  selectedMap,
  clubCounts,
  budgetRemaining,
  activePosition,
  onAddPlayer,
}: PlayerSearchPanelProps) {
  const selectedPlayerIds = new Set(
    Object.values(selectedMap)
      .filter(Boolean)
      .map((p) => p!.id),
  )

  return (
    <div className="flex flex-col gap-3">
      {/* Search input */}
      <SearchInput
        placeholder="Search players…"
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        aria-label="Search players"
      />

      {/* Position filter pills */}
      <div className="flex gap-1.5 overflow-x-auto pb-0.5 scrollbar-hide">
        {POSITIONS.map((pos) => {
          const key = pos ?? ''
          const isActive = positionFilter === pos
          return (
            <button
              key={key}
              onClick={() => onPositionChange(pos)}
              className={cn(
                'flex-none px-3 py-1.5 rounded-lg border-2 text-xs font-bold',
                'transition-all duration-100 cursor-pointer',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-1',
                isActive
                  ? 'bg-ink text-paper border-ink'
                  : 'bg-paper text-ink-muted border-ink-faint hover:border-ink hover:text-ink',
              )}
            >
              {POSITION_LABELS[key]}
            </button>
          )
        })}
      </div>

      {/* Active slot hint */}
      {activePosition && (
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-tint-blue border-2 border-marker-blue">
          <span className="text-xs font-bold text-ink">
            Select a <span className="text-marker-blue">{activePosition}</span> for the highlighted slot
          </span>
        </div>
      )}

      {/* Player list */}
      <div className="flex flex-col gap-1.5">
        {players.map((player) => (
          <PlayerListItem
            key={player.id}
            player={player}
            isSelected={selectedPlayerIds.has(player.id)}
            clubLimitReached={
              !selectedPlayerIds.has(player.id) &&
              (clubCounts[player.team_id] ?? 0) >= MAX_PER_CLUB
            }
            overBudget={
              !selectedPlayerIds.has(player.id) &&
              budgetRemaining < player.current_price
            }
            activePosition={activePosition}
            onAdd={onAddPlayer}
          />
        ))}

        {/* Empty state */}
        {!loading && players.length === 0 && (
          <div className="py-8 text-center">
            <p className="text-ink-muted text-sm">No players found.</p>
            {searchQuery && (
              <button
                onClick={() => onSearchChange('')}
                className="mt-2 text-xs text-marker-blue underline cursor-pointer"
              >
                Clear search
              </button>
            )}
          </div>
        )}

        {/* Load more */}
        {!loading && page < totalPages && (
          <Button
            variant="ghost"
            size="sm"
            fullWidth
            onClick={onLoadMore}
            className="mt-1"
          >
            Load more players
          </Button>
        )}

        {/* Loading state */}
        {loading && (
          <div className="py-6 text-center">
            <p className="text-ink-muted text-sm animate-pulse">Loading players…</p>
          </div>
        )}
      </div>
    </div>
  )
}
