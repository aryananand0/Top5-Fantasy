import { apiFetch, ApiError } from './client'
export { ApiError }

export interface UserInfo {
  id: number
  email: string
  username: string
  display_name: string | null
  is_active: boolean
}

export interface SignupData {
  email: string
  username: string
  password: string
  display_name?: string
}

export interface LoginData {
  login: string
  password: string
}

const USER_KEY = 'top5_user'

export function saveSession(token: string, user: UserInfo) {
  localStorage.setItem('top5_token', token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearSession() {
  localStorage.removeItem('top5_token')
  localStorage.removeItem(USER_KEY)
}

export function getStoredUser(): UserInfo | null {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserInfo
  } catch {
    return null
  }
}

export async function apiSignup(data: SignupData): Promise<UserInfo> {
  return apiFetch<UserInfo>('/api/v1/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export async function apiLogin(data: LoginData): Promise<{ access_token: string }> {
  return apiFetch<{ access_token: string }>('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export async function apiMe(token: string): Promise<UserInfo> {
  return apiFetch<UserInfo>('/api/v1/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  })
}
