'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import type { PlayerResponse } from '@/lib/api/players'
import type { Position, SquadResponse, ValidationError } from '@/lib/api/squad'
import { fetchSquad, createSquad, replaceSquad, ApiError } from '@/lib/api/squad'
import { fetchPlayers } from '@/lib/api/players'

// ── Slot definitions ──────────────────────────────────────────────────────────

export type SlotKey =
  | 'GK-0'
  | 'DEF-0' | 'DEF-1' | 'DEF-2'
  | 'MID-0' | 'MID-1' | 'MID-2' | 'MID-3'
  | 'FWD-0' | 'FWD-1' | 'FWD-2'

export interface Slot {
  key: SlotKey
  position: Position
}

export const SLOTS: Slot[] = [
  { key: 'GK-0',  position: 'GK'  },
  { key: 'DEF-0', position: 'DEF' },
  { key: 'DEF-1', position: 'DEF' },
  { key: 'DEF-2', position: 'DEF' },
  { key: 'MID-0', position: 'MID' },
  { key: 'MID-1', position: 'MID' },
  { key: 'MID-2', position: 'MID' },
  { key: 'MID-3', position: 'MID' },
  { key: 'FWD-0', position: 'FWD' },
  { key: 'FWD-1', position: 'FWD' },
  { key: 'FWD-2', position: 'FWD' },
]

const BUDGET_CAP = 100
const MAX_PER_CLUB = 2

export type Mode = 'loading' | 'view' | 'build' | 'saving'

export type SelectedMap = Partial<Record<SlotKey, PlayerResponse>>

// ── Return type ───────────────────────────────────────────────────────────────

export interface UseSquadBuilderReturn {
  // Mode
  mode: Mode
  existingSquad: SquadResponse | null
  loadError: string | null
  enterBuildMode: () => void
  cancelBuildMode: () => void

  // Slot state
  selectedMap: SelectedMap
  activeSlot: SlotKey | null
  setActiveSlot: (key: SlotKey | null) => void
  addPlayer: (player: PlayerResponse) => void
  removeSlot: (key: SlotKey) => void

  // Derived budget + counts
  budgetRemaining: number
  positionCounts: Record<Position, number>
  clubCounts: Record<number, number>
  selectedCount: number
  isReady: boolean

  // Player browser
  searchQuery: string
  setSearchQuery: (q: string) => void
  positionFilter: Position | null
  setPositionFilter: (p: Position | null) => void
  browserPlayers: PlayerResponse[]
  browserLoading: boolean
  browserPage: number
  browserTotalPages: number
  loadMorePlayers: () => void

  // Save
  validationErrors: ValidationError[]
  saveError: string | null
  saveSquad: (name?: string) => Promise<void>
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useSquadBuilder(): UseSquadBuilderReturn {
  // ── Core state ─────────────────────────────────────────────────────────────
  const [mode, setMode] = useState<Mode>('loading')
  const [existingSquad, setExistingSquad] = useState<SquadResponse | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  // Slot selection
  const [selectedMap, setSelectedMap] = useState<SelectedMap>({})
  const [activeSlot, setActiveSlot] = useState<SlotKey | null>(null)

  // Player browser
  const [searchQuery, setSearchQuery] = useState('')
  const [positionFilter, setPositionFilter] = useState<Position | null>(null)
  const [browserPlayers, setBrowserPlayers] = useState<PlayerResponse[]>([])
  const [browserLoading, setBrowserLoading] = useState(false)
  const [browserPage, setBrowserPage] = useState(1)
  const [browserTotalPages, setBrowserTotalPages] = useState(1)

  // Save state
  const [validationErrors, setValidationErrors] = useState<ValidationError[]>([])
  const [saveError, setSaveError] = useState<string | null>(null)

  // Debounce timer ref for search
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // ── Load existing squad on mount ───────────────────────────────────────────
  useEffect(() => {
    fetchSquad()
      .then((squad) => {
        if (squad) {
          setExistingSquad(squad)
          setMode('view')
        } else {
          setMode('build')
        }
      })
      .catch(() => {
        // Network error or API unavailable — enter build mode silently.
        // Errors are surfaced per-action (e.g., on save) when the user tries
        // to interact, not as a page-blocking state during load.
        setMode('build')
      })
  }, [])

  // ── Player browser fetch ───────────────────────────────────────────────────
  const fetchBrowserPage = useCallback(
    async (page: number, position: Position | null, search: string, append: boolean) => {
      setBrowserLoading(true)
      try {
        const result = await fetchPlayers({
          position: position ?? undefined,
          search: search || undefined,
          page,
          per_page: 40,
        })
        setBrowserPlayers((prev) =>
          append ? [...prev, ...result.players] : result.players,
        )
        setBrowserPage(result.page)
        setBrowserTotalPages(result.total_pages)
      } catch {
        // Silently fail — browser just shows empty state
      } finally {
        setBrowserLoading(false)
      }
    },
    [],
  )

  // Reload browser when filters change (debounce search input)
  useEffect(() => {
    if (mode !== 'build') return

    if (searchTimer.current) clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => {
      fetchBrowserPage(1, positionFilter, searchQuery, false)
    }, 300)

    return () => {
      if (searchTimer.current) clearTimeout(searchTimer.current)
    }
  }, [positionFilter, searchQuery, mode, fetchBrowserPage])

  const loadMorePlayers = useCallback(() => {
    if (browserLoading || browserPage >= browserTotalPages) return
    fetchBrowserPage(browserPage + 1, positionFilter, searchQuery, true)
  }, [browserLoading, browserPage, browserTotalPages, positionFilter, searchQuery, fetchBrowserPage])

  // ── Mode transitions ───────────────────────────────────────────────────────
  const enterBuildMode = useCallback(() => {
    if (existingSquad) {
      // Pre-populate slots from existing squad
      const map: SelectedMap = {}
      const slotsByPosition: Record<Position, SlotKey[]> = {
        GK:  SLOTS.filter((s) => s.position === 'GK').map((s) => s.key),
        DEF: SLOTS.filter((s) => s.position === 'DEF').map((s) => s.key),
        MID: SLOTS.filter((s) => s.position === 'MID').map((s) => s.key),
        FWD: SLOTS.filter((s) => s.position === 'FWD').map((s) => s.key),
      }
      const counters: Record<Position, number> = { GK: 0, DEF: 0, MID: 0, FWD: 0 }

      for (const p of existingSquad.players) {
        const idx = counters[p.position]
        const key = slotsByPosition[p.position][idx] as SlotKey
        if (key) {
          // Convert SquadPlayerResponse to PlayerResponse shape
          map[key] = {
            id: p.player_id,
            name: p.name,
            display_name: p.display_name,
            position: p.position,
            team_id: p.team_id,
            team_name: p.team_name,
            team_short_name: p.team_short_name,
            current_price: p.current_price,
            form_score: p.form_score,
            starter_confidence: p.starter_confidence,
            is_available: p.is_available,
            availability_note: null,
          }
          counters[p.position]++
        }
      }
      setSelectedMap(map)
    } else {
      setSelectedMap({})
    }
    setValidationErrors([])
    setSaveError(null)
    setActiveSlot(null)
    setSearchQuery('')
    setPositionFilter(null)
    setMode('build')
  }, [existingSquad])

  const cancelBuildMode = useCallback(() => {
    if (existingSquad) {
      setMode('view')
    }
    setSelectedMap({})
    setActiveSlot(null)
    setValidationErrors([])
    setSaveError(null)
  }, [existingSquad])

  // ── Slot operations ────────────────────────────────────────────────────────
  const handleSetActiveSlot = useCallback(
    (key: SlotKey | null) => {
      setActiveSlot(key)
      if (key) {
        const slot = SLOTS.find((s) => s.key === key)
        if (slot) setPositionFilter(slot.position)
      }
    },
    [],
  )

  const addPlayer = useCallback(
    (player: PlayerResponse) => {
      if (!activeSlot) return

      const targetSlot = SLOTS.find((s) => s.key === activeSlot)
      if (!targetSlot || targetSlot.position !== player.position) return

      setSelectedMap((prev) => {
        const next = { ...prev, [activeSlot]: player }
        return next
      })

      // Auto-advance to next empty slot of the same position (or any position)
      setActiveSlot((prev) => {
        if (!prev) return null
        const currentIdx = SLOTS.findIndex((s) => s.key === prev)
        for (let i = currentIdx + 1; i < SLOTS.length; i++) {
          const slot = SLOTS[i]
          if (!selectedMap[slot.key]) return slot.key
        }
        // Check from beginning
        for (let i = 0; i < currentIdx; i++) {
          const slot = SLOTS[i]
          if (!selectedMap[slot.key]) return slot.key
        }
        return null
      })
    },
    [activeSlot, selectedMap],
  )

  const removeSlot = useCallback((key: SlotKey) => {
    setSelectedMap((prev) => {
      const next = { ...prev }
      delete next[key]
      return next
    })
  }, [])

  // ── Derived values ─────────────────────────────────────────────────────────
  const filledPlayers = Object.values(selectedMap).filter(Boolean) as PlayerResponse[]
  const selectedCount = filledPlayers.length

  const budgetRemaining =
    BUDGET_CAP - filledPlayers.reduce((sum, p) => sum + p.current_price, 0)

  const positionCounts = filledPlayers.reduce(
    (acc, p) => ({ ...acc, [p.position]: (acc[p.position] ?? 0) + 1 }),
    { GK: 0, DEF: 0, MID: 0, FWD: 0 } as Record<Position, number>,
  )

  const clubCounts = filledPlayers.reduce(
    (acc, p) => ({ ...acc, [p.team_id]: (acc[p.team_id] ?? 0) + 1 }),
    {} as Record<number, number>,
  )

  const isReady = selectedCount === 11

  // ── Save ──────────────────────────────────────────────────────────────────
  const saveSquad = useCallback(
    async (name?: string) => {
      const playerIds = SLOTS.map((s) => selectedMap[s.key]?.id).filter(
        (id): id is number => id !== undefined,
      )
      if (playerIds.length !== 11) return

      setSaveError(null)
      setValidationErrors([])
      setMode('saving')

      try {
        if (existingSquad) {
          const { squad, errors } = await replaceSquad(playerIds)
          if (errors.length > 0) {
            setValidationErrors(errors)
            setMode('build')
            return
          }
          setExistingSquad(squad)
        } else {
          const { squad, errors } = await createSquad(playerIds, name)
          if (errors.length > 0) {
            setValidationErrors(errors)
            setMode('build')
            return
          }
          setExistingSquad(squad)
        }
        setMode('view')
        setSelectedMap({})
        setActiveSlot(null)
      } catch (err) {
        setSaveError(
          err instanceof ApiError ? err.message : 'Something went wrong. Please try again.',
        )
        setMode('build')
      }
    },
    [existingSquad, selectedMap],
  )

  // ── Canary: prevent adding player that breaks club limit or budget ─────────
  // (exposed via `canAdd` check in the player list item)
  // We expose clubCounts and budgetRemaining for the consumer to do this check.

  return {
    mode,
    existingSquad,
    loadError,
    enterBuildMode,
    cancelBuildMode,

    selectedMap,
    activeSlot,
    setActiveSlot: handleSetActiveSlot,
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
  }
}
