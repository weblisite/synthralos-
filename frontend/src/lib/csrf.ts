/**
 * CSRF Token Management
 *
 * Handles fetching, storing, and refreshing CSRF tokens for API requests.
 */

import { getApiPath } from "./api"

// CSRF token storage (in memory, not localStorage for security)
let csrfToken: string | null = null
let tokenExpiry: number = 0
const TOKEN_REFRESH_BUFFER = 60000 // Refresh 1 minute before expiry (15 min expiry)

/**
 * Fetch a new CSRF token from the backend
 */
export async function fetchCsrfToken(): Promise<string> {
  try {
    const url = getApiPath("/api/v1/utils/csrf-token")
    const response = await fetch(url, {
      method: "GET",
      credentials: "include", // Include cookies if needed
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch CSRF token: ${response.statusText}`)
    }

    const data = await response.json()
    const token = data.csrf_token

    if (!token) {
      throw new Error("CSRF token not found in response")
    }

    // Store token with expiration (15 minutes = 900000 ms)
    csrfToken = token
    tokenExpiry = Date.now() + 900000 - TOKEN_REFRESH_BUFFER

    return token
  } catch (error) {
    console.error("Failed to fetch CSRF token:", error)
    throw error
  }
}

/**
 * Get current CSRF token, fetching a new one if needed
 */
export async function getCsrfToken(): Promise<string> {
  // Check if token exists and is not expired
  if (csrfToken && Date.now() < tokenExpiry) {
    return csrfToken
  }

  // Fetch new token
  return await fetchCsrfToken()
}

/**
 * Clear CSRF token (e.g., on logout)
 */
export function clearCsrfToken(): void {
  csrfToken = null
  tokenExpiry = 0
}

/**
 * Check if CSRF token is valid (not expired)
 */
export function isCsrfTokenValid(): boolean {
  return csrfToken !== null && Date.now() < tokenExpiry
}
