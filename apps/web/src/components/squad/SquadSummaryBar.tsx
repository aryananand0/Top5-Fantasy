'use client'

import { cn } from '@/lib/cn'
import { Button } from '@/components/ui/Button'
import type { Position, ValidationError } from '@/lib/api/squad'

const POSITION_REQUIREMENTS: Record<Position, number> = {
  GK: 1,
  DEF: 3,
  MID: 4,
  FWD: 3,
}

const BUDGET_CAP = 100

interface SquadSummaryBarProps {
  budgetRemaining: number
  positionCounts: Record<Position, number>
  selectedCount: number
  isReady: boolean
  isSaving: boolean
  validationErrors: ValidationError[]
  saveError: string | null
  onSave: () => void
  onCancel: () => void
  /** Optional — shown when editing an existing squad */
  hasExistingSquad?: boolean
}

export function SquadSummaryBar({
  budgetRemaining,
  positionCounts,
  selectedCount,
  isReady,
  isSaving,
  validationErrors,
  saveError,
  onSave,
  onCancel,
  hasExistingSquad = false,
}: SquadSummaryBarProps) {
  const totalSpent = BUDGET_CAP - budgetRemaining
  const budgetPct = Math.min(100, (totalSpent / BUDGET_CAP) * 100)
  const isOverBudget = budgetRemaining < 0

  return (
    <div className="flex flex-col gap-3">
      {/* Budget bar */}
      <div className="rounded-2xl border-2 border-ink bg-paper p-3 shadow-sketch-sm">
        <div className="flex items-center justify-between mb-2">
          <span className="label-text text-ink-muted text-xs">Budget</span>
          <span
            className={cn(
              'font-display font-bold text-sm',
              isOverBudget ? 'text-marker-red' : 'text-ink',
            )}
          >
            £{budgetRemaining.toFixed(1)}M left
          </span>
        </div>

        {/* Progress bar */}
        <div className="h-2.5 bg-paper-dark border border-ink rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full rounded-full transition-all duration-300',
              isOverBudget ? 'bg-marker-red' : budgetPct > 90 ? 'bg-marker-orange' : 'bg-ink',
            )}
            style={{ width: `${budgetPct}%` }}
          />
        </div>

        <div className="flex items-center justify-between mt-1.5">
          <span className="text-[0.65rem] text-ink-muted">
            £{totalSpent.toFixed(1)}M spent
          </span>
          <span className="text-[0.65rem] text-ink-muted">of £{BUDGET_CAP}M</span>
        </div>
      </div>

      {/* Position slot counters */}
      <div className="grid grid-cols-4 gap-1.5">
        {(Object.keys(POSITION_REQUIREMENTS) as Position[]).map((pos) => {
          const current = positionCounts[pos] ?? 0
          const required = POSITION_REQUIREMENTS[pos]
          const isMet = current === required
          const isOver = current > required

          return (
            <div
              key={pos}
              className={cn(
                'rounded-xl border-2 p-2 text-center',
                isMet
                  ? 'border-marker-green bg-tint-green'
                  : isOver
                  ? 'border-marker-red bg-tint-red'
                  : 'border-ink-faint bg-paper',
              )}
            >
              <p
                className={cn(
                  'font-display font-black text-base leading-none',
                  isMet ? 'text-marker-green' : isOver ? 'text-marker-red' : 'text-ink-muted',
                )}
              >
                {current}/{required}
              </p>
              <p className="text-[0.6rem] font-bold text-ink-muted uppercase mt-0.5">{pos}</p>
            </div>
          )
        })}
      </div>

      {/* Server-side validation errors */}
      {validationErrors.length > 0 && (
        <div className="rounded-xl border-2 border-marker-red bg-tint-red p-3">
          <p className="text-xs font-bold text-marker-red mb-1.5">Fix these issues:</p>
          <ul className="flex flex-col gap-1">
            {validationErrors.map((err) => (
              <li key={err.code} className="text-xs text-ink flex items-start gap-1.5">
                <span className="mt-px text-marker-red">·</span>
                {err.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Generic save error */}
      {saveError && (
        <div className="rounded-xl border-2 border-marker-red bg-tint-red p-3">
          <p className="text-xs text-ink">{saveError}</p>
        </div>
      )}

      {/* CTA buttons */}
      <div className="flex gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={onCancel}
          disabled={isSaving}
          className="flex-none"
        >
          {hasExistingSquad ? 'Cancel' : 'Reset'}
        </Button>
        <Button
          variant="primary"
          size="md"
          fullWidth
          onClick={onSave}
          disabled={!isReady || isOverBudget || isSaving}
        >
          {isSaving
            ? 'Saving…'
            : hasExistingSquad
            ? `Update Squad (${selectedCount}/11)`
            : `Save Squad (${selectedCount}/11)`}
        </Button>
      </div>
    </div>
  )
}
