"""
Add PDF storage columns to analysis tables
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def add_pdf_storage_columns():
    """Add PDF storage columns to existing tables"""
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Adding PDF storage columns to database...")
        
        # Add pdf_report_path to resume_analyses table
        print("\n1. Adding pdf_report_path to resume_analyses table...")
        cur.execute("""
            ALTER TABLE resume_analyses 
            ADD COLUMN IF NOT EXISTS pdf_report_path TEXT
        """)
        conn.commit()
        print("✅ Added pdf_report_path to resume_analyses")
        
        # Add pdf_report_path to resume_analysis table (old system)
        print("\n2. Adding pdf_report_path to resume_analysis table...")
        cur.execute("""
            ALTER TABLE resume_analysis 
            ADD COLUMN IF NOT EXISTS pdf_report_path TEXT
        """)
        conn.commit()
        print("✅ Added pdf_report_path to resume_analysis")
        
        # Add pdf_report_path to ai_analysis table
        print("\n3. Adding pdf_report_path to ai_analysis table...")
        cur.execute("""
            ALTER TABLE ai_analysis 
            ADD COLUMN IF NOT EXISTS pdf_report_path TEXT
        """)
        conn.commit()
        print("✅ Added pdf_report_path to ai_analysis")
        
        # Create analysis_reports directory if it doesn't exist
        print("\n4. Creating analysis_reports directory...")
        import os
        os.makedirs('analysis_reports', exist_ok=True)
        print("✅ Created analysis_reports directory")
        
        # Verify columns were added
        print("\n5. Verifying columns...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'resume_analyses' 
            AND column_name = 'pdf_report_path'
        """)
        if cur.fetchone():
            print("✅ Verified: resume_analyses.pdf_report_path exists")
        
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'resume_analysis' 
            AND column_name = 'pdf_report_path'
        """)
        if cur.fetchone():
            print("✅ Verified: resume_analysis.pdf_report_path exists")
        
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ai_analysis' 
            AND column_name = 'pdf_report_path'
        """)
        if cur.fetchone():
            print("✅ Verified: ai_analysis.pdf_report_path exists")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ PDF STORAGE COLUMNS ADDED SUCCESSFULLY!")
        print("=" * 60)
        print("Tables updated:")
        print("  1. resume_analyses - Added pdf_report_path")
        print("  2. resume_analysis - Added pdf_report_path")
        print("  3. ai_analysis - Added pdf_report_path")
        print("\nDirectory created:")
        print("  - analysis_reports/ (for storing PDF files)")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    add_pdf_storage_columns()
