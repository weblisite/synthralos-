import { useAuth as useClerkAuth } from "@clerk/clerk-react"
import { createFileRoute, Outlet } from "@tanstack/react-router"
import { useEffect } from "react"
import { AgUIProvider } from "@/components/Chat/AgUIProvider"
import { Footer } from "@/components/Common/Footer"
import AppSidebar from "@/components/Sidebar/AppSidebar"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { useUserRealtime } from "@/hooks/useUserRealtime"
import { fetchCsrfToken } from "@/lib/csrf"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    // Clerk authentication check happens in the component
    // We can't use hooks in beforeLoad, so we'll check in the component
    // For now, allow the route to load and check in component
  },
})

function Layout() {
  const { isLoaded, isSignedIn } = useClerkAuth()

  // Subscribe to real-time user updates
  useUserRealtime()

  // Redirect to login if not authenticated
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      const currentPath = window.location.pathname
      // Only redirect if not already on login/signup pages
      if (currentPath !== "/login" && currentPath !== "/signup") {
        const redirectUrl = `/login?redirect=${encodeURIComponent(currentPath)}`
        window.location.href = redirectUrl
      }
    }
  }, [isLoaded, isSignedIn])

  // Initialize CSRF token on mount
  useEffect(() => {
    if (isSignedIn) {
      // Fetch CSRF token when layout loads (user is authenticated)
      fetchCsrfToken().catch((error) => {
        // Log but don't fail - CSRF may not be enabled in local dev
        console.warn("Failed to initialize CSRF token:", error)
      })
    }
  }, [isSignedIn])

  // Show loading state while Clerk is initializing
  if (!isLoaded) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="text-muted-foreground">Loading...</div>
        </div>
      </div>
    )
  }

  // Show loading/redirecting state if not signed in (redirect is in progress)
  if (!isSignedIn) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="text-muted-foreground">Redirecting to login...</div>
        </div>
      </div>
    )
  }

  return (
    <AgUIProvider>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-2 border-b px-4">
            <SidebarTrigger className="-ml-1 text-muted-foreground" />
          </header>
          <main className="flex-1 p-6 md:p-8">
            <div className="mx-auto max-w-7xl">
              <Outlet />
            </div>
          </main>
          <Footer />
        </SidebarInset>
      </SidebarProvider>
    </AgUIProvider>
  )
}

export default Layout
