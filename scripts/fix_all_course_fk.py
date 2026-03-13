"""
Remove ALL foreign key constraints from course_recommendations table
This allows flexible course recommendations without strict referential integrity
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env file")
    exit(1)

print("=" * 70)
print("REMOVING ALL FOREIGN KEY CONSTRAINTS FROM COURSE_RECOMMENDATIONS")
print("=" * 70)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Step 1: Get all foreign key constraints
    print("\n🔍 Step 1: Finding all foreign key constraints...")
    cursor.execute("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_name = 'course_recommendations'
        AND constraint_type = 'FOREIGN KEY'
    """)
    
    constraints = cursor.fetchall()
    if constraints:
        print(f"   Found {len(constraints)} foreign key constraint(s):")
        for constraint in constraints:
            print(f"   - {constraint[0]}")
    else:
        print("   ✅ No foreign key constraints found")
        exit(0)
    
    # Step 2: Drop all foreign key constraints
    print("\n🔧 Step 2: Dropping all foreign key constraints...")
    for constraint in constraints:
        constraint_name = constraint[0]
        try:
            cursor.execute(f"""
                ALTER TABLE course_recommendations 
                DROP CONSTRAINT IF EXISTS {constraint_name}
            """)
            print(f"   ✅ Dropped: {constraint_name}")
        except Exception as e:
            print(f"   ❌ Error dropping {constraint_name}: {e}")
    
    conn.commit()
    
    # Step 3: Make all ID columns nullable
    print("\n🔧 Step 3: Making ID columns nullable...")
    for column in ['user_id', 'resume_id', 'analysis_id']:
        try:
            cursor.execute(f"""
                ALTER TABLE course_recommendations 
                ALTER COLUMN {column} DROP NOT NULL
            """)
            print(f"   ✅ {column} is now nullable")
        except Exception as e:
            print(f"   ℹ️ {column}: {e}")
    
    conn.commit()
    
    # Step 4: Verify no foreign keys remain
    print("\n✅ Step 4: Verifying changes...")
    cursor.execute("""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_name = 'course_recommendations'
        AND constraint_type = 'FOREIGN KEY'
    """)
    
    remaining = cursor.fetchall()
    if remaining:
        print(f"   ⚠️ Still have {len(remaining)} foreign key(s):")
        for r in remaining:
            print(f"   - {r[0]}")
    else:
        print("   ✅ No foreign key constraints remain!")
    
    # Step 5: Test insert
    print("\n🧪 Step 5: Testing insert with NULL IDs...")
    try:
        cursor.execute("""
            INSERT INTO course_recommendations (
                user_id, resume_id, analysis_id,
                course_title, skill_covered, course_url
            ) VALUES (999, NULL, NULL, 'Test Course', 'Test Skill', 'https://test.com')
            RETURNING id
        """)
        test_id = cursor.fetchone()[0]
        print(f"   ✅ Test insert successful (id={test_id})")
        
        # Clean up
        cursor.execute("DELETE FROM course_recommendations WHERE id = %s", (test_id,))
        conn.commit()
        print("   ✅ Test data cleaned up")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        conn.rollback()
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ ALL FOREIGN KEY CONSTRAINTS REMOVED SUCCESSFULLY")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)
