"""
Migration: Create mock_interviews and interview_feedback tables
Run once: python scripts/create_interview_tables.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env")
    sys.exit(1)

import psycopg2

SQL = """
-- Mock interview sessions
CREATE TABLE IF NOT EXISTS mock_interviews (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_role          VARCHAR(200),
    experience_level  VARCHAR(100),
    interview_type    VARCHAR(50),
    difficulty        VARCHAR(30),
    language          VARCHAR(30) DEFAULT 'English',
    question_count    INTEGER DEFAULT 5,
    questions         JSONB DEFAULT '[]',
    status            VARCHAR(30) DEFAULT 'pending',
    created_at        TIMESTAMP DEFAULT NOW()
);

-- Interview feedback / results
CREATE TABLE IF NOT EXISTS interview_feedback (
    id                      SERIAL PRIMARY KEY,
    interview_id            INTEGER REFERENCES mock_interviews(id) ON DELETE CASCADE,
    user_id                 INTEGER REFERENCES users(id) ON DELETE CASCADE,
    transcript              JSONB DEFAULT '[]',
    total_score             INTEGER DEFAULT 0,
    category_scores         JSONB DEFAULT '{}',
    strengths               JSONB DEFAULT '[]',
    areas_for_improvement   JSONB DEFAULT '[]',
    skill_gaps_detected     JSONB DEFAULT '[]',
    speech_metrics          JSONB DEFAULT '{}',
    final_assessment        TEXT,
    hiring_recommendation   VARCHAR(50),
    improvement_plan        JSONB DEFAULT '{}',
    per_question_analysis   JSONB DEFAULT '[]',
    pdf_path                VARCHAR(500),
    created_at              TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mock_interviews_user_id ON mock_interviews(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_feedback_interview_id ON interview_feedback(interview_id);
CREATE INDEX IF NOT EXISTS idx_interview_feedback_user_id ON interview_feedback(user_id);
"""

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(SQL)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ mock_interviews and interview_feedback tables created successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
