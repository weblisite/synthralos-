/**
 * Clerk Authentication Utilities
 *
 * Helper functions for getting Clerk tokens outside of React components.
 * For use in API clients and other non-React contexts.
 */

let clerkClientInstance: any = null

/**
 * Set the Clerk client instance (called from ClerkProvider context)
 */
export function setClerkClient(client: any) {
  clerkClientInstance = client
}

/**
 * Get Clerk token (for use outside React components)
 * This is a fallback - prefer using useAuth hook in React components
 */
export async function getClerkToken(): Promise<string> {
  if (typeof window === "undefined") {
    return ""
  }

  try {
    // Try to get token from Clerk client if available
    if (clerkClientInstance?.session) {
      const token = await clerkClientInstance.session.getToken()
      return token || ""
    }

    // Fallback: Try to get from Clerk's internal storage
    // Clerk stores tokens in localStorage with key pattern: clerk-session-*
    const clerkKeys = Object.keys(localStorage).filter((key) =>
      key.startsWith("clerk-session-"),
    )

    if (clerkKeys.length > 0) {
      // Clerk stores session data, but we need to use their API to get token
      // For now, return empty and let the component handle it
      return ""
    }

    return ""
  } catch (error) {
    console.error("[getClerkToken] Error getting token:", error)
    return ""
  }
}
