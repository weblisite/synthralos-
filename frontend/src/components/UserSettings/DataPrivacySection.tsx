import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Database, Download, Shield, Upload } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { Switch } from "@/components/ui/switch"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import type { UserPreferences } from "@/types/api"

export function DataPrivacySection() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const { data: preferences, isLoading } = useQuery<UserPreferences>({
    queryKey: ["user-preferences"],
    queryFn: () => apiClient.users.getPreferences(),
  })

  const updatePreferencesMutation = useMutation({
    mutationFn: async (data: any) => {
      return apiClient.users.updatePreferences(data)
    },
    onSuccess: () => {
      showSuccessToast("Privacy settings updated")
      queryClient.invalidateQueries({ queryKey: ["user-preferences"] })
    },
    onError: (error: any) => {
      showErrorToast("Failed to update settings", error.message)
    },
  })

  const exportDataMutation = useMutation({
    mutationFn: async () => {
      return await apiClient.request<{
        download_url: string
        expires_at: string
        message: string
      }>("/api/v1/users/me/data/export", {
        method: "POST",
      })
    },
    onSuccess: (data) => {
      showSuccessToast(
        "Data export completed",
        "Your data export is ready for download",
      )
      // Open download URL in new tab
      if (data.download_url && data.download_url !== "#") {
        window.open(data.download_url, "_blank")
      }
    },
    onError: (error: any) => {
      showErrorToast("Failed to export data", error.message)
    },
  })

  const handleToggle = (key: string, value: boolean) => {
    updatePreferencesMutation.mutate({ [key]: value })
  }

  const handleExport = () => {
    if (
      !confirm(
        "This will generate a ZIP file with all your workflows, executions, and account data. Continue?",
      )
    ) {
      return
    }
    exportDataMutation.mutate()
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Data & Privacy</h2>
        <p className="text-muted-foreground">
          Manage your data and privacy settings
        </p>
      </div>

      {/* Data Export */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Data Export
          </CardTitle>
          <CardDescription>
            Export your workflows, executions, and account data
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Export All Data</p>
              <p className="text-sm text-muted-foreground">
                Download all your workflows, executions, and account data as a
                ZIP file
              </p>
            </div>
            <LoadingButton
              variant="outline"
              onClick={handleExport}
              loading={exportDataMutation.isPending}
            >
              <Download className="mr-2 h-4 w-4" />
              Export Data
            </LoadingButton>
          </div>
          <Alert>
            <AlertDescription>
              The export will include: workflows, workflow executions, API keys
              (masked), team memberships, and account settings. Large exports
              may take several minutes.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Data Import */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Data Import
          </CardTitle>
          <CardDescription>
            Import workflows and data from files
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Import Workflows</p>
              <p className="text-sm text-muted-foreground">
                Upload workflow files to import (JSON format)
              </p>
            </div>
            <input
              type="file"
              accept=".json"
              className="hidden"
              id="workflow-import"
              onChange={async (e) => {
                const file = e.target.files?.[0]
                if (file) {
                  try {
                    const text = await file.text()
                    const jsonData = JSON.parse(text)

                    const response = await apiClient.request<{
                      message: string
                    }>("/api/v1/users/me/data/import", {
                      method: "POST",
                      body: JSON.stringify(jsonData),
                      headers: {
                        "Content-Type": "application/json",
                      },
                    })

                    showSuccessToast("Import successful", response.message)
                    // Refresh workflows list if on workflows page
                    queryClient.invalidateQueries({ queryKey: ["workflows"] })
                  } catch (error: any) {
                    showErrorToast(
                      "Import failed",
                      error.message || "Invalid file format",
                    )
                  }
                }
              }}
            />
            <Button
              variant="outline"
              onClick={() =>
                document.getElementById("workflow-import")?.click()
              }
            >
              <Upload className="mr-2 h-4 w-4" />
              Import
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Privacy Settings
          </CardTitle>
          <CardDescription>
            Control your privacy and data sharing preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Analytics</Label>
              <p className="text-sm text-muted-foreground">
                Allow usage analytics to help improve the platform
              </p>
            </div>
            <Switch
              checked={preferences?.analytics_enabled ?? true}
              onCheckedChange={(checked) =>
                handleToggle("analytics_enabled", checked)
              }
              disabled={updatePreferencesMutation.isPending}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Error Reporting</Label>
              <p className="text-sm text-muted-foreground">
                Automatically report errors to help fix bugs
              </p>
            </div>
            <Switch
              checked={preferences?.error_reporting_enabled ?? true}
              onCheckedChange={(checked) =>
                handleToggle("error_reporting_enabled", checked)
              }
              disabled={updatePreferencesMutation.isPending}
            />
          </div>
        </CardContent>
      </Card>

      {/* Data Deletion */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Data Management
          </CardTitle>
          <CardDescription>Manage your stored data</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertDescription>
              <strong>Warning:</strong> Deleting your account will permanently
              remove all your data, workflows, and team memberships. This action
              cannot be undone.
            </AlertDescription>
          </Alert>
          <div className="mt-4">
            <p className="text-sm text-muted-foreground mb-2">
              To delete your account, visit the{" "}
              <a href="/settings/danger" className="text-primary underline">
                Danger Zone
              </a>
              .
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
