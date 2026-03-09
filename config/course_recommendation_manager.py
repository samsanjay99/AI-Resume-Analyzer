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
        """Find YouTube courses for given skills"""
        if not skills:
            return []
        
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            courses = []
            for skill in skills:
                # Fuzzy match skill names
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
                
                for row in cursor.fetchall():
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
            
            return courses
    
    @staticmethod
    def save_recommendations_for_user(user_id: int, resume_id: int, 
                                     analysis_id: int, missing_skills: List[str]) -> Dict:
        """Save personalized course recommendations for user"""
        try:
            # Find courses for missing skills
            courses = CourseRecommendationManager.find_courses_for_skills(missing_skills)
            
            if not courses:
                return {'success': False, 'message': 'No courses found for skills'}
            
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
                    return {'success': False, 'message': 'course_recommendations table not initialized yet. Please restart the app.'}
                
                saved_count = 0
                for course in courses:
                    try:
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
                    except Exception as e:
                        print(f"Error saving course {course['course_title']}: {e}")
                
                conn.commit()
                
                return {
                    'success': True,
                    'message': f'Saved {saved_count} course recommendations',
                    'count': saved_count,
                    'courses': courses
                }
        
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_user_recommendations(user_id: int, limit: int = 20) -> List[Dict]:
        """Get all course recommendations for user"""
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
            print(f"Error getting recommendations: {e}")
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
