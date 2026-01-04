import { SignUp } from "@clerk/clerk-react"
import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/signup")({
  component: SignUpPage,
})

function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md">
        <SignUp
          routing="virtual"
          signInUrl="/login"
          afterSignUpUrl="/"
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
