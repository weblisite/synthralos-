/**
 * Workflow Builder Component
 *
 * Main container component that combines canvas, palette, and config panel.
 */

import type { Connection, Edge, Node } from "@xyflow/react"
import { useCallback, useMemo, useRef, useState, useEffect } from "react"
import { Activity } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ExecutionPanel } from "./ExecutionPanel"
import { NodeConfigPanel } from "./NodeConfigPanel"
import { NodePalette } from "./NodePalette"
import { WorkflowCanvas } from "./WorkflowCanvas"

interface WorkflowBuilderProps {
  workflowId: string | null
  executionId?: string | null
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
  executionId: externalExecutionId,
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
  const [internalExecutionId, setInternalExecutionId] = useState<string | null>(null)
  // Use external executionId if provided, otherwise use internal state
  const executionId = externalExecutionId ?? internalExecutionId
  const [nodeStatuses, setNodeStatuses] = useState<Record<string, string>>({})
  const [showExecutionPanel, setShowExecutionPanel] = useState(false)
  // Track the last added node position for stacking
  const lastNodePositionRef = useRef<{ x: number; y: number } | null>(null)

  // Calculate center position for new nodes
  const getCenterPosition = useCallback(() => {
    // React Flow coordinates are relative to the flow, not the viewport
    // We'll use a fixed center point that works well for most screen sizes
    const centerX = 500 // Fixed center X coordinate
    const centerY = 300 // Fixed center Y coordinate
    
    // If we have a last node position, stack below it
    if (lastNodePositionRef.current) {
      return {
        x: lastNodePositionRef.current.x,
        y: lastNodePositionRef.current.y + 120, // Stack 120px below (node height + spacing)
      }
    }
    
    return { x: centerX, y: centerY }
  }, [])

  // Reset last node position when nodes are cleared
  useEffect(() => {
    if (nodes.length === 0) {
      lastNodePositionRef.current = null
    }
  }, [nodes.length])

  const handleDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const type = event.dataTransfer.getData("application/reactflow")

      if (!type || !reactFlowWrapper.current) {
        return
      }

      // Use center position for consistent placement (always stack from center)
      const position = getCenterPosition()

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

      // Update last node position for next node
      lastNodePositionRef.current = position
      
      onNodeAdd(newNode)
    },
    [onNodeAdd, getCenterPosition],
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

  // Intercept node addition to set center position
  const handleNodeAddWithPosition = useCallback(
    (node: Node) => {
      // If node position is (0,0), it means it was clicked (not dragged), so calculate center
      if (node.position.x === 0 && node.position.y === 0) {
        const centerPos = getCenterPosition()
        node.position = centerPos
        lastNodePositionRef.current = centerPos
      }
      
      onNodeAdd(node)
    },
    [onNodeAdd, getCenterPosition],
  )

  const handleExecutionStatusChange = useCallback((status: any) => {
    // Only update internal state if external executionId is not provided
    if (externalExecutionId === undefined) {
      setInternalExecutionId(status.execution_id)
    }
    // Auto-open execution panel when execution starts
    if (status.execution_id) {
      setShowExecutionPanel(true)
    }
  }, [externalExecutionId])

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
      <NodePalette onNodeAdd={handleNodeAddWithPosition} />
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
