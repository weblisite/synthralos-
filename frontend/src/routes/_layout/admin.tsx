import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Suspense } from "react"

import type { UserPublic } from "@/client"
import AddUser from "@/components/Admin/AddUser"
import { AdminConnectorManagement } from "@/components/Admin/AdminConnectorManagement"
import { AdminDashboard } from "@/components/Admin/AdminDashboard"
import { columns, type UserTableData } from "@/components/Admin/columns"
import { EmailTemplateManagement } from "@/components/Admin/EmailTemplateManagement"
import { PlatformSettings } from "@/components/Admin/PlatformSettings"
import { DataTable } from "@/components/Common/DataTable"
import PendingUsers from "@/components/Pending/PendingUsers"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useAuth from "@/hooks/useAuth"
import { apiClient } from "@/lib/apiClient"

function getUsersQueryOptions() {
  return {
    queryFn: () => apiClient.users.getAll(0, 100),
    queryKey: ["users"],
  }
}

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  head: () => ({
    meta: [
      {
        title: "Admin - SynthralOS",
      },
    ],
  }),
})

function UsersTableContent() {
  const { user: currentUser } = useAuth()
  const { data: users } = useSuspenseQuery(getUsersQueryOptions())

  const tableData: UserTableData[] = users.data.map((user: UserPublic) => ({
    ...user,
    isCurrentUser: currentUser?.id === user.id,
  }))

  return <DataTable columns={columns} data={tableData} />
}

function UsersTable() {
  return (
    <Suspense fallback={<PendingUsers />}>
      <UsersTableContent />
    </Suspense>
  )
}

function Admin() {
  const { user: currentUser } = useAuth()

  // Check if user is admin
  if (!currentUser?.is_superuser) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-semibold">Access Denied</h2>
          <p className="text-muted-foreground">
            You must be an admin to access this page.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Admin Panel</h1>
        <p className="text-muted-foreground">
          Manage users, executions, retries, and monitor costs
        </p>
      </div>

      <Tabs defaultValue="dashboard" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="connectors">Connectors</TabsTrigger>
          <TabsTrigger value="email-templates">Email Templates</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-4">
          <AdminDashboard />
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold tracking-tight">Users</h2>
              <p className="text-muted-foreground">
                Manage user accounts and permissions
              </p>
            </div>
            <AddUser />
          </div>
          <UsersTable />
        </TabsContent>

        <TabsContent value="connectors" className="space-y-4">
          <AdminConnectorManagement />
        </TabsContent>

        <TabsContent value="email-templates" className="space-y-4">
          <EmailTemplateManagement />
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <PlatformSettings />
        </TabsContent>
      </Tabs>
    </div>
  )
}
