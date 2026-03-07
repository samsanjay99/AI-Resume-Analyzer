"""
Create user_profiles table in Neon PostgreSQL
Linked to users table with foreign key constraint
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def create_user_profiles_table():
    """Create user_profiles table with all required fields"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Create user_profiles table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                full_name VARCHAR(255),
                username VARCHAR(100) UNIQUE,
                profile_picture_url TEXT,
                bio TEXT,
                location VARCHAR(255),
                education TEXT,
                experience_level VARCHAR(50),
                target_job_role VARCHAR(255),
                skills JSONB DEFAULT '[]'::jsonb,
                linkedin_url TEXT,
                github_url TEXT,
                portfolio_url TEXT,
                preferred_language VARCHAR(50) DEFAULT 'English',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create index on user_id for fast lookup
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id 
            ON user_profiles(user_id)
        """)
        
        # Create index on username for fast lookup
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_profiles_username 
            ON user_profiles(username)
        """)
        
        # Create trigger to auto-update updated_at
        cur.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        cur.execute("""
            DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
        """)
        
        cur.execute("""
            CREATE TRIGGER update_user_profiles_updated_at
            BEFORE UPDATE ON user_profiles
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)
        
        conn.commit()
        print("✅ user_profiles table created successfully")
        print("✅ Indexes created on user_id and username")
        print("✅ Foreign key constraint added")
        print("✅ Auto-update trigger for updated_at created")
        
        # Check if table exists
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_profiles'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("\n📋 Table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user_profiles table: {e}")
        return False

if __name__ == "__main__":
    create_user_profiles_table()
