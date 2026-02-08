-- Migration: 002_conversation_tables.sql
-- Phase III: Add conversation history tables for AI Chatbot
-- 
-- This migration adds tables for storing chat conversations and messages.
-- Part of the stateless architecture - all history persisted to DB.

BEGIN;

-- ============================================================================
-- CONVERSATIONS TABLE
-- Stores chat sessions for each user
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to users table (from Phase II)
    CONSTRAINT fk_conversations_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- Index for faster user conversation lookups
CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
    ON conversations(user_id);

-- Index for sorting by last activity
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at 
    ON conversations(updated_at DESC);


-- ============================================================================
-- MESSAGES TABLE
-- Stores individual messages within conversations
-- ============================================================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tools_used JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to conversations table
    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE,
    
    -- Ensure role is valid
    CONSTRAINT chk_messages_role
        CHECK (role IN ('user', 'assistant', 'system'))
);

-- Index for faster message lookups by conversation
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
    ON messages(conversation_id);

-- Index for chronological ordering
CREATE INDEX IF NOT EXISTS idx_messages_created_at 
    ON messages(created_at);

-- Composite index for efficient history queries
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created 
    ON messages(conversation_id, created_at);


-- ============================================================================
-- TRIGGER: Auto-update conversation.updated_at on new message
-- ============================================================================
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing trigger if exists (for idempotency)
DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON messages;

-- Create trigger
CREATE TRIGGER trigger_update_conversation_timestamp
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_timestamp();


COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES (for manual testing)
-- ============================================================================
-- SELECT table_name FROM information_schema.tables WHERE table_name IN ('conversations', 'messages');
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'conversations';
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'messages';
