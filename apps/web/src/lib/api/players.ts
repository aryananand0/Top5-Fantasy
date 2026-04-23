import { apiFetch } from './client'
import type { Position } from './squad'

export interface PlayerResponse {
  id: number
  name: string
  display_name: string | null
  position: Position
  team_id: number
  team_name: string
  team_short_name: string
  current_price: number
  form_score: number
  starter_confidence: number
  is_available: boolean
  availability_note: string | null
}

export interface PlayerListResponse {
  players: PlayerResponse[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface FetchPlayersOptions {
  position?: Position | null
  team_id?: number | null
  search?: string
  available_only?: boolean
  page?: number
  per_page?: number
}

export async function fetchPlayers(
  opts: FetchPlayersOptions = {},
): Promise<PlayerListResponse> {
  const params = new URLSearchParams()
  if (opts.position) params.set('position', opts.position)
  if (opts.team_id != null) params.set('team_id', String(opts.team_id))
  if (opts.search) params.set('search', opts.search)
  if (opts.available_only !== undefined)
    params.set('available_only', String(opts.available_only))
  params.set('page', String(opts.page ?? 1))
  params.set('per_page', String(opts.per_page ?? 40))

  return apiFetch<PlayerListResponse>(`/api/v1/players?${params}`)
}
