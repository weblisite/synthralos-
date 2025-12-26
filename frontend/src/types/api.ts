/**
 * API Response Types
 * Types for API responses that aren't in the OpenAPI SDK
 */

export interface UserPreferences {
  id: string
  user_id: string
  theme: string
  ui_density: string
  timezone: string
  language: string
  date_format: string
  time_format: string
  bio?: string | null
  company?: string | null
  avatar_url?: string | null
  email_workflow_events: boolean
  email_system_alerts: boolean
  email_team_invitations: boolean
  email_marketing: boolean
  notification_frequency: string
  quiet_hours_start?: string | null
  quiet_hours_end?: string | null
  in_app_notifications: boolean
  default_timeout: number
  default_retry_policy: Record<string, any>
  auto_save_interval: number
  auto_retry_on_failure: boolean
  failure_notification_threshold: number
  analytics_enabled: boolean
  error_reporting_enabled: boolean
  two_factor_enabled: boolean
  two_factor_secret?: string | null
  two_factor_backup_codes: string[]
  created_at: string
  updated_at: string
}

export interface UserSession {
  id: string
  user_id: string
  session_token: string
  device_info?: string | null
  ip_address?: string | null
  user_agent?: string | null
  location?: string | null
  last_active_at: string
  created_at: string
  expires_at: string
}

export interface LoginHistory {
  id: string
  user_id: string
  ip_address: string
  user_agent: string
  location?: string | null
  success: boolean
  failure_reason?: string | null
  created_at: string
}

export interface Team {
  id: string
  name: string
  slug: string
  description?: string | null
  owner_id: string
  created_at: string
  updated_at: string
  is_active: boolean
  settings: Record<string, any>
  // Member info (when returned from user teams list)
  role?: string
  member_count?: number
  joined_at?: string
}

export interface ConnectorConnection {
  id: string
  connector_id: string
  connector_slug?: string | null
  connector_name?: string | null
  nango_connection_id: string
  status: string
  connected_at?: string | null
  disconnected_at?: string | null
  last_synced_at?: string | null
  config?: Record<string, any> | null
  error_count: number
  last_error?: string | null
}
