/**
 * Admin Connector Management Component
 *
 * Admin-only interface for managing platform connectors.
 */

import { type ColumnDef } from "@tanstack/react-table"
import { Plus, Trash2 } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DataTable } from "@/components/Common/DataTable"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { apiRequest } from "@/lib/api"
import { ConnectorWizard } from "@/components/Connectors/ConnectorWizard"

interface Connector {
  id: string
  slug: string
  name: string
  status: "draft" | "beta" | "stable" | "deprecated"
  latest_version: string | null
  category?: string
  is_platform: boolean
  owner_id: string | null
  created_by: string | null
  created_at: string
}

export function AdminConnectorManagement() {
  const [connectors, setConnectors] = useState<Connector[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")
  const [isWizardOpen, setIsWizardOpen] = useState(false)
  const { showErrorToast, showSuccessToast } = useCustomToast()

  const fetchConnectors = useCallback(async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      if (selectedStatus !== "all") {
        params.append("status_filter", selectedStatus)
      }
      if (selectedCategory !== "all") {
        params.append("category", selectedCategory)
      }

      const data = await apiRequest<{ connectors: Connector[] }>(
        `/api/v1/admin/connectors/list?${params}`
      )
      setConnectors(data.connectors || [])
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to fetch connectors",
      )
    } finally {
      setIsLoading(false)
    }
  }, [selectedStatus, selectedCategory, showErrorToast])

  useEffect(() => {
    fetchConnectors()
  }, [fetchConnectors])

  const handleUpdateStatus = useCallback(async (slug: string, newStatus: string) => {
    try {
      await apiRequest(`/api/v1/admin/connectors/${slug}/status?new_status=${newStatus}`, {
        method: "PATCH",
      })
      showSuccessToast(`Connector status updated to ${newStatus}`)
      fetchConnectors()
    } catch (error) {
      showErrorToast("Failed to update connector status")
    }
  }, [showErrorToast, showSuccessToast, fetchConnectors])

  const handleDelete = useCallback(async (slug: string) => {
    if (!confirm(`Are you sure you want to delete connector "${slug}"? This action cannot be undone.`)) {
      return
    }

    try {
      await apiRequest(`/api/v1/admin/connectors/${slug}`, {
        method: "DELETE",
      })
      showSuccessToast("Connector deleted successfully")
      fetchConnectors()
    } catch (error) {
      showErrorToast("Failed to delete connector")
    }
  }, [showErrorToast, showSuccessToast, fetchConnectors])

  const getStatusBadge = (status: Connector["status"]) => {
    const variants: Record<string, "default" | "destructive" | "secondary"> = {
      stable: "default",
      beta: "secondary",
      draft: "secondary",
      deprecated: "destructive",
    }

    return <Badge variant={variants[status] || "secondary"}>{status}</Badge>
  }

  const categories = Array.from(
    new Set(connectors.map((c) => c.category).filter((cat): cat is string => Boolean(cat)))
  ).sort()

  const filteredConnectors = connectors.filter((connector) => {
    if (selectedCategory !== "all" && connector.category !== selectedCategory) {
      return false
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return (
        connector.name.toLowerCase().includes(query) ||
        connector.slug.toLowerCase().includes(query) ||
        connector.category?.toLowerCase().includes(query)
      )
    }

    return true
  })

  const columns: ColumnDef<Connector>[] = [
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => {
        const connector = row.original
        return (
          <div>
            <div className="font-semibold">{connector.name}</div>
            <div className="text-sm text-muted-foreground">{connector.slug}</div>
          </div>
        )
      },
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const connector = row.original
        return (
          <div className="flex items-center gap-2">
            {getStatusBadge(connector.status)}
            <Select
              value={connector.status}
              onValueChange={(value) => handleUpdateStatus(connector.slug, value)}
            >
              <SelectTrigger className="w-[120px] h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="beta">Beta</SelectItem>
                <SelectItem value="stable">Stable</SelectItem>
                <SelectItem value="deprecated">Deprecated</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )
      },
    },
    {
      accessorKey: "latest_version",
      header: "Version",
      cell: ({ row }) => {
        const version = row.original.latest_version
        return (
          <div className="text-sm">
            {version || <span className="text-muted-foreground">N/A</span>}
          </div>
        )
      },
    },
    {
      accessorKey: "category",
      header: "Category",
      cell: ({ row }) => {
        const category = row.original.category
        return category ? (
          <Badge variant="outline" className="text-xs">
            {category}
          </Badge>
        ) : (
          <span className="text-sm text-muted-foreground">-</span>
        )
      },
    },
    {
      accessorKey: "is_platform",
      header: "Type",
      cell: ({ row }) => {
        const isPlatform = row.original.is_platform
        return (
          <Badge variant={isPlatform ? "default" : "secondary"}>
            {isPlatform ? "Platform" : "Custom"}
          </Badge>
        )
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const connector = row.original
        return (
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleDelete(connector.slug)}
              disabled={connector.is_platform && connector.status !== "deprecated"}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        )
      },
    },
  ]

  if (isLoading) {
    return <div>Loading connectors...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Connector Management</h2>
          <p className="text-muted-foreground">
            Manage platform connectors available to all users
          </p>
        </div>
        <Dialog open={isWizardOpen} onOpenChange={setIsWizardOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Register Platform Connector
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Register Platform Connector</DialogTitle>
              <DialogDescription>
                Register a new platform connector that will be available to all users
              </DialogDescription>
            </DialogHeader>
            <ConnectorWizard
              onSuccess={() => {
                setIsWizardOpen(false)
                fetchConnectors()
              }}
              endpoint="/api/v1/admin/connectors/register"
              isPlatform={true}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex items-center gap-2">
        <Select value={selectedStatus} onValueChange={setSelectedStatus}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="beta">Beta</SelectItem>
            <SelectItem value="stable">Stable</SelectItem>
            <SelectItem value="deprecated">Deprecated</SelectItem>
          </SelectContent>
        </Select>

        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Input
          placeholder="Search connectors..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 max-w-sm"
        />
      </div>

      <DataTable columns={columns} data={filteredConnectors} />
    </div>
  )
}


