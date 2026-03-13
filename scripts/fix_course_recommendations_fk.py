"""
Fix foreign key constraint issue in course_recommendations table
This script removes the foreign key constraint on analysis_id
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
print("FIXING COURSE_RECOMMENDATIONS FOREIGN KEY CONSTRAINT")
print("=" * 70)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Step 1: Check if the foreign key constraint exists
    print("\n🔍 Step 1: Checking for foreign key constraints...")
    cursor.execute("""
        SELECT constraint_name, table_name
        FROM information_schema.table_constraints
        WHERE table_name = 'course_recommendations'
        AND constraint_type = 'FOREIGN KEY'
    """)
    
    constraints = cursor.fetchall()
    if constraints:
        print(f"   Found {len(constraints)} foreign key constraint(s):")
        for constraint in constraints:
            print(f"   - {constraint[0]} on {constraint[1]}")
    else:
        print("   ✅ No foreign key constraints found")
    
    # Step 2: Drop the foreign key constraint on analysis_id
    print("\n🔧 Step 2: Dropping foreign key constraint on analysis_id...")
    try:
        cursor.execute("""
            ALTER TABLE course_recommendations 
            DROP CONSTRAINT IF EXISTS course_recommendations_analysis_id_fkey
        """)
        conn.commit()
        print("   ✅ Foreign key constraint dropped successfully")
    except Exception as e:
        print(f"   ⚠️ Error dropping constraint: {e}")
        conn.rollback()
    
    # Step 3: Make analysis_id nullable (if not already)
    print("\n🔧 Step 3: Making analysis_id nullable...")
    try:
        cursor.execute("""
            ALTER TABLE course_recommendations 
            ALTER COLUMN analysis_id DROP NOT NULL
        """)
        conn.commit()
        print("   ✅ analysis_id is now nullable")
    except Exception as e:
        print(f"   ℹ️ Column might already be nullable: {e}")
        conn.rollback()
    
    # Step 4: Verify the changes
    print("\n✅ Step 4: Verifying changes...")
    cursor.execute("""
        SELECT constraint_name, table_name
        FROM information_schema.table_constraints
        WHERE table_name = 'course_recommendations'
        AND constraint_type = 'FOREIGN KEY'
    """)
    
    remaining_constraints = cursor.fetchall()
    if remaining_constraints:
        print(f"   Remaining foreign key constraints: {len(remaining_constraints)}")
        for constraint in remaining_constraints:
            print(f"   - {constraint[0]}")
    else:
        print("   ✅ No foreign key constraints on course_recommendations")
    
    # Step 5: Test insert with NULL analysis_id
    print("\n🧪 Step 5: Testing insert with NULL analysis_id...")
    try:
        cursor.execute("""
            INSERT INTO course_recommendations (
                user_id, resume_id, analysis_id,
                course_title, skill_covered, course_url
            ) VALUES (999, 999, NULL, 'Test Course', 'Test Skill', 'https://test.com')
            RETURNING id
        """)
        test_id = cursor.fetchone()[0]
        print(f"   ✅ Test insert successful (id={test_id})")
        
        # Clean up test data
        cursor.execute("DELETE FROM course_recommendations WHERE id = %s", (test_id,))
        conn.commit()
        print("   ✅ Test data cleaned up")
    except Exception as e:
        print(f"   ❌ Test insert failed: {e}")
        conn.rollback()
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ FOREIGN KEY CONSTRAINT FIX COMPLETED")
    print("=" * 70)
    print("\nYou can now save course recommendations without analysis_id!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)
