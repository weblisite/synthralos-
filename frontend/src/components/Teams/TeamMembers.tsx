/**
 * Team Members Component
 *
 * Displays and manages team members.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Shield, User, UserMinus, UserPlus } from "lucide-react"
import { useState } from "react"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface TeamMember {
  id: string
  team_id: string
  user_id: string
  role: string
  joined_at: string
  user?: {
    id: string
    email: string
    full_name?: string
  }
}

export function TeamMembers({ teamId }: { teamId: string }) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [formData, setFormData] = useState({
    user_id: "",
    role: "member",
  })

  // Fetch members
  const { data: membersData, isLoading } = useQuery({
    queryKey: ["team-members", teamId],
    queryFn: () => apiClient.teams.listMembers(teamId),
  })

  const members = (membersData as any)?.members || []

  // Fetch all users for adding members
  const { data: usersData } = useQuery({
    queryKey: ["users"],
    queryFn: () => apiClient.users.getAll(0, 100),
    enabled: isAddDialogOpen,
  })

  const users = (usersData as any)?.data || []

  // Add member mutation
  const addMemberMutation = useMutation({
    mutationFn: (data: any) => apiClient.teams.addMember(teamId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members", teamId] })
      setIsAddDialogOpen(false)
      setFormData({ user_id: "", role: "member" })
      showSuccessToast(
        "Member added",
        "Team member has been added successfully",
      )
    },
    onError: (error: any) => {
      showErrorToast("Failed to add member", error.message || "Unknown error")
    },
  })

  // Remove member mutation
  const removeMemberMutation = useMutation({
    mutationFn: (userId: string) =>
      apiClient.teams.removeMember(teamId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members", teamId] })
      showSuccessToast(
        "Member removed",
        "Team member has been removed successfully",
      )
    },
    onError: (error: any) => {
      showErrorToast(
        "Failed to remove member",
        error.message || "Unknown error",
      )
    },
  })

  // Update role mutation
  const updateRoleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: string }) =>
      apiClient.teams.updateMemberRole(teamId, userId, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members", teamId] })
      showSuccessToast(
        "Role updated",
        "Member role has been updated successfully",
      )
    },
    onError: (error: any) => {
      showErrorToast("Failed to update role", error.message || "Unknown error")
    },
  })

  const handleAddMember = () => {
    if (!formData.user_id) {
      showErrorToast("Validation error", "Please select a user")
      return
    }
    addMemberMutation.mutate(formData)
  }

  const handleRemoveMember = (member: TeamMember) => {
    if (
      confirm(
        `Remove ${member.user?.full_name || member.user?.email || "this member"} from the team?`,
      )
    ) {
      removeMemberMutation.mutate(member.user_id)
    }
  }

  const handleRoleChange = (member: TeamMember, newRole: string) => {
    updateRoleMutation.mutate({ userId: member.user_id, role: newRole })
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "owner":
        return <Shield className="h-4 w-4" />
      default:
        return <User className="h-4 w-4" />
    }
  }

  const _getRoleColor = (role: string) => {
    switch (role) {
      case "owner":
        return "default"
      case "admin":
        return "secondary"
      default:
        return "outline"
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Members</CardTitle>
            <CardDescription>
              Manage team members and their roles
            </CardDescription>
          </div>
          <Button size="sm" onClick={() => setIsAddDialogOpen(true)}>
            <UserPlus className="h-4 w-4 mr-2" />
            Add Member
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-4 text-muted-foreground">
            Loading members...
          </div>
        ) : members.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No members yet. Add your first team member.
          </div>
        ) : (
          <div className="space-y-3">
            {members.map((member: TeamMember) => (
              <div
                key={member.id}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted">
                    {getRoleIcon(member.role)}
                  </div>
                  <div>
                    <div className="font-medium">
                      {member.user?.full_name ||
                        member.user?.email ||
                        "Unknown User"}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {member.user?.email}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Select
                    value={member.role}
                    onValueChange={(value) => handleRoleChange(member, value)}
                  >
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="owner">Owner</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="member">Member</SelectItem>
                      <SelectItem value="viewer">Viewer</SelectItem>
                    </SelectContent>
                  </Select>
                  {member.role !== "owner" && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveMember(member)}
                      className="text-destructive"
                    >
                      <UserMinus className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      {/* Add Member Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Team Member</DialogTitle>
            <DialogDescription>Add a user to this team</DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">User</label>
              <Select
                value={formData.user_id}
                onValueChange={(value) =>
                  setFormData({ ...formData, user_id: value })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a user" />
                </SelectTrigger>
                <SelectContent>
                  {users
                    .filter(
                      (user: any) =>
                        !members.some((m: TeamMember) => m.user_id === user.id),
                    )
                    .map((user: any) => (
                      <SelectItem key={user.id} value={user.id}>
                        {user.full_name || user.email} ({user.email})
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Role</label>
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
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsAddDialogOpen(false)
                setFormData({ user_id: "", role: "member" })
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAddMember}
              disabled={addMemberMutation.isPending}
            >
              {addMemberMutation.isPending ? "Adding..." : "Add Member"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
