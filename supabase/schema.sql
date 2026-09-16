-- ==========================================================
-- ROUGHSET CHALLENGE - SUPABASE DATABASE SCHEMA
-- PostgreSQL schema for classroom educational game
-- ==========================================================

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Classroom Sessions Table
CREATE TABLE IF NOT EXISTS classroom_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(10) UNIQUE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    joining_open BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE
);

-- 2. Players Table
CREATE TABLE IF NOT EXISTS players (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    classroom_session_id UUID REFERENCES classroom_sessions(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    nickname VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Game Progress Table
CREATE TABLE IF NOT EXISTS game_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID UNIQUE REFERENCES players(id) ON DELETE CASCADE,
    current_level INTEGER DEFAULT 1,
    score INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    completed BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Level Results Table (Unique constraint prevents repeated level rewards)
CREATE TABLE IF NOT EXISTS level_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    level_number INTEGER NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    attempts INTEGER NOT NULL DEFAULT 1,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_player_level UNIQUE (player_id, level_number)
);

-- 5. Quiz Answers Table (Unique constraint prevents double question claiming)
CREATE TABLE IF NOT EXISTS quiz_answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    correct BOOLEAN NOT NULL DEFAULT FALSE,
    points INTEGER NOT NULL DEFAULT 0,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_player_question UNIQUE (player_id, question_number)
);

-- Indexes for high performance during live classroom queries
CREATE INDEX IF NOT EXISTS idx_classroom_code ON classroom_sessions(code);
CREATE INDEX IF NOT EXISTS idx_players_classroom ON players(classroom_session_id);
CREATE INDEX IF NOT EXISTS idx_progress_player ON game_progress(player_id);
CREATE INDEX IF NOT EXISTS idx_progress_score ON game_progress(score DESC);
CREATE INDEX IF NOT EXISTS idx_level_results_player ON level_results(player_id);
CREATE INDEX IF NOT EXISTS idx_quiz_player ON quiz_answers(player_id);
