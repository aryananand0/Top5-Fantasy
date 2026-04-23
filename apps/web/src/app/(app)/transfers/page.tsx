'use client'

import { cn } from '@/lib/cn'
import { PageShell } from '@/components/ui/PageShell'
import { Card } from '@/components/ui/Card'
import { Badge, PositionBadge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import Link from 'next/link'
import { EmptyState } from '@/components/ui/EmptyState'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { SearchInput } from '@/components/ui/SearchInput'
import { useTransfers } from '@/hooks/useTransfers'
import type { SquadPlayerResponse } from '@/lib/api/squad'
import type { PlayerResponse } from '@/lib/api/players'
import type { PendingPair } from '@/hooks/useTransfers'

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

/** Top banner — GW info, free transfers, budget */
function TransferBanner({
  summary,
  pendingCount,
  previewPointsHit,
}: {
  summary: NonNullable<ReturnType<typeof useTransfers>['summary']>
  pendingCount: number
  previewPointsHit: number
}) {
  const deadline = new Date(summary.gameweek_deadline)
  const deadlineStr = deadline.toLocaleDateString('en-GB', {
    weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
  const isEditable = summary.is_editable
  const freeLeft = Math.max(0, summary.free_transfers_available - pendingCount)
  const pointsHit = previewPointsHit

  return (
    <Card variant="tinted" color={isEditable ? 'blue' : 'red'} className="mb-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <Badge color="blue" variant="solid" size="sm">GW{summary.gameweek_number}</Badge>
            <Badge
              color={isEditable ? 'green' : 'red'}
              variant="tinted"
              size="sm"
            >
              {isEditable ? 'Transfers Open' : 'Locked'}
            </Badge>
          </div>
          <p className="font-display font-bold text-xl text-ink leading-tight">
            {freeLeft} free transfer{freeLeft !== 1 ? 's' : ''} left
          </p>
          {pointsHit > 0 && (
            <p className="text-xs text-marker-red font-bold mt-0.5">
              −{pointsHit} pts hit from pending transfers
            </p>
          )}
          <p className="text-xs text-ink-muted mt-0.5">
            Extra transfers cost <span className="font-bold text-marker-red">−4 pts</span> each
          </p>
        </div>
        <div className="text-right shrink-0">
          <p className="label-text text-ink-muted text-[0.65rem]">Deadline</p>
          <p className="text-xs font-bold text-ink mt-0.5 leading-tight">{deadlineStr}</p>
          <p className="text-xs text-ink-muted mt-1">
            £{summary.budget_remaining.toFixed(1)}M bank
          </p>
        </div>
      </div>
    </Card>
  )
}

/** One row in the squad list — tap to select for transfer out */
function SquadPlayerRow({
  player,
  isSelectedOut,
  isPendingOut,
  onSelect,
}: {
  player: SquadPlayerResponse
  isSelectedOut: boolean
  isPendingOut: boolean
  onSelect: () => void
}) {
  const displayName = player.display_name ?? player.name
  return (
    <button
      onClick={onSelect}
      className={cn(
        'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border-2 text-left transition-all duration-100',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink',
        isSelectedOut
          ? 'bg-tint-red border-marker-red'
          : isPendingOut
          ? 'bg-paper border-ink-faint opacity-50 cursor-not-allowed'
          : 'bg-paper border-ink hover:-translate-y-px hover:shadow-sketch-sm active:translate-y-px cursor-pointer',
      )}
    >
      <PositionBadge position={player.position} size="sm" />
      <div className="flex-1 min-w-0">
        <p className="font-display font-bold text-sm text-ink truncate leading-tight">
          {displayName}
        </p>
        <p className="text-[0.7rem] text-ink-muted leading-tight truncate">
          {player.team_short_name}
          {isPendingOut && (
            <span className="ml-1.5 text-marker-orange font-bold">· Transfer out</span>
          )}
        </p>
      </div>
      <div className="shrink-0 text-right">
        <p className="font-bold text-sm text-ink">£{player.current_price.toFixed(1)}M</p>
        {player.form_score > 0 && (
          <p className="text-[0.6rem] text-ink-muted">{player.form_score.toFixed(1)} form</p>
        )}
      </div>
      {isSelectedOut ? (
        <div className="shrink-0 w-6 h-6 rounded-full bg-marker-red flex items-center justify-center">
          <span className="text-paper text-xs font-black leading-none">−</span>
        </div>
      ) : !isPendingOut ? (
        <div className="shrink-0 w-5 h-5 rounded-md border-2 border-ink-faint flex items-center justify-center">
          <span className="text-ink-muted text-xs leading-none">→</span>
        </div>
      ) : null}
    </button>
  )
}

/** One row in the player browser — tap to select as replacement */
function BrowserPlayerRow({
  player,
  alreadyInSquad,
  onSelect,
}: {
  player: PlayerResponse
  alreadyInSquad: boolean
  onSelect: () => void
}) {
  const displayName = player.display_name ?? player.name
  const disabled = alreadyInSquad || !player.is_available

  return (
    <button
      onClick={() => !disabled && onSelect()}
      disabled={disabled}
      className={cn(
        'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border-2 text-left transition-all duration-100',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink',
        alreadyInSquad
          ? 'bg-tint-green border-marker-green opacity-60 cursor-not-allowed'
          : disabled
          ? 'bg-paper border-ink-faint opacity-40 cursor-not-allowed'
          : 'bg-paper border-ink hover:-translate-y-px hover:shadow-sketch-sm active:translate-y-px cursor-pointer shadow-[1px_1px_0px_#1C1917]',
      )}
    >
      <PositionBadge position={player.position} size="sm" />
      <div className="flex-1 min-w-0">
        <p className="font-display font-bold text-sm text-ink truncate leading-tight">
          {displayName}
        </p>
        <p className="text-[0.7rem] text-ink-muted leading-tight truncate">
          {player.team_short_name}
          {alreadyInSquad && <span className="ml-1.5 text-marker-green font-bold">· In squad</span>}
          {!alreadyInSquad && !player.is_available && (
            <span className="ml-1.5 text-marker-red font-bold">
              · {player.availability_note ?? 'Unavailable'}
            </span>
          )}
        </p>
      </div>
      <div className="shrink-0 text-right">
        <p className="font-bold text-sm text-ink">£{player.current_price.toFixed(1)}M</p>
        {player.form_score > 0 && (
          <p className="text-[0.6rem] text-marker-green font-bold">{player.form_score.toFixed(1)} form</p>
        )}
      </div>
      {!disabled && (
        <div className="shrink-0 w-6 h-6 rounded-full bg-ink flex items-center justify-center">
          <span className="text-paper text-sm font-bold leading-none">+</span>
        </div>
      )}
      {alreadyInSquad && (
        <div className="shrink-0 w-6 h-6 rounded-full bg-marker-green flex items-center justify-center">
          <span className="text-paper text-xs font-bold leading-none">✓</span>
        </div>
      )}
    </button>
  )
}

/** Pending transfer cart — shows queued pairs and confirm button */
function TransferCart({
  pairs,
  preview,
  previewLoading,
  applying,
  applyError,
  appliedSuccess,
  isEditable,
  onRemove,
  onApply,
}: {
  pairs: PendingPair[]
  preview: ReturnType<typeof useTransfers>['preview']
  previewLoading: boolean
  applying: boolean
  applyError: string | null
  appliedSuccess: boolean
  isEditable: boolean
  onRemove: (i: number) => void
  onApply: () => void
}) {
  if (pairs.length === 0 && !appliedSuccess) return null

  const budgetAfter = preview?.budget_after
  const errors = preview?.errors ?? []

  return (
    <div className="mt-4 rounded-2xl border-2 border-ink bg-paper shadow-sketch-sm overflow-hidden">
      <div className="px-4 py-3 border-b-2 border-ink bg-paper-dark flex items-center justify-between">
        <p className="font-display font-bold text-sm text-ink">
          {appliedSuccess ? 'Transfers Applied!' : `Pending (${pairs.length})`}
        </p>
        {preview && !previewLoading && (
          <p className={cn('text-xs font-bold', preview.total_points_hit > 0 ? 'text-marker-red' : 'text-marker-green')}>
            {preview.total_points_hit > 0
              ? `−${preview.total_points_hit} pts hit`
              : 'No point cost'}
          </p>
        )}
      </div>

      {appliedSuccess && (
        <div className="px-4 py-3">
          <p className="text-sm text-marker-green font-bold">
            Transfers confirmed. Your squad has been updated.
          </p>
        </div>
      )}

      {!appliedSuccess && (
        <>
          <div className="flex flex-col divide-y-2 divide-ink-faint">
            {pairs.map((pair, i) => (
              <div key={i} className="px-4 py-2.5 flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="text-xs font-bold text-marker-red leading-tight truncate max-w-[100px]">
                      {pair.playerOut.display_name ?? pair.playerOut.name}
                    </span>
                    <span className="text-ink-muted text-xs">→</span>
                    <span className="text-xs font-bold text-marker-green leading-tight truncate max-w-[100px]">
                      {pair.playerIn.display_name ?? pair.playerIn.name}
                    </span>
                  </div>
                  <p className="text-[0.65rem] text-ink-muted mt-0.5">
                    £{pair.playerOut.current_price.toFixed(1)} → £{pair.playerIn.current_price.toFixed(1)}
                    {pair.playerIn.current_price > pair.playerOut.current_price && (
                      <span className="text-marker-red ml-1">
                        (−£{(pair.playerIn.current_price - pair.playerOut.current_price).toFixed(1)})
                      </span>
                    )}
                    {pair.playerOut.current_price > pair.playerIn.current_price && (
                      <span className="text-marker-green ml-1">
                        (+£{(pair.playerOut.current_price - pair.playerIn.current_price).toFixed(1)})
                      </span>
                    )}
                  </p>
                </div>
                <button
                  onClick={() => onRemove(i)}
                  className="shrink-0 w-6 h-6 rounded-full border-2 border-ink-faint flex items-center justify-center text-ink-muted hover:border-marker-red hover:text-marker-red transition-colors"
                  aria-label="Remove transfer"
                >
                  <span className="text-xs font-bold leading-none">×</span>
                </button>
              </div>
            ))}
          </div>

          {budgetAfter !== undefined && (
            <div className="px-4 py-2 border-t-2 border-ink-faint bg-paper-dark">
              <p className="text-xs text-ink-muted">
                Bank after: <span className={cn('font-bold', budgetAfter < 0 ? 'text-marker-red' : 'text-ink')}>
                  £{budgetAfter.toFixed(1)}M
                </span>
              </p>
            </div>
          )}

          {errors.length > 0 && (
            <div className="px-4 py-2 border-t-2 border-marker-red bg-tint-red">
              {errors.map((e, i) => (
                <p key={i} className="text-xs text-marker-red font-medium">{e}</p>
              ))}
            </div>
          )}

          {applyError && (
            <div className="px-4 py-2 border-t-2 border-marker-red bg-tint-red">
              <p className="text-xs text-marker-red font-medium">{applyError}</p>
            </div>
          )}

          <div className="px-4 py-3 border-t-2 border-ink">
            <Button
              variant="primary"
              size="md"
              fullWidth
              disabled={!isEditable || applying || previewLoading || (preview != null && !preview.is_valid)}
              onClick={onApply}
            >
              {applying
                ? 'Applying…'
                : `Confirm ${pairs.length} Transfer${pairs.length !== 1 ? 's' : ''}`}
            </Button>
          </div>
        </>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Position filter bar
// ---------------------------------------------------------------------------

const POSITIONS = ['GK', 'DEF', 'MID', 'FWD'] as const

function PositionFilter({
  active,
  onChange,
}: {
  active: string | null
  onChange: (p: string | null) => void
}) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-0.5">
      <button
        onClick={() => onChange(null)}
        className={cn(
          'shrink-0 px-3 py-1 rounded-lg border-2 text-xs font-bold transition-colors',
          active === null
            ? 'border-ink bg-ink text-paper'
            : 'border-ink-faint text-ink-muted hover:border-ink',
        )}
      >
        All
      </button>
      {POSITIONS.map(p => (
        <button
          key={p}
          onClick={() => onChange(active === p ? null : p)}
          className={cn(
            'shrink-0 px-3 py-1 rounded-lg border-2 text-xs font-bold transition-colors',
            active === p
              ? 'border-ink bg-ink text-paper'
              : 'border-ink-faint text-ink-muted hover:border-ink',
          )}
        >
          {p}
        </button>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function TransfersPage() {
  const {
    loading,
    squad,
    summary,
    pendingPairs,
    selectedOut,
    selectPlayerOut,
    cancelSelection,
    view,
    browserPlayers,
    browserLoading,
    browserQuery,
    setBrowserQuery,
    browserPosition,
    setBrowserPosition,
    browserPage,
    browserTotalPages,
    loadMoreBrowserPlayers,
    selectPlayerIn,
    removePair,
    preview,
    previewLoading,
    applying,
    applyError,
    applyTransfersNow,
    appliedSuccess,
  } = useTransfers()

  // Player IDs currently in squad (for browser "already in squad" state)
  const squadPlayerIds = new Set(
    (squad?.players ?? []).map(p => p.player_id)
  )
  // IDs going out in pending pairs — free slots again
  const outgoingIds = new Set(pendingPairs.map(p => p.playerOut.player_id))
  // IDs coming in — treat as already in squad
  const incomingIds = new Set(pendingPairs.map(p => p.playerIn.id))

  const pendingOutIds = new Set(pendingPairs.map(p => p.playerOut.player_id))

  if (loading) {
    return (
      <PageShell maxWidth="lg">
        <div className="flex items-center justify-center py-20">
          <p className="text-ink-muted text-sm animate-pulse">Loading transfers…</p>
        </div>
      </PageShell>
    )
  }

  if (!squad || !summary) {
    return (
      <PageShell maxWidth="lg">
        <EmptyState
          title="No squad yet"
          description="Build your squad first before making transfers."
          action={<Link href="/squad"><Button variant="primary" size="md">Build Squad</Button></Link>}
        />
      </PageShell>
    )
  }

  return (
    <PageShell maxWidth="lg">
      {/* ── Status banner ── */}
      <TransferBanner
        summary={summary}
        pendingCount={pendingPairs.length}
        previewPointsHit={preview?.total_points_hit ?? 0}
      />

      {view === 'squad' ? (
        <>
          {/* ── Squad list ── */}
          <SectionHeader
            title="Your Squad"
            subtitle={
              pendingPairs.length > 0
                ? `${pendingPairs.length} transfer${pendingPairs.length !== 1 ? 's' : ''} pending — tap another player to add more`
                : 'Tap a player to transfer them out'
            }
            className="mb-3"
          />

          <div className="flex flex-col gap-2">
            {(squad.players ?? []).map(player => (
              <SquadPlayerRow
                key={player.player_id}
                player={player}
                isSelectedOut={selectedOut?.player_id === player.player_id}
                isPendingOut={pendingOutIds.has(player.player_id)}
                onSelect={() => {
                  if (!summary.is_editable) return
                  if (pendingOutIds.has(player.player_id)) return
                  selectPlayerOut(player)
                }}
              />
            ))}
          </div>

          {/* ── Transfer cart ── */}
          <TransferCart
            pairs={pendingPairs}
            preview={preview}
            previewLoading={previewLoading}
            applying={applying}
            applyError={applyError}
            appliedSuccess={appliedSuccess}
            isEditable={summary.is_editable}
            onRemove={removePair}
            onApply={applyTransfersNow}
          />

          {!summary.is_editable && (
            <div className="mt-4 rounded-xl border-2 border-marker-red bg-tint-red p-3 text-center">
              <p className="text-sm font-bold text-marker-red">
                Transfers are locked for GW{summary.gameweek_number}
              </p>
            </div>
          )}
        </>
      ) : (
        <>
          {/* ── Player browser header ── */}
          <div className="flex items-center gap-3 mb-3">
            <button
              onClick={cancelSelection}
              className="shrink-0 px-3 py-1.5 rounded-xl border-2 border-ink text-xs font-bold hover:bg-paper-dark transition-colors"
            >
              ← Cancel
            </button>
            <div className="flex-1 min-w-0">
              <p className="font-display font-bold text-sm text-ink leading-tight truncate">
                Replacing:{' '}
                <span className="text-marker-red">
                  {selectedOut?.display_name ?? selectedOut?.name}
                </span>
              </p>
              <p className="text-xs text-ink-muted">
                £{selectedOut?.current_price.toFixed(1)}M · {selectedOut?.position}
              </p>
            </div>
          </div>

          <div className="flex flex-col gap-2 mb-3">
            <SearchInput
              value={browserQuery}
              onChange={e => setBrowserQuery(e.target.value)}
              placeholder="Search players…"
            />
            <PositionFilter
              active={browserPosition}
              onChange={setBrowserPosition}
            />
          </div>

          <div className="flex flex-col gap-2">
            {browserLoading && browserPlayers.length === 0 ? (
              <p className="text-center text-ink-muted text-sm py-8 animate-pulse">
                Loading players…
              </p>
            ) : browserPlayers.length === 0 ? (
              <p className="text-center text-ink-muted text-sm py-8">No players found.</p>
            ) : (
              browserPlayers.map(player => {
                const effectiveSquadIds = (squadPlayerIds as Set<number>)
                const isIn = (effectiveSquadIds.has(player.id) && !outgoingIds.has(player.id))
                  || incomingIds.has(player.id)
                return (
                  <BrowserPlayerRow
                    key={player.id}
                    player={player}
                    alreadyInSquad={isIn}
                    onSelect={() => selectPlayerIn(player)}
                  />
                )
              })
            )}

            {browserPage < browserTotalPages && (
              <Button
                variant="ghost"
                size="sm"
                fullWidth
                onClick={loadMoreBrowserPlayers}
                disabled={browserLoading}
                className="mt-2"
              >
                {browserLoading ? 'Loading…' : 'Load more'}
              </Button>
            )}
          </div>
        </>
      )}
    </PageShell>
  )
}
