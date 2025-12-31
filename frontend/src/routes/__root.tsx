import { ClerkProvider } from "@clerk/clerk-react"
import { ReactQueryDevtools } from "@tanstack/react-query-devtools"
import { createRootRoute, HeadContent, Outlet } from "@tanstack/react-router"
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools"
import ErrorComponent from "@/components/Common/ErrorComponent"
import NotFound from "@/components/Common/NotFound"

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || ""

export const Route = createRootRoute({
  component: () => {
    // Only show devtools in development mode
    const isDevelopment = import.meta.env.DEV

    return (
      <ClerkProvider publishableKey={clerkPubKey}>
        <HeadContent />
        <Outlet />
        {isDevelopment && (
          <>
            <TanStackRouterDevtools position="bottom-right" />
            <ReactQueryDevtools initialIsOpen={false} />
          </>
        )}
      </ClerkProvider>
    )
  },
  notFoundComponent: () => <NotFound />,
  errorComponent: () => <ErrorComponent />,
})
