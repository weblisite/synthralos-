import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { formatDistanceToNow } from "date-fns"
import { Clock, LogOut, Shield, Smartphone, Trash2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

export function SecuritySection() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  // Fetch preferences for 2FA status
  const { data: preferences } = useQuery({
    queryKey: ["user-preferences"],
    queryFn: () => apiClient.users.getPreferences(),
  })

  // Fetch sessions
  const { data: sessions = [], isLoading: sessionsLoading } = useQuery({
    queryKey: ["user-sessions"],
    queryFn: () => apiClient.users.getSessions(),
  })

  // Fetch login history
  const { data: loginHistory = [], isLoading: historyLoading } = useQuery({
    queryKey: ["user-login-history"],
    queryFn: () => apiClient.users.getLoginHistory(),
  })

  const toggle2FAMutation = useMutation({
    mutationFn: async (enabled: boolean) => {
      // TODO: Implement 2FA enable/disable logic
      return apiClient.users.updatePreferences({
        two_factor_enabled: enabled,
      })
    },
    onSuccess: () => {
      showSuccessToast("2FA settings updated")
      queryClient.invalidateQueries({ queryKey: ["user-preferences"] })
    },
    onError: (error: any) => {
      showErrorToast("Failed to update 2FA", error.message)
    },
  })

  const revokeSessionMutation = useMutation({
    mutationFn: async (sessionId: string) => {
      return apiClient.users.revokeSession(sessionId)
    },
    onSuccess: () => {
      showSuccessToast("Session revoked")
      queryClient.invalidateQueries({ queryKey: ["user-sessions"] })
    },
    onError: (error: any) => {
      showErrorToast("Failed to revoke session", error.message)
    },
  })

  const revokeAllSessionsMutation = useMutation({
    mutationFn: async () => {
      return apiClient.users.revokeAllSessions()
    },
    onSuccess: () => {
      showSuccessToast("All sessions revoked")
      queryClient.invalidateQueries({ queryKey: ["user-sessions"] })
    },
    onError: (error: any) => {
      showErrorToast("Failed to revoke sessions", error.message)
    },
  })

  const handleRevokeAll = () => {
    if (
      !confirm(
        "Are you sure you want to revoke all sessions? You will be logged out from all devices.",
      )
    ) {
      return
    }
    revokeAllSessionsMutation.mutate()
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Security</h2>
        <p className="text-muted-foreground">
          Manage your account security settings
        </p>
      </div>

      {/* Two-Factor Authentication */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Two-Factor Authentication
          </CardTitle>
          <CardDescription>
            Add an extra layer of security to your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <p className="font-medium">Enable 2FA</p>
                {preferences?.two_factor_enabled && (
                  <Badge variant="default">Active</Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground">
                Require a verification code in addition to your password
              </p>
            </div>
            <Switch
              checked={preferences?.two_factor_enabled ?? false}
              onCheckedChange={(checked) => toggle2FAMutation.mutate(checked)}
              disabled={toggle2FAMutation.isPending}
            />
          </div>
          {preferences?.two_factor_enabled && (
            <div className="mt-4 space-y-2">
              <p className="text-sm text-muted-foreground">
                Two-factor authentication is enabled. You'll need to enter a
                verification code when signing in.
              </p>
              <Button variant="outline" size="sm">
                View Recovery Codes
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Active Sessions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Smartphone className="h-5 w-5" />
            Active Sessions
          </CardTitle>
          <CardDescription>
            Manage your active sessions across devices
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sessionsLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading sessions...
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No active sessions
            </div>
          ) : (
            <div className="space-y-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Device</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>IP Address</TableHead>
                    <TableHead>Last Active</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sessions.map((session: any) => (
                    <TableRow key={session.id}>
                      <TableCell className="font-medium">
                        {session.device_info || "Unknown Device"}
                      </TableCell>
                      <TableCell>{session.location || "Unknown"}</TableCell>
                      <TableCell className="font-mono text-sm">
                        {session.ip_address || "N/A"}
                      </TableCell>
                      <TableCell>
                        {formatDistanceToNow(new Date(session.last_active_at), {
                          addSuffix: true,
                        })}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            revokeSessionMutation.mutate(session.id)
                          }
                          disabled={revokeSessionMutation.isPending}
                        >
                          <LogOut className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="flex justify-end">
                <Button
                  variant="outline"
                  onClick={handleRevokeAll}
                  disabled={revokeAllSessionsMutation.isPending}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Revoke All Sessions
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Login History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Login History
          </CardTitle>
          <CardDescription>Recent login attempts and activity</CardDescription>
        </CardHeader>
        <CardContent>
          {historyLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading history...
            </div>
          ) : loginHistory.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No login history available
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loginHistory.map((entry: any) => (
                  <TableRow key={entry.id}>
                    <TableCell>
                      {new Date(entry.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>{entry.location || "Unknown"}</TableCell>
                    <TableCell className="font-mono text-sm">
                      {entry.ip_address}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={entry.success ? "default" : "destructive"}
                      >
                        {entry.success ? "Success" : "Failed"}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
