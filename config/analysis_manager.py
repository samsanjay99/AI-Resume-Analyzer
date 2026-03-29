"""
Resume Analysis Manager - Backend for resume storage and analysis
Handles CRUD operations for resumes and analysis results
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


class AnalysisManager:
    """Manage resume uploads and analysis results"""
    
    @staticmethod
    def _get_connection():
        """Get database connection"""
        return psycopg2.connect(DATABASE_URL)
    
    # ==================== RESUME OPERATIONS ====================
    
    @staticmethod
    def save_resume(user_id: int, file_name: str, parsed_text: str, 
                   file_url: str = None, file_type: str = None) -> Dict:
        """
        Save uploaded resume
        
        Args:
            user_id: User ID
            file_name: Name of uploaded file
            parsed_text: Extracted text from resume
            file_url: Optional URL where file is stored
            file_type: File type (pdf, docx, etc.)
            
        Returns:
            dict: Success status and resume_id
        """
        try:
            conn = AnalysisManager._get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO resumes (user_id, file_name, file_url, file_type, 
                                   parsed_text, analysis_status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (user_id, file_name, file_url, file_type, parsed_text, 'pending'))
            
            resume_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'Resume saved successfully',
                'resume_id': resume_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error saving resume: {str(e)}'
            }
    
    @staticmethod
    def get_user_resumes(user_id: int, limit: int = 50) -> List[Dict]:
        """
        Get all resumes for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of resumes to return
            
        Returns:
            list: List of resume records
        """
        try:
            conn = AnalysisManager._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT id, file_name, file_type, upload_date, 
                       detected_job_role, analysis_status, created_at
                FROM resumes
                WHERE user_id = %s
                ORDER BY upload_date DESC
                LIMIT %s
            """, (user_id, limit))
            
            resumes = cur.fetchall()
            cur.close()
            conn.close()
            
            return [dict(r) for r in resumes]
            
        except Exception as e:
            print(f"Error getting resumes: {e}")
            return []
    
    @staticmethod
    def get_resume(resume_id: int, user_id: int) -> Optional[Dict]:
        """
        Get specific resume (with security check)
        
        Args:
            resume_id: Resume ID
            user_id: User ID (for security)
            
        Returns:
            dict: Resume data or None
        """
        try:
            conn = AnalysisManager._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT * FROM resumes
                WHERE id = %s AND user_id = %s
            """, (resume_id, user_id))
            
            resume = cur.fetchone()
            cur.close()
            conn.close()
            
            return dict(resume) if resume else None
            
        except Exception as e:
            print(f"Error getting resume: {e}")
            return None
    
    @staticmethod
    def update_resume_status(resume_id: int, status: str, 
                            detected_job_role: str = None) -> Dict:
        """
        Update resume analysis status
        
        Args:
            resume_id: Resume ID
            status: New status (pending, analyzing, completed, failed)
            detected_job_role: Optional detected job role
            
        Returns:
            dict: Success status
        """
        try:
            conn = AnalysisManager._get_connection()
            cur = conn.cursor()
            
            if detected_job_role:
                cur.execute("""
                    UPDATE resumes 
                    SET analysis_status = %s, detected_job_role = %s
                    WHERE id = %s
                """, (status, detected_job_role, resume_id))
            else:
                cur.execute("""
                    UPDATE resumes 
                    SET analysis_status = %s
                    WHERE id = %s
                """, (status, resume_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True, 'message': 'Status updated'}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    # ==================== ANALYSIS OPERATIONS ====================
    
    @staticmethod
    def save_analysis(user_id: int, resume_id: int, analysis_data: Dict, pdf_path: str = None) -> Dict:
        """
        Save resume analysis results
        
        Args:
            user_id: User ID
            resume_id: Resume ID
            analysis_data: Dictionary with analysis results
            pdf_path: Optional path to saved PDF report
            
        Returns:
            dict: Success status and analysis_id
        """
        try:
            conn = AnalysisManager._get_connection()
            cur = conn.cursor()
            
            # Extract data from analysis_data
            detected_skills = json.dumps(analysis_data.get('detected_skills', []))
            projects = json.dumps(analysis_data.get('projects_detected', []))
            certifications = json.dumps(analysis_data.get('certifications_detected', []))
            
            cur.execute("""
                INSERT INTO resume_analyses (
                    user_id, resume_id, detected_skills, experience_years,
                    education_detected, projects_detected, certifications_detected,
                    resume_score, analysis_summary, ai_feedback, pdf_report_path
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_id, resume_id, detected_skills,
                analysis_data.get('experience_years'),
                analysis_data.get('education_detected'),
                projects, certifications,
                analysis_data.get('resume_score'),
                analysis_data.get('analysis_summary'),
                analysis_data.get('ai_feedback'),
                pdf_path
            ))
            
            analysis_id = cur.fetchone()[0]
            conn.commit()
            
            # Update resume status
            cur.execute("""
                UPDATE resumes SET analysis_status = 'completed' WHERE id = %s
            """, (resume_id,))
            conn.commit()
            
            cur.close()
            conn.close()
            
            return {
                'success': True,
                'message': 'Analysis saved successfully',
                'analysis_id': analysis_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error saving analysis: {str(e)}'
            }
    
    @staticmethod
    def get_resume_analyses(resume_id: int, user_id: int) -> List[Dict]:
        """
        Get all analyses for a resume
        
        Args:
            resume_id: Resume ID
            user_id: User ID (for security)
            
        Returns:
            list: List of analysis records
        """
        try:
            conn = AnalysisManager._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT * FROM resume_analyses
                WHERE resume_id = %s AND user_id = %s
                ORDER BY created_at DESC
            """, (resume_id, user_id))
            
            analyses = cur.fetchall()
            cur.close()
            conn.close()
            
            # Parse JSON fields
            result = []
            for analysis in analyses:
                a = dict(analysis)
                a['detected_skills'] = a.get('detected_skills', [])
                a['projects_detected'] = a.get('projects_detected', [])
                a['certifications_detected'] = a.get('certifications_detected', [])
                result.append(a)
            
            return result
            
        except Exception as e:
            print(f"Error getting analyses: {e}")
            return []
    
    @staticmethod
    def get_latest_analysis(resume_id: int, user_id: int) -> Optional[Dict]:
        """
        Get latest analysis for a resume
        
        Args:
            resume_id: Resume ID
            user_id: User ID (for security)
            
        Returns:
            dict: Latest analysis or None
        """
        analyses = AnalysisManager.get_resume_analyses(resume_id, user_id)
        return analyses[0] if analyses else None
    
    @staticmethod
    def get_user_all_analyses(user_id: int, limit: int = 50) -> List[Dict]:
        """
        Get all analyses for a user across all resumes
        
        Args:
            user_id: User ID
            limit: Maximum number to return
            
        Returns:
            list: List of analyses with resume info
        """
        try:
            conn = AnalysisManager._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT 
                    ra.*,
                    r.file_name,
                    r.detected_job_role
                FROM resume_analyses ra
                JOIN resumes r ON ra.resume_id = r.id
                WHERE ra.user_id = %s
                ORDER BY ra.created_at DESC
                LIMIT %s
            """, (user_id, limit))
            
            analyses = cur.fetchall()
            cur.close()
            conn.close()
            
            # Parse JSON fields
            result = []
            for analysis in analyses:
                a = dict(analysis)
                a['detected_skills'] = a.get('detected_skills', [])
                a['projects_detected'] = a.get('projects_detected', [])
                a['certifications_detected'] = a.get('certifications_detected', [])
                result.append(a)
            
            return result
            
        except Exception as e:
            print(f"Error getting all analyses: {e}")
            return []
    
    # ==================== STATISTICS ====================
    
    @staticmethod
    def get_user_stats(user_id: int) -> Dict:
        """
        Get user statistics
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Statistics
        """
        try:
            conn = AnalysisManager._get_connection()
            cur = conn.cursor()
            
            # Count resumes
            cur.execute("SELECT COUNT(*) FROM resumes WHERE user_id = %s", (user_id,))
            total_resumes = cur.fetchone()[0]
            
            # Count analyses
            cur.execute("SELECT COUNT(*) FROM resume_analyses WHERE user_id = %s", (user_id,))
            total_analyses = cur.fetchone()[0]
            
            # Average score
            cur.execute("""
                SELECT AVG(resume_score) FROM resume_analyses WHERE user_id = %s
            """, (user_id,))
            avg_score = cur.fetchone()[0] or 0
            
            # Latest analysis date
            cur.execute("""
                SELECT MAX(created_at) FROM resume_analyses WHERE user_id = %s
            """, (user_id,))
            latest_analysis = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            
            return {
                'total_resumes': total_resumes,
                'total_analyses': total_analyses,
                'average_score': round(float(avg_score), 1) if avg_score else 0,
                'latest_analysis': latest_analysis
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total_resumes': 0,
                'total_analyses': 0,
                'average_score': 0,
                'latest_analysis': None
            }
