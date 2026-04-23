'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import type { SquadResponse, SquadPlayerResponse } from '@/lib/api/squad'
import { fetchSquad } from '@/lib/api/squad'
import { fetchPlayers } from '@/lib/api/players'
import type { PlayerResponse } from '@/lib/api/players'
import {
  fetchTransferSummary,
  previewTransfers,
  applyTransfers,
} from '@/lib/api/transfer'
import { ApiError } from '@/lib/api/client'
import type {
  TransferSummaryResponse,
  TransferPreviewResponse,
  TransferPairRequest,
} from '@/lib/api/transfer'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface PendingPair {
  playerOut: SquadPlayerResponse
  playerIn: PlayerResponse
}

export type TransferView = 'squad' | 'browser'

export interface UseTransfersReturn {
  // Loading states
  loading: boolean
  applyError: string | null

  // Data
  squad: SquadResponse | null
  summary: TransferSummaryResponse | null

  // Pending transfer pairs
  pendingPairs: PendingPair[]

  // Current selection (one pair in progress)
  selectedOut: SquadPlayerResponse | null
  selectPlayerOut: (player: SquadPlayerResponse) => void
  cancelSelection: () => void

  // View toggle between squad list and player browser
  view: TransferView

  // Player browser
  browserPlayers: PlayerResponse[]
  browserLoading: boolean
  browserQuery: string
  setBrowserQuery: (q: string) => void
  browserPosition: string | null
  setBrowserPosition: (p: string | null) => void
  browserPage: number
  browserTotalPages: number
  loadMoreBrowserPlayers: () => void
  selectPlayerIn: (player: PlayerResponse) => void

  // Remove a pending pair
  removePair: (index: number) => void

  // Preview
  preview: TransferPreviewResponse | null
  previewLoading: boolean
  refreshPreview: () => void

  // Apply
  applying: boolean
  applyTransfersNow: () => Promise<void>
  appliedSuccess: boolean
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useTransfers(): UseTransfersReturn {
  const [loading, setLoading] = useState(true)
  const [squad, setSquad] = useState<SquadResponse | null>(null)
  const [summary, setSummary] = useState<TransferSummaryResponse | null>(null)

  const [pendingPairs, setPendingPairs] = useState<PendingPair[]>([])
  const [selectedOut, setSelectedOut] = useState<SquadPlayerResponse | null>(null)
  const [view, setView] = useState<TransferView>('squad')

  const [browserPlayers, setBrowserPlayers] = useState<PlayerResponse[]>([])
  const [browserLoading, setBrowserLoading] = useState(false)
  const [browserQuery, setBrowserQueryState] = useState('')
  const [browserPosition, setBrowserPositionState] = useState<string | null>(null)
  const [browserPage, setBrowserPage] = useState(1)
  const [browserTotalPages, setBrowserTotalPages] = useState(1)
  const browserQueryRef = useRef('')
  const browserPositionRef = useRef<string | null>(null)

  const [preview, setPreview] = useState<TransferPreviewResponse | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)

  const [applying, setApplying] = useState(false)
  const [applyError, setApplyError] = useState<string | null>(null)
  const [appliedSuccess, setAppliedSuccess] = useState(false)

  // ── Initial load ────────────────────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    Promise.all([
      fetchSquad().catch(() => null),
      fetchTransferSummary().catch(() => null),
    ]).then(([squadData, summaryData]) => {
      if (cancelled) return
      setSquad(squadData)
      setSummary(summaryData)
      setLoading(false)
    })
    return () => { cancelled = true }
  }, [])

  // ── Player browser fetch ─────────────────────────────────────────────────────
  const fetchBrowserPage = useCallback(async (
    query: string,
    position: string | null,
    page: number,
    append: boolean,
  ) => {
    setBrowserLoading(true)
    try {
      const result = await fetchPlayers({
        search: query || undefined,
        position: (position as any) || undefined,
        page,
        per_page: 30,
        available_only: false,
      })
      setBrowserPlayers(prev => append ? [...prev, ...result.players] : result.players)
      setBrowserPage(result.page)
      setBrowserTotalPages(result.total_pages)
    } catch {
      // ignore browser errors silently
    } finally {
      setBrowserLoading(false)
    }
  }, [])

  // Trigger browser fetch when view switches to browser or filters change
  useEffect(() => {
    if (view !== 'browser') return
    fetchBrowserPage(browserQuery, browserPosition, 1, false)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view, browserQuery, browserPosition])

  const setBrowserQuery = useCallback((q: string) => {
    setBrowserQueryState(q)
    browserQueryRef.current = q
    setBrowserPage(1)
  }, [])

  const setBrowserPosition = useCallback((p: string | null) => {
    setBrowserPositionState(p)
    browserPositionRef.current = p
    setBrowserPage(1)
  }, [])

  const loadMoreBrowserPlayers = useCallback(() => {
    if (browserPage < browserTotalPages && !browserLoading) {
      fetchBrowserPage(browserQuery, browserPosition, browserPage + 1, true)
    }
  }, [browserPage, browserTotalPages, browserLoading, browserQuery, browserPosition, fetchBrowserPage])

  // ── Selection ────────────────────────────────────────────────────────────────
  const selectPlayerOut = useCallback((player: SquadPlayerResponse) => {
    setSelectedOut(player)
    setBrowserQueryState('')
    // Default browser to same position as the outgoing player
    setBrowserPositionState(player.position)
    setBrowserPage(1)
    setView('browser')
  }, [])

  const cancelSelection = useCallback(() => {
    setSelectedOut(null)
    setView('squad')
  }, [])

  const selectPlayerIn = useCallback((player: PlayerResponse) => {
    if (!selectedOut) return
    setPendingPairs(prev => {
      // Replace any existing pair that transfers out the same player
      const filtered = prev.filter(p => p.playerOut.player_id !== selectedOut.player_id)
      return [...filtered, { playerOut: selectedOut, playerIn: player }]
    })
    setSelectedOut(null)
    setView('squad')
  }, [selectedOut])

  const removePair = useCallback((index: number) => {
    setPendingPairs(prev => prev.filter((_, i) => i !== index))
  }, [])

  // ── Preview ──────────────────────────────────────────────────────────────────
  const refreshPreview = useCallback(async () => {
    if (pendingPairs.length === 0) {
      setPreview(null)
      return
    }
    setPreviewLoading(true)
    try {
      const pairs: TransferPairRequest[] = pendingPairs.map(p => ({
        player_out_id: p.playerOut.player_id,
        player_in_id: p.playerIn.id,
      }))
      const result = await previewTransfers(pairs)
      setPreview(result)
    } catch {
      setPreview(null)
    } finally {
      setPreviewLoading(false)
    }
  }, [pendingPairs])

  // Auto-refresh preview when pairs change
  useEffect(() => {
    if (pendingPairs.length > 0) {
      refreshPreview()
    } else {
      setPreview(null)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingPairs])

  // ── Apply ────────────────────────────────────────────────────────────────────
  const applyTransfersNow = useCallback(async () => {
    if (pendingPairs.length === 0) return
    setApplying(true)
    setApplyError(null)
    try {
      const pairs: TransferPairRequest[] = pendingPairs.map(p => ({
        player_out_id: p.playerOut.player_id,
        player_in_id: p.playerIn.id,
      }))
      const result = await applyTransfers(pairs)
      setSquad(result.squad)
      setSummary(prev => prev ? {
        ...prev,
        free_transfers_available: result.free_transfers_remaining,
        transfers_made_this_gw: result.transfers_this_gw,
        budget_remaining: result.squad.budget_remaining,
      } : prev)
      setPendingPairs([])
      setPreview(null)
      setAppliedSuccess(true)
    } catch (err) {
      if (err instanceof ApiError) {
        const detail = err.detail as any
        const msgs: string[] = Array.isArray(detail?.errors)
          ? detail.errors
          : [err.message]
        setApplyError(msgs.join(' · '))
      } else {
        setApplyError('Something went wrong. Please try again.')
      }
    } finally {
      setApplying(false)
    }
  }, [pendingPairs])

  return {
    loading,
    applyError,
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
    refreshPreview,
    applying,
    applyTransfersNow,
    appliedSuccess,
  }
}
