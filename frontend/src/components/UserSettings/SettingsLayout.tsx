import { Link, useLocation } from "@tanstack/react-router"
import {
  Bell,
  ChevronRight,
  Code,
  Database,
  Key,
  Lock,
  Palette,
  Settings,
  Trash2,
  User,
  Users,
} from "lucide-react"
import type { ReactNode } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"

interface SettingsSection {
  id: string
  title: string
  icon: ReactNode
  path: string
  badge?: number
}

const settingsSections: SettingsSection[] = [
  {
    id: "profile",
    title: "Profile",
    icon: <User className="h-4 w-4" />,
    path: "/settings/profile",
  },
  {
    id: "security",
    title: "Security",
    icon: <Lock className="h-4 w-4" />,
    path: "/settings/security",
  },
  {
    id: "notifications",
    title: "Notifications",
    icon: <Bell className="h-4 w-4" />,
    path: "/settings/notifications",
  },
  {
    id: "preferences",
    title: "Preferences",
    icon: <Settings className="h-4 w-4" />,
    path: "/settings/preferences",
  },
  {
    id: "appearance",
    title: "Appearance",
    icon: <Palette className="h-4 w-4" />,
    path: "/settings/appearance",
  },
  {
    id: "api-keys",
    title: "API Keys",
    icon: <Key className="h-4 w-4" />,
    path: "/settings/api-keys",
  },
  {
    id: "integrations",
    title: "Integrations",
    icon: <Database className="h-4 w-4" />,
    path: "/settings/integrations",
  },
  {
    id: "teams",
    title: "Teams",
    icon: <Users className="h-4 w-4" />,
    path: "/settings/teams",
  },
  {
    id: "data",
    title: "Data & Privacy",
    icon: <Database className="h-4 w-4" />,
    path: "/settings/data",
  },
  {
    id: "developer",
    title: "Developer",
    icon: <Code className="h-4 w-4" />,
    path: "/settings/developer",
  },
  {
    id: "danger",
    title: "Danger Zone",
    icon: <Trash2 className="h-4 w-4" />,
    path: "/settings/danger",
  },
]

interface SettingsLayoutProps {
  children: ReactNode
  currentSection?: string
}

export function SettingsLayout({
  children,
  currentSection,
}: SettingsLayoutProps) {
  const location = useLocation()

  return (
    <div className="flex h-full gap-6">
      {/* Sidebar Navigation */}
      <aside className="w-64 flex-shrink-0">
        <div className="sticky top-4">
          <div className="mb-4">
            <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Manage your account settings
            </p>
          </div>

          <ScrollArea className="h-[calc(100vh-8rem)]">
            <nav className="space-y-1">
              {settingsSections.map((section) => {
                const isActive =
                  location.pathname === section.path ||
                  (currentSection && section.id === currentSection)

                return (
                  <Link
                    key={section.id}
                    to={section.path}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-accent text-accent-foreground"
                        : "text-muted-foreground hover:bg-accent/50 hover:text-foreground",
                    )}
                  >
                    {section.icon}
                    <span className="flex-1">{section.title}</span>
                    {section.badge && (
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs">
                        {section.badge}
                      </span>
                    )}
                    <ChevronRight className="h-4 w-4 opacity-50" />
                  </Link>
                )
              })}
            </nav>
          </ScrollArea>
        </div>
      </aside>

      <Separator orientation="vertical" />

      {/* Main Content */}
      <main className="flex-1 min-w-0">
        <div className="max-w-4xl">{children}</div>
      </main>
    </div>
  )
}
