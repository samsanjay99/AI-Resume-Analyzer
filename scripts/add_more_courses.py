"""Add more popular courses to skill_course_mapping table"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

courses = [
    # HTML/CSS
    ('HTML', 'HTML Tutorial for Beginners', 'qz0aGYrrlhU', 'Programming with Mosh', '1:00:41', 'Beginner'),
    ('CSS', 'CSS Tutorial for Beginners', 'yfoY53QXEnI', 'Programming with Mosh', '1:11:37', 'Beginner'),
    
    # Responsive Design
    ('Responsive Design', 'Responsive Web Design Tutorial', 'srvUrASNj0s', 'freeCodeCamp.org', '4:25:00', 'Beginner'),
    
    # Testing
    ('Testing', 'JavaScript Testing Tutorial', 'FgnxcUQ5vho', 'freeCodeCamp.org', '1:36:00', 'Intermediate'),
    ('Testing Frameworks', 'Jest Testing Tutorial', 'IPiUDhwnZxA', 'Codevolution', '2:38:00', 'Intermediate'),
    
    # State Management
    ('State Management', 'Redux Tutorial for Beginners', 'poQXNp9ItL4', 'Programming with Mosh', '1:01:54', 'Intermediate'),
    
    # API/REST
    ('API', 'REST API Tutorial', 'SLwpqD8n3d0', 'Programming with Mosh', '1:13:07', 'Beginner'),
    ('RESTful API', 'Build a REST API with Node.js', 'fgTGADljAeg', 'Programming with Mosh', '1:03:17', 'Intermediate'),
    
    # Deployment
    ('Deployment', 'Deploy Web Apps Tutorial', 'l134cBAJCuc', 'freeCodeCamp.org', '1:11:28', 'Intermediate'),
    
    # Debugging
    ('Debugging', 'Chrome DevTools Tutorial', 'x4q86IjJFag', 'freeCodeCamp.org', '1:23:00', 'Beginner'),
    ('Problem Solving', 'Problem Solving Techniques', '8ext9G7xspg', 'freeCodeCamp.org', '3:00:00', 'Intermediate'),
    
    # CodeWithHarry Courses
    ('Python', 'Python Tutorial in Hindi', 'gfDE2a7MKjA', 'CodeWithHarry', '13:44:00', 'Beginner'),
    ('JavaScript', 'JavaScript Tutorial in Hindi', 'ER9SspLe4Hg', 'CodeWithHarry', '6:00:00', 'Beginner'),
    ('React', 'React JS Tutorial in Hindi', 'RGKi6LSPDLU', 'CodeWithHarry', '2:33:00', 'Beginner'),
    ('Web Development', 'Web Development Course', 'tVzUXW6siu0', 'CodeWithHarry', '13:16:00', 'Beginner'),
    ('HTML', 'HTML Tutorial in Hindi', 'BsDoLVMnmZs', 'CodeWithHarry', '2:33:00', 'Beginner'),
    ('CSS', 'CSS Tutorial in Hindi', 'Edsxf_NBFrw', 'CodeWithHarry', '4:00:00', 'Beginner'),
    
    # More popular courses
    ('Python', 'Python for Everybody', 'eWRfhZUzrAc', 'freeCodeCamp.org', '13:26:00', 'Beginner'),
    ('Data Structures', 'Data Structures and Algorithms', 'RBSGKlAvoiM', 'freeCodeCamp.org', '5:00:00', 'Intermediate'),
]

print("=" * 70)
print("ADDING MORE POPULAR COURSES")
print("=" * 70)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    added = 0
    skipped = 0
    
    for skill, title, video_id, channel, duration, level in courses:
        try:
            thumbnail = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
            url = f'https://youtube.com/watch?v={video_id}'
            
            cursor.execute("""
                INSERT INTO skill_course_mapping 
                (skill_name, course_title, youtube_video_id, thumbnail_url, 
                 channel_name, video_duration, course_url, difficulty_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (skill_name, youtube_video_id) DO NOTHING
            """, (skill, title, video_id, thumbnail, channel, duration, url, level))
            
            if cursor.rowcount > 0:
                added += 1
                print(f"✅ Added: {title} ({skill})")
            else:
                skipped += 1
                print(f"⏭️  Skipped (exists): {title}")
                
        except Exception as e:
            print(f"❌ Error adding {title}: {e}")
    
    conn.commit()
    
    # Show summary
    print("\n" + "=" * 70)
    print(f"✅ Added {added} new courses")
    print(f"⏭️  Skipped {skipped} existing courses")
    
    # Show course count by skill
    cursor.execute("""
        SELECT skill_name, COUNT(*) as count 
        FROM skill_course_mapping 
        GROUP BY skill_name 
        ORDER BY count DESC, skill_name
    """)
    
    print("\n📊 Courses per skill:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} courses")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"❌ Error: {e}")
