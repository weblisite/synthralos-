/**
 * Workflows Page
 *
 * Main page for workflow management and builder.
 */

import { createFileRoute } from "@tanstack/react-router"
import type { Connection, Edge, Node } from "@xyflow/react"
import { Play, Save } from "lucide-react"
import { useCallback, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { WorkflowBuilder } from "@/components/Workflow/WorkflowBuilder"
import useCustomToast from "@/hooks/useCustomToast"
import { supabase } from "@/lib/supabase"

export const Route = createFileRoute("/_layout/workflows")({
  component: WorkflowsPage,
  head: () => ({
    meta: [
      {
        title: "Workflows - SynthralOS",
      },
    ],
  }),
})

function WorkflowsPage() {
  const [workflowName, setWorkflowName] = useState("")
  const [workflowDescription, setWorkflowDescription] = useState("")
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [workflowId, setWorkflowId] = useState<string | null>(null)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleNodesChange = useCallback((updatedNodes: Node[]) => {
    setNodes(updatedNodes)
  }, [])

  const handleEdgesChange = useCallback((updatedEdges: Edge[]) => {
    setEdges(updatedEdges)
  }, [])

  const handleConnect = useCallback((connection: Connection) => {
    // Connection handled by React Flow
    console.log("Connected:", connection)
  }, [])

  const handleNodeAdd = useCallback((newNode: Node) => {
    setNodes((prev) => [...prev, newNode])
  }, [])

  const handleNodeSelect = useCallback((node: Node | null) => {
    setSelectedNode(node)
  }, [])

  const handleNodeUpdate = useCallback(
    (nodeId: string, updates: Partial<Node>) => {
      setNodes((prev) =>
        prev.map((node) =>
          node.id === nodeId ? { ...node, ...updates } : node,
        ),
      )
    },
    [],
  )

  const handleSave = useCallback(async () => {
    if (!workflowName.trim()) {
      showErrorToast("Workflow name is required")
      return
    }

    try {
      // Convert React Flow nodes/edges to backend format
      const graphConfig = {
        nodes: nodes.map((node) => ({
          node_id: node.id,
          node_type: node.type || "unknown",
          position_x: node.position.x,
          position_y: node.position.y,
          config: node.data.config || {},
        })),
        edges: edges.map((edge) => ({
          from: edge.source,
          to: edge.target,
        })),
        entry_node_id: nodes.find((n) => n.type === "trigger")?.id || null,
      }

      const triggerConfig: Record<string, any> = {}
      const triggerNode = nodes.find((n) => n.type === "trigger")
      if (triggerNode?.data.config) {
        triggerConfig.type = triggerNode.data.config.trigger_type || "manual"
        if (triggerNode.data.config.cron_expression) {
          triggerConfig.cron = triggerNode.data.config.cron_expression
        }
      }

      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        showErrorToast("You must be logged in to save workflows")
        return
      }

      const response = await fetch("/api/v1/workflows", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          name: workflowName,
          description: workflowDescription || null,
          trigger_config: triggerConfig,
          graph_config: graphConfig,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to save workflow")
      }

      const workflow = await response.json()
      setWorkflowId(workflow.id)
      showSuccessToast(`Workflow "${workflowName}" saved successfully`)

      // Reset form
      setWorkflowName("")
      setWorkflowDescription("")
      setNodes([])
      setEdges([])
      setSelectedNode(null)
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to save workflow",
      )
    }
  }, [
    workflowName,
    workflowDescription,
    nodes,
    edges,
    showErrorToast,
    showSuccessToast,
  ])

  const handleRun = useCallback(async () => {
    // TODO: Implement workflow execution
    showSuccessToast("Workflow execution will be implemented soon")
  }, [
    // TODO: Implement workflow execution
    showSuccessToast,
  ])

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      <div className="p-4 border-b space-y-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Workflow Builder</h1>
            <p className="text-sm text-muted-foreground">
              Create and manage automation workflows
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleRun}>
              <Play className="h-4 w-4 mr-2" />
              Run
            </Button>
            <Button onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              Save Workflow
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="workflow-name">Workflow Name</Label>
            <Input
              id="workflow-name"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              placeholder="My Automation Workflow"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="workflow-description">Description (Optional)</Label>
            <Textarea
              id="workflow-description"
              value={workflowDescription}
              onChange={(e) => setWorkflowDescription(e.target.value)}
              placeholder="Describe what this workflow does..."
              rows={1}
            />
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden min-h-0">
        <WorkflowBuilder
          workflowId={workflowId}
          nodes={nodes}
          edges={edges}
          onNodesChange={handleNodesChange}
          onEdgesChange={handleEdgesChange}
          onConnect={handleConnect}
          onNodeAdd={handleNodeAdd}
          onNodeSelect={handleNodeSelect}
          selectedNode={selectedNode}
          onNodeUpdate={handleNodeUpdate}
        />
      </div>
    </div>
  )
}
