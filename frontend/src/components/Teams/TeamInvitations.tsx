/**
 * Team Invitations Component
 *
 * Manages team invitations and allows sending invites via email.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Mail, Send, X } from "lucide-react"
import { useState } from "react"
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
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface TeamInvitation {
  id: string
  team_id: string
  email: string
  token: string
  role: string
  invited_by: string
  expires_at: string
  accepted_at?: string
  revoked_at?: string
  created_at: string
}

export function TeamInvitations({ teamId }: { teamId: string }) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false)
  const [formData, setFormData] = useState({
    email: "",
    role: "member",
    expires_in_hours: 168, // 7 days
  })

  // Fetch invitations
  const { data: invitationsData, isLoading } = useQuery({
    queryKey: ["team-invitations", teamId],
    queryFn: () => apiClient.teams.listInvitations(teamId, false),
  })

  const invitations = (invitationsData as any)?.invitations || []

  // Create invitation mutation
  const createInvitationMutation = useMutation({
    mutationFn: (data: any) => apiClient.teams.createInvitation(teamId, data),
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ["team-invitations", teamId] })
      setIsInviteDialogOpen(false)
      setFormData({ email: "", role: "member", expires_in_hours: 168 })
      if (data.email_sent) {
        showSuccessToast(
          "Invitation sent",
          "Invitation email has been sent successfully",
        )
      } else {
        showSuccessToast(
          "Invitation created",
          "Invitation created but email failed to send",
        )
      }
    },
    onError: (error: any) => {
      showErrorToast(
        "Failed to send invitation",
        error.message || "Unknown error",
      )
    },
  })

  // Revoke invitation mutation
  const revokeInvitationMutation = useMutation({
    mutationFn: (invitationId: string) =>
      apiClient.teams.revokeInvitation(invitationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-invitations", teamId] })
      showSuccessToast(
        "Invitation revoked",
        "Invitation has been revoked successfully",
      )
    },
    onError: (error: any) => {
      showErrorToast(
        "Failed to revoke invitation",
        error.message || "Unknown error",
      )
    },
  })

  const handleSendInvitation = () => {
    if (!formData.email.trim()) {
      showErrorToast("Validation error", "Email is required")
      return
    }
    createInvitationMutation.mutate(formData)
  }

  const handleRevokeInvitation = (invitation: TeamInvitation) => {
    if (confirm(`Revoke invitation for ${invitation.email}?`)) {
      revokeInvitationMutation.mutate(invitation.id)
    }
  }

  const isExpired = (expiresAt: string) => {
    return new Date(expiresAt) < new Date()
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Invitations</CardTitle>
            <CardDescription>
              Send email invitations to join the team
            </CardDescription>
          </div>
          <Button size="sm" onClick={() => setIsInviteDialogOpen(true)}>
            <Send className="h-4 w-4 mr-2" />
            Send Invite
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-4 text-muted-foreground">
            Loading invitations...
          </div>
        ) : invitations.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No pending invitations. Send your first invite.
          </div>
        ) : (
          <div className="space-y-3">
            {invitations.map((invitation: TeamInvitation) => (
              <div
                key={invitation.id}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <div className="font-medium">{invitation.email}</div>
                    <Badge variant="outline">{invitation.role}</Badge>
                    {isExpired(invitation.expires_at) && (
                      <Badge variant="destructive">Expired</Badge>
                    )}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">
                    Expires: {formatDate(invitation.expires_at)}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRevokeInvitation(invitation)}
                  className="text-destructive"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      {/* Send Invitation Dialog */}
      <Dialog open={isInviteDialogOpen} onOpenChange={setIsInviteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Send Team Invitation</DialogTitle>
            <DialogDescription>
              Send an email invitation to join this team
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                placeholder="user@example.com"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Select
                value={formData.role}
                onValueChange={(value) =>
                  setFormData({ ...formData, role: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="member">Member</SelectItem>
                  <SelectItem value="viewer">Viewer</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="expires_in_hours">Expires In (hours)</Label>
              <Input
                id="expires_in_hours"
                type="number"
                value={formData.expires_in_hours}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    expires_in_hours: parseInt(e.target.value, 10) || 168,
                  })
                }
                min={1}
                max={720}
              />
              <p className="text-xs text-muted-foreground">
                Default: 168 hours (7 days)
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsInviteDialogOpen(false)
                setFormData({
                  email: "",
                  role: "member",
                  expires_in_hours: 168,
                })
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSendInvitation}
              disabled={createInvitationMutation.isPending}
            >
              <Send className="h-4 w-4 mr-2" />
              {createInvitationMutation.isPending
                ? "Sending..."
                : "Send Invitation"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
