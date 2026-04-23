import { apiFetch, ApiError } from './client'

export type Position = 'GK' | 'DEF' | 'MID' | 'FWD'

export interface SquadPlayerResponse {
  player_id: number
  name: string
  display_name: string | null
  position: Position
  team_id: number
  team_name: string
  team_short_name: string
  purchase_price: number
  current_price: number
  form_score: number
  starter_confidence: number
  is_available: boolean
}

export interface SquadResponse {
  id: number
  name: string
  budget_remaining: number
  total_cost: number
  total_points: number
  free_transfers_banked: number
  players: SquadPlayerResponse[]
  created_at: string
  updated_at: string
}

export interface ValidationError {
  code: string
  message: string
}

export interface SquadErrorDetail {
  message: string
  errors: ValidationError[]
}

export { ApiError }

export async function fetchSquad(): Promise<SquadResponse | null> {
  try {
    return await apiFetch<SquadResponse>('/api/v1/squad')
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) return null
    throw err
  }
}

export async function createSquad(
  playerIds: number[],
  name?: string,
): Promise<{ squad: SquadResponse; errors: ValidationError[] }> {
  try {
    const squad = await apiFetch<SquadResponse>('/api/v1/squad', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_ids: playerIds, name }),
    })
    return { squad, errors: [] }
  } catch (err) {
    if (err instanceof ApiError && err.status === 400) {
      const detail = err.detail as SquadErrorDetail | undefined
      return { squad: null as never, errors: detail?.errors ?? [] }
    }
    throw err
  }
}

export async function replaceSquad(
  playerIds: number[],
): Promise<{ squad: SquadResponse; errors: ValidationError[] }> {
  try {
    const squad = await apiFetch<SquadResponse>('/api/v1/squad', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_ids: playerIds }),
    })
    return { squad, errors: [] }
  } catch (err) {
    if (err instanceof ApiError && err.status === 400) {
      const detail = err.detail as SquadErrorDetail | undefined
      return { squad: null as never, errors: detail?.errors ?? [] }
    }
    throw err
  }
}
