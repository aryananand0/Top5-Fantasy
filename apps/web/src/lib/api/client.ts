const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('top5_token')
}

export function apiHeaders(extra: HeadersInit = {}): HeadersInit {
  const token = getToken()
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  }
}

export function apiUrl(path: string): string {
  return `${API_BASE}${path}`
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly detail?: unknown,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(apiUrl(path), {
    ...init,
    headers: apiHeaders(init?.headers),
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const msg =
      typeof body?.detail === 'string'
        ? body.detail
        : body?.detail?.message ?? `Request failed (${res.status})`
    throw new ApiError(res.status, msg, body?.detail)
  }

  return res.json() as Promise<T>
}
