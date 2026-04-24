import { apiFetch } from './client'

export interface FixtureResponse {
  id: number
  competition_code: string
  competition_name: string
  home_team: string
  home_team_short: string
  away_team: string
  away_team_short: string
  kickoff_at: string | null
  status: 'SCHEDULED' | 'LIVE' | 'FINISHED' | 'POSTPONED' | 'CANCELLED'
  home_score: number | null
  away_score: number | null
}

export interface FixtureListResponse {
  fixtures: FixtureResponse[]
  total: number
}

export interface FetchFixturesOptions {
  competition_code?: string
  days_back?: number
  days_forward?: number
  status?: string
}

export async function fetchFixtures(opts: FetchFixturesOptions = {}): Promise<FixtureListResponse> {
  const params = new URLSearchParams()
  if (opts.competition_code) params.set('competition_code', opts.competition_code)
  if (opts.days_back !== undefined) params.set('days_back', String(opts.days_back))
  if (opts.days_forward !== undefined) params.set('days_forward', String(opts.days_forward))
  if (opts.status) params.set('status', opts.status)
  return apiFetch<FixtureListResponse>(`/api/v1/fixtures?${params}`)
}
