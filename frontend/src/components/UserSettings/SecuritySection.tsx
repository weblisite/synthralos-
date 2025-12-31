import { useQuery } from "@tanstack/react-query"
import { formatDistanceToNow } from "date-fns"
import { History, Shield } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { apiClient } from "@/lib/apiClient"
import type { LoginHistory } from "@/types/api"

export function SecuritySection() {
  // NOTE: MFA, Sessions, and Account Management are now handled by Clerk's UserProfile
  // This section only shows platform-specific security features:
  // - Login history (from our backend tracking)
  // - Platform-specific security settings

  // Fetch login history (from our backend tracking)
  const { data: loginHistory = [], isLoading: historyLoading } = useQuery<
    LoginHistory[]
  >({
    queryKey: ["user-login-history"],
    queryFn: () => apiClient.users.getLoginHistory(),
  })

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Security</h2>
        <p className="text-muted-foreground">
          Manage your account security settings. For password, MFA, and session
          management, visit the{" "}
          <a
            href="/settings/profile"
            className="text-primary underline hover:text-primary/80"
          >
            Profile
          </a>{" "}
          page.
        </p>
      </div>

      {/* Login History - Platform-specific */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Login History
          </CardTitle>
          <CardDescription>
            View your account login history from our platform
          </CardDescription>
        </CardHeader>
        <CardContent>
          {historyLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading login history...
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
                  <TableHead>IP Address</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Device</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loginHistory.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>
                      {formatDistanceToNow(new Date(entry.created_at), {
                        addSuffix: true,
                      })}
                    </TableCell>
                    <TableCell>{entry.ip_address || "N/A"}</TableCell>
                    <TableCell>{entry.location || "N/A"}</TableCell>
                    <TableCell>{entry.user_agent || "N/A"}</TableCell>
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

      {/* Platform Security Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Platform Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-sm text-muted-foreground">
            <p>
              <strong>Account Security:</strong> Managed by Clerk. Visit the{" "}
              <a
                href="/settings/profile"
                className="text-primary underline hover:text-primary/80"
              >
                Profile
              </a>{" "}
              page to:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Change your password</li>
              <li>Set up multi-factor authentication (MFA)</li>
              <li>Manage active sessions</li>
              <li>Connect social accounts</li>
              <li>Verify email and phone</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
