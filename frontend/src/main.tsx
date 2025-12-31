import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query"
import { createRouter, RouterProvider } from "@tanstack/react-router"
import axios from "axios"
import { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import { ApiError, OpenAPI } from "./client"
import { ThemeProvider } from "./components/theme-provider"
import { Toaster } from "./components/ui/sonner"
import { getApiUrl } from "./lib/api"
import "./index.css"
import { routeTree } from "./routeTree.gen"

// CRITICAL: Axios interceptor to catch and convert ANY HTTP requests to HTTPS
// The OpenAPI SDK uses axios, not fetch, so we need this interceptor too
if (typeof window !== "undefined") {
  axios.interceptors.request.use(
    (config) => {
      // Log all axios requests for debugging
      const originalUrl = config.url || ""
      const originalBaseURL = config.baseURL || ""
      const fullUrl = originalBaseURL
        ? `${originalBaseURL}${originalUrl.startsWith("/") ? "" : "/"}${originalUrl}`
        : originalUrl

      // Check if this is a production domain request
      const isProductionDomain =
        fullUrl.includes(".onrender.com") ||
        fullUrl.includes(".vercel.app") ||
        fullUrl.includes(".netlify.app") ||
        fullUrl.includes(".herokuapp.com") ||
        fullUrl.includes(".fly.dev") ||
        originalBaseURL.includes(".onrender.com") ||
        originalBaseURL.includes(".vercel.app") ||
        originalBaseURL.includes(".netlify.app") ||
        originalBaseURL.includes(".herokuapp.com") ||
        originalBaseURL.includes(".fly.dev")

      const isLocalhost =
        fullUrl.includes("localhost") ||
        fullUrl.includes("127.0.0.1") ||
        originalBaseURL.includes("localhost") ||
        originalBaseURL.includes("127.0.0.1")

      // CRITICAL: Convert HTTP to HTTPS for production domains
      // Check and fix baseURL
      if (config.baseURL?.startsWith("http://")) {
        if (
          isProductionDomain ||
          (window.location.protocol === "https:" && !isLocalhost)
        ) {
          config.baseURL = config.baseURL.replace("http://", "https://")
          console.error(
            "[Axios Interceptor] CRITICAL: Converting baseURL HTTP to HTTPS:",
            config.baseURL,
            "(original:",
            `${originalBaseURL})`,
            "| Full URL:",
            `${config.baseURL}${originalUrl}`,
            "| Stack:",
            new Error().stack?.split("\n").slice(0, 5).join("\n"),
          )
        }
      }

      // Check and fix url if it's a full URL
      if (config.url?.startsWith("http://")) {
        if (
          isProductionDomain ||
          (window.location.protocol === "https:" && !isLocalhost)
        ) {
          config.url = config.url.replace("http://", "https://")
          console.error(
            "[Axios Interceptor] CRITICAL: Converting url HTTP to HTTPS:",
            config.url,
            "(original:",
            `${originalUrl})`,
            "| Stack:",
            new Error().stack?.split("\n").slice(0, 5).join("\n"),
          )
        }
      }

      // Also fix axios.defaults.baseURL if it's HTTP
      if (axios.defaults.baseURL?.startsWith("http://")) {
        if (
          isProductionDomain ||
          (window.location.protocol === "https:" && !isLocalhost)
        ) {
          axios.defaults.baseURL = axios.defaults.baseURL.replace(
            "http://",
            "https://",
          )
          console.error(
            "[Axios Interceptor] CRITICAL: Converting axios.defaults.baseURL HTTP to HTTPS:",
            axios.defaults.baseURL,
          )
        }
      }

      // Log all axios requests to production domains for debugging
      if (isProductionDomain && !isLocalhost) {
        const finalUrl = config.baseURL
          ? `${config.baseURL}${config.url?.startsWith("/") ? "" : "/"}${config.url || ""}`
          : config.url || ""
        console.log(
          "[Axios Interceptor] Request to production domain:",
          finalUrl,
          "| baseURL:",
          config.baseURL || "none",
          "| url:",
          config.url || "none",
        )
      }

      return config
    },
    (error) => {
      return Promise.reject(error)
    },
  )
  console.log("[Axios Interceptor] Installed successfully")
}

// CRITICAL: Global fetch interceptor to catch and convert ANY HTTP requests to HTTPS
// This is the ultimate safety net to prevent Mixed Content errors
if (typeof window !== "undefined") {
  const originalFetch = window.fetch
  window.fetch = async function (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> {
    let url: string
    let modifiedInput: RequestInfo | URL = input

    // Extract URL from input
    if (typeof input === "string") {
      url = input
    } else if (input instanceof URL) {
      url = input.toString()
    } else if (input instanceof Request) {
      url = input.url
    } else {
      url = String(input)
    }

    // CRITICAL: Convert HTTP to HTTPS for production domains
    const isProductionDomain =
      url.includes(".onrender.com") ||
      url.includes(".vercel.app") ||
      url.includes(".netlify.app") ||
      url.includes(".herokuapp.com") ||
      url.includes(".fly.dev")

    const isLocalhost = url.includes("localhost") || url.includes("127.0.0.1")

    // Check if we need to convert HTTP to HTTPS
    if (
      (isProductionDomain ||
        (window.location.protocol === "https:" && !isLocalhost)) &&
      url.startsWith("http://")
    ) {
      const httpsUrl = url.replace("http://", "https://")
      console.error(
        "[Global Fetch Interceptor] CRITICAL: Converting HTTP to HTTPS:",
        httpsUrl,
        "(original:",
        `${url})`,
        "| Stack:",
        new Error().stack?.split("\n").slice(0, 5).join("\n"),
      )

      // Create new input with HTTPS URL
      if (typeof input === "string") {
        modifiedInput = httpsUrl
      } else if (input instanceof URL) {
        modifiedInput = new URL(httpsUrl)
      } else if (input instanceof Request) {
        // Create new Request with HTTPS URL, preserving all other properties
        // IMPORTANT: Clone the body if it's been read, otherwise use the original
        let bodyToUse: BodyInit | null = null
        try {
          // Try to clone the body if it's a ReadableStream
          if (input.body && input.bodyUsed === false) {
            bodyToUse = input.body
          }
        } catch (_e) {
          // If cloning fails, try to get body from init
          bodyToUse = init?.body || null
        }

        modifiedInput = new Request(httpsUrl, {
          method: input.method,
          headers: input.headers,
          body: bodyToUse || init?.body || null,
          mode: input.mode,
          credentials: input.credentials,
          cache: input.cache,
          redirect: input.redirect,
          referrer: input.referrer,
          integrity: input.integrity,
          keepalive: input.keepalive,
          signal: input.signal,
        })
      }
    }

    return originalFetch.call(this, modifiedInput, init)
  }
  console.log("[Global Fetch Interceptor] Installed successfully")
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

  const isLocalhost =
    finalUrl.includes("localhost") || finalUrl.includes("127.0.0.1")

  // Force HTTPS for production domains (CRITICAL FIX)
  if (isProductionDomain && finalUrl.startsWith("http://")) {
    finalUrl = finalUrl.replace("http://", "https://")
    console.warn(
      "[main.tsx] CRITICAL: Converted OpenAPI.BASE HTTP to HTTPS:",
      finalUrl,
    )
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

  // CRITICAL: Remove /api/v1 from BASE if present, since generated client paths already include it
  // This prevents URL duplication like /api/v1/api/v1/users/me
  finalUrl = finalUrl.replace(/\/api\/v1\/?$/, "")

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
// OpenAPI.TOKEN will be set dynamically from useAuth hook
// This is a placeholder that will be replaced
OpenAPI.TOKEN = async () => {
  // This will be set by the auth hook
  return ""
}

const handleApiError = (error: Error) => {
  if (error instanceof ApiError && [401, 403].includes(error.status)) {
    // Redirect to login - Clerk will handle sign out
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
