import { apiFetch, ApiError } from './client'

export type GameweekStatus = 'UPCOMING' | 'LOCKED' | 'ACTIVE' | 'SCORING' | 'FINISHED'
export type Position = 'GK' | 'DEF' | 'MID' | 'FWD'

export interface LineupPlayer {
  player_id: number
  name: string
  display_name: string | null
  position: Position
  team_name: string
  team_short_name: string
  current_price: number
  form_score: number
  is_available: boolean
  is_captain: boolean
  is_vice_captain: boolean
  points_scored: number | null
}

export interface LineupResponse {
  id: number
  gameweek_id: number
  gameweek_number: number
  gameweek_name: string
  gameweek_deadline: string
  gameweek_status: GameweekStatus
  is_locked: boolean
  is_editable: boolean
  captain_player_id: number | null
  vice_captain_player_id: number | null
  players: LineupPlayer[]
  points_scored: number | null
  created_at: string
  updated_at: string
}

export { ApiError }

export async function fetchCurrentLineup(): Promise<LineupResponse | null> {
  try {
    return await apiFetch<LineupResponse>('/api/v1/lineups/current')
  } catch (err) {
    if (err instanceof ApiError && (err.status === 404 || err.status === 503)) return null
    throw err
  }
}

export async function updateCaptain(
  captainPlayerId: number,
  vcPlayerId: number,
): Promise<LineupResponse> {
  return apiFetch<LineupResponse>('/api/v1/lineups/current', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      captain_player_id: captainPlayerId,
      vice_captain_player_id: vcPlayerId,
    }),
  })
}
