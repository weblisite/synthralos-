/**
 * Unified API Client
 *
 * Provides a single interface for API calls that defaults to apiRequest()
 * but can leverage OpenAPI SDK when available for type safety.
 *
 * Strategy:
 * - Use apiRequest() as the default (flexible, works for all endpoints)
 * - Use OpenAPI SDK services when available (type-safe, better for stable endpoints)
 */

// Import OpenAPI SDK services for endpoints that have them
import {
  LoginService,
  type Message,
  type UpdatePassword,
  type UserCreate,
  type UserPublic,
  type UsersPublic,
  UsersService,
  type UserUpdate,
  type UserUpdateMe,
  UtilsService,
} from "@/client"
import type {
  ConnectorConnection,
  LoginHistory,
  Team,
  UserPreferences,
  UserSession,
} from "@/types/api"
import { apiRequest, getApiPath } from "./api"

/**
 * Unified API Client Interface
 *
 * This provides a single entry point for all API calls.
 * It defaults to apiRequest() but can use OpenAPI SDK when appropriate.
 */
export const apiClient = {
  /**
   * Users API
   * Uses OpenAPI SDK for type safety
   */
  users: {
    /**
     * Get current user
     * Uses OpenAPI SDK for type safety
     */
    getMe: async (): Promise<UserPublic> => {
      return UsersService.readUserMe()
    },

    /**
     * Get all users (admin)
     * Uses OpenAPI SDK for type safety
     */
    getAll: async (skip = 0, limit = 100): Promise<UsersPublic> => {
      return UsersService.readUsers({ skip, limit })
    },

    /**
     * Get user by ID
     * Uses OpenAPI SDK for type safety
     */
    getById: async (userId: string): Promise<UserPublic> => {
      return UsersService.readUserById({ userId })
    },

    /**
     * Create user
     * Uses OpenAPI SDK for type safety
     */
    create: async (data: UserCreate): Promise<UserPublic> => {
      return UsersService.createUser({ requestBody: data })
    },

    /**
     * Update user
     * Uses OpenAPI SDK for type safety
     */
    update: async (userId: string, data: UserUpdate): Promise<UserPublic> => {
      return UsersService.updateUser({ userId, requestBody: data })
    },

    /**
     * Update current user
     * Uses OpenAPI SDK for type safety
     */
    updateMe: async (data: UserUpdateMe): Promise<UserPublic> => {
      return UsersService.updateUserMe({ requestBody: data })
    },

    /**
     * Update password
     * Uses OpenAPI SDK for type safety
     */
    updatePassword: async (data: UpdatePassword): Promise<Message> => {
      return UsersService.updatePasswordMe({ requestBody: data })
    },

    /**
     * Delete user
     * Uses OpenAPI SDK for type safety
     */
    delete: async (userId: string): Promise<Message> => {
      return UsersService.deleteUser({ userId })
    },

    /**
     * Get user preferences
     */
    getPreferences: async (): Promise<UserPreferences> => {
      return apiRequest<UserPreferences>("/api/v1/users/me/preferences", {
        method: "GET",
      })
    },

    /**
     * Update user preferences
     */
    updatePreferences: async (
      data: Partial<UserPreferences>,
    ): Promise<UserPreferences> => {
      return apiRequest<UserPreferences>("/api/v1/users/me/preferences", {
        method: "PATCH",
        body: JSON.stringify(data),
      })
    },

    /**
     * Get user sessions
     */
    getSessions: async (limit = 50): Promise<UserSession[]> => {
      return apiRequest<UserSession[]>(
        `/api/v1/users/me/sessions?limit=${limit}`,
        {
          method: "GET",
        },
      )
    },

    /**
     * Revoke a session
     */
    revokeSession: async (sessionId: string): Promise<Message> => {
      return apiRequest<Message>(`/api/v1/users/me/sessions/${sessionId}`, {
        method: "DELETE",
      })
    },

    /**
     * Revoke all sessions except current
     */
    revokeAllSessions: async (): Promise<Message> => {
      return apiRequest<Message>("/api/v1/users/me/sessions", {
        method: "DELETE",
      })
    },

    /**
     * Get login history
     */
    getLoginHistory: async (limit = 50): Promise<LoginHistory[]> => {
      return apiRequest<LoginHistory[]>(
        `/api/v1/users/me/login-history?limit=${limit}`,
        {
          method: "GET",
        },
      )
    },

    /**
     * Track login event (called after Clerk authentication)
     */
    trackLogin: async () => {
      return apiRequest("/api/v1/users/me/track-login", {
        method: "POST",
      })
    },

    /**
     * Delete current user
     * Uses OpenAPI SDK for type safety
     */
    deleteMe: async (): Promise<Message> => {
      return UsersService.deleteUserMe()
    },
  },

  /**
   * Login/Auth API
   * Uses OpenAPI SDK for type safety
   */
  auth: {
    /**
     * Recover password
     * Uses OpenAPI SDK for type safety
     */
    recoverPassword: async (email: string): Promise<Message> => {
      return LoginService.recoverPassword({ email })
    },

    /**
     * Reset password
     * Uses OpenAPI SDK for type safety
     */
    resetPassword: async (
      token: string,
      newPassword: string,
    ): Promise<Message> => {
      return LoginService.resetPassword({
        requestBody: {
          token,
          new_password: newPassword,
        },
      })
    },
  },

  /**
   * Utils API
   * Uses OpenAPI SDK for type safety
   */
  utils: {
    /**
     * Health check
     * Uses OpenAPI SDK for type safety
     */
    healthCheck: async () => {
      return UtilsService.healthCheck()
    },

    /**
     * Test email
     * Uses OpenAPI SDK for type safety
     */
    testEmail: async (email: string): Promise<Message> => {
      return UtilsService.testEmail({ emailTo: email })
    },
  },

  /**
   * Connectors API
   */
  connectors: {
    /**
     * List user's connector connections
     */
    listConnections: async (
      connectorId?: string,
    ): Promise<{ connections: ConnectorConnection[]; total_count: number }> => {
      const url = connectorId
        ? `/api/v1/connectors/connections?connector_id=${connectorId}`
        : "/api/v1/connectors/connections"
      return apiRequest<{
        connections: ConnectorConnection[]
        total_count: number
      }>(url, { method: "GET" })
    },
  },

  /**
   * Teams API
   * Uses apiRequest for flexibility
   */
  teams: {
    /**
     * Create a new team
     */
    create: async (data: {
      name: string
      slug?: string
      description?: string
    }) => {
      return apiRequest("/teams", {
        method: "POST",
        body: JSON.stringify(data),
      })
    },

    /**
     * List all teams for current user
     */
    list: async (): Promise<Team[]> => {
      const response = await apiRequest<{ teams: Team[]; count: number }>(
        "/teams",
        { method: "GET" },
      )
      return response.teams
    },

    /**
     * Get team by ID
     */
    getById: async (teamId: string) => {
      return apiRequest(`/teams/${teamId}`, { method: "GET" })
    },

    /**
     * Update team
     */
    update: async (
      teamId: string,
      data: { name?: string; description?: string; is_active?: boolean },
    ) => {
      return apiRequest(`/teams/${teamId}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      })
    },

    /**
     * Delete team
     */
    delete: async (teamId: string) => {
      return apiRequest(`/teams/${teamId}`, { method: "DELETE" })
    },

    /**
     * List team members
     */
    listMembers: async (teamId: string) => {
      return apiRequest(`/teams/${teamId}/members`, { method: "GET" })
    },

    /**
     * Add team member
     */
    addMember: async (
      teamId: string,
      data: { user_id: string; role: string },
    ) => {
      return apiRequest(`/teams/${teamId}/members`, {
        method: "POST",
        body: JSON.stringify(data),
      })
    },

    /**
     * Remove team member
     */
    removeMember: async (teamId: string, userId: string) => {
      return apiRequest(`/teams/${teamId}/members/${userId}`, {
        method: "DELETE",
      })
    },

    /**
     * Update member role
     */
    updateMemberRole: async (teamId: string, userId: string, role: string) => {
      return apiRequest(`/teams/${teamId}/members/${userId}/role`, {
        method: "PATCH",
        body: JSON.stringify({ role }),
      })
    },

    /**
     * Create invitation
     */
    createInvitation: async (
      teamId: string,
      data: { email: string; role: string; expires_in_hours?: number },
    ) => {
      return apiRequest(`/teams/${teamId}/invitations`, {
        method: "POST",
        body: JSON.stringify(data),
      })
    },

    /**
     * List team invitations
     */
    listInvitations: async (teamId: string, includeAccepted = false) => {
      return apiRequest(
        `/teams/${teamId}/invitations?include_accepted=${includeAccepted}`,
        { method: "GET" },
      )
    },

    /**
     * Accept invitation
     */
    acceptInvitation: async (token: string) => {
      return apiRequest("/teams/invitations/accept", {
        method: "POST",
        body: JSON.stringify({ token }),
      })
    },

    /**
     * Revoke invitation
     */
    revokeInvitation: async (invitationId: string) => {
      return apiRequest(`/teams/invitations/${invitationId}`, {
        method: "DELETE",
      })
    },
  },

  /**
   * Email Templates API
   * Uses apiRequest for flexibility
   */
  emailTemplates: {
    /**
     * Create email template
     */
    create: async (data: {
      name: string
      slug?: string
      subject: string
      html_content: string
      text_content?: string
      category?: string
      variables?: Record<string, any>
    }) => {
      return apiRequest("/email-templates", {
        method: "POST",
        body: JSON.stringify(data),
      })
    },

    /**
     * List email templates
     */
    list: async (params?: {
      category?: string
      is_active?: boolean
      include_system?: boolean
    }) => {
      const queryParams = new URLSearchParams()
      if (params?.category) queryParams.append("category", params.category)
      if (params?.is_active !== undefined)
        queryParams.append("is_active", String(params.is_active))
      if (params?.include_system !== undefined)
        queryParams.append("include_system", String(params.include_system))
      const query = queryParams.toString()
      return apiRequest(`/email-templates${query ? `?${query}` : ""}`, {
        method: "GET",
      })
    },

    /**
     * Get email template by ID
     */
    getById: async (templateId: string) => {
      return apiRequest(`/email-templates/${templateId}`, { method: "GET" })
    },

    /**
     * Get email template by slug
     */
    getBySlug: async (slug: string) => {
      return apiRequest(`/email-templates/slug/${slug}`, { method: "GET" })
    },

    /**
     * Update email template
     */
    update: async (
      templateId: string,
      data: {
        name?: string
        subject?: string
        html_content?: string
        text_content?: string
        category?: string
        variables?: Record<string, any>
        is_active?: boolean
      },
    ) => {
      return apiRequest(`/email-templates/${templateId}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      })
    },

    /**
     * Delete email template
     */
    delete: async (templateId: string) => {
      return apiRequest(`/email-templates/${templateId}`, { method: "DELETE" })
    },

    /**
     * Initialize default templates
     */
    initializeDefaults: async () => {
      return apiRequest("/email-templates/initialize-defaults", {
        method: "POST",
      })
    },
  },

  /**
   * Generic API request method
   * Defaults to apiRequest() for all other endpoints
   *
   * Use this for endpoints not covered by OpenAPI SDK:
   * - Dashboard stats
   * - Agents
   * - Connectors
   * - Workflows
   * - RAG
   * - OCR
   * - Scraping
   * - Browser
   * - OSINT
   * - Code
   * - Storage
   * - Admin endpoints
   * - Chat
   */
  request: apiRequest,

  /**
   * Get API URL helper
   */
  getApiUrl: getApiPath,
}

/**
 * Re-export OpenAPI SDK services for direct use when needed
 */
export { LoginService, UsersService, UtilsService } from "@/client"
/**
 * Default export - use apiRequest() directly for flexibility
 * This is the primary method for most API calls
 */
export { apiRequest, getApiPath, getApiUrl } from "./api"
