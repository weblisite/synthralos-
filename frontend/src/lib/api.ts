/**
 * API utility functions
 *
 * Provides a centralized way to construct API URLs and make authenticated requests.
 */

import { getCsrfToken } from "./csrf"
import { supabase } from "./supabase"

/**
 * Get the base API URL from environment variable
 * Falls back to localhost for development
 * 
 * Automatically converts HTTP to HTTPS in production (browser context)
 * to prevent Mixed Content errors when frontend is served over HTTPS
 */
export function getApiUrl(): string {
  let apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
  
  // In browser context (production), ensure HTTPS is used if frontend is HTTPS
  // This prevents Mixed Content errors
  if (typeof window !== "undefined") {
    const isHttps = window.location.protocol === "https:"
    const isHttp = apiUrl.startsWith("http://")
    const isNotLocalhost = !apiUrl.includes("localhost")
    
    // Convert HTTP to HTTPS for production deployments
    if (isHttps && isHttp && isNotLocalhost) {
      apiUrl = apiUrl.replace("http://", "https://")
      console.warn(
        "[API] Converted HTTP API URL to HTTPS to prevent Mixed Content errors:",
        apiUrl,
        "(original:", import.meta.env.VITE_API_URL + ")"
      )
    }
  }
  
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
  options: RequestInit = {},
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

  // Add CSRF token for state-changing requests (POST, PUT, DELETE, PATCH)
  const method = options.method?.toUpperCase() || "GET"
  if (["POST", "PUT", "DELETE", "PATCH"].includes(method)) {
    try {
      const csrfToken = await getCsrfToken()
      headers.set("X-CSRF-Token", csrfToken)
    } catch (error) {
      // Log error but don't fail the request (CSRF may not be enabled in local dev)
      console.warn("Failed to get CSRF token:", error)
    }
  }

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
      `API request failed: ${response.status} ${response.statusText} - ${errorText}`,
    )
  }

  return response.json()
}
