/**
 * Workflow Builder Component
 *
 * Main container component that combines canvas, palette, and config panel.
 */

import type { Connection, Edge, Node } from "@xyflow/react"
import { useCallback, useMemo, useRef, useState } from "react"
import { Activity } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ExecutionPanel } from "./ExecutionPanel"
import { NodeConfigPanel } from "./NodeConfigPanel"
import { NodePalette } from "./NodePalette"
import { WorkflowCanvas } from "./WorkflowCanvas"

interface WorkflowBuilderProps {
  workflowId: string | null
  nodes: Node[]
  edges: Edge[]
  onNodesChange: (nodes: Node[]) => void
  onEdgesChange: (edges: Edge[]) => void
  onConnect: (connection: Connection) => void
  onNodeAdd: (node: Node) => void
  onNodeSelect: (node: Node | null) => void
  selectedNode: Node | null
  onNodeUpdate: (nodeId: string, updates: Partial<Node>) => void
}

export function WorkflowBuilder({
  workflowId,
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onConnect,
  onNodeAdd,
  onNodeSelect,
  selectedNode,
  onNodeUpdate,
}: WorkflowBuilderProps) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [executionId, setExecutionId] = useState<string | null>(null)
  const [nodeStatuses, setNodeStatuses] = useState<Record<string, string>>({})
  const [showExecutionPanel, setShowExecutionPanel] = useState(false)

  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const type = event.dataTransfer.getData("application/reactflow")

      if (!type || !reactFlowWrapper.current) {
        return
      }

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect()
      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      }

      // Check if this is a connector node
      const connectorSlug = event.dataTransfer.getData("connector-slug")
      const isConnector = type.startsWith("connector-")
      
      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type: isConnector ? "connector" : type,
        position,
        data: {
          label: isConnector && connectorSlug
            ? connectorSlug.charAt(0).toUpperCase() + connectorSlug.slice(1).replace(/-/g, " ")
            : type.charAt(0).toUpperCase() + type.slice(1).replace(/_/g, " "),
          config: isConnector && connectorSlug
            ? { connector_slug: connectorSlug }
            : {},
        },
      }

      onNodeAdd(newNode)
    },
    [onNodeAdd],
  )

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = "move"
  }, [])

  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      onNodeSelect(node)
    },
    [onNodeSelect],
  )

  const handlePaneClick = useCallback(() => {
    onNodeSelect(null)
    // Close execution panel when clicking canvas if no execution is running
    if (!executionId) {
      setShowExecutionPanel(false)
    }
  }, [onNodeSelect, executionId])

  const handleExecutionStatusChange = useCallback((status: any) => {
    setExecutionId(status.execution_id)
    // Auto-open execution panel when execution starts
    if (status.execution_id) {
      setShowExecutionPanel(true)
    }
  }, [])

  const handleNodeStatusChange = useCallback(
    (nodeId: string, status: string) => {
      setNodeStatuses((prev) => {
        // Only update if status actually changed
        if (prev[nodeId] === status) return prev
        return { ...prev, [nodeId]: status }
      })
    },
    [],
  )

  // Update nodes with statuses using useMemo to prevent unnecessary recalculations
  const nodesWithStatus = useMemo(
    () =>
      nodes.map((node) => ({
        ...node,
        data: {
          ...node.data,
          status: nodeStatuses[node.id] || "idle",
        },
      })),
    [nodes, nodeStatuses],
  )

  // Determine which panel to show (node config takes priority)
  const showNodeConfig = selectedNode !== null
  const showExecutionDetails = showExecutionPanel && !showNodeConfig

  return (
    <div className="flex h-full relative">
      <NodePalette onNodeAdd={onNodeAdd} />
      <div
        ref={reactFlowWrapper}
        className={`flex-1 min-h-0 transition-all duration-300 ${
          showNodeConfig || showExecutionDetails ? "mr-80" : ""
        }`}
        style={{ height: '100%' }}
        role="application"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        {/* Canvas Header with Execution Details Button */}
        <div className="absolute top-2 right-2 z-10 flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setShowExecutionPanel(!showExecutionPanel)
              if (showExecutionPanel) {
                onNodeSelect(null) // Close node config if open
              }
            }}
            className="bg-background/80 backdrop-blur-sm"
          >
            <Activity className="h-4 w-4 mr-2" />
            {showExecutionPanel ? "Hide" : "Show"} Execution Details
          </Button>
        </div>
        <WorkflowCanvas
          initialNodes={nodesWithStatus}
          initialEdges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={handleNodeClick}
          onPaneClick={handlePaneClick}
        />
      </div>
      
      {/* Node Configuration Panel - Slides in from right */}
      {showNodeConfig && (
        <div className="absolute right-0 top-0 bottom-0 w-80 bg-background border-l shadow-lg z-20 animate-in slide-in-from-right duration-300">
          <NodeConfigPanel
            node={selectedNode}
            onClose={() => onNodeSelect(null)}
            onUpdate={onNodeUpdate}
          />
        </div>
      )}
      
      {/* Execution Panel - Slides in from right */}
      {showExecutionDetails && (
        <div className="absolute right-0 top-0 bottom-0 w-80 bg-background border-l shadow-lg z-20 animate-in slide-in-from-right duration-300">
          <ExecutionPanel
            workflowId={workflowId}
            executionId={executionId}
            nodes={nodes}
            edges={edges}
            onExecutionStatusChange={handleExecutionStatusChange}
            onNodeStatusChange={handleNodeStatusChange}
            onClose={() => setShowExecutionPanel(false)}
          />
        </div>
      )}
    </div>
  )
}
