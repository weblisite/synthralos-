import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Camera, Upload } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { OpenAPI } from "@/client"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import type { UserPreferences } from "@/types/api"

const profileSchema = z.object({
  full_name: z.string().max(255).optional(),
  email: z.email({ message: "Invalid email address" }),
  bio: z.string().max(500).optional(),
  company: z.string().max(255).optional(),
  timezone: z.string().min(1),
  language: z.string().min(1),
})

type ProfileFormData = z.infer<typeof profileSchema>

// Common timezones
const timezones = [
  { value: "UTC", label: "UTC (Coordinated Universal Time)" },
  { value: "America/New_York", label: "Eastern Time (ET)" },
  { value: "America/Chicago", label: "Central Time (CT)" },
  { value: "America/Denver", label: "Mountain Time (MT)" },
  { value: "America/Los_Angeles", label: "Pacific Time (PT)" },
  { value: "Europe/London", label: "London (GMT)" },
  { value: "Europe/Paris", label: "Paris (CET)" },
  { value: "Asia/Tokyo", label: "Tokyo (JST)" },
  { value: "Asia/Shanghai", label: "Shanghai (CST)" },
  { value: "Australia/Sydney", label: "Sydney (AEDT)" },
]

const languages = [
  { value: "en", label: "English" },
  { value: "es", label: "Spanish" },
  { value: "fr", label: "French" },
  { value: "de", label: "German" },
  { value: "ja", label: "Japanese" },
  { value: "zh", label: "Chinese" },
]

export function ProfileSection() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { user: currentUser } = useAuth()
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)

  // Fetch preferences
  const {
    data: preferences,
    isLoading: preferencesLoading,
    error: preferencesError,
  } = useQuery<UserPreferences, Error>({
    queryKey: ["user-preferences"],
    queryFn: async (): Promise<UserPreferences> => {
      return apiClient.users.getPreferences()
    },
    retry: false, // Disable retries to prevent refresh loops
    refetchOnWindowFocus: false, // Prevent refetch on window focus
  })

  // Handle errors (React Query v5 removed onError callback)
  // Use a ref to prevent showing the same error multiple times
  const errorShownRef = useRef<string | null>(null)
  useEffect(() => {
    if (preferencesError) {
      const errorMessage =
        preferencesError instanceof Error
          ? preferencesError.message
          : "Failed to load preferences"

      // Only show error if it's different from the last one shown
      if (errorShownRef.current !== errorMessage) {
        console.error(
          "[ProfileSection] Error fetching preferences:",
          preferencesError,
        )
        errorShownRef.current = errorMessage
        showErrorToast(errorMessage, "Error loading profile")
      }
    } else {
      // Reset error ref when error is cleared
      errorShownRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preferencesError, showErrorToast])

  const form = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: currentUser?.full_name ?? "",
      email: currentUser?.email ?? "",
      bio: preferences?.bio ?? "",
      company: preferences?.company ?? "",
      timezone: preferences?.timezone ?? "UTC",
      language: preferences?.language ?? "en",
    },
  })

  // Update form when preferences load
  useEffect(() => {
    if (preferences && currentUser) {
      form.reset({
        full_name: currentUser.full_name ?? "",
        email: currentUser.email,
        bio: preferences.bio ?? "",
        company: preferences.company ?? "",
        timezone: preferences.timezone ?? "UTC",
        language: preferences.language ?? "en",
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [preferences, currentUser, form.reset])

  const updateProfileMutation = useMutation({
    mutationFn: async (data: ProfileFormData) => {
      // Update user profile
      await apiClient.users.updateMe({
        full_name: data.full_name,
        email: data.email,
      })

      // Update preferences
      await apiClient.users.updatePreferences({
        bio: data.bio,
        company: data.company,
        timezone: data.timezone,
        language: data.language,
      })
    },
    onSuccess: () => {
      showSuccessToast("Profile updated successfully")
      queryClient.invalidateQueries({ queryKey: ["user-preferences"] })
      queryClient.invalidateQueries({ queryKey: ["current-user"] })
    },
    onError: (error: any) => {
      showErrorToast(error.message, "Failed to update profile")
    },
  })

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 2 * 1024 * 1024) {
        showErrorToast("Avatar must be less than 2MB", "File too large")
        return
      }
      if (!file.type.startsWith("image/")) {
        showErrorToast("Please upload an image file", "Invalid file type")
        return
      }
      setAvatarFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleAvatarUpload = async () => {
    if (!avatarFile) return

    try {
      const formData = new FormData()
      formData.append("file", avatarFile)

      // Get Clerk token for authorization
      const token = await OpenAPI.TOKEN()

      const response = await fetch("/api/v1/users/me/avatar", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to upload avatar")
      }

      const data = await response.json()

      // Update preferences with new avatar URL
      await apiClient.users.updatePreferences({
        avatar_url: data.avatar_url,
      })

      showSuccessToast("Avatar uploaded successfully")
      queryClient.invalidateQueries({ queryKey: ["user-preferences"] })
      setAvatarFile(null)
      setAvatarPreview(null)
    } catch (error: any) {
      showErrorToast(error.message, "Failed to upload avatar")
    }
  }

  const onSubmit = (data: ProfileFormData) => {
    updateProfileMutation.mutate(data)
  }

  const getInitials = () => {
    if (currentUser?.full_name) {
      return currentUser.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    }
    return currentUser?.email?.[0].toUpperCase() ?? "U"
  }

  if (preferencesLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-muted-foreground">Loading profile...</div>
        </div>
      </div>
    )
  }

  if (preferencesError) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center space-y-2">
          <div className="text-destructive font-medium">
            Failed to load profile
          </div>
          <div className="text-sm text-muted-foreground">
            {preferencesError instanceof Error
              ? preferencesError.message
              : "An error occurred while loading your profile"}
          </div>
          <Button
            variant="outline"
            onClick={() => {
              queryClient.invalidateQueries({ queryKey: ["user-preferences"] })
            }}
            className="mt-4"
          >
            Retry
          </Button>
        </div>
      </div>
    )
  }

  if (!currentUser) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-muted-foreground">
            Please log in to view your profile
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Profile</h2>
        <p className="text-muted-foreground">
          Manage your profile information and preferences
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profile Picture</CardTitle>
          <CardDescription>
            Upload a profile picture. JPG, PNG or GIF. Max size 2MB.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-6">
            <Avatar className="h-24 w-24">
              <AvatarImage
                src={avatarPreview || preferences?.avatar_url || undefined}
              />
              <AvatarFallback className="text-2xl">
                {getInitials()}
              </AvatarFallback>
            </Avatar>
            <div className="space-y-2">
              <input
                type="file"
                accept="image/*"
                onChange={handleAvatarChange}
                className="hidden"
                id="avatar-upload"
              />
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() =>
                    document.getElementById("avatar-upload")?.click()
                  }
                >
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Photo
                </Button>
                {avatarFile && (
                  <Button
                    type="button"
                    onClick={handleAvatarUpload}
                    disabled={updateProfileMutation.isPending}
                  >
                    <Camera className="mr-2 h-4 w-4" />
                    Save
                  </Button>
                )}
              </div>
              {avatarFile && (
                <p className="text-sm text-muted-foreground">
                  {avatarFile.name} ({(avatarFile.size / 1024).toFixed(1)} KB)
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
          <CardDescription>
            Update your personal information and contact details
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="full_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Full Name</FormLabel>
                    <FormControl>
                      <Input placeholder="John Doe" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="john@example.com"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Your email address is used for account notifications and
                      login
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="bio"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Bio</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Tell us about yourself..."
                        rows={4}
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      A short bio about yourself (max 500 characters)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="company"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Company</FormLabel>
                    <FormControl>
                      <Input placeholder="Acme Inc." {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="timezone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Timezone</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        value={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select timezone" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {timezones.map((tz) => (
                            <SelectItem key={tz.value} value={tz.value}>
                              {tz.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="language"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Language</FormLabel>
                      <Select
                        onValueChange={field.onChange}
                        value={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select language" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {languages.map((lang) => (
                            <SelectItem key={lang.value} value={lang.value}>
                              {lang.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="flex justify-end">
                <LoadingButton
                  type="submit"
                  loading={updateProfileMutation.isPending}
                  disabled={!form.formState.isDirty}
                >
                  Save Changes
                </LoadingButton>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}
