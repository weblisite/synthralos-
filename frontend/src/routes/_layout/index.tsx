import { createFileRoute } from "@tanstack/react-router"
import { DashboardStats } from "@/components/Dashboard/DashboardStats"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Dashboard - SynthralOS",
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Welcome back, {currentUser?.full_name || currentUser?.email} 👋
        </h1>
        <p className="text-muted-foreground mt-2">
          Here's an overview of your automation platform
        </p>
      </div>
      <DashboardStats />
    </div>
  )
}
