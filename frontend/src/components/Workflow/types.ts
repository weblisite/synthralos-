/**
 * Workflow Types
 *
 * Type definitions for workflow builder components.
 */

export interface WorkflowNode {
  id: string
  type: string
  position: { x: number; y: number }
  data: {
    label: string
    config?: Record<string, any>
    [key: string]: any
  }
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  sourceHandle?: string
  targetHandle?: string
}

export interface WorkflowGraph {
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
}

export interface WorkflowConfig {
  name: string
  description?: string
  trigger_config?: Record<string, any>
  graph_config: WorkflowGraph
}

export type NodeType =
  | "trigger"
  | "ai_prompt"
  | "agent"
  | "connector"
  | "code"
  | "condition"
  | "switch"
  | "rag_switch"
  | "ocr_switch"
  | "scraping"
  | "browser"
  | "http_request"
  | "sub_workflow"
  | "sub-workflow"
  | "loop"
  | "for"
  | "while"
  | "repeat"
  | "delay"
  | "wait"
  | "try"
  | "catch"
  | "finally"
  | "map"
  | "filter"
  | "reduce"
  | "merge"
  | "split"
  | "set_variable"
  | "get_variable"
  | "break"
  | "continue"
  | "storage"
  | "social_monitoring"
  | "human_approval"
  | "notification"
