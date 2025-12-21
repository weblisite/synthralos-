import { createFileRoute } from "@tanstack/react-router"
import { SocialMonitoringManager } from "@/components/SocialMonitoring/SocialMonitoringManager"

export const Route = createFileRoute("/_layout/social-monitoring")({
  component: SocialMonitoringPage,
  head: () => ({
    meta: [
      {
        title: "Social Monitoring - SynthralOS",
      },
    ],
  }),
})

function SocialMonitoringPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Social Monitoring</h1>
        <p className="text-muted-foreground mt-2">
          Manage social media streams, signals, and alerts for real-time
          monitoring
        </p>
      </div>
      <SocialMonitoringManager />
    </div>
  )
}
