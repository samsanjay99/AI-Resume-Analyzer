"""
User Profile Manager - Backend API for profile operations
Handles CRUD operations for user profiles in Neon PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from typing import Dict, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


class ProfileManager:
    """Manage user profiles with secure database operations"""
    
    @staticmethod
    def _get_connection():
        """Get database connection"""
        return psycopg2.connect(DATABASE_URL)
    
    @staticmethod
    def create_profile(user_id: int, full_name: str = None) -> Dict:
        """
        Create a new profile for a user (called during signup)
        
        Args:
            user_id: User ID from users table
            full_name: Optional full name from signup
            
        Returns:
            dict: Success status and profile data
        """
        try:
            conn = ProfileManager._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Check if profile already exists
            cur.execute("SELECT id FROM user_profiles WHERE user_id = %s", (user_id,))
            existing = cur.fetchone()
            
            if existing:
                cur.close()
                conn.close()
                return {
                    'success': True,
                    'message': 'Profile already exists',
                    'profile_id': existing['id']
                }
            
            # Create new profile
            cur.execute("""
                INSERT INTO user_profiles (user_id, full_name, skills)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (user_id, full_name, json.dumps([])))
            
            profile_id = cur.fetchone()['id']
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'Profile created successfully',
                'profile_id': profile_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating profile: {str(e)}'
            }
    
    @staticmethod
    def get_profile(user_id: int) -> Optional[Dict]:
        """
        Get user profile by user_id (optimized with connection pooling)
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Profile data or None
        """
        try:
            conn = ProfileManager._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Optimized query - only fetch needed fields
            cur.execute("""
                SELECT id, user_id, full_name, username, profile_picture_url, 
                       bio, location, education, experience_level, target_job_role,
                       skills, linkedin_url, github_url, portfolio_url, 
                       preferred_language, created_at, updated_at
                FROM user_profiles 
                WHERE user_id = %s
            """, (user_id,))
            
            profile = cur.fetchone()
            cur.close()
            conn.close()
            
            if profile:
                # Convert to dict and parse JSON fields
                profile_dict = dict(profile)
                if profile_dict.get('skills'):
                    profile_dict['skills'] = profile_dict['skills']
                else:
                    profile_dict['skills'] = []
                return profile_dict
            
            return None
            
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    @staticmethod
    def update_profile(user_id: int, profile_data: Dict) -> Dict:
        """
        Update user profile
        
        Args:
            user_id: User ID
            profile_data: Dictionary with fields to update
            
        Returns:
            dict: Success status and message
        """
        try:
            conn = ProfileManager._get_connection()
            cur = conn.cursor()
            
            # Build dynamic UPDATE query
            allowed_fields = [
                'full_name', 'username', 'profile_picture_url', 'bio',
                'location', 'education', 'experience_level', 'target_job_role',
                'skills', 'linkedin_url', 'github_url', 'portfolio_url',
                'preferred_language'
            ]
            
            update_fields = []
            values = []
            
            for field, value in profile_data.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = %s")
                    # Convert skills list to JSON
                    if field == 'skills' and isinstance(value, list):
                        values.append(json.dumps(value))
                    else:
                        values.append(value)
            
            if not update_fields:
                return {
                    'success': False,
                    'message': 'No valid fields to update'
                }
            
            # Add user_id to values
            values.append(user_id)
            
            query = f"""
                UPDATE user_profiles 
                SET {', '.join(update_fields)}
                WHERE user_id = %s
            """
            
            cur.execute(query, values)
            rows_updated = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            
            if rows_updated > 0:
                return {
                    'success': True,
                    'message': 'Profile updated successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Profile not found'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating profile: {str(e)}'
            }
    
    @staticmethod
    def get_profile_stats(user_id: int) -> Dict:
        """
        Get profile completion statistics
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Profile completion stats
        """
        profile = ProfileManager.get_profile(user_id)
        
        if not profile:
            return {
                'completion_percentage': 0,
                'completed_fields': 0,
                'total_fields': 0
            }
        
        # Define important fields for completion
        important_fields = [
            'full_name', 'bio', 'location', 'education',
            'experience_level', 'target_job_role', 'skills',
            'linkedin_url', 'github_url'
        ]
        
        completed = 0
        for field in important_fields:
            value = profile.get(field)
            if value:
                if field == 'skills' and len(value) > 0:
                    completed += 1
                elif field != 'skills' and value.strip():
                    completed += 1
        
        total = len(important_fields)
        percentage = int((completed / total) * 100)
        
        return {
            'completion_percentage': percentage,
            'completed_fields': completed,
            'total_fields': total,
            'missing_fields': [f for f in important_fields if not profile.get(f)]
        }
    
    @staticmethod
    def check_username_available(username: str, exclude_user_id: int = None) -> bool:
        """
        Check if username is available
        
        Args:
            username: Username to check
            exclude_user_id: Exclude this user_id from check (for updates)
            
        Returns:
            bool: True if available
        """
        try:
            conn = ProfileManager._get_connection()
            cur = conn.cursor()
            
            if exclude_user_id:
                cur.execute("""
                    SELECT id FROM user_profiles 
                    WHERE username = %s AND user_id != %s
                """, (username, exclude_user_id))
            else:
                cur.execute("""
                    SELECT id FROM user_profiles WHERE username = %s
                """, (username,))
            
            exists = cur.fetchone()
            cur.close()
            conn.close()
            
            return exists is None
            
        except Exception as e:
            print(f"Error checking username: {e}")
            return False
    
    @staticmethod
    def get_profile_by_username(username: str) -> Optional[Dict]:
        """
        Get profile by username (for public profiles)
        
        Args:
            username: Username
            
        Returns:
            dict: Profile data or None
        """
        try:
            conn = ProfileManager._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT * FROM user_profiles WHERE username = %s
            """, (username,))
            
            profile = cur.fetchone()
            cur.close()
            conn.close()
            
            if profile:
                profile_dict = dict(profile)
                if profile_dict.get('skills'):
                    profile_dict['skills'] = profile_dict['skills']
                else:
                    profile_dict['skills'] = []
                return profile_dict
            
            return None
            
        except Exception as e:
            print(f"Error getting profile by username: {e}")
            return None
