import { useMutation } from "@tanstack/react-query"
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router"
import { CheckCircle2, Loader2, XCircle } from "lucide-react"
import { useEffect, useState } from "react"
import { z } from "zod"
import { AuthLayout } from "@/components/Common/AuthLayout"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import { supabase } from "@/lib/supabase"

const searchSchema = z.object({
  token: z.string().min(1, "Invitation token is required"),
})

export const Route = createFileRoute("/teams/invitations/accept")({
  component: AcceptInvitation,
  validateSearch: searchSchema,
  beforeLoad: async ({ search }) => {
    // Check if user is authenticated
    const {
      data: { session },
    } = await supabase.auth.getSession()
    if (!session) {
      // Redirect to login with return URL and token
      const redirectUrl = `/teams/invitations/accept?token=${encodeURIComponent(search.token)}`
      throw redirect({
        to: "/login",
        search: {
          redirect: redirectUrl,
        },
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Accept Team Invitation - SynthralOS",
      },
    ],
  }),
})

function AcceptInvitation() {
  const navigate = useNavigate()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { token } = Route.useSearch()
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle")
  const [errorMessage, setErrorMessage] = useState<string>("")

  // Accept invitation mutation
  const acceptMutation = useMutation({
    mutationFn: (invitationToken: string) =>
      apiClient.teams.acceptInvitation(invitationToken),
    onSuccess: (data: any) => {
      setStatus("success")
      showSuccessToast(
        "Invitation accepted",
        data.message || "You have successfully joined the team",
      )
      // Redirect to teams page after 3 seconds
      setTimeout(() => {
        navigate({ to: "/teams" })
      }, 3000)
    },
    onError: (error: any) => {
      setStatus("error")
      const message =
        error?.response?.data?.detail ||
        error?.message ||
        "Failed to accept invitation"
      setErrorMessage(message)
      showErrorToast("Failed to accept invitation", message)
    },
  })

  // Auto-accept on mount if token is present
  useEffect(() => {
    if (token && status === "idle") {
      acceptMutation.mutate(token)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, acceptMutation.mutate, status])

  return (
    <AuthLayout>
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Accept Team Invitation</CardTitle>
            <CardDescription>
              {status === "idle" && "Processing your invitation..."}
              {status === "success" && "Invitation accepted successfully!"}
              {status === "error" && "Failed to accept invitation"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {status === "idle" && (
              <div className="flex flex-col items-center justify-center py-8">
                <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
                <p className="text-muted-foreground text-center">
                  Accepting your team invitation...
                </p>
              </div>
            )}

            {status === "success" && (
              <div className="space-y-4">
                <Alert className="border-green-500 bg-green-50 dark:bg-green-950">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800 dark:text-green-200">
                    You have successfully joined the team! Redirecting to teams
                    page...
                  </AlertDescription>
                </Alert>
                <Button
                  onClick={() => navigate({ to: "/teams" })}
                  className="w-full"
                >
                  Go to Teams
                </Button>
              </div>
            )}

            {status === "error" && (
              <div className="space-y-4">
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>{errorMessage}</AlertDescription>
                </Alert>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    Possible reasons:
                  </p>
                  <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                    <li>Invitation token is invalid or expired</li>
                    <li>Invitation has already been accepted</li>
                    <li>Invitation has been revoked</li>
                    <li>Your email does not match the invitation email</li>
                    <li>You are already a member of this team</li>
                  </ul>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => navigate({ to: "/teams" })}
                    className="flex-1"
                  >
                    Go to Teams
                  </Button>
                  <Button
                    onClick={() => {
                      setStatus("idle")
                      setErrorMessage("")
                      acceptMutation.mutate(token)
                    }}
                    className="flex-1"
                  >
                    Try Again
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AuthLayout>
  )
}
