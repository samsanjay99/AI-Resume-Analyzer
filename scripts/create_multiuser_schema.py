"""
Create multi-user database schema
Adds users table and user_id to all existing tables
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

print("=" * 70)
print("CREATING MULTI-USER DATABASE SCHEMA")
print("=" * 70)

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

try:
    # Step 1: Create users table
    print("\n1. Creating users table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    print("   ✅ Users table created")
    
    # Step 2: Add user_id to resume_data
    print("\n2. Adding user_id to resume_data...")
    cursor.execute("""
        ALTER TABLE resume_data 
        ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    """)
    print("   ✅ user_id added to resume_data")
    
    # Step 3: Add user_id to resume_analysis
    print("\n3. Adding user_id to resume_analysis...")
    cursor.execute("""
        ALTER TABLE resume_analysis 
        ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    """)
    print("   ✅ user_id added to resume_analysis")
    
    # Step 4: Add user_id to ai_analysis
    print("\n4. Adding user_id to ai_analysis...")
    cursor.execute("""
        ALTER TABLE ai_analysis 
        ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    """)
    print("   ✅ user_id added to ai_analysis")
    
    # Step 5: Add user_id to uploaded_files
    print("\n5. Adding user_id to uploaded_files...")
    cursor.execute("""
        ALTER TABLE uploaded_files 
        ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    """)
    print("   ✅ user_id added to uploaded_files")
    
    # Step 6: Add user_id to feedback
    print("\n6. Adding user_id to feedback...")
    cursor.execute("""
        ALTER TABLE feedback 
        ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    """)
    print("   ✅ user_id added to feedback")
    
    # Step 7: Create indexes for performance
    print("\n7. Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resume_data_user_id ON resume_data(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resume_analysis_user_id ON resume_analysis(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_analysis_user_id ON ai_analysis(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_uploaded_files_user_id ON uploaded_files(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id)")
    print("   ✅ Indexes created")
    
    # Step 8: Create a default test user for existing data
    print("\n8. Creating default test user for existing data...")
    cursor.execute("""
        INSERT INTO users (email, password_hash, full_name)
        VALUES ('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qZqK7QVVS', 'Test User')
        ON CONFLICT (email) DO NOTHING
        RETURNING id
    """)
    result = cursor.fetchone()
    if result:
        test_user_id = result[0]
        print(f"   ✅ Test user created with ID: {test_user_id}")
        
        # Update existing data to belong to test user
        print("\n9. Assigning existing data to test user...")
        cursor.execute("UPDATE resume_data SET user_id = %s WHERE user_id IS NULL", (test_user_id,))
        cursor.execute("UPDATE resume_analysis SET user_id = %s WHERE user_id IS NULL", (test_user_id,))
        cursor.execute("UPDATE ai_analysis SET user_id = %s WHERE user_id IS NULL", (test_user_id,))
        cursor.execute("UPDATE uploaded_files SET user_id = %s WHERE user_id IS NULL", (test_user_id,))
        cursor.execute("UPDATE feedback SET user_id = %s WHERE user_id IS NULL", (test_user_id,))
        print("   ✅ Existing data assigned to test user")
    else:
        print("   ℹ️  Test user already exists")
    
    conn.commit()
    
    print("\n" + "=" * 70)
    print("✅ MULTI-USER SCHEMA CREATED SUCCESSFULLY!")
    print("=" * 70)
    print("\nTest User Credentials:")
    print("  Email: test@example.com")
    print("  Password: password123")
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    conn.rollback()
    import traceback
    traceback.print_exc()
finally:
    cursor.close()
    conn.close()
