import { createFileRoute, redirect } from "@tanstack/react-router"

// Redirect old settings route to new profile settings
export const Route = createFileRoute("/_layout/settings")({
  beforeLoad: () => {
    throw redirect({ to: "/settings/profile" as any })
  },
})
