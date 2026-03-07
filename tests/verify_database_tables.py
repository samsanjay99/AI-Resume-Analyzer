"""
Verify database tables and create analysis storage schema
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def verify_and_create_tables():
    """Verify existing tables and create analysis storage tables"""
    
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        print("✅ Connected successfully!")
        
        # Check existing tables
        print("\nChecking existing tables...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f"\nFound {len(tables)} existing tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if users table exists
        table_names = [t[0] for t in tables]
        if 'users' not in table_names:
            print("\n⚠️ WARNING: 'users' table does not exist!")
            print("Creating 'users' table first...")
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            conn.commit()
            print("✅ 'users' table created")
        
        # Create resumes table
        print("\nCreating 'resumes' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                file_name TEXT NOT NULL,
                file_url TEXT,
                file_type TEXT,
                parsed_text TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                detected_job_role TEXT,
                analysis_status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ 'resumes' table created")
        
        # Create indexes
        print("\nCreating indexes on 'resumes'...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_resumes_user_id 
            ON resumes(user_id)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_resumes_upload_date 
            ON resumes(upload_date DESC)
        """)
        conn.commit()
        print("✅ Indexes created")
        
        # Create resume_analyses table
        print("\nCreating 'resume_analyses' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resume_analyses (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
                detected_skills JSONB,
                experience_years INTEGER,
                education_detected TEXT,
                projects_detected JSONB,
                certifications_detected JSONB,
                resume_score INTEGER,
                analysis_summary TEXT,
                ai_feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ 'resume_analyses' table created")
        
        # Create indexes
        print("\nCreating indexes on 'resume_analyses'...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_resume_analyses_user_id 
            ON resume_analyses(user_id)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_resume_analyses_resume_id 
            ON resume_analyses(resume_id)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_resume_analyses_created_at 
            ON resume_analyses(created_at DESC)
        """)
        conn.commit()
        print("✅ Indexes created")
        
        # Verify all tables now exist
        print("\nVerifying all tables...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        all_tables = cur.fetchall()
        print(f"\nTotal tables in database: {len(all_tables)}")
        for table in all_tables:
            print(f"  ✓ {table[0]}")
        
        # Check if our new tables exist
        table_names = [t[0] for t in all_tables]
        if 'resumes' in table_names and 'resume_analyses' in table_names:
            print("\n✅ SUCCESS! Analysis storage tables created successfully!")
        else:
            print("\n❌ ERROR: Tables were not created properly")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("DATABASE SETUP COMPLETE!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    verify_and_create_tables()
