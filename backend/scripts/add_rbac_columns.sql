-- Migration script to add RBAC columns to connector table
-- Run this script against your PostgreSQL database

-- Add new columns to connector table
ALTER TABLE connector 
ADD COLUMN IF NOT EXISTS owner_id UUID REFERENCES "user"(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS is_platform BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES "user"(id) ON DELETE SET NULL;

-- Update existing connectors to be platform connectors
UPDATE connector 
SET owner_id = NULL, 
    is_platform = TRUE, 
    created_by = NULL
WHERE owner_id IS NULL;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_connector_owner_id ON connector(owner_id);
CREATE INDEX IF NOT EXISTS idx_connector_is_platform ON connector(is_platform);
CREATE INDEX IF NOT EXISTS idx_connector_created_by ON connector(created_by);

-- Add comments for documentation
COMMENT ON COLUMN connector.owner_id IS 'NULL for platform connectors, UUID for user-owned connectors';
COMMENT ON COLUMN connector.is_platform IS 'TRUE for platform connectors (available to all users), FALSE for user-specific connectors';
COMMENT ON COLUMN connector.created_by IS 'User ID who created the connector';

