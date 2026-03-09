"""
Setup Learning Dashboard Tables in Neon Database
Run this script to create tables and seed initial course data
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def setup_learning_tables():
    """Create learning dashboard tables and seed data"""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("Make sure you have a .env file with DATABASE_URL set")
        return False
    
    print("🔄 Connecting to Neon database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        print("\n" + "="*60)
        print("Creating Learning Dashboard Tables...")
        print("="*60 + "\n")
        
        # 1. Create course_recommendations table
        print("📋 Creating course_recommendations table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_recommendations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                resume_id INTEGER,
                analysis_id INTEGER,
                course_title TEXT NOT NULL,
                course_platform TEXT DEFAULT 'YouTube',
                skill_covered TEXT NOT NULL,
                course_description TEXT,
                youtube_video_id TEXT,
                thumbnail_url TEXT,
                channel_name TEXT,
                video_duration TEXT,
                course_url TEXT NOT NULL,
                course_type TEXT DEFAULT 'video',
                is_watched BOOLEAN DEFAULT FALSE,
                is_bookmarked BOOLEAN DEFAULT FALSE,
                watch_progress INTEGER DEFAULT 0,
                recommended_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                UNIQUE(user_id, youtube_video_id)
            )
        """)
        print("   ✅ course_recommendations table created")
        
        # 2. Create skill_course_mapping table
        print("📋 Creating skill_course_mapping table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_course_mapping (
                id SERIAL PRIMARY KEY,
                skill_name TEXT NOT NULL,
                course_title TEXT NOT NULL,
                youtube_video_id TEXT NOT NULL,
                thumbnail_url TEXT,
                channel_name TEXT,
                video_duration TEXT,
                course_url TEXT NOT NULL,
                difficulty_level TEXT DEFAULT 'Beginner',
                rating REAL DEFAULT 0.0,
                view_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(skill_name, youtube_video_id)
            )
        """)
        print("   ✅ skill_course_mapping table created")
        
        # 3. Create indexes
        print("📋 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_user_id ON course_recommendations(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_skill ON course_recommendations(skill_covered)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_platform ON course_recommendations(course_platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_skill_name ON skill_course_mapping(skill_name)")
        print("   ✅ Indexes created")
        
        # 4. Seed initial courses
        print("\n📚 Seeding initial course data...")
        
        courses = [
            ('Python', 'Python Full Course for Beginners', 'rfscVS0vtbw', 
             'https://img.youtube.com/vi/rfscVS0vtbw/maxresdefault.jpg',
             'Programming with Mosh', '6:14:07', 
             'https://youtube.com/watch?v=rfscVS0vtbw', 'Beginner'),
            
            ('SQL', 'SQL Full Course for Beginners', 'HXV3zeQKqGY',
             'https://img.youtube.com/vi/HXV3zeQKqGY/maxresdefault.jpg',
             'freeCodeCamp.org', '4:20:44',
             'https://youtube.com/watch?v=HXV3zeQKqGY', 'Beginner'),
            
            ('JavaScript', 'JavaScript Full Course for Beginners', 'PkZNo7MFNFg',
             'https://img.youtube.com/vi/PkZNo7MFNFg/maxresdefault.jpg',
             'freeCodeCamp.org', '3:26:42',
             'https://youtube.com/watch?v=PkZNo7MFNFg', 'Beginner'),
            
            ('React', 'React Course - Beginners Tutorial', 'bMknfKXIFA8',
             'https://img.youtube.com/vi/bMknfKXIFA8/maxresdefault.jpg',
             'freeCodeCamp.org', '11:55:27',
             'https://youtube.com/watch?v=bMknfKXIFA8', 'Beginner'),
            
            ('Java', 'Java Full Course for Beginners', 'xk4_1vDrzzo',
             'https://img.youtube.com/vi/xk4_1vDrzzo/maxresdefault.jpg',
             'Programming with Mosh', '2:30:28',
             'https://youtube.com/watch?v=xk4_1vDrzzo', 'Beginner'),
            
            ('Machine Learning', 'Machine Learning Course for Beginners', 'NWONeJKn6kc',
             'https://img.youtube.com/vi/NWONeJKn6kc/maxresdefault.jpg',
             'freeCodeCamp.org', '20:23:47',
             'https://youtube.com/watch?v=NWONeJKn6kc', 'Intermediate'),
            
            ('Data Science', 'Data Science Full Course for Beginners', 'ua-CiDNNj30',
             'https://img.youtube.com/vi/ua-CiDNNj30/maxresdefault.jpg',
             'freeCodeCamp.org', '12:18:40',
             'https://youtube.com/watch?v=ua-CiDNNj30', 'Beginner'),
            
            ('AWS', 'AWS Certified Cloud Practitioner Training', 'SOTamWNgDKc',
             'https://img.youtube.com/vi/SOTamWNgDKc/maxresdefault.jpg',
             'freeCodeCamp.org', '13:56:31',
             'https://youtube.com/watch?v=SOTamWNgDKc', 'Beginner'),
            
            ('Docker', 'Docker Tutorial for Beginners', 'fqMOX6JJhGo',
             'https://img.youtube.com/vi/fqMOX6JJhGo/maxresdefault.jpg',
             'Programming with Mosh', '1:08:08',
             'https://youtube.com/watch?v=fqMOX6JJhGo', 'Beginner'),
            
            ('Git', 'Git and GitHub for Beginners', 'RGOj5yH7evk',
             'https://img.youtube.com/vi/RGOj5yH7evk/maxresdefault.jpg',
             'freeCodeCamp.org', '1:08:41',
             'https://youtube.com/watch?v=RGOj5yH7evk', 'Beginner'),
            
            ('Node.js', 'Node.js Full Course for Beginners', 'Oe421EPjeBE',
             'https://img.youtube.com/vi/Oe421EPjeBE/maxresdefault.jpg',
             'freeCodeCamp.org', '8:16:48',
             'https://youtube.com/watch?v=Oe421EPjeBE', 'Beginner'),
            
            ('Angular', 'Angular Full Course for Beginners', 'k5E2AVpwsko',
             'https://img.youtube.com/vi/k5E2AVpwsko/maxresdefault.jpg',
             'Programming with Mosh', '2:02:50',
             'https://youtube.com/watch?v=k5E2AVpwsko', 'Beginner'),
            
            ('MongoDB', 'MongoDB Crash Course', 'ofme2o29ngU',
             'https://img.youtube.com/vi/ofme2o29ngU/maxresdefault.jpg',
             'Web Dev Simplified', '30:44',
             'https://youtube.com/watch?v=ofme2o29ngU', 'Beginner'),
            
            ('Kubernetes', 'Kubernetes Tutorial for Beginners', 'X48VuDVv0do',
             'https://img.youtube.com/vi/X48VuDVv0do/maxresdefault.jpg',
             'TechWorld with Nana', '3:53:27',
             'https://youtube.com/watch?v=X48VuDVv0do', 'Beginner'),
            
            ('TypeScript', 'TypeScript Full Course for Beginners', 'gp5H0Vw39yw',
             'https://img.youtube.com/vi/gp5H0Vw39yw/maxresdefault.jpg',
             'freeCodeCamp.org', '8:07:00',
             'https://youtube.com/watch?v=gp5H0Vw39yw', 'Beginner'),
        ]
        
        seeded_count = 0
        for skill, title, video_id, thumbnail, channel, duration, url, level in courses:
            try:
                cursor.execute("""
                    INSERT INTO skill_course_mapping 
                    (skill_name, course_title, youtube_video_id, thumbnail_url, 
                     channel_name, video_duration, course_url, difficulty_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (skill_name, youtube_video_id) DO NOTHING
                """, (skill, title, video_id, thumbnail, channel, duration, url, level))
                seeded_count += 1
                print(f"   ✅ {skill}: {title}")
            except Exception as e:
                print(f"   ⚠️  Error seeding {title}: {e}")
        
        # Commit all changes
        conn.commit()
        
        print(f"\n✅ Successfully seeded {seeded_count} courses!")
        
        # Verify
        print("\n" + "="*60)
        print("Verification")
        print("="*60 + "\n")
        
        cursor.execute("SELECT COUNT(*) FROM course_recommendations")
        rec_count = cursor.fetchone()[0]
        print(f"📊 course_recommendations: {rec_count} rows")
        
        cursor.execute("SELECT COUNT(*) FROM skill_course_mapping")
        skill_count = cursor.fetchone()[0]
        print(f"📊 skill_course_mapping: {skill_count} rows")
        
        print("\n" + "="*60)
        print("✅ Learning Dashboard Setup Complete!")
        print("="*60)
        print("\n🎉 You can now:")
        print("   1. Analyze a resume in your app")
        print("   2. Check the Learning Dashboard")
        print("   3. See personalized course recommendations!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Learning Dashboard Setup Script")
    print("="*60 + "\n")
    
    success = setup_learning_tables()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
