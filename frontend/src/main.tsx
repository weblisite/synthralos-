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
import { supabase } from "./lib/supabase"
import "./index.css"
import { routeTree } from "./routeTree.gen"

OpenAPI.BASE = import.meta.env.VITE_API_URL
OpenAPI.TOKEN = async () => {
  try {
    const {
      data: { session },
      error,
    } = await supabase.auth.getSession()
    
    if (error) {
      console.error('[OpenAPI.TOKEN] Error getting session:', error)
      return ""
    }
    
    if (!session) {
      console.warn('[OpenAPI.TOKEN] No session found')
      return ""
    }
    
    const token = session.access_token || ""
    
    if (!token) {
      console.warn('[OpenAPI.TOKEN] No access token found in session', {
        hasSession: !!session,
        hasUser: !!session.user,
        expiresAt: session.expires_at
      })
    } else {
      console.log('[OpenAPI.TOKEN] Token retrieved successfully', {
        tokenLength: token.length,
        tokenPrefix: token.substring(0, 20) + '...'
      })
    }
    
    return token
  } catch (error) {
    console.error('[OpenAPI.TOKEN] Exception getting session:', error)
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
