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

  // Always convert HTTP to HTTPS for production domains (Render, etc.)
  // This prevents Mixed Content errors when frontend is served over HTTPS
  const isProductionDomain =
    apiUrl.includes(".onrender.com") ||
    apiUrl.includes(".vercel.app") ||
    apiUrl.includes(".netlify.app") ||
    apiUrl.includes(".herokuapp.com") ||
    apiUrl.includes(".fly.dev")

  const isLocalhost =
    apiUrl.includes("localhost") || apiUrl.includes("127.0.0.1")

  // CRITICAL: Convert HTTP to HTTPS for production domains IMMEDIATELY
  // This must happen before any API calls to prevent Mixed Content errors
  if (isProductionDomain && apiUrl.startsWith("http://")) {
    apiUrl = apiUrl.replace("http://", "https://")
    console.warn(
      "[API] Converted HTTP API URL to HTTPS for production domain:",
      apiUrl,
      "(original:",
      `${import.meta.env.VITE_API_URL})`,
    )
  }
  
  // Also ensure HTTPS if we're in a browser HTTPS context (double safety)
  if (typeof window !== "undefined" && window.location.protocol === "https:") {
    if (apiUrl.startsWith("http://") && !isLocalhost) {
      apiUrl = apiUrl.replace("http://", "https://")
      console.warn(
        "[API] Converted HTTP API URL to HTTPS (browser HTTPS context):",
        apiUrl,
        "(original:",
        `${import.meta.env.VITE_API_URL})`,
      )
    }
  }

  // In browser context, also check window.location.protocol as a safety net
  if (typeof window !== "undefined") {
    try {
      const isHttps = window.location.protocol === "https:"
      const isHttp = apiUrl.startsWith("http://")

      // Convert HTTP to HTTPS if frontend is HTTPS and not localhost
      if (isHttps && isHttp && !isLocalhost) {
        apiUrl = apiUrl.replace("http://", "https://")
        console.warn(
          "[API] Converted HTTP API URL to HTTPS (browser check):",
          apiUrl,
          "(original:",
          `${import.meta.env.VITE_API_URL})`,
        )
      }
    } catch (e) {
      // If window.location is not available yet, log but don't fail
      console.warn("[API] Could not check window.location.protocol:", e)
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

  let url = getApiPath(path)

  // Double-check HTTPS conversion at request time (safety net)
  // Check for production domains first
  const isProductionDomain =
    url.includes(".onrender.com") ||
    url.includes(".vercel.app") ||
    url.includes(".netlify.app") ||
    url.includes(".herokuapp.com") ||
    url.includes(".fly.dev")

  const isLocalhost = url.includes("localhost") || url.includes("127.0.0.1")

  // CRITICAL: Always convert HTTP to HTTPS for production domains
  // This is the absolute last line of defense against Mixed Content errors
  if (isProductionDomain && url.startsWith("http://")) {
    url = url.replace("http://", "https://")
    console.error(
      "[apiRequest] CRITICAL: Converted HTTP URL to HTTPS (production domain check):",
      url,
      "(original path:",
      `${path})`,
    )
  }

  // Also check window.location.protocol as additional safety net
  if (typeof window !== "undefined" && window.location.protocol === "https:") {
    if (url.startsWith("http://") && !isLocalhost) {
      url = url.replace("http://", "https://")
      console.error(
        "[apiRequest] CRITICAL: Converted HTTP URL to HTTPS (browser check):",
        url,
        "(original path:",
        `${path})`,
      )
    }
  }

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
