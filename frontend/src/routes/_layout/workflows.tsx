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
  const [executionId, setExecutionId] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
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
    // Prevent multiple simultaneous saves
    if (isSaving) {
      return
    }
    
    if (!workflowName.trim()) {
      showErrorToast("Workflow name is required")
      return
    }

    setIsSaving(true)

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

      interface TriggerConfig {
        trigger_type?: string
        cron_expression?: string
        [key: string]: any
      }

      const triggerConfig: Record<string, any> = {}
      const triggerNode = nodes.find((n) => n.type === "trigger")
      if (triggerNode?.data.config) {
        const config = triggerNode.data.config as TriggerConfig
        triggerConfig.type = config.trigger_type || "manual"
        if (config.cron_expression) {
          triggerConfig.cron = config.cron_expression
        }
      }

      const workflow = await apiRequest<{ id: string }>("/api/v1/workflows", {
        method: "POST",
        body: JSON.stringify({
          name: workflowName,
          description: workflowDescription || null,
          trigger_config: triggerConfig,
          graph_config: graphConfig,
        }),
      })
      
      setWorkflowId(workflow.id)
      
      // Show prominent success notification
      showSuccessToast(
        `Workflow "${workflowName}" has been saved successfully!`,
        "✅ Workflow Saved"
      )

      // Reset form after a short delay to allow toast to show
      setTimeout(() => {
        setWorkflowName("")
        setWorkflowDescription("")
        setNodes([])
        setEdges([])
        setSelectedNode(null)
        setExecutionId(null) // Reset execution when saving new workflow
      }, 100)
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to save workflow",
      )
    } finally {
      setIsSaving(false)
    }
  }, [
    workflowName,
    workflowDescription,
    nodes,
    edges,
    isSaving,
    showErrorToast,
    showSuccessToast,
  ])

  const handleRun = useCallback(async () => {
    // Check if workflow has been saved
    if (!workflowId) {
      showErrorToast("Please save the workflow before running it")
      return
    }

    // Validate workflow has nodes
    if (nodes.length === 0) {
      showErrorToast("Workflow must have at least one node to run")
      return
    }

    // Check for trigger node
    const triggerNode = nodes.find((n) => n.type === "trigger")
    if (!triggerNode) {
      showErrorToast("Workflow must have a trigger node to run")
      return
    }

    try {
      // Call backend API to run workflow
      // FastAPI expects trigger_data directly in the body (not wrapped)
      const triggerData = triggerNode.data.config || {}
      const execution = await apiRequest<{ execution_id: string }>(
        `/api/v1/workflows/${workflowId}/run`,
        {
          method: "POST",
          body: JSON.stringify(triggerData),
        }
      )
      showSuccessToast(`Workflow execution started: ${execution.execution_id}`)

      // Update executionId to show in ExecutionPanel
      setExecutionId(execution.execution_id)
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to run workflow",
      )
    }
  }, [
    workflowId,
    nodes,
    showErrorToast,
    showSuccessToast,
  ])

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      <div className="p-4 space-y-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Workflow Builder</h1>
            <p className="text-sm text-muted-foreground">
              Create and manage automation workflows
            </p>
          </div>
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={handleRun}>
              <Play className="h-4 w-4 mr-2" />
              Run
            </Button>
            <Button type="button" onClick={handleSave} disabled={isSaving}>
              <Save className="h-4 w-4 mr-2" />
              {isSaving ? "Saving..." : "Save Workflow"}
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
            <Input
              id="workflow-description"
              value={workflowDescription}
              onChange={(e) => setWorkflowDescription(e.target.value)}
              placeholder="Describe what this workflow does..."
            />
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden min-h-0">
        <WorkflowBuilder
          workflowId={workflowId}
          executionId={executionId}
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
