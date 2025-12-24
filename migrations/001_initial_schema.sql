-- Lambrk Compression Service Database Schema
-- Database: lambrk
-- Note: videos table is managed by Node.js backend service
-- This script only ensures the trigger function exists for video_qualities table

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- UPDATE TRIGGER FUNCTION
-- ============================================
-- This function is used by video_qualities table trigger
-- It may already exist from Node.js backend migrations
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

