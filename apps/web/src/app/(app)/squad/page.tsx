'use client'

import { PageShell } from '@/components/ui/PageShell'
import { SectionHeader } from '@/components/ui/SectionHeader'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Badge, PositionBadge } from '@/components/ui/Badge'
import { Divider } from '@/components/ui/Divider'
import { SquadFormationBoard } from '@/components/squad/SquadFormationBoard'
import { PlayerSearchPanel } from '@/components/squad/PlayerSearchPanel'
import { SquadSummaryBar } from '@/components/squad/SquadSummaryBar'
import { GameweekBanner } from '@/components/lineup/GameweekBanner'
import { CaptainPicker } from '@/components/lineup/CaptainPicker'
import { useSquadBuilder } from '@/hooks/useSquadBuilder'
import { useCurrentLineup } from '@/hooks/useCurrentLineup'

// ── Loading skeleton ───────────────────────────────────────────────────────────

function LoadingSkeleton() {
  return (
    <PageShell maxWidth="lg">
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-paper-darker rounded-xl w-40" />
        <div className="h-16 bg-paper-darker rounded-2xl" />
        <div className="h-64 bg-paper-darker rounded-2xl" />
        <div className="h-48 bg-paper-darker rounded-2xl" />
      </div>
    </PageShell>
  )
}

// ── Lineup section (captain/VC picker) ────────────────────────────────────────

function LineupSection() {
  const {
    loadState,
    lineup,
    pendingCaptainId,
    pendingVcId,
    setPendingCaptain,
    setPendingVC,
    hasUnsavedChanges,
    selectionIsValid,
    saveState,
    saveError,
    saveSelection,
  } = useCurrentLineup()

  if (loadState === 'loading') {
    return (
      <div className="animate-pulse rounded-2xl border-2 border-ink-faint bg-paper h-20" />
    )
  }

  if (loadState === 'no_squad' || loadState === 'no_gameweek' || !lineup) {
    return null
  }

  if (loadState === 'error') {
    return null
  }

  return (
    <div className="flex flex-col gap-3">
      <GameweekBanner
        gameweekNumber={lineup.gameweek_number}
        gameweekName={lineup.gameweek_name}
        deadline={lineup.gameweek_deadline}
        status={lineup.gameweek_status}
        isEditable={lineup.is_editable}
      />

      <SectionHeader
        title="Captain & Vice-Captain"
        subtitle={
          lineup.is_editable
            ? 'Captain earns 2× points · VC covers if captain doesn\'t play'
            : 'Lineup locked'
        }
        className="mb-0"
      />

      <CaptainPicker
        players={lineup.players}
        captainId={pendingCaptainId}
        vcId={pendingVcId}
        isEditable={lineup.is_editable}
        isLocked={lineup.is_locked}
        hasUnsavedChanges={hasUnsavedChanges}
        selectionIsValid={selectionIsValid}
        saveState={saveState}
        saveError={saveError}
        onSetCaptain={setPendingCaptain}
        onSetVC={setPendingVC}
        onSave={saveSelection}
      />
    </div>
  )
}

// ── View mode: existing squad display ─────────────────────────────────────────

function ViewSquad({
  squad,
  onEdit,
}: {
  squad: NonNullable<ReturnType<typeof useSquadBuilder>['existingSquad']>
  onEdit: () => void
}) {
  const budgetUsed = squad.total_cost
  const budgetPct = Math.min(100, (budgetUsed / 100) * 100)

  const sortOrder = { GK: 0, DEF: 1, MID: 2, FWD: 3 }
  const sorted = [...squad.players].sort(
    (a, b) => sortOrder[a.position] - sortOrder[b.position],
  )

  return (
    <PageShell maxWidth="lg">
      <SectionHeader
        title={squad.name}
        subtitle={`${squad.players.length} players · ${squad.total_points} pts`}
        action={
          <Button variant="tinted" color="blue" size="sm" onClick={onEdit}>
            Manage
          </Button>
        }
        className="mb-4"
      />

      {/* ── Gameweek lineup section ── */}
      <div className="mb-4">
        <LineupSection />
      </div>

      <Divider style="wavy" spacing="sm" />

      {/* Budget bar */}
      <Card variant="flat" padding="sm" className="mb-4 mt-2">
        <div className="flex items-center justify-between mb-2">
          <span className="label-text text-ink-muted text-xs">Budget used</span>
          <span className="font-display font-bold text-sm text-ink">
            £{budgetUsed.toFixed(1)}M / £100M
          </span>
        </div>
        <div className="h-3 bg-paper-dark border-2 border-ink rounded-full overflow-hidden">
          <div
            className="h-full bg-ink rounded-full transition-all"
            style={{ width: `${budgetPct}%` }}
          />
        </div>
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs text-ink-muted">
            <span className="font-bold text-marker-green">
              £{squad.budget_remaining.toFixed(1)}M
            </span>{' '}
            remaining
          </span>
          <Badge color="orange" variant="tinted" size="sm">
            Team Value £{(100 - squad.budget_remaining).toFixed(1)}M
          </Badge>
        </div>
      </Card>

      {/* Pitch formation */}
      <div className="mb-4">
        <SquadFormationBoard
          mode="view"
          selectedMap={{}}
          activeSlot={null}
          onSlotClick={() => {}}
          onRemoveSlot={() => {}}
          viewPlayers={squad.players}
        />
      </div>

      <Divider style="dashed" spacing="sm" />

      {/* Player detail list */}
      <SectionHeader title="Player Details" className="mb-3 mt-1" />
      <div className="flex flex-col gap-2">
        {sorted.map((player) => (
          <Card key={player.player_id} variant="flat" padding="sm">
            <div className="flex items-center gap-3">
              <PositionBadge position={player.position} />
              <div className="flex-1 min-w-0">
                <p className="font-display font-bold text-sm text-ink truncate">
                  {player.display_name ?? player.name}
                </p>
                <p className="text-xs text-ink-muted">{player.team_name}</p>
              </div>
              <div className="text-right shrink-0">
                <p className="font-display font-bold text-sm text-ink">
                  £{player.current_price.toFixed(1)}M
                </p>
                {player.form_score > 0 && (
                  <p className="text-[0.65rem] text-marker-green font-bold">
                    {player.form_score.toFixed(1)} form
                  </p>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </PageShell>
  )
}

// ── Build / Edit mode ─────────────────────────────────────────────────────────

function BuildSquad({
  builder,
}: {
  builder: ReturnType<typeof useSquadBuilder>
}) {
  const {
    mode,
    existingSquad,
    selectedMap,
    activeSlot,
    setActiveSlot,
    addPlayer,
    removeSlot,
    budgetRemaining,
    positionCounts,
    clubCounts,
    selectedCount,
    isReady,
    searchQuery,
    setSearchQuery,
    positionFilter,
    setPositionFilter,
    browserPlayers,
    browserLoading,
    browserPage,
    browserTotalPages,
    loadMorePlayers,
    validationErrors,
    saveError,
    saveSquad,
    cancelBuildMode,
  } = builder

  const isSaving = mode === 'saving'
  const activePosition = activeSlot
    ? (activeSlot.split('-')[0] as 'GK' | 'DEF' | 'MID' | 'FWD')
    : null

  return (
    <PageShell maxWidth="lg">
      <SectionHeader
        title={existingSquad ? 'Edit Squad' : 'Build Squad'}
        subtitle={
          existingSquad
            ? 'Replace your current squad (full swap)'
            : 'Pick 11 players · £100M budget · max 2 per club'
        }
        className="mb-4"
      />

      {/* ── Desktop: two-column layout ── */}
      <div className="md:grid md:grid-cols-[1fr_340px] md:gap-5 md:items-start">
        {/* Left: formation board + summary bar */}
        <div className="flex flex-col gap-4">
          <SquadFormationBoard
            mode={mode}
            selectedMap={selectedMap}
            activeSlot={activeSlot}
            onSlotClick={setActiveSlot}
            onRemoveSlot={removeSlot}
          />

          <SquadSummaryBar
            budgetRemaining={budgetRemaining}
            positionCounts={positionCounts}
            selectedCount={selectedCount}
            isReady={isReady}
            isSaving={isSaving}
            validationErrors={validationErrors}
            saveError={saveError}
            onSave={() => saveSquad()}
            onCancel={cancelBuildMode}
            hasExistingSquad={!!existingSquad}
          />
        </div>

        {/* Right: player browser */}
        <div className="mt-4 md:mt-0 md:sticky md:top-20">
          <div className="rounded-2xl border-2 border-ink bg-paper shadow-sketch p-4">
            <p className="label-text text-ink-muted mb-3">Player Browser</p>
            <PlayerSearchPanel
              players={browserPlayers}
              loading={browserLoading}
              page={browserPage}
              totalPages={browserTotalPages}
              onLoadMore={loadMorePlayers}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              positionFilter={positionFilter}
              onPositionChange={setPositionFilter}
              selectedMap={selectedMap}
              clubCounts={clubCounts}
              budgetRemaining={budgetRemaining}
              activePosition={activePosition}
              onAddPlayer={addPlayer}
            />
          </div>
        </div>
      </div>
    </PageShell>
  )
}

// ── Page root ─────────────────────────────────────────────────────────────────

export default function SquadPage() {
  const builder = useSquadBuilder()
  const { mode, existingSquad, enterBuildMode } = builder

  if (mode === 'loading') return <LoadingSkeleton />

  if (mode === 'view' && existingSquad) {
    return <ViewSquad squad={existingSquad} onEdit={enterBuildMode} />
  }

  return <BuildSquad builder={builder} />
}
