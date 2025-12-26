import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/settings/" as any)({
  component: SettingsRedirect,
  beforeLoad: () => {
    throw redirect({ to: "/settings/profile" as any })
  },
})

function SettingsRedirect() {
  return null
}
