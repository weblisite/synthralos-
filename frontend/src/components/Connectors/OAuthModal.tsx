/**
 * OAuth Modal Component
 *
 * Handles OAuth flow for connector authentication.
 */

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"
import { supabase } from "@/lib/supabase"

interface OAuthModalProps {
  connectorSlug: string
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export function OAuthModal({
  connectorSlug,
  isOpen,
  onClose,
  onSuccess: _onSuccess,
}: OAuthModalProps) {
  const [authUrl, setAuthUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { showErrorToast } = useCustomToast()

  useEffect(() => {
    if (isOpen && connectorSlug) {
      fetchAuthUrl()
    }
  }, [isOpen, connectorSlug])

  const fetchAuthUrl = async () => {
    setIsLoading(true)
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        showErrorToast("You must be logged in to authorize connectors")
        return
      }

      const response = await fetch(
        `/api/v1/connectors/${connectorSlug}/authorize`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({
            redirect_uri: window.location.origin + "/connectors/oauth/callback",
            scopes: null,
          }),
        },
      )

      if (!response.ok) {
        throw new Error("Failed to get OAuth authorization URL")
      }

      const data = await response.json()
      setAuthUrl(data.authorization_url)
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to start OAuth flow",
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleAuthorize = () => {
    if (authUrl) {
      // Open OAuth flow in popup or redirect
      window.location.href = authUrl
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Authorize {connectorSlug}</DialogTitle>
          <DialogDescription>
            Connect your {connectorSlug} account to use this connector in your
            workflows
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {isLoading ? (
            <div className="text-center py-4">Loading authorization URL...</div>
          ) : authUrl ? (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Click the button below to authorize this connector. You will be
                redirected to {connectorSlug} to complete the authorization.
              </p>
              <Button onClick={handleAuthorize} className="w-full">
                Authorize {connectorSlug}
              </Button>
            </div>
          ) : (
            <div className="text-center py-4 text-muted-foreground">
              Failed to load authorization URL
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

