"""
Fix mock_interviews table schema - add missing columns
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("🔧 Fixing mock_interviews table...")
    
    # Add missing columns to mock_interviews
    columns_to_add = [
        ("job_description", "TEXT"),
        ("expected_answers", "JSONB DEFAULT '[]'"),
        ("skills_to_test", "JSONB DEFAULT '[]'"),
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cur.execute(f"""
                ALTER TABLE mock_interviews 
                ADD COLUMN IF NOT EXISTS {col_name} {col_type}
            """)
            print(f"  ✅ Added column: {col_name}")
        except Exception as e:
            print(f"  ⚠️  Column {col_name}: {e}")
    
    print("\n🔧 Fixing interview_feedback table...")
    
    # Add missing columns to interview_feedback
    feedback_columns = [
        ("communication_score", "INTEGER DEFAULT 0"),
        ("technical_score", "INTEGER DEFAULT 0"),
        ("problem_solving_score", "INTEGER DEFAULT 0"),
        ("confidence_score", "INTEGER DEFAULT 0"),
        ("relevance_score", "INTEGER DEFAULT 0"),
        ("filler_word_count", "INTEGER DEFAULT 0"),
        ("avg_answer_length", "FLOAT DEFAULT 0"),
    ]
    
    for col_name, col_type in feedback_columns:
        try:
            cur.execute(f"""
                ALTER TABLE interview_feedback 
                ADD COLUMN IF NOT EXISTS {col_name} {col_type}
            """)
            print(f"  ✅ Added column: {col_name}")
        except Exception as e:
            print(f"  ⚠️  Column {col_name}: {e}")
    
    # Change column types if needed
    try:
        cur.execute("""
            ALTER TABLE interview_feedback 
            ALTER COLUMN strengths TYPE TEXT,
            ALTER COLUMN areas_for_improvement TYPE TEXT,
            ALTER COLUMN improvement_plan TYPE TEXT
        """)
        print("  ✅ Updated column types")
    except Exception as e:
        print(f"  ⚠️  Type update: {e}")
    
    # Rename columns if needed
    try:
        cur.execute("""
            ALTER TABLE interview_feedback 
            RENAME COLUMN skill_gaps_detected TO skill_gaps
        """)
        print("  ✅ Renamed skill_gaps_detected to skill_gaps")
    except Exception as e:
        if "does not exist" not in str(e):
            print(f"  ⚠️  Rename: {e}")
    
    try:
        cur.execute("""
            ALTER TABLE interview_feedback 
            RENAME COLUMN per_question_analysis TO per_question_feedback
        """)
        print("  ✅ Renamed per_question_analysis to per_question_feedback")
    except Exception as e:
        if "does not exist" not in str(e):
            print(f"  ⚠️  Rename: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n✅ Interview tables fixed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
