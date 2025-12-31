import { UserProfile } from "@clerk/clerk-react"
import { createFileRoute } from "@tanstack/react-router"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/profile" as any)({
  component: ProfileSettings,
  head: () => ({
    meta: [
      {
        title: "Profile Settings - SynthralOS",
      },
    ],
  }),
})

function ProfileSettings() {
  return (
    <SettingsLayout currentSection="profile">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Profile</h2>
          <p className="text-muted-foreground">
            Manage your account profile, security, and connected accounts. Clerk
            handles profile picture, name, email, password, MFA, sessions, and
            social account connections.
          </p>
        </div>

        {/* Clerk's UserProfile component handles:
            - Profile picture
            - Name, email, phone
            - Password change
            - Email/phone verification
            - MFA setup (TOTP, SMS, Email codes)
            - Connected accounts (social logins)
            - Active sessions
            - Account deletion
        */}
        <UserProfile
          appearance={{
            elements: {
              rootBox: "w-full",
              card: "shadow-lg",
              navbar: "border-b",
              navbarButton: "text-sm",
              formButtonPrimary:
                "bg-primary text-primary-foreground hover:bg-primary/90",
              formButtonReset: "text-muted-foreground hover:text-foreground",
              footerActionLink: "text-primary hover:text-primary/80",
            },
          }}
          routing="path"
          path="/settings/profile"
        />
      </div>
    </SettingsLayout>
  )
}
