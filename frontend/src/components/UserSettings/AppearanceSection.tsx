import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Monitor, Moon, Palette, Sun } from "lucide-react"
import { useEffect, useState } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
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

// Theme hook - simple implementation
const useTheme = () => {
  const [theme, setThemeState] = useState<"light" | "dark" | "system">("system")

  useEffect(() => {
    // Initialize theme from localStorage or system preference
    const savedTheme = localStorage.getItem("theme") as
      | "light"
      | "dark"
      | "system"
      | null
    if (savedTheme) {
      setThemeState(savedTheme)
    }
  }, [])

  const setTheme = (newTheme: "light" | "dark" | "system") => {
    setThemeState(newTheme)
    localStorage.setItem("theme", newTheme)
    // Apply theme to document
    if (newTheme === "system") {
      const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)",
      ).matches
      document.documentElement.classList.toggle("dark", prefersDark)
    } else {
      document.documentElement.classList.toggle("dark", newTheme === "dark")
    }
  }

  return { theme, setTheme }
}

export function AppearanceSection() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const { theme, setTheme } = useTheme()

  const { data: preferences, isLoading } = useQuery({
    queryKey: ["user-preferences"],
    queryFn: () => apiClient.users.getPreferences(),
  })

  const updatePreferencesMutation = useMutation({
    mutationFn: async (data: any) => {
      return apiClient.users.updatePreferences(data)
    },
    onSuccess: () => {
      showSuccessToast("Appearance preferences updated")
      queryClient.invalidateQueries({ queryKey: ["user-preferences"] })
    },
    onError: (error: any) => {
      showErrorToast("Failed to update preferences", error.message)
    },
  })

  const handleThemeChange = (newTheme: string) => {
    setTheme(newTheme as "light" | "dark" | "system")
    updatePreferencesMutation.mutate({ theme: newTheme })
  }

  const handleSelectChange = (key: string, value: string) => {
    updatePreferencesMutation.mutate({ [key]: value })
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Appearance</h2>
        <p className="text-muted-foreground">
          Customize the look and feel of the application
        </p>
      </div>

      {/* Theme */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            Theme
          </CardTitle>
          <CardDescription>Choose your preferred color scheme</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Theme</Label>
            <Select
              value={preferences?.theme ?? theme ?? "system"}
              onValueChange={handleThemeChange}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">
                  <div className="flex items-center gap-2">
                    <Sun className="h-4 w-4" />
                    Light
                  </div>
                </SelectItem>
                <SelectItem value="dark">
                  <div className="flex items-center gap-2">
                    <Moon className="h-4 w-4" />
                    Dark
                  </div>
                </SelectItem>
                <SelectItem value="system">
                  <div className="flex items-center gap-2">
                    <Monitor className="h-4 w-4" />
                    System
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              Choose between light, dark, or system theme
            </p>
          </div>
        </CardContent>
      </Card>

      {/* UI Density */}
      <Card>
        <CardHeader>
          <CardTitle>UI Density</CardTitle>
          <CardDescription>
            Adjust the spacing and size of UI elements
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Density</Label>
            <Select
              value={preferences?.ui_density ?? "comfortable"}
              onValueChange={(value) => handleSelectChange("ui_density", value)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="compact">Compact</SelectItem>
                <SelectItem value="comfortable">Comfortable</SelectItem>
                <SelectItem value="spacious">Spacious</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              Choose how compact or spacious the interface should be
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
