-- Migration: Add missing columns to findings table
-- Run this on Render PostgreSQL database

ALTER TABLE findings
ADD COLUMN IF NOT EXISTS assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS resolution_notes TEXT,
ADD COLUMN IF NOT EXISTS marked_resolved_by UUID REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS status_changed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS status_changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS finding_data JSONB;

-- Add status column if it doesn't exist (should already exist)
ALTER TABLE findings
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'open' NOT NULL;

-- Create index on status for faster queries
CREATE INDEX IF NOT EXISTS idx_findings_status ON findings(status);

-- Verify columns were added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'findings'
ORDER BY ordinal_position;
