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
