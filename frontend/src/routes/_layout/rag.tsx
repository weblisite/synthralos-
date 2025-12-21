import { createFileRoute } from "@tanstack/react-router"
import { RAGIndexManager } from "@/components/RAG/RAGIndexManager"
import { RoutingLogs } from "@/components/RAG/RoutingLogs"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export const Route = createFileRoute("/_layout/rag")({
  component: RAGPage,
  head: () => ({
    meta: [
      {
        title: "RAG - SynthralOS",
      },
    ],
  }),
})

function RAGPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">RAG Management</h1>
        <p className="text-muted-foreground mt-2">
          Manage your RAG indexes, documents, and queries
        </p>
      </div>
      <Tabs defaultValue="indexes" className="space-y-4">
        <TabsList>
          <TabsTrigger value="indexes">Indexes</TabsTrigger>
          <TabsTrigger value="routing">Routing Logs</TabsTrigger>
        </TabsList>
        <TabsContent value="indexes">
          <RAGIndexManager />
        </TabsContent>
        <TabsContent value="routing">
          <RoutingLogs />
        </TabsContent>
      </Tabs>
    </div>
  )
}
