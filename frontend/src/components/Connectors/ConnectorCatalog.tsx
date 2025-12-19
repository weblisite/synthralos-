/**
 * Connector Catalog Component
 *
 * Displays a catalog of available connectors with search, filtering, and registration.
 */

import { type ColumnDef } from "@tanstack/react-table"
import { ExternalLink, Plus, Search, X, CheckCircle2, XCircle } from "lucide-react"
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
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import { ConnectorWizard } from "./ConnectorWizard"
import { OAuthModal } from "./OAuthModal"
import { ConnectorTestRunner } from "./ConnectorTestRunner"

interface Connector {
  id: string
  slug: string
  name: string
  status: "draft" | "beta" | "stable" | "deprecated"
  latest_version: string | null
  created_at: string
  description?: string
  category?: string
  is_platform?: boolean
  owner_id?: string | null
  auth_status?: "authorized" | "not_authorized" | "unknown"
}

export function ConnectorCatalog() {
  const [connectors, setConnectors] = useState<Connector[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [activeTab, setActiveTab] = useState<"platform" | "custom">("platform")
  const [selectedConnector, setSelectedConnector] = useState<Connector | null>(null)
  const [isWizardOpen, setIsWizardOpen] = useState(false)
  const [isOAuthModalOpen, setIsOAuthModalOpen] = useState(false)
  const [connectorDetails, setConnectorDetails] = useState<any>(null)
  const [authStatuses, setAuthStatuses] = useState<Record<string, any>>({})
  const { showErrorToast, showSuccessToast } = useCustomToast()

  const fetchConnectors = useCallback(async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      if (selectedCategory !== "all") {
        params.append("category", selectedCategory)
      }
      params.append("include_custom", "true")

      const data = await apiClient.request<{ connectors?: Connector[] } | Connector[]>(
        `/api/v1/connectors/list?${params}`
      )
      // Handle both old array format and new object format
      const connectorsList = Array.isArray(data) ? data : (data.connectors || [])
      setConnectors(connectorsList)
      
      // Fetch authorization statuses for all connectors
      await fetchAuthStatuses(connectorsList)
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to fetch connectors",
      )
    } finally {
      setIsLoading(false)
    }
  }, [showErrorToast, selectedCategory])

  const fetchAuthStatuses = useCallback(async (connectorsList: Connector[]) => {
    try {
      const statusPromises = connectorsList.map(async (connector) => {
        try {
          const status = await apiClient.request(`/api/v1/connectors/${connector.slug}/auth-status`)
          return { slug: connector.slug, status }
        } catch (error) {
          // Ignore errors for individual status checks
        }
        return { slug: connector.slug, status: { authorized: false } }
      })

      const statuses = await Promise.all(statusPromises)
      const statusMap: Record<string, any> = {}
      statuses.forEach(({ slug, status }) => {
        statusMap[slug] = status
      })
      setAuthStatuses(statusMap)
    } catch (error) {
      // Ignore errors
    }
  }, [])

  const fetchConnectorDetails = useCallback(async (slug: string) => {
    try {
      const details = await apiClient.request(`/api/v1/connectors/${slug}`)
      setConnectorDetails(details)
    } catch (error) {
      showErrorToast("Failed to fetch connector details")
    }
  }, [showErrorToast])

  const handleDisconnect = useCallback(async (slug: string) => {
    try {
      await apiClient.request(`/api/v1/connectors/${slug}/authorization`, {
        method: "DELETE",
      })
      showSuccessToast("Authorization revoked successfully")
      // Refresh auth status
      await fetchAuthStatuses(connectors)
      if (selectedConnector?.slug === slug) {
        fetchConnectorDetails(slug)
      }
    } catch (error) {
      showErrorToast("Failed to revoke authorization")
    }
  }, [connectors, selectedConnector, showErrorToast, showSuccessToast, fetchAuthStatuses, fetchConnectorDetails])

  useEffect(() => {
    fetchConnectors()
  }, [fetchConnectors, selectedCategory])

  // Get unique categories
  const categories = Array.from(
    new Set(connectors.map((c) => c.category).filter((cat): cat is string => Boolean(cat)))
  ).sort()

  const filteredConnectors = connectors.filter((connector) => {
    // Filter by tab (platform vs custom)
    if (activeTab === "platform" && !connector.is_platform) return false
    if (activeTab === "custom" && connector.is_platform) return false

    // Filter by category
    if (selectedCategory !== "all" && connector.category !== selectedCategory) {
      return false
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return (
        connector.name.toLowerCase().includes(query) ||
        connector.slug.toLowerCase().includes(query) ||
        connector.description?.toLowerCase().includes(query) ||
        connector.category?.toLowerCase().includes(query)
      )
    }

    return true
  })

  const getStatusBadge = (status: Connector["status"]) => {
    const variants: Record<string, "default" | "destructive" | "secondary"> = {
      stable: "default",
      beta: "secondary",
      draft: "secondary",
      deprecated: "destructive",
    }

    return <Badge variant={variants[status] || "secondary"}>{status}</Badge>
  }

  const getAuthStatusBadge = (slug: string) => {
    const status = authStatuses[slug]
    if (!status) {
      return (
        <Badge variant="secondary" className="text-xs">
          Unknown
        </Badge>
      )
    }
    
    if (status.authorized) {
      return (
        <Badge variant="default" className="text-xs bg-green-500">
          <CheckCircle2 className="h-3 w-3 mr-1" />
          Authorized
        </Badge>
      )
    }
    
    return (
      <Badge variant="secondary" className="text-xs">
        <XCircle className="h-3 w-3 mr-1" />
        Not Authorized
      </Badge>
    )
  }

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
      cell: ({ row }) => getStatusBadge(row.original.status),
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
      id: "auth_status",
      header: "Authorization",
      cell: ({ row }) => {
        const connector = row.original
        return getAuthStatusBadge(connector.slug)
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
              onClick={() => {
                setSelectedConnector(connector)
                fetchConnectorDetails(connector.slug)
              }}
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              View
            </Button>
          </div>
        )
      },
    },
  ]

  if (isLoading) {
    return <div>Loading connectors...</div>
  }

  const platformConnectors = filteredConnectors.filter((c) => c.is_platform)
  const customConnectors = filteredConnectors.filter((c) => !c.is_platform)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Connector Catalog</h2>
          <p className="text-muted-foreground">
            Browse and register connectors for your workflows
          </p>
        </div>
        <Dialog open={isWizardOpen} onOpenChange={setIsWizardOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Register Custom Connector
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Register Custom Connector</DialogTitle>
              <DialogDescription>
                Register your own custom connector by providing its manifest and wheel URL
              </DialogDescription>
            </DialogHeader>
            <ConnectorWizard
              onSuccess={() => {
                setIsWizardOpen(false)
                fetchConnectors()
              }}
              onClose={() => setIsWizardOpen(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "platform" | "custom")}>
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="platform">Platform Connectors</TabsTrigger>
            <TabsTrigger value="custom">My Custom Connectors</TabsTrigger>
          </TabsList>
          
          <div className="flex items-center gap-2">
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
            
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search connectors..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>
        </div>

        <TabsContent value="platform" className="space-y-4">
          <DataTable columns={columns} data={platformConnectors} />
        </TabsContent>

        <TabsContent value="custom" className="space-y-4">
          {customConnectors.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>You haven't created any custom connectors yet.</p>
              <p className="text-sm mt-2">Click "Register Custom Connector" to create one.</p>
            </div>
          ) : (
            <DataTable columns={columns} data={customConnectors} />
          )}
        </TabsContent>
      </Tabs>

      {selectedConnector && (
        <Dialog
          open={!!selectedConnector}
          onOpenChange={() => {
            setSelectedConnector(null)
            setConnectorDetails(null)
          }}
        >
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{selectedConnector.name}</DialogTitle>
              <DialogDescription>
                Connector details, OAuth authorization, and testing
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-6">
              <div className="space-y-2">
                <div>
                  <strong>Slug:</strong> {selectedConnector.slug}
                </div>
                <div>
                  <strong>Status:</strong> {getStatusBadge(selectedConnector.status)}
                </div>
                {selectedConnector.latest_version && (
                  <div>
                    <strong>Version:</strong> {selectedConnector.latest_version}
                  </div>
                )}
                {connectorDetails?.manifest?.description && (
                  <div>
                    <strong>Description:</strong>
                    <p className="text-sm text-muted-foreground mt-1">
                      {connectorDetails.manifest.description}
                    </p>
                  </div>
                )}
                {connectorDetails?.manifest?.categories &&
                  connectorDetails.manifest.categories.length > 0 && (
                    <div>
                      <strong>Categories:</strong>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {connectorDetails.manifest.categories.map((cat: string) => (
                          <Badge key={cat} variant="outline">
                            {cat}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
              </div>

              {connectorDetails?.manifest?.oauth && (
                <div className="space-y-2">
                  {authStatuses[selectedConnector.slug]?.authorized ? (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                        <span>Authorized</span>
                        {authStatuses[selectedConnector.slug]?.expires_at && (
                          <span className="text-xs">
                            (Expires: {new Date(authStatuses[selectedConnector.slug].expires_at).toLocaleDateString()})
                          </span>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => setIsOAuthModalOpen(true)}
                          variant="outline"
                          className="flex-1"
                        >
                          Re-authorize {selectedConnector.name}
                        </Button>
                        <Button
                          onClick={() => handleDisconnect(selectedConnector.slug)}
                          variant="destructive"
                          className="flex-1"
                        >
                          <X className="h-4 w-4 mr-2" />
                          Disconnect
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <Button
                      onClick={() => setIsOAuthModalOpen(true)}
                      variant="default"
                      className="w-full"
                    >
                      Authorize {selectedConnector.name}
                    </Button>
                  )}
                </div>
              )}

              {connectorDetails && (
                <ConnectorTestRunner
                  connectorSlug={selectedConnector.slug}
                  actions={
                    connectorDetails.manifest?.actions
                      ? Object.keys(connectorDetails.manifest.actions)
                      : []
                  }
                  triggers={
                    connectorDetails.manifest?.triggers
                      ? Object.keys(connectorDetails.manifest.triggers)
                      : []
                  }
                />
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}

      {selectedConnector && (
        <OAuthModal
          connectorSlug={selectedConnector.slug}
          isOpen={isOAuthModalOpen}
          onClose={() => setIsOAuthModalOpen(false)}
          onSuccess={() => {
            setIsOAuthModalOpen(false)
            fetchConnectorDetails(selectedConnector.slug)
          }}
        />
      )}
    </div>
  )
}

