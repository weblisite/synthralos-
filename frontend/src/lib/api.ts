/**
 * API utility functions
 * 
 * Provides a centralized way to construct API URLs and make authenticated requests.
 */

import { supabase } from "./supabase"

/**
 * Get the base API URL from environment variable
 * Falls back to localhost for development
 */
export function getApiUrl(): string {
  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
  // Remove trailing slash if present
  return apiUrl.replace(/\/$/, "")
}

/**
 * Construct a full API URL from a relative path
 * @param path - Relative API path (e.g., "/api/v1/stats/dashboard")
 * @returns Full URL (e.g., "https://backend.onrender.com/api/v1/stats/dashboard")
 */
export function getApiPath(path: string): string {
  const baseUrl = getApiUrl()
  // Ensure path starts with /
  const normalizedPath = path.startsWith("/") ? path : `/${path}`
  return `${baseUrl}${normalizedPath}`
}

/**
 * Make an authenticated API request
 * Automatically includes the Supabase session token
 * @param path - Relative API path
 * @param options - Fetch options (headers will be merged with auth headers)
 */
export async function apiRequest<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to make API requests")
  }

  const url = getApiPath(path)
  const headers = new Headers(options.headers)
  headers.set("Authorization", `Bearer ${session.access_token}`)
  
  // Don't set Content-Type for FormData - browser will set it with boundary
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json")
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error")
    throw new Error(
      `API request failed: ${response.status} ${response.statusText} - ${errorText}`
    )
  }

  return response.json()
}

