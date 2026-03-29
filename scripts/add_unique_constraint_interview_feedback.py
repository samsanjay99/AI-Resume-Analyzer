"""
Add UNIQUE constraint on interview_feedback.interview_id
Required for the Vercel API's ON CONFLICT upsert to work.
Run once against Neon DB.
"""
from config.database import get_database_connection

with get_database_connection() as conn:
    cursor = conn.cursor()
    try:
        cursor.execute("""
            ALTER TABLE interview_feedback
            ADD CONSTRAINT interview_feedback_interview_id_unique
            UNIQUE (interview_id)
        """)
        conn.commit()
        print("✅ Unique constraint added")
    except Exception as e:
        if "already exists" in str(e):
            print("✅ Constraint already exists")
        else:
            print(f"❌ Error: {e}")
