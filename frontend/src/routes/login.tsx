import { SignIn } from "@clerk/clerk-react"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

const searchSchema = z.object({
  redirect: z.string().optional(),
})

export const Route = createFileRoute("/login")({
  component: LoginPage,
  validateSearch: searchSchema,
})

function LoginPage() {
  const { redirect } = Route.useSearch()
  // Default to dashboard ("/") if no redirect parameter is provided
  const afterSignInUrl = redirect || "/"

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md">
        <SignIn
          routing="virtual"
          signUpUrl="/signup"
          afterSignInUrl={afterSignInUrl}
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-lg",
              headerTitle: "text-2xl font-bold",
              headerSubtitle: "text-muted-foreground",
              socialButtonsBlockButton: "border-border",
              formButtonPrimary:
                "bg-primary text-primary-foreground hover:bg-primary/90",
              footerActionLink: "text-primary hover:text-primary/80",
            },
          }}
        />
      </div>
    </div>
  )
}
