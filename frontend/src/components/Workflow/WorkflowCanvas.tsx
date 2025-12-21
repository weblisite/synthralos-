/**
 * Workflow Canvas Component
 *
 * Main React Flow canvas for building workflows.
 * Handles node creation, connection, and layout.
 */

import {
  addEdge,
  applyNodeChanges,
  Background,
  type Connection,
  Controls,
  type Edge,
  MiniMap,
  type Node,
  type NodeChange,
  type NodeMouseHandler,
  type NodeTypes,
  ReactFlow,
} from "@xyflow/react"
import { useCallback, useEffect } from "react"
import "@xyflow/react/dist/style.css"

import { AINode } from "./nodes/AINode"
import { BrowserNode } from "./nodes/BrowserNode"
import { CodeNode } from "./nodes/CodeNode"
import { ConnectorNode } from "./nodes/ConnectorNode"
import { HTTPRequestNode } from "./nodes/HTTPRequestNode"
import { LogicNode } from "./nodes/LogicNode"
import { OCRSwitchNode } from "./nodes/OCRSwitchNode"
import { RAGSwitchNode } from "./nodes/RAGSwitchNode"
import { ScrapingNode } from "./nodes/ScrapingNode"
import { TriggerNode } from "./nodes/TriggerNode"

const nodeTypes: NodeTypes = {
  trigger: TriggerNode,
  ai_prompt: AINode,
  connector: ConnectorNode,
  code: CodeNode,
  condition: LogicNode,
  switch: LogicNode,
  rag_switch: RAGSwitchNode,
  ocr_switch: OCRSwitchNode,
  scraping: ScrapingNode,
  browser: BrowserNode,
  http_request: HTTPRequestNode,
}

interface WorkflowCanvasProps {
  initialNodes: Node[]
  initialEdges: Edge[]
  onNodesChange: (nodes: Node[]) => void
  onEdgesChange: (edges: Edge[]) => void
  onConnect: (connection: Connection) => void
  onNodeClick?: NodeMouseHandler
  onPaneClick?: (event: React.MouseEvent) => void
  onNodeDelete?: (nodeId: string) => void
  readonly?: boolean
}

export function WorkflowCanvas({
  initialNodes,
  initialEdges,
  onNodesChange,
  onEdgesChange,
  onConnect,
  onNodeClick,
  onPaneClick,
  onNodeDelete,
  readonly = false,
}: WorkflowCanvasProps) {
  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      // Handle node deletion via keyboard (Delete/Backspace)
      const deleteChanges = changes.filter((change) => change.type === "remove")

      if (deleteChanges.length > 0 && onNodeDelete) {
        // React Flow handles deletion internally, but we can also call onNodeDelete
        // for custom handling if needed
        deleteChanges.forEach((change) => {
          if (change.type === "remove" && change.id) {
            onNodeDelete(change.id)
          }
        })
      }

      // Apply changes to current nodes using React Flow's helper
      const updatedNodes = applyNodeChanges(changes, initialNodes)
      onNodesChange(updatedNodes)
    },
    [initialNodes, onNodesChange, onNodeDelete],
  )

  // Add keyboard shortcut for delete (Delete/Backspace keys)
  useEffect(() => {
    if (readonly || !onNodeDelete) return

    const handleKeyDown = (event: KeyboardEvent) => {
      // Check if Delete or Backspace is pressed
      if (event.key === "Delete" || event.key === "Backspace") {
        // Don't delete if user is typing in an input/textarea
        const target = event.target as HTMLElement
        if (
          target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.isContentEditable
        ) {
          return
        }

        // React Flow will handle the deletion via handleNodesChange
        // This is just for additional handling if needed
        event.preventDefault()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => {
      window.removeEventListener("keydown", handleKeyDown)
    }
  }, [readonly, onNodeDelete])

  const handleEdgesChange = useCallback(
    (changes: any) => {
      // React Flow passes EdgeChange array
      const updatedEdges = changes.reduce((acc: Edge[], change: any) => {
        if (change.type === "remove") {
          return acc.filter((e) => e.id !== change.id)
        }
        if (change.type === "add") {
          return [...acc, change.item]
        }
        // Update existing edge
        return acc.map((edge) =>
          edge.id === change.id ? { ...edge, ...change } : edge,
        )
      }, initialEdges)
      onEdgesChange(updatedEdges)
    },
    [initialEdges, onEdgesChange],
  )

  const handleConnect = useCallback(
    (params: Connection) => {
      if (readonly) return
      const newEdge = addEdge(params, initialEdges)
      onEdgesChange(newEdge)
      onConnect(params)
    },
    [initialEdges, readonly, onConnect, onEdgesChange],
  )

  return (
    <>
      <style>{`
        .react-flow__attribution {
          display: none !important;
        }
      `}</style>
      <div
        className="w-full h-full"
        style={{
          width: "100%",
          height: "100%",
          minWidth: "100%",
          minHeight: "100%",
        }}
      >
        <ReactFlow
          nodes={initialNodes}
          edges={initialEdges}
          onNodesChange={handleNodesChange}
          onEdgesChange={handleEdgesChange}
          onConnect={handleConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2, maxZoom: 1.5 }}
          minZoom={0.1}
          maxZoom={2}
          defaultEdgeOptions={{
            type: "smoothstep",
            animated: true,
          }}
          nodesDraggable={!readonly}
          nodesConnectable={!readonly}
          elementsSelectable={!readonly}
          proOptions={{ hideAttribution: true }}
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </>
  )
}
