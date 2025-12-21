import {
  Bot,
  Code,
  Database,
  Folder,
  Globe,
  Home,
  MessageSquare,
  Monitor,
  Plug,
  ScrollText,
  Search,
  Users,
  Workflow,
} from "lucide-react"
import * as React from "react"

import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { type Item, Main } from "./Main"
import { User } from "./User"

const baseItems: Item[] = [
  { icon: Home, title: "Dashboard", path: "/" },
  { icon: Workflow, title: "Workflows", path: "/workflows" },
  { icon: Plug, title: "Connectors", path: "/connectors" },
  { icon: Bot, title: "Agents", path: "/agents" },
  { icon: Database, title: "RAG", path: "/rag" },
  { icon: ScrollText, title: "OCR", path: "/ocr" },
  { icon: Globe, title: "Scraping", path: "/scraping" },
  { icon: Monitor, title: "Browser", path: "/browser" },
  { icon: Search, title: "Social Monitoring", path: "/social-monitoring" },
  { icon: Code, title: "Code", path: "/code" },
  { icon: Folder, title: "Storage", path: "/storage" },
  { icon: MessageSquare, title: "Chat", path: "/chat" },
]

export function AppSidebar() {
  const { user: currentUser, isLoading: isUserLoading } = useAuth()

  // Debug logging
  React.useEffect(() => {
    console.log("[AppSidebar] Current user:", currentUser)
    console.log("[AppSidebar] User is null/undefined:", !currentUser)
    console.log("[AppSidebar] Is user loading:", isUserLoading)
  }, [currentUser, isUserLoading])

  const items = currentUser?.is_superuser
    ? [...baseItems, { icon: Users, title: "Admin", path: "/admin" }]
    : baseItems

  // Always render User component - it will handle null/undefined internally
  // React Query keeps previous data visible during refetches by default
  // This ensures the component stays visible across all pages and during refetches
  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent>
        <Main items={items} />
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
