"""
Create Course Recommendations Database Schema
Stores personalized YouTube course recommendations based on skill gaps
"""
from config.database import get_database_connection

def create_course_recommendations_table():
    """Create course_recommendations table with YouTube video support"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        # Create course_recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_recommendations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                resume_id INTEGER REFERENCES resume_data(id),
                analysis_id INTEGER REFERENCES resume_analysis(id),
                
                -- Course Information
                course_title TEXT NOT NULL,
                course_platform TEXT DEFAULT 'YouTube',
                skill_covered TEXT NOT NULL,
                course_description TEXT,
                
                -- YouTube Specific Fields
                youtube_video_id TEXT,
                thumbnail_url TEXT,
                channel_name TEXT,
                video_duration TEXT,
                course_url TEXT NOT NULL,
                course_type TEXT DEFAULT 'video',
                
                -- Metadata
                is_watched BOOLEAN DEFAULT FALSE,
                is_bookmarked BOOLEAN DEFAULT FALSE,
                watch_progress INTEGER DEFAULT 0,
                recommended_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                
                -- Indexes for faster queries
                UNIQUE(user_id, youtube_video_id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_course_user_id 
            ON course_recommendations(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_course_skill 
            ON course_recommendations(skill_covered)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_course_platform 
            ON course_recommendations(course_platform)
        """)
        
        conn.commit()
        print("✅ course_recommendations table created successfully")

def create_skill_course_mapping_table():
    """Create mapping table for skills to courses"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
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
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_skill_name 
            ON skill_course_mapping(skill_name)
        """)
        
        conn.commit()
        print("✅ skill_course_mapping table created successfully")

def seed_initial_courses():
    """Seed database with popular YouTube courses for common skills"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        # Popular courses for common skills
        courses = [
            # Python
            ('Python', 'Python Full Course for Beginners', 'rfscVS0vtbw', 
             'https://img.youtube.com/vi/rfscVS0vtbw/maxresdefault.jpg',
             'Programming with Mosh', '6:14:07', 
             'https://youtube.com/watch?v=rfscVS0vtbw', 'Beginner'),
            
            # SQL
            ('SQL', 'SQL Full Course for Beginners', 'HXV3zeQKqGY',
             'https://img.youtube.com/vi/HXV3zeQKqGY/maxresdefault.jpg',
             'freeCodeCamp.org', '4:20:44',
             'https://youtube.com/watch?v=HXV3zeQKqGY', 'Beginner'),
            
            # JavaScript
            ('JavaScript', 'JavaScript Full Course for Beginners', 'PkZNo7MFNFg',
             'https://img.youtube.com/vi/PkZNo7MFNFg/maxresdefault.jpg',
             'freeCodeCamp.org', '3:26:42',
             'https://youtube.com/watch?v=PkZNo7MFNFg', 'Beginner'),
            
            # React
            ('React', 'React Course - Beginners Tutorial', 'bMknfKXIFA8',
             'https://img.youtube.com/vi/bMknfKXIFA8/maxresdefault.jpg',
             'freeCodeCamp.org', '11:55:27',
             'https://youtube.com/watch?v=bMknfKXIFA8', 'Beginner'),
            
            # Java
            ('Java', 'Java Full Course for Beginners', 'xk4_1vDrzzo',
             'https://img.youtube.com/vi/xk4_1vDrzzo/maxresdefault.jpg',
             'Programming with Mosh', '2:30:28',
             'https://youtube.com/watch?v=xk4_1vDrzzo', 'Beginner'),
            
            # Machine Learning
            ('Machine Learning', 'Machine Learning Course for Beginners', 'NWONeJKn6kc',
             'https://img.youtube.com/vi/NWONeJKn6kc/maxresdefault.jpg',
             'freeCodeCamp.org', '20:23:47',
             'https://youtube.com/watch?v=NWONeJKn6kc', 'Intermediate'),
            
            # Data Science
            ('Data Science', 'Data Science Full Course for Beginners', 'ua-CiDNNj30',
             'https://img.youtube.com/vi/ua-CiDNNj30/maxresdefault.jpg',
             'freeCodeCamp.org', '12:18:40',
             'https://youtube.com/watch?v=ua-CiDNNj30', 'Beginner'),
            
            # AWS
            ('AWS', 'AWS Certified Cloud Practitioner Training', 'SOTamWNgDKc',
             'https://img.youtube.com/vi/SOTamWNgDKc/maxresdefault.jpg',
             'freeCodeCamp.org', '13:56:31',
             'https://youtube.com/watch?v=SOTamWNgDKc', 'Beginner'),
            
            # Docker
            ('Docker', 'Docker Tutorial for Beginners', 'fqMOX6JJhGo',
             'https://img.youtube.com/vi/fqMOX6JJhGo/maxresdefault.jpg',
             'Programming with Mosh', '1:08:08',
             'https://youtube.com/watch?v=fqMOX6JJhGo', 'Beginner'),
            
            # Git
            ('Git', 'Git and GitHub for Beginners', 'RGOj5yH7evk',
             'https://img.youtube.com/vi/RGOj5yH7evk/maxresdefault.jpg',
             'freeCodeCamp.org', '1:08:41',
             'https://youtube.com/watch?v=RGOj5yH7evk', 'Beginner'),
        ]
        
        for skill, title, video_id, thumbnail, channel, duration, url, level in courses:
            try:
                cursor.execute("""
                    INSERT INTO skill_course_mapping 
                    (skill_name, course_title, youtube_video_id, thumbnail_url, 
                     channel_name, video_duration, course_url, difficulty_level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (skill_name, youtube_video_id) DO NOTHING
                """, (skill, title, video_id, thumbnail, channel, duration, url, level))
            except Exception as e:
                print(f"⚠️ Error inserting {title}: {e}")
        
        conn.commit()
        print(f"✅ Seeded {len(courses)} courses successfully")

def main():
    """Run all schema creation and seeding"""
    print("Creating course recommendations schema...")
    print("=" * 60)
    
    try:
        create_course_recommendations_table()
        create_skill_course_mapping_table()
        seed_initial_courses()
        
        print("\n" + "=" * 60)
        print("✅ Course recommendations system ready!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
