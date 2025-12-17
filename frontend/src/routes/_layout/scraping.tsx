import { createFileRoute } from "@tanstack/react-router"
import { ScrapingJobManager } from "@/components/Scraping/ScrapingJobManager"

export const Route = createFileRoute("/_layout/scraping")({
  component: ScrapingPage,
  head: () => ({
    meta: [
      {
        title: "Scraping - SynthralOS",
      },
    ],
  }),
})

function ScrapingPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Scraping Management</h1>
        <p className="text-muted-foreground mt-2">
          Manage web scraping jobs with proxy support and multiple engines
        </p>
      </div>
      <ScrapingJobManager />
    </div>
  )
}
