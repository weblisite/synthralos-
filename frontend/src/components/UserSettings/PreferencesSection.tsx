import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { RefreshCw, Settings } from "lucide-react"
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
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

export function PreferencesSection() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const { data: preferences, isLoading } = useQuery({
    queryKey: ["user-preferences"],
    queryFn: () => apiClient.users.getPreferences(),
  })

  const updatePreferencesMutation = useMutation({
    mutationFn: async (data: any) => {
      return apiClient.users.updatePreferences(data)
    },
    onSuccess: () => {
      showSuccessToast("Preferences updated")
      queryClient.invalidateQueries({ queryKey: ["user-preferences"] })
    },
    onError: (error: any) => {
      showErrorToast("Failed to update preferences", error.message)
    },
  })

  const handleToggle = (key: string, value: boolean) => {
    updatePreferencesMutation.mutate({ [key]: value })
  }

  const handleNumberChange = (key: string, value: number) => {
    updatePreferencesMutation.mutate({ [key]: value })
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Preferences</h2>
        <p className="text-muted-foreground">
          Configure default settings for workflows and executions
        </p>
      </div>

      {/* Workflow Defaults */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Workflow Defaults
          </CardTitle>
          <CardDescription>
            Set default values for new workflows
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Default Timeout (seconds)</Label>
            <Input
              type="number"
              min="1"
              value={preferences?.default_timeout ?? 300}
              onChange={(e) =>
                handleNumberChange(
                  "default_timeout",
                  parseInt(e.target.value, 10),
                )
              }
            />
            <p className="text-sm text-muted-foreground">
              Default timeout for workflow executions in seconds
            </p>
          </div>

          <div className="space-y-2">
            <Label>Auto-Save Interval (seconds)</Label>
            <Input
              type="number"
              min="1"
              value={preferences?.auto_save_interval ?? 30}
              onChange={(e) =>
                handleNumberChange(
                  "auto_save_interval",
                  parseInt(e.target.value, 10),
                )
              }
            />
            <p className="text-sm text-muted-foreground">
              How often to auto-save workflow changes
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Execution Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Execution Preferences
          </CardTitle>
          <CardDescription>
            Configure how workflows are executed
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Auto-Retry on Failure</Label>
              <p className="text-sm text-muted-foreground">
                Automatically retry failed workflow executions
              </p>
            </div>
            <Switch
              checked={preferences?.auto_retry_on_failure ?? true}
              onCheckedChange={(checked) =>
                handleToggle("auto_retry_on_failure", checked)
              }
              disabled={updatePreferencesMutation.isPending}
            />
          </div>

          <div className="space-y-2">
            <Label>Failure Notification Threshold</Label>
            <Input
              type="number"
              min="1"
              value={preferences?.failure_notification_threshold ?? 1}
              onChange={(e) =>
                handleNumberChange(
                  "failure_notification_threshold",
                  parseInt(e.target.value, 10),
                )
              }
            />
            <p className="text-sm text-muted-foreground">
              Number of failures before sending a notification
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
