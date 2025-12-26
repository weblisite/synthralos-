import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Bell, Clock, Mail } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import type { UserPreferences } from "@/types/api"

export function NotificationsSection() {
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
      showSuccessToast("Notification preferences updated")
      queryClient.invalidateQueries({ queryKey: ["user-preferences"] })
    },
    onError: (error: any) => {
      showErrorToast("Failed to update preferences", error.message)
    },
  })

  const handleToggle = (key: string, value: boolean) => {
    updatePreferencesMutation.mutate({ [key]: value })
  }

  const handleSelectChange = (key: string, value: string) => {
    updatePreferencesMutation.mutate({ [key]: value })
  }

  const handleTimeChange = (key: string, value: string) => {
    updatePreferencesMutation.mutate({ [key]: value })
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Notifications</h2>
        <p className="text-muted-foreground">
          Manage your notification preferences
        </p>
      </div>

      {/* Email Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Email Notifications
          </CardTitle>
          <CardDescription>
            Choose what email notifications you want to receive
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Workflow Events</Label>
              <p className="text-sm text-muted-foreground">
                Get notified when workflows start, complete, or fail
              </p>
            </div>
            <Switch
              checked={preferences?.email_workflow_events ?? true}
              onCheckedChange={(checked) =>
                handleToggle("email_workflow_events", checked)
              }
              disabled={updatePreferencesMutation.isPending}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>System Alerts</Label>
              <p className="text-sm text-muted-foreground">
                Important system updates and security alerts
              </p>
            </div>
            <Switch
              checked={preferences?.email_system_alerts ?? true}
              onCheckedChange={(checked) =>
                handleToggle("email_system_alerts", checked)
              }
              disabled={updatePreferencesMutation.isPending}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Team Invitations</Label>
              <p className="text-sm text-muted-foreground">
                Notifications when you're invited to teams
              </p>
            </div>
            <Switch
              checked={preferences?.email_team_invitations ?? true}
              onCheckedChange={(checked) =>
                handleToggle("email_team_invitations", checked)
              }
              disabled={updatePreferencesMutation.isPending}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Marketing Emails</Label>
              <p className="text-sm text-muted-foreground">
                Product updates, tips, and promotional content
              </p>
            </div>
            <Switch
              checked={preferences?.email_marketing ?? false}
              onCheckedChange={(checked) =>
                handleToggle("email_marketing", checked)
              }
              disabled={updatePreferencesMutation.isPending}
            />
          </div>
        </CardContent>
      </Card>

      {/* Notification Frequency */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notification Frequency
          </CardTitle>
          <CardDescription>
            Control how often you receive notifications
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Frequency</Label>
            <Select
              value={preferences?.notification_frequency ?? "realtime"}
              onValueChange={(value) =>
                handleSelectChange("notification_frequency", value)
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="realtime">Real-time</SelectItem>
                <SelectItem value="digest">Digest (hourly)</SelectItem>
                <SelectItem value="daily">Daily digest</SelectItem>
                <SelectItem value="weekly">Weekly digest</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              Choose how frequently you want to receive notifications
            </p>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>In-App Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Show notifications within the application
              </p>
            </div>
            <Switch
              checked={preferences?.in_app_notifications ?? true}
              onCheckedChange={(checked) =>
                handleToggle("in_app_notifications", checked)
              }
              disabled={updatePreferencesMutation.isPending}
            />
          </div>
        </CardContent>
      </Card>

      {/* Quiet Hours */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Quiet Hours
          </CardTitle>
          <CardDescription>
            Set times when you don't want to receive notifications
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Start Time</Label>
              <Input
                type="time"
                value={preferences?.quiet_hours_start ?? ""}
                onChange={(e) =>
                  handleTimeChange("quiet_hours_start", e.target.value)
                }
              />
            </div>
            <div className="space-y-2">
              <Label>End Time</Label>
              <Input
                type="time"
                value={preferences?.quiet_hours_end ?? ""}
                onChange={(e) =>
                  handleTimeChange("quiet_hours_end", e.target.value)
                }
              />
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            Notifications will be paused during these hours
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
