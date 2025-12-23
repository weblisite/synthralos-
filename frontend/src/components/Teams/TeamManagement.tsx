/**
 * Team Management Component
 *
 * Allows users to create and manage teams.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus, Settings, Trash2, Users } from "lucide-react"
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
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import { TeamInvitations } from "./TeamInvitations"
import { TeamMembers } from "./TeamMembers"

interface Team {
  id: string
  name: string
  slug: string
  description?: string
  owner_id: string
  created_at: string
  updated_at: string
  is_active: boolean
}

export function TeamManagement() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    slug: "",
    description: "",
  })

  // Fetch teams
  const { data: teamsData, isLoading } = useQuery({
    queryKey: ["teams"],
    queryFn: () => apiClient.teams.list(),
  })

  const teams = (teamsData as any)?.teams || []

  // Create team mutation
  const createMutation = useMutation({
    mutationFn: (data: any) => apiClient.teams.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] })
      setIsCreateDialogOpen(false)
      resetForm()
      showSuccessToast("Team created", "Team has been created successfully")
    },
    onError: (error: any) => {
      showErrorToast("Failed to create team", error.message || "Unknown error")
    },
  })

  // Delete team mutation
  const deleteMutation = useMutation({
    mutationFn: (teamId: string) => apiClient.teams.delete(teamId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams"] })
      setSelectedTeam(null)
      showSuccessToast("Team deleted", "Team has been deleted successfully")
    },
    onError: (error: any) => {
      showErrorToast("Failed to delete team", error.message || "Unknown error")
    },
  })

  const resetForm = () => {
    setFormData({
      name: "",
      slug: "",
      description: "",
    })
  }

  const handleCreate = () => {
    if (!formData.name.trim()) {
      showErrorToast("Validation error", "Team name is required")
      return
    }
    createMutation.mutate(formData)
  }

  const handleDelete = (team: Team) => {
    if (
      confirm(
        `Are you sure you want to delete "${team.name}"? This action cannot be undone.`,
      )
    ) {
      deleteMutation.mutate(team.id)
    }
  }

  if (selectedTeam) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Button
              variant="ghost"
              onClick={() => setSelectedTeam(null)}
              className="mb-2"
            >
              ← Back to Teams
            </Button>
            <h2 className="text-2xl font-bold tracking-tight">
              {selectedTeam.name}
            </h2>
            <p className="text-muted-foreground">
              {selectedTeam.description || "No description"}
            </p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <TeamMembers teamId={selectedTeam.id} />
          <TeamInvitations teamId={selectedTeam.id} />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Teams</h2>
          <p className="text-muted-foreground">
            Create and manage teams for collaboration
          </p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Team
        </Button>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-muted-foreground">
          Loading teams...
        </div>
      ) : teams.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Users className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No teams yet</h3>
            <p className="text-muted-foreground mb-4">
              Create your first team to start collaborating
            </p>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Team
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {teams.map((team: Team) => (
            <Card
              key={team.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => setSelectedTeam(team)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-base">{team.name}</CardTitle>
                    <CardDescription className="mt-1">
                      {team.slug}
                    </CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(team)
                    }}
                    className="text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {team.description || "No description"}
                </p>
                <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
                  <Settings className="h-4 w-4" />
                  <span>Click to manage</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Team Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Team</DialogTitle>
            <DialogDescription>
              Create a new team to collaborate with others
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Team Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="e.g., Engineering Team"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="slug">Slug</Label>
              <Input
                id="slug"
                value={formData.slug}
                onChange={(e) =>
                  setFormData({ ...formData, slug: e.target.value })
                }
                placeholder="auto-generated if empty"
              />
              <p className="text-xs text-muted-foreground">
                URL-friendly identifier (auto-generated from name if empty)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Optional team description"
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsCreateDialogOpen(false)
                resetForm()
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? "Creating..." : "Create Team"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
