/**
 * Hook for subscribing to real-time user updates via Supabase Realtime
 */

import { useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useAuth } from "@/hooks/useAuth"
import { supabase } from "@/lib/supabase"

interface UserUpdateEvent {
  user_id: string
  event_type: "created" | "updated" | "deleted"
  data: {
    email?: string
    full_name?: string | null
    clerk_user_id?: string | null
    phone_number?: string | null
    email_verified?: boolean
    is_active?: boolean
    updated_fields?: string[]
  }
}

export function useUserRealtime() {
  const queryClient = useQueryClient()
  const { user } = useAuth()

  useEffect(() => {
    if (!user?.id) {
      return
    }

    // Subscribe to user updates channel
    const channel = supabase
      .channel(`user_updates:${user.id}`)
      .on(
        "broadcast",
        { event: "user_created" },
        (payload: { payload: UserUpdateEvent }) => {
          console.log("[Realtime] User created:", payload.payload)
          // Invalidate user queries to refetch
          queryClient.invalidateQueries({ queryKey: ["user", user.id] })
          queryClient.invalidateQueries({ queryKey: ["currentUser"] })
        },
      )
      .on(
        "broadcast",
        { event: "user_updated" },
        (payload: { payload: UserUpdateEvent }) => {
          console.log("[Realtime] User updated:", payload.payload)
          // Invalidate user queries to refetch
          queryClient.invalidateQueries({ queryKey: ["user", user.id] })
          queryClient.invalidateQueries({ queryKey: ["currentUser"] })

          // Update cached user data if available
          const updateData = payload.payload.data
          queryClient.setQueryData(["user", user.id], (old: any) => {
            if (old) {
              return { ...old, ...updateData }
            }
            return old
          })
        },
      )
      .on(
        "broadcast",
        { event: "user_deleted" },
        (payload: { payload: UserUpdateEvent }) => {
          console.log("[Realtime] User deleted:", payload.payload)
          // Invalidate all user queries
          queryClient.invalidateQueries({ queryKey: ["user"] })
          queryClient.invalidateQueries({ queryKey: ["currentUser"] })
        },
      )
      .subscribe((status) => {
        console.log("[Realtime] Subscription status:", status)
      })

    return () => {
      // Cleanup: unsubscribe when component unmounts
      supabase.removeChannel(channel)
    }
  }, [user?.id, queryClient])
}
