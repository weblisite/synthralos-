/**
 * Email Template Management Component
 *
 * Allows admins to manage email templates for platform notifications.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Edit, Plus, Save, Trash2, X } from "lucide-react"
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
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface EmailTemplate {
  id: string
  name: string
  slug: string
  subject: string
  html_content: string
  text_content?: string
  category: string
  variables: Record<string, any>
  is_active: boolean
  is_system: boolean
  created_at: string
  updated_at: string
}

export function EmailTemplateManagement() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(
    null,
  )
  const [formData, setFormData] = useState({
    name: "",
    slug: "",
    subject: "",
    html_content: "",
    text_content: "",
    category: "general",
    is_active: true,
  })

  // Fetch templates
  const { data: templatesData, isLoading } = useQuery({
    queryKey: ["email-templates"],
    queryFn: () => apiClient.emailTemplates.list({ include_system: true }),
  })

  const templates = (templatesData as any)?.templates || []

  // Create template mutation
  const createMutation = useMutation({
    mutationFn: (data: any) => apiClient.emailTemplates.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["email-templates"] })
      setIsCreateDialogOpen(false)
      resetForm()
      showSuccessToast(
        "Template created",
        "Email template has been created successfully",
      )
    },
    onError: (error: any) => {
      showErrorToast(
        "Failed to create template",
        error.message || "Unknown error",
      )
    },
  })

  // Update template mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      apiClient.emailTemplates.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["email-templates"] })
      setEditingTemplate(null)
      resetForm()
      showSuccessToast(
        "Template updated",
        "Email template has been updated successfully",
      )
    },
    onError: (error: any) => {
      showErrorToast(
        "Failed to update template",
        error.message || "Unknown error",
      )
    },
  })

  // Delete template mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.emailTemplates.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["email-templates"] })
      showSuccessToast(
        "Template deleted",
        "Email template has been deleted successfully",
      )
    },
    onError: (error: any) => {
      showErrorToast(
        "Failed to delete template",
        error.message || "Unknown error",
      )
    },
  })

  // Initialize defaults mutation
  const initializeDefaultsMutation = useMutation({
    mutationFn: () => apiClient.emailTemplates.initializeDefaults(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["email-templates"] })
      showSuccessToast(
        "Defaults initialized",
        "Default email templates have been initialized",
      )
    },
    onError: (error: any) => {
      showErrorToast(
        "Failed to initialize defaults",
        error.message || "Unknown error",
      )
    },
  })

  const resetForm = () => {
    setFormData({
      name: "",
      slug: "",
      subject: "",
      html_content: "",
      text_content: "",
      category: "general",
      is_active: true,
    })
  }

  const handleCreate = () => {
    createMutation.mutate(formData)
  }

  const handleEdit = (template: EmailTemplate) => {
    setEditingTemplate(template)
    setFormData({
      name: template.name,
      slug: template.slug,
      subject: template.subject,
      html_content: template.html_content,
      text_content: template.text_content || "",
      category: template.category,
      is_active: template.is_active,
    })
    setIsCreateDialogOpen(true)
  }

  const handleUpdate = () => {
    if (!editingTemplate) return
    updateMutation.mutate({
      id: editingTemplate.id,
      data: formData,
    })
  }

  const handleDelete = (template: EmailTemplate) => {
    if (template.is_system) {
      showErrorToast("Cannot delete", "System templates cannot be deleted")
      return
    }
    if (confirm(`Are you sure you want to delete "${template.name}"?`)) {
      deleteMutation.mutate(template.id)
    }
  }

  const handleInitializeDefaults = () => {
    if (confirm("This will create default email templates. Continue?")) {
      initializeDefaultsMutation.mutate()
    }
  }

  const groupedTemplates = templates.reduce(
    (acc: any, template: EmailTemplate) => {
      const category = template.category || "general"
      if (!acc[category]) acc[category] = []
      acc[category].push(template)
      return acc
    },
    {},
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Email Templates</h2>
          <p className="text-muted-foreground">
            Manage email templates for platform notifications
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleInitializeDefaults}
            disabled={initializeDefaultsMutation.isPending}
          >
            Initialize Defaults
          </Button>
          <Button
            onClick={() => {
              resetForm()
              setEditingTemplate(null)
              setIsCreateDialogOpen(true)
            }}
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Template
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-muted-foreground">
          Loading templates...
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedTemplates).map(
            ([category, categoryTemplates]: [string, any]) => (
              <div key={category}>
                <h3 className="text-lg font-semibold mb-3 capitalize">
                  {category}
                </h3>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {categoryTemplates.map((template: EmailTemplate) => (
                    <Card key={template.id}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <CardTitle className="text-base">
                              {template.name}
                            </CardTitle>
                            <CardDescription className="mt-1">
                              {template.slug}
                            </CardDescription>
                          </div>
                          {template.is_system && (
                            <Badge variant="secondary" className="ml-2">
                              System
                            </Badge>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="text-sm">
                            <span className="font-medium">Subject:</span>{" "}
                            {template.subject}
                          </div>
                          <div className="flex items-center gap-2">
                            <Switch
                              checked={template.is_active}
                              disabled={true}
                              onCheckedChange={() => {}}
                            />
                            <span className="text-sm text-muted-foreground">
                              {template.is_active ? "Active" : "Inactive"}
                            </span>
                          </div>
                          <div className="flex gap-2 pt-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEdit(template)}
                              className="flex-1"
                            >
                              <Edit className="h-3 w-3 mr-1" />
                              Edit
                            </Button>
                            {!template.is_system && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDelete(template)}
                                className="flex-1 text-destructive"
                              >
                                <Trash2 className="h-3 w-3 mr-1" />
                                Delete
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ),
          )}
        </div>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingTemplate
                ? "Edit Email Template"
                : "Create Email Template"}
            </DialogTitle>
            <DialogDescription>
              {editingTemplate
                ? "Update the email template details"
                : "Create a new email template for platform notifications"}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="e.g., Welcome Email"
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
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="subject">Subject *</Label>
              <Input
                id="subject"
                value={formData.subject}
                onChange={(e) =>
                  setFormData({ ...formData, subject: e.target.value })
                }
                placeholder="e.g., Welcome to {{ project_name }}!"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value) =>
                    setFormData({ ...formData, category: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="general">General</SelectItem>
                    <SelectItem value="invitation">Invitation</SelectItem>
                    <SelectItem value="notification">Notification</SelectItem>
                    <SelectItem value="workflow">Workflow</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2 flex items-end">
                <div className="flex items-center gap-2">
                  <Switch
                    id="is_active"
                    checked={formData.is_active}
                    onCheckedChange={(checked) =>
                      setFormData({ ...formData, is_active: checked })
                    }
                  />
                  <Label htmlFor="is_active">Active</Label>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="html_content">HTML Content *</Label>
              <Textarea
                id="html_content"
                value={formData.html_content}
                onChange={(e) =>
                  setFormData({ ...formData, html_content: e.target.value })
                }
                placeholder="HTML email content (supports Jinja2 templates)"
                rows={12}
                className="font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground">
                Use Jinja2 syntax for variables: {`{{ variable_name }}`}
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="text_content">Text Content (Optional)</Label>
              <Textarea
                id="text_content"
                value={formData.text_content}
                onChange={(e) =>
                  setFormData({ ...formData, text_content: e.target.value })
                }
                placeholder="Plain text version (optional)"
                rows={6}
                className="font-mono text-sm"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsCreateDialogOpen(false)
                resetForm()
                setEditingTemplate(null)
              }}
            >
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button
              onClick={editingTemplate ? handleUpdate : handleCreate}
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              <Save className="h-4 w-4 mr-2" />
              {editingTemplate ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
