import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/settings/")({
  component: SettingsRedirect,
  beforeLoad: () => {
    throw redirect({ to: "/settings/profile" })
  },
})

function SettingsRedirect() {
  return null
}
