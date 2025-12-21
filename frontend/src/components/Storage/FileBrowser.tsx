/**
 * File Browser Component
 *
 * Lists, downloads, and deletes files from Supabase Storage buckets.
 * Integrates unused storage endpoints:
 * - GET /api/v1/storage/list/{bucket}
 * - GET /api/v1/storage/download/{bucket}/{file_path}
 * - DELETE /api/v1/storage/delete/{bucket}/{file_path}
 * - POST /api/v1/storage/signed-url
 * - GET /api/v1/storage/buckets
 */

import type { ColumnDef } from "@tanstack/react-table"
import { format } from "date-fns"
import {
  Download,
  FileText,
  Folder,
  RefreshCw,
  Trash2,
  Upload,
} from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { DataTable } from "@/components/Common/DataTable"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
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
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import { FileUpload } from "./FileUpload"

interface StorageFile {
  name: string
  path: string
  size: number
  content_type: string
  created_at: string
  updated_at: string
}

interface Bucket {
  name: string
  category: string
}

interface FileListResponse {
  files: StorageFile[]
  total_count: number
  bucket: string
  folder_path: string
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
  if (bytes < 1024 * 1024 * 1024)
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

export function FileBrowser() {
  const [buckets, setBuckets] = useState<Bucket[]>([])
  const [selectedBucket, setSelectedBucket] = useState<string>("")
  const [files, setFiles] = useState<StorageFile[]>([])
  const [currentFolder, setCurrentFolder] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingBuckets, setIsLoadingBuckets] = useState(false)
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Fetch available buckets
  const fetchBuckets = useCallback(async () => {
    setIsLoadingBuckets(true)
    try {
      const response = await apiClient.request<{
        buckets: string[]
        bucket_info?: Record<string, { description: string; category: string }>
      }>("/api/v1/storage/buckets")
      // Convert bucket names to Bucket objects with categories
      const bucketList: Bucket[] = response.buckets.map((name) => {
        const info = response.bucket_info?.[name]
        return {
          name,
          category: info?.category
            ? info.category
                .replace(/_/g, " ")
                .replace(/\b\w/g, (l) => l.toUpperCase())
            : name.includes("documents")
              ? "Documents"
              : name.includes("images")
                ? "Images"
                : name.includes("uploads")
                  ? "Uploads"
                  : "General",
        }
      })
      setBuckets(bucketList)
      if (bucketList.length > 0 && !selectedBucket) {
        setSelectedBucket(bucketList[0].name)
      }
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to fetch buckets",
      )
    } finally {
      setIsLoadingBuckets(false)
    }
  }, [selectedBucket, showErrorToast])

  // Fetch files in selected bucket
  const fetchFiles = useCallback(async () => {
    if (!selectedBucket) return

    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      if (currentFolder) {
        params.append("folder_path", currentFolder)
      }
      params.append("limit", "100")
      params.append("offset", "0")

      const response = await apiClient.request<FileListResponse>(
        `/api/v1/storage/list/${selectedBucket}?${params.toString()}`,
      )
      setFiles(response.files || [])
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to fetch files",
      )
      setFiles([])
    } finally {
      setIsLoading(false)
    }
  }, [selectedBucket, currentFolder, showErrorToast])

  useEffect(() => {
    fetchBuckets()
  }, [fetchBuckets])

  useEffect(() => {
    if (selectedBucket) {
      fetchFiles()
    }
  }, [selectedBucket, fetchFiles])

  // Handle file download
  const handleDownload = useCallback(
    async (file: StorageFile) => {
      try {
        // Get signed URL for download
        const { url } = await apiClient.request<{ url: string }>(
          "/api/v1/storage/signed-url",
          {
            method: "POST",
            body: JSON.stringify({
              bucket: selectedBucket,
              file_path: file.path,
              expires_in: 3600, // 1 hour
            }),
          },
        )
        // Open download link
        window.open(url, "_blank")
        showSuccessToast("Download started")
      } catch (error) {
        showErrorToast(
          error instanceof Error ? error.message : "Failed to download file",
        )
      }
    },
    [selectedBucket, showSuccessToast, showErrorToast],
  )

  // Handle file deletion
  const handleDelete = useCallback(
    async (file: StorageFile) => {
      if (
        !confirm(
          `Are you sure you want to delete "${file.name}"? This action cannot be undone.`,
        )
      ) {
        return
      }

      try {
        await apiClient.request(
          `/api/v1/storage/delete/${selectedBucket}/${encodeURIComponent(file.path)}`,
          {
            method: "DELETE",
          },
        )
        showSuccessToast("File deleted successfully")
        fetchFiles() // Refresh file list
      } catch (error) {
        showErrorToast(
          error instanceof Error ? error.message : "Failed to delete file",
        )
      }
    },
    [selectedBucket, fetchFiles, showSuccessToast, showErrorToast],
  )

  // Handle folder navigation
  const handleFolderClick = useCallback((folderPath: string) => {
    setCurrentFolder(folderPath)
  }, [])

  // Handle navigate up
  const handleNavigateUp = useCallback(() => {
    const parts = currentFolder.split("/").filter(Boolean)
    parts.pop()
    setCurrentFolder(parts.join("/"))
  }, [currentFolder])

  const columns: ColumnDef<StorageFile>[] = [
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => {
        const file = row.original
        const isFolder =
          file.content_type === "folder" || file.path.endsWith("/")
        return (
          <div className="flex items-center gap-2">
            {isFolder ? (
              <Folder className="h-4 w-4 text-blue-500" />
            ) : (
              <FileText className="h-4 w-4 text-muted-foreground" />
            )}
            <span
              className={isFolder ? "cursor-pointer hover:underline" : ""}
              onClick={() => isFolder && handleFolderClick(file.path)}
            >
              {file.name}
            </span>
          </div>
        )
      },
    },
    {
      accessorKey: "size",
      header: "Size",
      cell: ({ row }) => {
        const size = row.original.size
        return size > 0 ? formatFileSize(size) : "-"
      },
    },
    {
      accessorKey: "content_type",
      header: "Type",
      cell: ({ row }) => {
        const contentType = row.original.content_type
        if (contentType === "folder")
          return <Badge variant="secondary">Folder</Badge>
        const type = contentType.split("/")[0]
        return <Badge variant="outline">{type}</Badge>
      },
    },
    {
      accessorKey: "updated_at",
      header: "Modified",
      cell: ({ row }) => {
        const date = new Date(row.original.updated_at)
        return (
          <div className="text-sm">{format(date, "MMM d, yyyy HH:mm")}</div>
        )
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const file = row.original
        const isFolder =
          file.content_type === "folder" || file.path.endsWith("/")
        return (
          <div className="flex items-center gap-2">
            {!isFolder && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDownload(file)}
                >
                  <Download className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(file)}
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </>
            )}
          </div>
        )
      },
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">File Browser</h2>
          <p className="text-sm text-muted-foreground">
            Manage files in Supabase Storage buckets
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchFiles}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Dialog
            open={isUploadDialogOpen}
            onOpenChange={setIsUploadDialogOpen}
          >
            <DialogTrigger asChild>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Upload File
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Upload File</DialogTitle>
                <DialogDescription>
                  Upload a file to {selectedBucket || "selected bucket"}
                </DialogDescription>
              </DialogHeader>
              {selectedBucket && (
                <FileUpload
                  bucket={selectedBucket}
                  folderPath={currentFolder}
                  onUploadComplete={() => {
                    setIsUploadDialogOpen(false)
                    fetchFiles()
                  }}
                />
              )}
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Bucket Selector */}
      <Card>
        <CardHeader>
          <CardTitle>Select Bucket</CardTitle>
          <CardDescription>Choose a storage bucket to browse</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingBuckets ? (
            <Skeleton className="h-10 w-64" />
          ) : (
            <Select
              value={selectedBucket}
              onValueChange={(value) => {
                setSelectedBucket(value)
                setCurrentFolder("") // Reset folder when changing bucket
              }}
            >
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Select a bucket" />
              </SelectTrigger>
              <SelectContent>
                {buckets.map((bucket) => (
                  <SelectItem key={bucket.name} value={bucket.name}>
                    <div className="flex items-center gap-2">
                      <span>{bucket.name}</span>
                      <Badge variant="secondary" className="ml-2">
                        {bucket.category}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </CardContent>
      </Card>

      {/* Breadcrumb Navigation */}
      {selectedBucket && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-sm">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentFolder("")}
              >
                {selectedBucket}
              </Button>
              {currentFolder
                .split("/")
                .filter(Boolean)
                .map((part, index, arr) => {
                  const path = arr.slice(0, index + 1).join("/")
                  return (
                    <div key={path} className="flex items-center gap-2">
                      <span>/</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setCurrentFolder(path)}
                      >
                        {part}
                      </Button>
                    </div>
                  )
                })}
              {currentFolder && (
                <Button variant="ghost" size="sm" onClick={handleNavigateUp}>
                  <RefreshCw className="h-4 w-4 rotate-180" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* File List */}
      {selectedBucket && (
        <Card>
          <CardHeader>
            <CardTitle>Files</CardTitle>
            <CardDescription>
              {files.length} file(s) in {currentFolder || "root"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : files.length > 0 ? (
              <DataTable columns={columns} data={files} />
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No files found in this folder</p>
                <Button
                  variant="outline"
                  className="mt-4"
                  onClick={() => setIsUploadDialogOpen(true)}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload File
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {!selectedBucket && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8 text-muted-foreground">
              <Folder className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Select a bucket to browse files</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
