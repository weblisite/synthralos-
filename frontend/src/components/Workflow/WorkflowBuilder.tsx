/**
 * Workflow Builder Component
 *
 * Main container component that combines canvas, palette, and config panel.
 */

import type { Connection, Edge, Node } from "@xyflow/react"
import { useCallback, useMemo, useRef, useState } from "react"
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

      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: {
          label:
            type.charAt(0).toUpperCase() + type.slice(1).replace(/_/g, " "),
          config: {},
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
  }, [onNodeSelect])

  const handleExecutionStatusChange = useCallback((status: any) => {
    setExecutionId(status.execution_id)
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

  return (
    <div className="flex h-full">
      <NodePalette onNodeAdd={onNodeAdd} />
      <div
        ref={reactFlowWrapper}
        className="flex-1 min-h-0"
        style={{ height: '100%' }}
        role="application"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
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
      <NodeConfigPanel
        node={selectedNode}
        onClose={() => onNodeSelect(null)}
        onUpdate={onNodeUpdate}
      />
      <ExecutionPanel
        workflowId={workflowId}
        executionId={executionId}
        nodes={nodes}
        edges={edges}
        onExecutionStatusChange={handleExecutionStatusChange}
        onNodeStatusChange={handleNodeStatusChange}
      />
    </div>
  )
}
