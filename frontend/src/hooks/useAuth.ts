import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import * as React from "react"
import { useEffect, useMemo, useRef, useState } from "react"
import type { UserPublic } from "@/client"
import { apiClient } from "@/lib/apiClient"
import { clearCsrfToken } from "@/lib/csrf"
import { supabase } from "@/lib/supabase"
import useCustomToast from "./useCustomToast"

export const isLoggedIn = async (): Promise<boolean> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()
  return !!session
}

export const useAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

  // Get current session from Supabase
  const [hasSession, setHasSession] = useState(false)
  const sessionInitializedRef = useRef(false)
  const hasEverHadSessionRef = useRef(false) // Track if we've ever had a session

  useEffect(() => {
    let mounted = true

    // Initial session check (only run if not already initialized)
    const initializeSession = async () => {
      // Skip if already initialized to prevent multiple calls
      if (sessionInitializedRef.current) {
        return
      }

      try {
        const {
          data: { session },
          error,
        } = await supabase.auth.getSession()
        console.log("[useAuth] Initial session check:", {
          hasSession: !!session,
          error: error?.message,
          userId: session?.user?.id,
        })

        if (mounted) {
          sessionInitializedRef.current = true
          // Only set hasSession to true if session exists
          // Never set to false here - preserve current state to prevent flipping
          if (session) {
            hasEverHadSessionRef.current = true
            setHasSession(true)
            queryClient.invalidateQueries({ queryKey: ["currentUser"] })
          } else if (hasEverHadSessionRef.current) {
            // If we've ever had a session, preserve true state
            // Don't flip to false unless explicitly signed out
            setHasSession(true)
          }
        }
      } catch (err) {
        console.error("[useAuth] Error getting session:", err)
        if (mounted) {
          sessionInitializedRef.current = true
          // Don't set to false on error - preserve current state
          // Only set to false on explicit SIGNED_OUT event
        }
      }
    }

    initializeSession()

    // Set up auth state change listener
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      // Skip INITIAL_SESSION if we already handled it manually
      if (event === "INITIAL_SESSION" && sessionInitializedRef.current) {
        console.log(
          "[useAuth] Skipping INITIAL_SESSION event (already handled manually)",
        )
        return
      }

      console.log("[useAuth] Auth state changed:", {
        event,
        hasSession: !!session,
        userId: session?.user?.id,
      })

      if (mounted) {
        // Always verify actual session state before making decisions
        const {
          data: { session: currentSession },
        } = await supabase.auth.getSession()
        const actuallyHasSession = !!currentSession

        // Handle explicit sign out
        if (event === "SIGNED_OUT") {
          hasEverHadSessionRef.current = false
          setHasSession(false)
          userDataRef.current = null
          queryClient.clear()

          if (
            window.location.pathname !== "/login" &&
            window.location.pathname !== "/signup"
          ) {
            window.location.href = "/login"
          }
          return
        }

        // For all other events, only update hasSession if we have a verified session
        // Never set to false except on SIGNED_OUT - this prevents flipping
        if (session || actuallyHasSession) {
          hasEverHadSessionRef.current = true
          setHasSession(true)
          // Only invalidate if we have a new session (not just a refresh)
          if (event === "SIGNED_IN" || event === "TOKEN_REFRESHED") {
            queryClient.invalidateQueries({ queryKey: ["currentUser"] })
          }
        } else if (hasEverHadSessionRef.current) {
          // If we've ever had a session, preserve true state even if current check fails
          // This prevents flipping when React remounts or navigates
          setHasSession(true)
        }
        // If no session and never had one, keep false (initial state)
      }
    })

    // Automatic session refresh to prevent freezing after inactivity
    const refreshSessionInterval = setInterval(
      async () => {
        if (!mounted) return

        try {
          const {
            data: { session },
          } = await supabase.auth.getSession()

          if (session?.expires_at) {
            // Check if session expires soon (within 5 minutes)
            const expiresAt = session.expires_at
            const now = Math.floor(Date.now() / 1000)
            const timeUntilExpiry = expiresAt - now

            // Refresh if less than 5 minutes remaining
            if (timeUntilExpiry < 300) {
              console.log("[useAuth] Refreshing session before expiration")
              await supabase.auth.refreshSession()
              queryClient.invalidateQueries({ queryKey: ["currentUser"] })
            }
          }
        } catch (error) {
          console.error("[useAuth] Error refreshing session:", error)
        }
      },
      2 * 60 * 1000,
    ) // Check every 2 minutes

    // Refresh session on visibility change (when user returns to tab)
    const handleVisibilityChange = async () => {
      if (!document.hidden && mounted) {
        try {
          const {
            data: { session },
          } = await supabase.auth.getSession()
          if (session) {
            await supabase.auth.refreshSession()
            queryClient.invalidateQueries({ queryKey: ["currentUser"] })
          }
        } catch (error) {
          console.error(
            "[useAuth] Error refreshing session on visibility change:",
            error,
          )
        }
      }
    }

    document.addEventListener("visibilitychange", handleVisibilityChange)

    return () => {
      mounted = false
      subscription.unsubscribe()
      clearInterval(refreshSessionInterval)
      document.removeEventListener("visibilitychange", handleVisibilityChange)
    }
  }, [queryClient])

  // Use a ref to persist user data across query disable/enable cycles
  const userDataRef = React.useRef<UserPublic | null>(null)

  // Fetch user from backend API
  const {
    data: user,
    isLoading,
    isFetching,
    error,
  } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: async () => {
      // Wait a bit for session to be ready (helps with race conditions)
      await new Promise((resolve) => setTimeout(resolve, 100))

      // Always verify session before making API call
      const {
        data: { session: currentSession },
      } = await supabase.auth.getSession()
      if (!currentSession?.access_token) {
        console.log(
          "[useAuth] No session or access token, returning cached data or null",
        )
        // Return cached data if available, otherwise null
        // Don't clear cached data here - it might be a temporary state flip
        return userDataRef.current
      }

      try {
        console.log("[useAuth] Fetching user data...")
        const userData = await apiClient.users.getMe()
        console.log("[useAuth] User data fetched successfully:", userData)
        // Store successful user data in ref for persistence
        if (userData) {
          userDataRef.current = userData
        }
        return userData
      } catch (error: any) {
        console.error("[useAuth] Failed to fetch user data:", error)
        console.error("[useAuth] Error details:", {
          message: error?.message,
          status: error?.status,
          body: error?.body,
        })

        // If 403, verify session before clearing
        if (error?.status === 403) {
          const {
            data: { session: verifySession },
          } = await supabase.auth.getSession()
          if (!verifySession) {
            // Only clear if session is actually gone
            userDataRef.current = null
          }
          // Otherwise keep cached data - might be a temporary API issue
          // Re-throw to trigger retry
          throw error
        }

        // Return cached data if available, otherwise null
        return userDataRef.current
      }
    },
    enabled: hasSession, // Only enable when we have a session
    // Retry logic for transient 403 errors
    retry: (failureCount, error: any) => {
      // Don't retry if it's a 403 and we've already tried 2 times
      if (error?.status === 403 && failureCount >= 2) {
        return false
      }
      // Retry up to 3 times for other errors
      return failureCount < 3
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    // Use cached ref data as initial data to prevent null returns
    initialData: () => userDataRef.current,
    // Use select to always fall back to ref if query data is null
    select: (data) => data || userDataRef.current || null,
    // Keep previous REAL data visible during refetches to prevent flickering
    // This uses the actual previous query result (real data), not mock/placeholder data
    // It ensures the User component stays visible with real data during refetches
    placeholderData: (previousData) =>
      previousData || userDataRef.current || null,
    // Keep data fresh for 5 minutes to reduce unnecessary API calls
    staleTime: 5 * 60 * 1000,
    // Keep data in cache for 10 minutes even when component unmounts
    gcTime: 10 * 60 * 1000,
    // Refetch on window focus to ensure data is up to date
    refetchOnWindowFocus: true,
    // Refetch on reconnect
    refetchOnReconnect: true,
  })

  // Update ref when user data changes (always keep it updated)
  // This ensures we always have the latest user data cached
  React.useEffect(() => {
    if (user) {
      userDataRef.current = user
    }
    // Don't clear ref when user becomes null/undefined - keep last known good value
    // Only clear on explicit logout
  }, [user])

  // Use useMemo to ensure effectiveUser always falls back to ref
  // This is critical - it ensures user data persists even when query returns null
  // Priority: 1) user (from query, if truthy), 2) userDataRef.current (persisted), 3) null
  const effectiveUser = useMemo(() => {
    // Always prefer query data if it exists and is truthy
    if (user && typeof user === "object" && Object.keys(user).length > 0) {
      return user
    }
    // Fall back to ref if query data is null/undefined/empty
    if (
      userDataRef.current &&
      typeof userDataRef.current === "object" &&
      Object.keys(userDataRef.current).length > 0
    ) {
      return userDataRef.current
    }
    return null
  }, [user]) // Only recompute when user changes, ref is stable

  // Never clear ref based on hasSession state - only clear on explicit logout
  // The ref persists user data across all state flips and navigation
  // This ensures the User component always has data when available

  // Debug logging
  useEffect(() => {
    console.log("[useAuth] User state:", {
      user,
      effectiveUser,
      isLoading,
      error,
      hasSession,
      refData: userDataRef.current,
    })
  }, [user, effectiveUser, isLoading, error, hasSession])

  const login = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) throw error
    return data
  }

  const signUp = async (email: string, password: string, fullName?: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
        },
      },
    })

    if (error) throw error
    return data
  }

  const logout = async () => {
    // Clear CSRF token on logout
    clearCsrfToken()
    await supabase.auth.signOut()
    queryClient.clear()
    // Force full page reload to ensure session is cleared and route protection works
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
    isLoading,
    isFetching,
    loginMutation,
    signUpMutation,
    logout,
    isAuthenticated: !!effectiveUser,
  }
}

// Default export for backward compatibility
export default useAuth
