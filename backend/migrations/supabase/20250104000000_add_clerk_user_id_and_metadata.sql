-- Migration: add_clerk_user_id_and_metadata
-- Revision ID: 20250104000000
-- Revises: 20250102000000
-- Create Date: 2025-01-04 00:00:00.000000

-- Add clerk_user_id column to user table
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS clerk_user_id VARCHAR(255);

-- Add index on clerk_user_id for faster lookups (unique)
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_clerk_user_id ON "user"(clerk_user_id);

-- Add phone_number column
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS phone_number VARCHAR(50);

-- Add email_verified column
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT false;

-- Add clerk_metadata column (JSONB for storing additional Clerk metadata)
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS clerk_metadata JSONB DEFAULT '{}';

-- Create index on email_verified for filtering
CREATE INDEX IF NOT EXISTS ix_user_email_verified ON "user"(email_verified);

-- Update Alembic version tracking
-- Note: This will be done separately after verifying the migration succeeded
