/**
 * Monaco Editor Component
 *
 * Wrapper around Monaco Editor for inline code editing with syntax highlighting and auto-completion.
 */

import Editor from "@monaco-editor/react"
import { useTheme } from "@/components/theme-provider"
import { useMemo, useEffect, useState } from "react"

interface MonacoEditorProps {
  value: string
  onChange?: (value: string | undefined) => void
  language?: string
  height?: string
  readOnly?: boolean
  theme?: "light" | "dark" | "auto"
  options?: Record<string, any>
  className?: string
}

export function MonacoEditor({
  value,
  onChange,
  language = "python",
  height = "400px",
  readOnly = false,
  theme: themeProp,
  options = {},
  className,
}: MonacoEditorProps) {
  const { resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
  }, [])
  
  // Determine theme
  const editorTheme = useMemo(() => {
    if (!mounted) return "vs" // Default to light theme until mounted
    if (themeProp === "light") return "vs"
    if (themeProp === "dark") return "vs-dark"
    if (themeProp === "auto" || !themeProp) {
      return resolvedTheme === "dark" ? "vs-dark" : "vs"
    }
    return "vs"
  }, [themeProp, resolvedTheme, mounted])

  // Default editor options
  const editorOptions = useMemo(
    () => ({
      minimap: { enabled: false },
      fontSize: 14,
      lineNumbers: "on",
      roundedSelection: false,
      scrollBeyondLastLine: false,
      readOnly,
      automaticLayout: true,
      tabSize: 2,
      wordWrap: "on",
      ...options,
    }),
    [readOnly, options],
  )

  const handleEditorChange = (value: string | undefined) => {
    if (onChange) {
      onChange(value)
    }
  }

  return (
    <div className={className}>
      <Editor
        height={height}
        language={language}
        value={value}
        theme={editorTheme}
        onChange={handleEditorChange}
        options={editorOptions}
      />
    </div>
  )
}

