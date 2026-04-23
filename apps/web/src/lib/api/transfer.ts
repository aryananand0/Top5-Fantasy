import { apiFetch, ApiError } from './client'
import type { SquadResponse } from './squad'

export type { ApiError }

// ---------------------------------------------------------------------------
// Shared types
// ---------------------------------------------------------------------------

export interface PlayerBrief {
  id: number
  name: string
  display_name: string | null
  position: string
  team_name: string
  team_short_name: string
  current_price: number
}

export interface TransferPairPreview {
  player_out: PlayerBrief
  player_in: PlayerBrief
  price_out: number
  price_in: number
  budget_delta: number
  is_free: boolean
  point_cost: number
}

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

export interface TransferSummaryResponse {
  gameweek_id: number
  gameweek_number: number
  gameweek_name: string
  gameweek_deadline: string
  gameweek_status: string
  is_editable: boolean
  free_transfers_available: number
  transfers_made_this_gw: number
  points_hit_this_gw: number
  budget_remaining: number
}

export async function fetchTransferSummary(): Promise<TransferSummaryResponse | null> {
  try {
    return await apiFetch<TransferSummaryResponse>('/api/v1/transfers/summary')
  } catch (err) {
    if (err instanceof ApiError && (err.status === 404 || err.status === 503)) return null
    throw err
  }
}

// ---------------------------------------------------------------------------
// Preview
// ---------------------------------------------------------------------------

export interface TransferPreviewResponse {
  gameweek_id: number
  gameweek_number: number
  is_editable: boolean
  transfers: TransferPairPreview[]
  budget_before: number
  budget_after: number
  total_points_hit: number
  free_transfers_before: number
  free_transfers_after: number
  is_valid: boolean
  errors: string[]
}

export interface TransferPairRequest {
  player_out_id: number
  player_in_id: number
}

export async function previewTransfers(
  pairs: TransferPairRequest[],
): Promise<TransferPreviewResponse> {
  return apiFetch<TransferPreviewResponse>('/api/v1/transfers/preview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transfers: pairs }),
  })
}

// ---------------------------------------------------------------------------
// Apply
// ---------------------------------------------------------------------------

export interface TransferApplyResponse {
  applied_transfers: TransferPairPreview[]
  squad: SquadResponse
  total_points_hit: number
  free_transfers_remaining: number
  transfers_this_gw: number
}

export async function applyTransfers(
  pairs: TransferPairRequest[],
): Promise<TransferApplyResponse> {
  return apiFetch<TransferApplyResponse>('/api/v1/transfers/apply', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transfers: pairs }),
  })
}

// ---------------------------------------------------------------------------
// History
// ---------------------------------------------------------------------------

export interface TransferHistoryItem {
  id: number
  gameweek_number: number
  player_out_id: number
  player_out_name: string
  player_in_id: number
  player_in_name: string
  price_out: number
  price_in: number
  is_free: boolean
  point_cost: number
  created_at: string
}

export interface TransferHistoryResponse {
  transfers: TransferHistoryItem[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export async function fetchTransferHistory(
  page = 1,
  perPage = 20,
): Promise<TransferHistoryResponse> {
  return apiFetch<TransferHistoryResponse>(
    `/api/v1/transfers/history?page=${page}&per_page=${perPage}`,
  )
}
