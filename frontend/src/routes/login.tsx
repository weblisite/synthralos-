import { SignIn } from "@clerk/clerk-react"
import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/login")({
  component: LoginPage,
})

function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md">
        <SignIn
          routing="path"
          path="/login"
          signUpUrl="/signup"
          afterSignInUrl="/"
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
