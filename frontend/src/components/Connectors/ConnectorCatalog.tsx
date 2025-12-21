/**
 * Connector Catalog Component
 *
 * Displays a catalog of available connectors with search, filtering, and registration.
 */

import type { ColumnDef } from "@tanstack/react-table"
import { ExternalLink, Plus, Search, X } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { DataTable } from "@/components/Common/DataTable"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useConnections } from "@/hooks/useConnections"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import { getConnectorLogoUrls } from "@/lib/connectorLogos"
import { ConnectButton } from "./ConnectButton"
import { ConnectionStatus } from "./ConnectionStatus"
import { ConnectorDetails } from "./ConnectorDetails"
import { ConnectorTestRunner } from "./ConnectorTestRunner"
import { ConnectorWizard } from "./ConnectorWizard"
import { OAuthModal } from "./OAuthModal"

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
  nango_enabled?: boolean
  nango_provider_key?: string
}

export function ConnectorCatalog() {
  const [connectors, setConnectors] = useState<Connector[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [activeTab, setActiveTab] = useState<"platform" | "custom">("platform")
  const [selectedConnector, setSelectedConnector] = useState<Connector | null>(
    null,
  )
  const [isWizardOpen, setIsWizardOpen] = useState(false)
  const [isOAuthModalOpen, setIsOAuthModalOpen] = useState(false)
  const [connectorDetails, setConnectorDetails] = useState<any>(null)
  const { showErrorToast } = useCustomToast()

  // Use Nango connections hook
  const { isConnected, disconnect, getConnectionStatus } = useConnections()

  const fetchConnectors = useCallback(async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      if (selectedCategory !== "all") {
        params.append("category", selectedCategory)
      }
      params.append("include_custom", "true")

      const data = await apiClient.request<
        { connectors?: Connector[] } | Connector[]
      >(`/api/v1/connectors/list?${params}`)
      // Handle both old array format and new object format
      const connectorsList = Array.isArray(data) ? data : data.connectors || []
      setConnectors(connectorsList)
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to fetch connectors",
      )
    } finally {
      setIsLoading(false)
    }
  }, [showErrorToast, selectedCategory])

  const fetchConnectorDetails = useCallback(
    async (slug: string) => {
      try {
        const details = await apiClient.request(`/api/v1/connectors/${slug}`)
        setConnectorDetails(details)
      } catch (_error) {
        showErrorToast("Failed to fetch connector details")
      }
    },
    [showErrorToast],
  )

  useEffect(() => {
    fetchConnectors()
  }, [fetchConnectors])

  // Refresh connections when component mounts or connectors change
  useEffect(() => {
    // Connections are automatically fetched by useConnections hook
    // This effect ensures we refresh when connectors list changes
  }, [])

  // Get unique categories
  const categories = Array.from(
    new Set(
      connectors
        .map((c) => c.category)
        .filter((cat): cat is string => Boolean(cat)),
    ),
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

  // Connector name cell component with logo
  function ConnectorNameCell({ connector }: { connector: Connector }) {
    const [logoUrl, setLogoUrl] = useState<string | null>(null)

    useEffect(() => {
      if (connector.slug && !logoUrl) {
        const logoUrls = getConnectorLogoUrls(connector.slug)
        let currentIndex = 0

        const tryNextLogo = () => {
          if (currentIndex >= logoUrls.length) {
            setLogoUrl(null)
            return
          }

          const img = new Image()
          img.onload = () => setLogoUrl(logoUrls[currentIndex]!)
          img.onerror = () => {
            currentIndex++
            tryNextLogo()
          }
          img.src = logoUrls[currentIndex]!
        }

        tryNextLogo()
      }
    }, [connector.slug, logoUrl])

    return (
      <div className="flex items-center gap-2">
        {logoUrl ? (
          <img
            src={logoUrl}
            alt={connector.name}
            className="h-5 w-5 object-contain flex-shrink-0"
            onError={() => setLogoUrl(null)}
          />
        ) : (
          <div className="h-5 w-5 flex-shrink-0" /> // Placeholder for alignment
        )}
        <div>
          <div className="font-semibold">{connector.name}</div>
          <div className="text-sm text-muted-foreground">{connector.slug}</div>
        </div>
      </div>
    )
  }

  const columns: ColumnDef<Connector>[] = [
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => <ConnectorNameCell connector={row.original} />,
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
      id: "connection_status",
      header: "Connection",
      cell: ({ row }) => {
        const connector = row.original
        const connection = getConnectionStatus(connector.id)
        const status = connection?.status || "disconnected"
        return (
          <ConnectionStatus
            status={
              status as "connected" | "disconnected" | "pending" | "error"
            }
          />
        )
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const connector = row.original
        const connection = getConnectionStatus(connector.id)
        const isConn = isConnected(connector.id)
        // Check if connector has Nango enabled (from connector list or details)
        const connectorData = connectors.find((c) => c.id === connector.id)
        const hasNango =
          connectorData?.nango_enabled ||
          connectorDetails?.manifest?.nango?.enabled

        const isDetailsOpen = selectedConnector?.id === connector.id

        return (
          <div className="flex items-center gap-2">
            <Dialog
              open={isDetailsOpen}
              onOpenChange={(open) => {
                if (!open) {
                  setSelectedConnector(null)
                } else {
                  setSelectedConnector(connector)
                  fetchConnectorDetails(connector.slug)
                }
              }}
            >
              <DialogTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedConnector(connector)
                    fetchConnectorDetails(connector.slug)
                  }}
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Details
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Connector Details</DialogTitle>
                  <DialogDescription>
                    View actions, triggers, and versions for {connector.name}
                  </DialogDescription>
                </DialogHeader>
                <ConnectorDetails
                  connectorSlug={connector.slug}
                  connectorName={connector.name}
                  onClose={() => {
                    setSelectedConnector(null)
                  }}
                />
              </DialogContent>
            </Dialog>
            {hasNango &&
              (isConn ? (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    if (connection) {
                      disconnect({
                        connectorId: connector.id,
                        connectionId: connection.id,
                      })
                    }
                  }}
                >
                  <X className="h-4 w-4 mr-2" />
                  Disconnect
                </Button>
              ) : (
                <ConnectButton
                  connectorId={connector.id}
                  connectorName={connector.name}
                  onConnected={() => {
                    fetchConnectors()
                  }}
                  className="text-sm"
                />
              ))}
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
                Register your own custom connector by providing its manifest and
                wheel URL
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

      <Tabs
        value={activeTab}
        onValueChange={(v) => setActiveTab(v as "platform" | "custom")}
      >
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="platform">Platform Connectors</TabsTrigger>
            <TabsTrigger value="custom">My Custom Connectors</TabsTrigger>
          </TabsList>

          <div className="flex items-center gap-2">
            <Select
              value={selectedCategory}
              onValueChange={setSelectedCategory}
            >
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
              <p className="text-sm mt-2">
                Click "Register Custom Connector" to create one.
              </p>
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
                  <strong>Status:</strong>{" "}
                  {getStatusBadge(selectedConnector.status)}
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
                        {connectorDetails.manifest.categories.map(
                          (cat: string) => (
                            <Badge key={cat} variant="outline">
                              {cat}
                            </Badge>
                          ),
                        )}
                      </div>
                    </div>
                  )}
              </div>

              {(connectorDetails?.manifest?.oauth ||
                connectorDetails?.manifest?.nango?.enabled) && (
                <div className="space-y-2">
                  <h3 className="font-semibold">Connection</h3>
                  {isConnected(selectedConnector.id) ? (
                    <div className="space-y-2">
                      <ConnectionStatus status="connected" />
                      {(() => {
                        const connection = getConnectionStatus(
                          selectedConnector.id,
                        )
                        return (
                          connection?.connected_at && (
                            <p className="text-sm text-muted-foreground">
                              Connected:{" "}
                              {new Date(
                                connection.connected_at,
                              ).toLocaleDateString()}
                              {connection.last_synced_at && (
                                <>
                                  {" "}
                                  • Last synced:{" "}
                                  {new Date(
                                    connection.last_synced_at,
                                  ).toLocaleDateString()}
                                </>
                              )}
                            </p>
                          )
                        )
                      })()}
                      <div className="flex gap-2">
                        <ConnectButton
                          connectorId={selectedConnector.id}
                          connectorName={selectedConnector.name}
                          onConnected={() => {
                            fetchConnectorDetails(selectedConnector.slug)
                            fetchConnectors()
                          }}
                          className="flex-1"
                        />
                        <Button
                          variant="destructive"
                          onClick={() => {
                            const connection = getConnectionStatus(
                              selectedConnector.id,
                            )
                            if (connection) {
                              disconnect({
                                connectorId: selectedConnector.id,
                                connectionId: connection.id,
                              })
                              fetchConnectorDetails(selectedConnector.slug)
                            }
                          }}
                          className="flex-1"
                        >
                          <X className="h-4 w-4 mr-2" />
                          Disconnect
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <ConnectionStatus status="disconnected" />
                      <ConnectButton
                        connectorId={selectedConnector.id}
                        connectorName={selectedConnector.name}
                        onConnected={() => {
                          fetchConnectorDetails(selectedConnector.slug)
                          fetchConnectors()
                        }}
                        className="w-full"
                      />
                    </div>
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
