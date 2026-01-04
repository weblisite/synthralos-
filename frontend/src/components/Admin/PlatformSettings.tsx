/**
 * Platform Settings Component
 *
 * Manages platform-wide configuration and settings.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Save, Settings } from "lucide-react"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

export function PlatformSettings() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const [settings, setSettings] = useState({
    platformName: "SynthralOS",
    maintenanceMode: false,
    registrationEnabled: true,
    maxUsers: 1000,
    maxWorkflowsPerUser: 100,
    defaultExecutionTimeout: 300,
    maintenanceMessage: "",
  })

  // Fetch platform settings
  const { data: platformSettings, isLoading } = useQuery({
    queryKey: ["platformSettings"],
    queryFn: async () => {
      return await apiClient.request<Record<string, { value: any }>>(
        "/api/v1/admin/system/settings",
      )
    },
  })

  // Update settings when data loads
  useEffect(() => {
    if (platformSettings) {
      setSettings({
        platformName: platformSettings.platform_name?.value || "SynthralOS",
        maintenanceMode: platformSettings.maintenance_mode?.value || false,
        registrationEnabled:
          platformSettings.registration_enabled?.value ?? true,
        maxUsers: platformSettings.max_users?.value || 1000,
        maxWorkflowsPerUser:
          platformSettings.max_workflows_per_user?.value || 100,
        defaultExecutionTimeout:
          platformSettings.default_execution_timeout?.value || 300,
        maintenanceMessage: platformSettings.maintenance_message?.value || "",
      })
    }
  }, [platformSettings])

  // Save settings mutation
  const saveMutation = useMutation({
    mutationFn: async (settingsToSave: typeof settings) => {
      return await apiClient.request("/api/v1/admin/system/settings", {
        method: "PUT",
        body: JSON.stringify({
          platform_name: settingsToSave.platformName,
          maintenance_mode: settingsToSave.maintenanceMode,
          registration_enabled: settingsToSave.registrationEnabled,
          max_users: settingsToSave.maxUsers,
          max_workflows_per_user: settingsToSave.maxWorkflowsPerUser,
          default_execution_timeout: settingsToSave.defaultExecutionTimeout,
          maintenance_message: settingsToSave.maintenanceMessage,
        }),
      })
    },
    onSuccess: () => {
      showSuccessToast("Settings saved", "Platform settings have been updated")
      queryClient.invalidateQueries({ queryKey: ["platformSettings"] })
    },
    onError: (error: Error) => {
      showErrorToast(
        "Failed to save settings",
        error instanceof Error ? error.message : "Unknown error",
      )
    },
  })

  const handleSave = async () => {
    saveMutation.mutate(settings)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Platform Settings</h2>
        <p className="text-muted-foreground">
          Configure platform-wide settings and preferences
        </p>
      </div>

      {/* General Settings */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            <CardTitle>General Settings</CardTitle>
          </div>
          <CardDescription>Basic platform configuration</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="platformName">Platform Name</Label>
            <Input
              id="platformName"
              value={settings.platformName}
              onChange={(e) =>
                setSettings({ ...settings, platformName: e.target.value })
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="maintenanceMode">Maintenance Mode</Label>
              <p className="text-sm text-muted-foreground">
                Disable platform access for all users except admins
              </p>
            </div>
            <Switch
              id="maintenanceMode"
              checked={settings.maintenanceMode}
              onCheckedChange={(checked) =>
                setSettings({ ...settings, maintenanceMode: checked })
              }
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="registrationEnabled">User Registration</Label>
              <p className="text-sm text-muted-foreground">
                Allow new users to sign up
              </p>
            </div>
            <Switch
              id="registrationEnabled"
              checked={settings.registrationEnabled}
              onCheckedChange={(checked) =>
                setSettings({ ...settings, registrationEnabled: checked })
              }
            />
          </div>

          {settings.maintenanceMode && (
            <div className="space-y-2">
              <Label htmlFor="maintenanceMessage">Maintenance Message</Label>
              <Textarea
                id="maintenanceMessage"
                value={settings.maintenanceMessage}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    maintenanceMessage: e.target.value,
                  })
                }
                placeholder="Message to display to users during maintenance..."
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Limits & Quotas */}
      <Card>
        <CardHeader>
          <CardTitle>Limits & Quotas</CardTitle>
          <CardDescription>Resource limits and quotas</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="maxUsers">Maximum Users</Label>
              <Input
                id="maxUsers"
                type="number"
                value={settings.maxUsers}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    maxUsers: parseInt(e.target.value, 10) || 0,
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="maxWorkflowsPerUser">
                Max Workflows per User
              </Label>
              <Input
                id="maxWorkflowsPerUser"
                type="number"
                value={settings.maxWorkflowsPerUser}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    maxWorkflowsPerUser: parseInt(e.target.value, 10) || 0,
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="defaultExecutionTimeout">
                Default Execution Timeout (seconds)
              </Label>
              <Input
                id="defaultExecutionTimeout"
                type="number"
                value={settings.defaultExecutionTimeout}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    defaultExecutionTimeout: parseInt(e.target.value, 10) || 0,
                  })
                }
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          disabled={saveMutation.isPending || isLoading}
        >
          <Save className="mr-2 h-4 w-4" />
          {saveMutation.isPending ? "Saving..." : "Save Settings"}
        </Button>
      </div>

      <div className="text-xs text-muted-foreground">
        Note: Platform settings are stored in the database and affect all users.
        Changes take effect immediately.
      </div>
    </div>
  )
}
