import { useState, useCallback } from "react"
import { Upload, X, FileText, Loader2, CheckCircle2, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { supabase } from "@/lib/supabase"
import useCustomToast from "@/hooks/useCustomToast"

interface FileUploadProps {
  bucket: string
  folderPath?: string
  onUploadComplete?: (result: {
    file_id: string
    path: string
    url: string
    size: number
    content_type: string
  }) => void
  onUploadError?: (error: string) => void
  accept?: string
  maxSize?: number // in bytes
  multiple?: boolean
  className?: string
}

export function FileUpload({
  bucket,
  folderPath = "",
  onUploadComplete,
  onUploadError,
  accept,
  maxSize = 10 * 1024 * 1024, // 10MB default
  multiple = false,
  className = "",
}: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})
  const [uploadedFiles, setUploadedFiles] = useState<Record<string, any>>({})
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleFileSelect = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFiles = Array.from(event.target.files || [])
      
      // Validate file size
      const oversizedFiles = selectedFiles.filter((file) => file.size > maxSize)
      if (oversizedFiles.length > 0) {
        showErrorToast(
          `File(s) too large. Maximum size is ${(maxSize / 1024 / 1024).toFixed(2)}MB`
        )
        return
      }
      
      // Validate file type if accept is specified
      if (accept) {
        const acceptTypes = accept.split(",").map((t) => t.trim())
        const invalidFiles = selectedFiles.filter((file) => {
          const fileType = file.type || ""
          const fileExtension = "." + file.name.split(".").pop()?.toLowerCase()
          return !acceptTypes.some(
            (acceptType) =>
              fileType === acceptType ||
              fileType.startsWith(acceptType.split("/")[0] + "/") ||
              acceptType === fileExtension ||
              acceptType === "*"
          )
        })
        
        if (invalidFiles.length > 0) {
          showErrorToast(`Invalid file type(s). Accepted types: ${accept}`)
          return
        }
      }
      
      if (multiple) {
        setFiles((prev) => [...prev, ...selectedFiles])
      } else {
        setFiles(selectedFiles)
      }
    },
    [accept, maxSize, multiple, showErrorToast]
  )

  const handleUpload = useCallback(async () => {
    if (files.length === 0) {
      showErrorToast("Please select at least one file")
      return
    }

    setUploading(true)
    setUploadProgress({})
    setUploadedFiles({})

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        showErrorToast("You must be logged in to upload files")
        setUploading(false)
        return
      }

      const uploadPromises = files.map(async (file) => {
        const formData = new FormData()
        formData.append("file", file)
        formData.append("bucket", bucket)
        if (folderPath) {
          formData.append("folder_path", folderPath)
        }

        return fetch("/api/v1/storage/upload", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${session.access_token}`,
          },
          body: formData,
        })
          .then(async (response) => {
            if (!response.ok) {
              const error = await response.json().catch(() => ({ detail: "Upload failed" }))
              throw new Error(error.detail || "Upload failed")
            }
            return response.json()
          })
          .then((result) => {
            setUploadProgress((prev) => ({
              ...prev,
              [file.name]: 100,
            }))
            setUploadedFiles((prev) => ({
              ...prev,
              [file.name]: result,
            }))
            onUploadComplete?.(result)
            return result
          })
          .catch((error) => {
            setUploadProgress((prev) => ({
              ...prev,
              [file.name]: -1, // Error state
            }))
            throw error
          })
      })

      await Promise.all(uploadPromises)
      showSuccessToast(`Successfully uploaded ${files.length} file(s)`)
      
      // Clear files after successful upload
      setFiles([])
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Upload failed"
      showErrorToast(errorMessage)
      onUploadError?.(errorMessage)
    } finally {
      setUploading(false)
    }
  }, [files, bucket, folderPath, onUploadComplete, onUploadError, showSuccessToast, showErrorToast])

  const handleRemoveFile = useCallback(
    (fileName: string) => {
      setFiles((prev) => prev.filter((f) => f.name !== fileName))
      setUploadProgress((prev) => {
        const newProgress = { ...prev }
        delete newProgress[fileName]
        return newProgress
      })
      setUploadedFiles((prev) => {
        const newUploaded = { ...prev }
        delete newUploaded[fileName]
        return newUploaded
      })
    },
    []
  )

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B"
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB"
    return (bytes / (1024 * 1024)).toFixed(2) + " MB"
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center gap-4">
        <Label htmlFor="file-upload" className="cursor-pointer">
          <div className="flex items-center gap-2 px-4 py-2 border rounded-md hover:bg-accent transition-colors">
            <Upload className="h-4 w-4" />
            <span>Select Files</span>
          </div>
        </Label>
        <Input
          id="file-upload"
          type="file"
          className="hidden"
          onChange={handleFileSelect}
          accept={accept}
          multiple={multiple}
        />
        {files.length > 0 && (
          <Button onClick={handleUpload} disabled={uploading}>
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Upload {files.length} file(s)
              </>
            )}
          </Button>
        )}
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file) => {
            const progress = uploadProgress[file.name]
            const uploaded = uploadedFiles[file.name]
            const hasError = progress === -1

            return (
              <div
                key={file.name}
                className="flex items-center gap-4 p-3 border rounded-md bg-background"
              >
                <FileText className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(file.size)}
                  </p>
                  {progress !== undefined && progress >= 0 && progress < 100 && (
                    <div className="mt-2 w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  )}
                  {uploaded && (
                    <div className="flex items-center gap-2 mt-2 text-xs text-green-600">
                      <CheckCircle2 className="h-3 w-3" />
                      <span>Uploaded successfully</span>
                    </div>
                  )}
                  {hasError && (
                    <div className="flex items-center gap-2 mt-2 text-xs text-red-600">
                      <AlertCircle className="h-3 w-3" />
                      <span>Upload failed</span>
                    </div>
                  )}
                </div>
                {!uploading && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveFile(file.name)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

