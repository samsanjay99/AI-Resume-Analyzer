"""
Course Recommendation Manager
Manages personalized YouTube course recommendations based on skill gaps
"""
from config.database import get_database_connection
from typing import List, Dict, Optional
import re

class CourseRecommendationManager:
    """Manage course recommendations for users"""
    
    @staticmethod
    def extract_youtube_video_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)',
            r'youtube\.com/embed/([^&\n?#]+)',
            r'youtube\.com/v/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def generate_thumbnail_url(video_id: str, quality: str = 'maxresdefault') -> str:
        """Generate YouTube thumbnail URL"""
        # Quality options: maxresdefault, sddefault, hqdefault, mqdefault, default
        return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"
    
    @staticmethod
    def find_courses_for_skills(skills: List[str], limit: int = 3) -> List[Dict]:
        """Find YouTube courses for given skills with intelligent matching"""
        if not skills:
            print("⚠️ find_courses_for_skills: No skills provided")
            return []
        
        print(f"🔍 find_courses_for_skills: Processing {len(skills)} skills")
        
        # Skill mapping: maps common skill phrases to database skill names
        skill_mapping = {
            'react': 'React',
            'angular': 'Angular',
            'vue': 'React',  # Map Vue to React as alternative
            'frontend': 'React',
            'ui': 'React',
            'ux': 'React',
            'javascript': 'JavaScript',
            'js': 'JavaScript',
            'typescript': 'TypeScript',
            'ts': 'TypeScript',
            'python': 'Python',
            'java': 'Java',
            'sql': 'SQL',
            'database': 'SQL',
            'git': 'Git',
            'github': 'Git',
            'version control': 'Git',
            'docker': 'Docker',
            'container': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes',
            'aws': 'AWS',
            'cloud': 'AWS',
            'node': 'Node.js',
            'nodejs': 'Node.js',
            'backend': 'Node.js',
            'mongodb': 'MongoDB',
            'nosql': 'MongoDB',
            'machine learning': 'Machine Learning',
            'ml': 'Machine Learning',
            'ai': 'Machine Learning',
            'data science': 'Data Science',
            'data': 'Data Science',
            'analytics': 'Data Science',
        }
        
        # Map skills to database skills
        mapped_skills = set()
        for skill in skills:
            skill_lower = skill.lower().strip()
            
            # Check direct mapping
            if skill_lower in skill_mapping:
                mapped_skills.add(skill_mapping[skill_lower])
            else:
                # Check if any mapping key is in the skill
                for key, value in skill_mapping.items():
                    if key in skill_lower:
                        mapped_skills.add(value)
                        break
                else:
                    # No mapping found, use original skill
                    mapped_skills.add(skill)
        
        print(f"🔍 Mapped to {len(mapped_skills)} database skills: {mapped_skills}")
        
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            courses = []
            seen_videos = set()  # Avoid duplicates
            
            for skill in mapped_skills:
                # Try exact match first
                cursor.execute("""
                    SELECT 
                        skill_name,
                        course_title,
                        youtube_video_id,
                        thumbnail_url,
                        channel_name,
                        video_duration,
                        course_url,
                        difficulty_level
                    FROM skill_course_mapping
                    WHERE LOWER(skill_name) = LOWER(%s)
                    ORDER BY rating DESC, view_count DESC
                    LIMIT %s
                """, (skill, limit))
                
                rows = cursor.fetchall()
                print(f"🔍 Exact match for '{skill}': {len(rows)} courses")
                
                for row in rows:
                    video_id = row[2]
                    if video_id not in seen_videos:
                        seen_videos.add(video_id)
                        courses.append({
                            'skill_name': row[0],
                            'course_title': row[1],
                            'youtube_video_id': row[2],
                            'thumbnail_url': row[3],
                            'channel_name': row[4],
                            'video_duration': row[5],
                            'course_url': row[6],
                            'difficulty_level': row[7]
                        })
                
                # If no exact match, try fuzzy match
                if len(rows) == 0:
                    cursor.execute("""
                        SELECT 
                            skill_name,
                            course_title,
                            youtube_video_id,
                            thumbnail_url,
                            channel_name,
                            video_duration,
                            course_url,
                            difficulty_level
                        FROM skill_course_mapping
                        WHERE LOWER(skill_name) LIKE LOWER(%s)
                        ORDER BY rating DESC, view_count DESC
                        LIMIT %s
                    """, (f'%{skill}%', limit))
                    
                    fuzzy_rows = cursor.fetchall()
                    print(f"🔍 Fuzzy match for '{skill}': {len(fuzzy_rows)} courses")
                    
                    for row in fuzzy_rows:
                        video_id = row[2]
                        if video_id not in seen_videos:
                            seen_videos.add(video_id)
                            courses.append({
                                'skill_name': row[0],
                                'course_title': row[1],
                                'youtube_video_id': row[2],
                                'thumbnail_url': row[3],
                                'channel_name': row[4],
                                'video_duration': row[5],
                                'course_url': row[6],
                                'difficulty_level': row[7]
                            })
            
            print(f"✅ Total courses found: {len(courses)}")
            return courses
    
    @staticmethod
    def save_recommendations_for_user(user_id: int, resume_id: int, 
                                     analysis_id: int, missing_skills: List[str]) -> Dict:
        """Save personalized course recommendations for user"""
        try:
            print(f"🔍 save_recommendations_for_user called: user_id={user_id}, resume_id={resume_id}, skills={len(missing_skills)}")
            
            # Find courses for missing skills
            courses = CourseRecommendationManager.find_courses_for_skills(missing_skills)
            
            print(f"🔍 Found {len(courses)} courses to save")
            
            if not courses:
                return {'success': False, 'message': 'No courses found for skills', 'count': 0}
            
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                # Check if table exists first
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'course_recommendations'
                    )
                """)
                table_exists = cursor.fetchone()[0]
                
                print(f"🔍 Table exists: {table_exists}")
                
                if not table_exists:
                    return {'success': False, 'message': 'course_recommendations table not initialized yet. Please restart the app.', 'count': 0}
                
                saved_count = 0
                for course in courses:
                    try:
                        print(f"🔍 Saving course: {course['course_title']}")
                        cursor.execute("""
                            INSERT INTO course_recommendations (
                                user_id, resume_id, analysis_id,
                                course_title, course_platform, skill_covered,
                                youtube_video_id, thumbnail_url, channel_name,
                                video_duration, course_url, course_type
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (user_id, youtube_video_id) DO UPDATE
                            SET recommended_date = CURRENT_TIMESTAMP
                        """, (
                            user_id, resume_id, analysis_id,
                            course['course_title'], 'YouTube', course['skill_name'],
                            course['youtube_video_id'], course['thumbnail_url'],
                            course['channel_name'], course['video_duration'],
                            course['course_url'], 'video'
                        ))
                        saved_count += 1
                        print(f"✅ Saved course {saved_count}")
                    except Exception as e:
                        print(f"❌ Error saving course {course['course_title']}: {e}")
                
                conn.commit()
                print(f"✅ Committed {saved_count} courses to database")
                
                return {
                    'success': True,
                    'message': f'Saved {saved_count} course recommendations',
                    'count': saved_count,
                    'courses': courses
                }
        
        except Exception as e:
            print(f"❌ Error in save_recommendations_for_user: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': str(e), 'count': 0}
    
    @staticmethod
    def get_user_recommendations(user_id: int, limit: int = 20) -> List[Dict]:
        """Get all course recommendations for user with retry logic"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with get_database_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Check if table exists first
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'course_recommendations'
                        )
                    """)
                    table_exists = cursor.fetchone()[0]
                    
                    if not table_exists:
                        print("⚠️ course_recommendations table doesn't exist yet")
                        return []
                    
                    cursor.execute("""
                        SELECT 
                            id, course_title, course_platform, skill_covered,
                            youtube_video_id, thumbnail_url, channel_name,
                            video_duration, course_url, course_type,
                            is_watched, is_bookmarked, watch_progress,
                            recommended_date
                        FROM course_recommendations
                        WHERE user_id = %s
                        ORDER BY recommended_date DESC
                        LIMIT %s
                    """, (user_id, limit))
                    
                    recommendations = []
                    for row in cursor.fetchall():
                        recommendations.append({
                            'id': row[0],
                            'course_title': row[1],
                            'course_platform': row[2],
                            'skill_covered': row[3],
                            'youtube_video_id': row[4],
                            'thumbnail_url': row[5],
                            'channel_name': row[6],
                            'video_duration': row[7],
                            'course_url': row[8],
                            'course_type': row[9],
                            'is_watched': row[10],
                            'is_bookmarked': row[11],
                            'watch_progress': row[12],
                            'recommended_date': row[13]
                        })
                    
                    return recommendations
                    
            except Exception as e:
                retry_count += 1
                print(f"⚠️ Error getting recommendations (attempt {retry_count}/{max_retries}): {e}")
                
                if retry_count >= max_retries:
                    print(f"❌ Failed to get recommendations after {max_retries} attempts")
                    return []
                
                # Wait a bit before retrying
                import time
                time.sleep(0.5 * retry_count)  # Exponential backoff
        
        return []
    
    @staticmethod
    def mark_as_watched(recommendation_id: int, user_id: int) -> bool:
        """Mark a course as watched"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE course_recommendations
                    SET is_watched = TRUE, last_accessed = CURRENT_TIMESTAMP
                    WHERE id = %s AND user_id = %s
                """, (recommendation_id, user_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error marking as watched: {e}")
            return False
    
    @staticmethod
    def toggle_bookmark(recommendation_id: int, user_id: int) -> bool:
        """Toggle bookmark status"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE course_recommendations
                    SET is_bookmarked = NOT is_bookmarked
                    WHERE id = %s AND user_id = %s
                """, (recommendation_id, user_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error toggling bookmark: {e}")
            return False
    
    @staticmethod
    def update_watch_progress(recommendation_id: int, user_id: int, progress: int) -> bool:
        """Update watch progress (0-100)"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE course_recommendations
                    SET watch_progress = %s, last_accessed = CURRENT_TIMESTAMP
                    WHERE id = %s AND user_id = %s
                """, (progress, recommendation_id, user_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating progress: {e}")
            return False
    
    @staticmethod
    def get_recommendations_by_skill(user_id: int, skill: str) -> List[Dict]:
        """Get recommendations filtered by skill"""
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, course_title, course_platform, skill_covered,
                    youtube_video_id, thumbnail_url, channel_name,
                    video_duration, course_url, course_type,
                    is_watched, is_bookmarked
                FROM course_recommendations
                WHERE user_id = %s AND LOWER(skill_covered) LIKE LOWER(%s)
                ORDER BY recommended_date DESC
            """, (user_id, f'%{skill}%'))
            
            recommendations = []
            for row in cursor.fetchall():
                recommendations.append({
                    'id': row[0],
                    'course_title': row[1],
                    'course_platform': row[2],
                    'skill_covered': row[3],
                    'youtube_video_id': row[4],
                    'thumbnail_url': row[5],
                    'channel_name': row[6],
                    'video_duration': row[7],
                    'course_url': row[8],
                    'course_type': row[9],
                    'is_watched': row[10],
                    'is_bookmarked': row[11]
                })
            
            return recommendations
