'use client'

import { useState, useEffect, useCallback } from 'react'
import { fetchDashboard, type DashboardSummary } from '@/lib/api/dashboard'
import { ApiError } from '@/lib/api/client'

export type DashboardLoadState = 'loading' | 'ready' | 'error'

export interface UseDashboardReturn {
  loadState: DashboardLoadState
  data: DashboardSummary | null
  error: string | null
  reload: () => Promise<void>
}

export function useDashboard(): UseDashboardReturn {
  const [loadState, setLoadState] = useState<DashboardLoadState>('loading')
  const [data, setData] = useState<DashboardSummary | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoadState('loading')
    setError(null)
    try {
      const summary = await fetchDashboard()
      setData(summary)
      setLoadState('ready')
    } catch (err) {
      const msg =
        err instanceof ApiError && err.status === 401
          ? 'Please log in to view your dashboard.'
          : 'Could not load dashboard. Please refresh.'
      setError(msg)
      setLoadState('error')
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return { loadState, data, error, reload: load }
}
