import { createFileRoute } from "@tanstack/react-router"
import { CodeToolRegistry } from "@/components/Code/CodeToolRegistry"

export const Route = createFileRoute("/_layout/code")({
  component: CodePage,
  head: () => ({
    meta: [
      {
        title: "Code - SynthralOS",
      },
    ],
  }),
})

function CodePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Code Management</h1>
        <p className="text-muted-foreground mt-2">
          Manage code tools, sandboxes, and execute code in secure environments
        </p>
      </div>
      <CodeToolRegistry />
    </div>
  )
}
