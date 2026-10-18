# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Database Schema for Mythara AI Team
Creates tables for leads, conversations, tasks, and bot performance.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

# Database connection string
# Option 1: Local PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/mythara_ai_team')

# Option 2: Heroku Postgres (uncomment after setting up Heroku)
# DATABASE_URL = os.getenv('DATABASE_URL')  # Heroku automatically sets this

SCHEMA_SQL = """
-- ============================================================================
-- LEADS TABLE (Marketing Bot)
-- ============================================================================
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    company VARCHAR(255),
    industry VARCHAR(100),
    revenue VARCHAR(50),
    score INTEGER DEFAULT 0,  -- 0-100 lead score
    status VARCHAR(50) DEFAULT 'new',  -- new, contacted, qualified, lost, closed
    source VARCHAR(100),  -- google_ads, linkedin, referral, inbound
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_industry ON leads(industry);

-- ============================================================================
-- CONVERSATIONS TABLE (Sales Bot + Sales Trainer Bot)
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    messages JSONB,  -- Array of {role: 'bot'|'prospect', content: '...', timestamp: '...'}
    outcome VARCHAR(50),  -- closed, lost, no_response, in_progress
    tactics_used TEXT[],  -- Array of tactics: ['urgency', 'competitive_pressure', etc]
    close_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversations_lead ON conversations(lead_id);
CREATE INDEX IF NOT EXISTS idx_conversations_outcome ON conversations(outcome);

-- ============================================================================
-- TASKS TABLE (Backlog Bot)
-- ============================================================================
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',  -- high, medium, low
    status VARCHAR(50) DEFAULT 'not_started',  -- not_started, in_progress, blocked, done
    task_type VARCHAR(100),  -- revenue_blocking, customer_bug, feature_request, etc
    assigned_to VARCHAR(100),  -- marketing_bot, sales_trainer_bot, herbert, etc
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);

-- ============================================================================
-- BOT PERFORMANCE TABLE (All Bots)
-- ============================================================================
CREATE TABLE IF NOT EXISTS bot_performance (
    id SERIAL PRIMARY KEY,
    bot_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2),
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bot_performance_bot ON bot_performance(bot_name);
CREATE INDEX IF NOT EXISTS idx_bot_performance_date ON bot_performance(date);

-- ============================================================================
-- CONTENT TABLE (Brand Awareness Bot)
-- ============================================================================
CREATE TABLE IF NOT EXISTS content (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50),  -- linkedin, twitter, blog
    content_type VARCHAR(50),  -- post, tweet, article
    title VARCHAR(500),
    body TEXT,
    url VARCHAR(500),
    engagement_likes INTEGER DEFAULT 0,
    engagement_comments INTEGER DEFAULT 0,
    engagement_shares INTEGER DEFAULT 0,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_content_platform ON content(platform);
CREATE INDEX IF NOT EXISTS idx_content_published ON content(published_at);

-- ============================================================================
-- CANDIDATES TABLE (HR Bot)
-- ============================================================================
CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    role VARCHAR(100),
    resume_url VARCHAR(500),
    score INTEGER DEFAULT 0,  -- 0-100 candidate score
    status VARCHAR(50) DEFAULT 'new',  -- new, screening, interview, offer, hired, rejected
    years_experience INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_candidates_score ON candidates(score DESC);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_role ON candidates(role);
"""

def create_database_schema():
    """Create all tables for Mythara AI Team."""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔨 Creating Mythara AI Team database schema...")
        
        # Execute schema SQL
        cursor.execute(SCHEMA_SQL)
        
        print("✅ Database schema created successfully!")
        print("\nTables created:")
        print("   - leads (Marketing Bot)")
        print("   - conversations (Sales Bot + Sales Trainer Bot)")
        print("   - tasks (Backlog Bot)")
        print("   - bot_performance (All Bots)")
        print("   - content (Brand Awareness Bot)")
        print("   - candidates (HR Bot)")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        print("\nTroubleshooting:")
        print("1. Is PostgreSQL installed? Download: https://www.postgresql.org/download/")
        print("2. Is PostgreSQL running? Check: pg_ctl status")
        print("3. Does database exist? Create: createdb mythara_ai_team")
        print("\nOR use Heroku Postgres:")
        print("   heroku addons:create heroku-postgresql:hobby-dev")
        print("   heroku config:get DATABASE_URL")

if __name__ == "__main__":
    create_database_schema()
