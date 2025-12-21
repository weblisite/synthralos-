import { createFileRoute } from "@tanstack/react-router"
import { FileBrowser } from "@/components/Storage/FileBrowser"

export const Route = createFileRoute("/_layout/storage")({
  component: StoragePage,
  head: () => ({
    meta: [
      {
        title: "Storage - SynthralOS",
      },
    ],
  }),
})

function StoragePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">File Storage</h1>
        <p className="text-muted-foreground mt-2">
          Browse, upload, download, and manage files in Supabase Storage
        </p>
      </div>
      <FileBrowser />
    </div>
  )
}
