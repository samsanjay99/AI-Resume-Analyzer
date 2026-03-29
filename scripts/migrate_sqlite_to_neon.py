"""
Simple SQLite to Neon PostgreSQL Migration Script
Migrates all data from resume_data.db to Neon PostgreSQL
"""
import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database URLs
SQLITE_DB = 'resume_data.db'
POSTGRES_URL = os.getenv('DATABASE_URL')

print("=" * 70)
print("SQLite to Neon PostgreSQL Migration")
print("=" * 70)
print()

# Step 1: Connect to both databases
print("Step 1: Connecting to databases...")
try:
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_cursor = sqlite_conn.cursor()
    print("✅ Connected to SQLite")
except Exception as e:
    print(f"❌ SQLite connection failed: {e}")
    exit(1)

try:
    pg_conn = psycopg2.connect(POSTGRES_URL)
    pg_cursor = pg_conn.cursor()
    print("✅ Connected to PostgreSQL")
except Exception as e:
    print(f"❌ PostgreSQL connection failed: {e}")
    print("Please check your DATABASE_URL in .env file")
    exit(1)

print()

# Step 2: Create PostgreSQL tables
print("Step 2: Creating PostgreSQL tables...")

tables_sql = """
-- Resume data table
CREATE TABLE IF NOT EXISTS resume_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    linkedin VARCHAR(500),
    github VARCHAR(500),
    portfolio VARCHAR(500),
    summary TEXT,
    target_role VARCHAR(255),
    target_category VARCHAR(255),
    education TEXT,
    experience TEXT,
    projects TEXT,
    skills TEXT,
    template VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume skills table
CREATE TABLE IF NOT EXISTS resume_skills (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resume_data(id) ON DELETE CASCADE,
    skill_name VARCHAR(255) NOT NULL,
    skill_category VARCHAR(100) NOT NULL,
    proficiency_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume analysis table
CREATE TABLE IF NOT EXISTS resume_analysis (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resume_data(id) ON DELETE CASCADE,
    ats_score REAL,
    keyword_match_score REAL,
    format_score REAL,
    section_score REAL,
    missing_skills TEXT,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI analysis table
CREATE TABLE IF NOT EXISTS ai_analysis (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resume_data(id) ON DELETE CASCADE,
    model_used VARCHAR(255),
    resume_score INTEGER,
    job_role VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin table
CREATE TABLE IF NOT EXISTS admin (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin logs table
CREATE TABLE IF NOT EXISTS admin_logs (
    id SERIAL PRIMARY KEY,
    admin_email VARCHAR(255) NOT NULL,
    action VARCHAR(500) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    rating INTEGER,
    usability_score INTEGER,
    feature_satisfaction INTEGER,
    missing_features TEXT,
    improvement_suggestions TEXT,
    user_experience TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Uploaded files table
CREATE TABLE IF NOT EXISTS uploaded_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    original_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    upload_source VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_resume_email ON resume_data(email);
CREATE INDEX IF NOT EXISTS idx_resume_created ON resume_data(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_resume ON resume_analysis(resume_id);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_resume ON ai_analysis(resume_id);
"""

try:
    pg_cursor.execute(tables_sql)
    pg_conn.commit()
    print("✅ PostgreSQL tables created")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    exit(1)

print()

# Step 3: Migrate data
print("Step 3: Migrating data...")

# Get list of tables to migrate
tables_to_migrate = [
    'resume_data',
    'resume_skills',
    'resume_analysis',
    'ai_analysis',
    'admin',
    'admin_logs',
    'feedback',
    'uploaded_files'
]

total_migrated = 0

for table in tables_to_migrate:
    try:
        # Check if table exists in SQLite
        sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not sqlite_cursor.fetchone():
            print(f"  ⏭️  {table}: Table doesn't exist in SQLite, skipping")
            continue
        
        # Get all data from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"  ⏭️  {table}: No data to migrate")
            continue
        
        # Get column names
        sqlite_cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in sqlite_cursor.fetchall() if col[1] != 'id']  # Exclude id (auto-increment)
        
        # Insert into PostgreSQL
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        insert_sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        
        migrated_count = 0
        for row in rows:
            try:
                # Skip the id column (first column)
                data = row[1:]
                pg_cursor.execute(insert_sql, data)
                migrated_count += 1
            except Exception as e:
                print(f"    ⚠️  Error migrating row: {e}")
        
        pg_conn.commit()
        total_migrated += migrated_count
        print(f"  ✅ {table}: Migrated {migrated_count} records")
        
    except Exception as e:
        print(f"  ❌ {table}: Migration failed - {e}")

print()
print("=" * 70)
print(f"✅ Migration Complete!")
print(f"Total records migrated: {total_migrated}")
print("=" * 70)
print()
print("Next steps:")
print("1. Your data is now in Neon PostgreSQL")
print("2. The app will automatically use PostgreSQL")
print("3. Your SQLite database is backed up as 'resume_data.db'")
print()

# Close connections
sqlite_conn.close()
pg_conn.close()
