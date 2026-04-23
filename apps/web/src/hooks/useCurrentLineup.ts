'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  fetchCurrentLineup,
  updateCaptain,
  ApiError,
  type LineupResponse,
} from '@/lib/api/lineup'

export type LineupLoadState = 'loading' | 'ready' | 'no_squad' | 'no_gameweek' | 'error'
export type SaveState = 'idle' | 'saving' | 'saved' | 'error'

export interface UseCurrentLineupReturn {
  // Load state
  loadState: LineupLoadState
  lineup: LineupResponse | null
  loadError: string | null

  // Pending selection (local, not yet saved)
  pendingCaptainId: number | null
  pendingVcId: number | null
  setPendingCaptain: (playerId: number) => void
  setPendingVC: (playerId: number) => void

  // Derived
  hasUnsavedChanges: boolean
  selectionIsValid: boolean  // both set and different

  // Save
  saveState: SaveState
  saveError: string | null
  saveSelection: () => Promise<void>

  // Reload
  reload: () => Promise<void>
}

export function useCurrentLineup(): UseCurrentLineupReturn {
  const [loadState, setLoadState] = useState<LineupLoadState>('loading')
  const [lineup, setLineup] = useState<LineupResponse | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  // Local pending selections — separate from saved state so the user sees
  // their pending changes immediately without waiting for the network.
  const [pendingCaptainId, setPendingCaptainIdRaw] = useState<number | null>(null)
  const [pendingVcId, setPendingVcIdRaw] = useState<number | null>(null)

  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [saveError, setSaveError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoadState('loading')
    setLoadError(null)
    try {
      const data = await fetchCurrentLineup()
      if (!data) {
        // 404 = no squad yet, or no current gameweek
        setLoadState('no_squad')
        setLineup(null)
        return
      }
      setLineup(data)
      setLoadState('ready')
      // Seed pending selections from saved state
      setPendingCaptainIdRaw(data.captain_player_id)
      setPendingVcIdRaw(data.vice_captain_player_id)
    } catch (err) {
      setLoadError(
        err instanceof ApiError && err.status === 401
          ? 'Please log in to manage your lineup.'
          : 'Failed to load lineup. Please refresh.',
      )
      setLoadState('error')
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const setPendingCaptain = useCallback(
    (playerId: number) => {
      setPendingCaptainIdRaw(playerId)
      // If same as vc, clear vc so the user must re-pick
      if (playerId === pendingVcId) {
        setPendingVcIdRaw(null)
      }
      setSaveState('idle')
      setSaveError(null)
    },
    [pendingVcId],
  )

  const setPendingVC = useCallback(
    (playerId: number) => {
      setPendingVcIdRaw(playerId)
      // If same as captain, clear captain so the user must re-pick
      if (playerId === pendingCaptainId) {
        setPendingCaptainIdRaw(null)
      }
      setSaveState('idle')
      setSaveError(null)
    },
    [pendingCaptainId],
  )

  const hasUnsavedChanges =
    pendingCaptainId !== lineup?.captain_player_id ||
    pendingVcId !== lineup?.vice_captain_player_id

  const selectionIsValid =
    pendingCaptainId !== null &&
    pendingVcId !== null &&
    pendingCaptainId !== pendingVcId

  const saveSelection = useCallback(async () => {
    if (!selectionIsValid || !pendingCaptainId || !pendingVcId) return
    setSaveState('saving')
    setSaveError(null)
    try {
      const updated = await updateCaptain(pendingCaptainId, pendingVcId)
      setLineup(updated)
      setSaveState('saved')
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : 'Could not save. Please try again.'
      setSaveError(msg)
      setSaveState('error')
    }
  }, [selectionIsValid, pendingCaptainId, pendingVcId])

  return {
    loadState,
    lineup,
    loadError,
    pendingCaptainId,
    pendingVcId,
    setPendingCaptain,
    setPendingVC,
    hasUnsavedChanges,
    selectionIsValid,
    saveState,
    saveError,
    saveSelection,
    reload: load,
  }
}
