import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { ApiError, OpenAPI } from "./client"
import { ThemeProvider } from "./components/theme-provider"
import { Toaster } from "./components/ui/sonner"
import { getApiUrl } from "./lib/api"
import { supabase } from "./lib/supabase"
import "./index.css"
import { routeTree } from "./routeTree.gen"

// CRITICAL: Global fetch interceptor to catch and convert ANY HTTP requests to HTTPS
// This is the ultimate safety net to prevent Mixed Content errors
if (typeof window !== "undefined") {
  const originalFetch = window.fetch
  window.fetch = async function (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> {
    let url: string

    if (typeof input === "string") {
      url = input
    } else if (input instanceof URL) {
      url = input.toString()
    } else {
      url = input.url
    }

    // CRITICAL: Convert HTTP to HTTPS for production domains
    const isProductionDomain =
      url.includes(".onrender.com") ||
      url.includes(".vercel.app") ||
      url.includes(".netlify.app") ||
      url.includes(".herokuapp.com") ||
      url.includes(".fly.dev")

    const isLocalhost = url.includes("localhost") || url.includes("127.0.0.1")

    if (isProductionDomain && url.startsWith("http://")) {
      const httpsUrl = url.replace("http://", "https://")
      console.error(
        "[Global Fetch Interceptor] CRITICAL: Converting HTTP to HTTPS:",
        httpsUrl,
        "(original:",
        url + ")",
      )

      // Update the URL in the input
      if (typeof input === "string") {
        input = httpsUrl
      } else if (input instanceof URL) {
        input = new URL(httpsUrl)
      } else {
        input = new Request(httpsUrl, input)
      }
      url = httpsUrl
    } else if (
      typeof window !== "undefined" &&
      window.location.protocol === "https:" &&
      url.startsWith("http://") &&
      !isLocalhost
    ) {
      const httpsUrl = url.replace("http://", "https://")
      console.error(
        "[Global Fetch Interceptor] CRITICAL: Converting HTTP to HTTPS (browser check):",
        httpsUrl,
        "(original:",
        url + ")",
      )

      if (typeof input === "string") {
        input = httpsUrl
      } else if (input instanceof URL) {
        input = new URL(httpsUrl)
      } else {
        input = new Request(httpsUrl, input)
      }
      url = httpsUrl
    }

    return originalFetch.call(this, input, init)
  }
}

// Use getApiUrl() to ensure HTTPS in production (prevents Mixed Content errors)
// Set OpenAPI.BASE dynamically to ensure HTTPS conversion applies
const setOpenApiBase = () => {
  const apiUrl = getApiUrl()
  // getApiUrl() already handles HTTPS conversion, but ensure it's applied
  let finalUrl = apiUrl

  // CRITICAL: Additional safety check for production domains
  // This ensures OpenAPI.BASE is NEVER HTTP for production domains
  const isProductionDomain =
    finalUrl.includes(".onrender.com") ||
    finalUrl.includes(".vercel.app") ||
    finalUrl.includes(".netlify.app") ||
    finalUrl.includes(".herokuapp.com") ||
    finalUrl.includes(".fly.dev")

  const isLocalhost = finalUrl.includes("localhost") || finalUrl.includes("127.0.0.1")

  // Force HTTPS for production domains (CRITICAL FIX)
  if (isProductionDomain && finalUrl.startsWith("http://")) {
    finalUrl = finalUrl.replace("http://", "https://")
    console.warn("[main.tsx] CRITICAL: Converted OpenAPI.BASE HTTP to HTTPS:", finalUrl)
  }

  // Also check window.location.protocol as additional safety net
  if (typeof window !== "undefined" && window.location.protocol === "https:") {
    if (finalUrl.startsWith("http://") && !isLocalhost) {
      finalUrl = finalUrl.replace("http://", "https://")
      console.warn(
        "[main.tsx] Converted OpenAPI.BASE HTTP to HTTPS (browser check):",
        finalUrl,
      )
    }
  }

  // CRITICAL: Ensure no trailing slash (OpenAPI SDK may add one)
  finalUrl = finalUrl.replace(/\/$/, "")

  OpenAPI.BASE = finalUrl
  console.log("[main.tsx] OpenAPI.BASE set to:", OpenAPI.BASE)
}

// Set immediately
setOpenApiBase()

// Re-set OpenAPI.BASE after DOM is ready to ensure HTTPS conversion works
if (typeof window !== "undefined") {
  // Set immediately if window is available
  setOpenApiBase()

  // Also set on DOMContentLoaded as a fallback
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setOpenApiBase)
  }

  // Also set on window load as final fallback
  window.addEventListener("load", setOpenApiBase)
}
OpenAPI.TOKEN = async () => {
  try {
    const {
      data: { session },
      error,
    } = await supabase.auth.getSession()

    if (error) {
      console.error("[OpenAPI.TOKEN] Error getting session:", error)
      return ""
    }

    if (!session) {
      console.warn("[OpenAPI.TOKEN] No session found")
      return ""
    }

    const token = session.access_token || ""

    if (!token) {
      console.warn("[OpenAPI.TOKEN] No access token found in session", {
        hasSession: !!session,
        hasUser: !!session.user,
        expiresAt: session.expires_at,
      })
    } else {
      console.log("[OpenAPI.TOKEN] Token retrieved successfully", {
        tokenLength: token.length,
        tokenPrefix: `${token.substring(0, 20)}...`,
      })
    }

    return token
  } catch (error) {
    console.error("[OpenAPI.TOKEN] Exception getting session:", error)
    return ""
  }
}

const handleApiError = (error: Error) => {
  if (error instanceof ApiError && [401, 403].includes(error.status)) {
    supabase.auth.signOut()
    window.location.href = "/login"
  }
}
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleApiError,
  }),
  mutationCache: new MutationCache({
    onError: handleApiError,
  }),
})

const router = createRouter({ routeTree })
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <Toaster richColors closeButton />
      </QueryClientProvider>
    </ThemeProvider>
  </StrictMode>,
)
