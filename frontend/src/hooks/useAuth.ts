import { useAuth as useClerkAuth, useUser } from "@clerk/clerk-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useEffect, useMemo, useRef } from "react"
import type { UserPublic } from "@/client"
import { OpenAPI } from "@/client"
import { apiClient } from "@/lib/apiClient"
import { clearCsrfToken } from "@/lib/csrf"
import useCustomToast from "./useCustomToast"

export const isLoggedIn = async (): Promise<boolean> => {
  // Clerk handles this internally via useAuth hook
  // This function is kept for backward compatibility
  return false // Will be handled by Clerk's isSignedIn
}

export const useAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

  // Clerk hooks
  const {
    isLoaded: clerkLoaded,
    isSignedIn,
    getToken,
    signOut: clerkSignOut,
  } = useClerkAuth()
  const { user: clerkUser, isLoaded: userLoaded } = useUser()

  // Set OpenAPI token getter when Clerk is ready
  useEffect(() => {
    if (clerkLoaded && isSignedIn && userLoaded) {
      OpenAPI.TOKEN = async () => {
        try {
          const token = await getToken()
          return token || ""
        } catch (error) {
          console.error("[OpenAPI.TOKEN] Error getting Clerk token:", error)
          return ""
        }
      }
    } else {
      OpenAPI.TOKEN = async () => ""
    }
  }, [clerkLoaded, isSignedIn, userLoaded, getToken])

  // Fetch user data from backend
  const {
    data: user,
    isLoading,
    isFetching,
    error,
  } = useQuery<UserPublic | null>({
    queryKey: ["currentUser"],
    queryFn: async () => {
      if (!isSignedIn || !clerkUser) {
        return null
      }

      try {
        return await apiClient.users.getMe()
      } catch (err) {
        console.error("[useAuth] Failed to fetch user data:", err)
        return null
      }
    },
    enabled: isSignedIn && !!clerkUser && clerkLoaded && userLoaded,
    retry: false,
    refetchOnWindowFocus: false,
  })

  // Track user data with ref for persistence
  const userDataRef = useRef<UserPublic | null>(null)

  useEffect(() => {
    if (user) {
      userDataRef.current = user
    }
  }, [user])

  const effectiveUser = useMemo(() => {
    if (user && typeof user === "object" && Object.keys(user).length > 0) {
      return user
    }
    if (
      userDataRef.current &&
      typeof userDataRef.current === "object" &&
      Object.keys(userDataRef.current).length > 0
    ) {
      return userDataRef.current
    }
    return null
  }, [user])

  // Debug logging
  useEffect(() => {
    console.log("[useAuth] User state:", {
      user,
      effectiveUser,
      isLoading,
      error,
      hasSession: isSignedIn,
      clerkLoaded,
    })
  }, [user, effectiveUser, isLoading, error, isSignedIn, clerkLoaded])

  const login = async (_email: string, _password: string) => {
    // Clerk handles login via SignIn component
    // This is kept for backward compatibility but won't be used
    throw new Error("Use Clerk SignIn component instead")
  }

  const signUp = async (
    _email: string,
    _password: string,
    _fullName?: string,
  ) => {
    // Clerk handles signup via SignUp component
    // This is kept for backward compatibility but won't be used
    throw new Error("Use Clerk SignUp component instead")
  }

  const logout = async () => {
    clearCsrfToken()
    // Clerk handles logout
    await clerkSignOut()
    queryClient.clear()
    window.location.href = "/login"
  }

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      login(email, password),
    onSuccess: () => {
      navigate({ to: "/" })
    },
    onError: (error: Error) => {
      showErrorToast(error.message)
    },
  })

  const signUpMutation = useMutation({
    mutationFn: ({
      email,
      password,
      full_name,
    }: {
      email: string
      password: string
      full_name?: string
    }) => signUp(email, password, full_name),
    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: (error: Error) => {
      showErrorToast(error.message)
    },
  })

  return {
    user: effectiveUser,
    isLoading: isLoading || !clerkLoaded || !userLoaded,
    isFetching,
    loginMutation,
    signUpMutation,
    logout,
    isAuthenticated: isSignedIn && !!effectiveUser,
    hasSession: isSignedIn,
  }
}

// Default export for backward compatibility
export default useAuth
