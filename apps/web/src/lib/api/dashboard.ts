import { apiFetch } from './client'

export interface CaptainInfo {
  player_id: number
  name: string
  display_name: string | null
  position: string
  team_name: string
  gw_points: number | null
}

export interface FixtureInfo {
  fixture_id: number
  home_team: string
  home_team_short: string
  away_team: string
  away_team_short: string
  home_score: number | null
  away_score: number | null
  kickoff_at: string | null
  status: string
  has_squad_players: boolean
}

export interface DashboardSummary {
  gameweek_id: number | null
  gameweek_number: number | null
  gameweek_name: string | null
  gameweek_status: string | null
  deadline_at: string | null

  gw_points: number | null
  gw_raw_points: number | null
  gw_transfer_cost: number
  gw_captain_bonus: number
  gw_rank: number | null
  score_is_final: boolean

  season_points: number

  captain: CaptainInfo | null
  vice_captain: CaptainInfo | null

  has_squad: boolean
  has_lineup: boolean
  is_editable: boolean
  can_transfer: boolean

  free_transfers: number
  transfers_made: number
  transfer_hit: number
  budget_remaining: number

  fixtures: FixtureInfo[]
}

export async function fetchDashboard(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>('/api/v1/dashboard')
}
