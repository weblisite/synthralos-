import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import { AgUIProvider } from "@/components/Chat/AgUIProvider"
import { Footer } from "@/components/Common/Footer"
import AppSidebar from "@/components/Sidebar/AppSidebar"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { supabase } from "@/lib/supabase"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    const {
      data: { session },
    } = await supabase.auth.getSession()
    if (!session) {
      throw redirect({
        to: "/login",
        replace: true, // Replace history entry to prevent back navigation
      })
    }
  },
})

function Layout() {
  return (
    <AgUIProvider>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-2 border-b px-4">
            <SidebarTrigger className="-ml-1 text-muted-foreground" />
          </header>
          <main className="flex-1 p-6 md:p-8">
            <div className="mx-auto max-w-7xl">
              <Outlet />
            </div>
          </main>
          <Footer />
        </SidebarInset>
      </SidebarProvider>
    </AgUIProvider>
  )
}

export default Layout
