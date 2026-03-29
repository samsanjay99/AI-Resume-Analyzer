"""
User Data Manager - Retrieve all user-specific historical data
Ensures complete data persistence and access for each user
"""
from config.database import get_database_connection
from datetime import datetime
import json


class UserDataManager:
    """Manages retrieval of all user-specific data"""
    
    @staticmethod
    def get_user_resumes(user_id):
        """Get all resumes created by user"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        id, name, email, phone, linkedin, github, portfolio,
                        summary, target_role, target_category, education,
                        experience, projects, skills, template, created_at
                    FROM resume_data
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
                
                resumes = []
                for row in cursor.fetchall():
                    resumes.append({
                        'id': row[0],
                        'name': row[1],
                        'email': row[2],
                        'phone': row[3],
                        'linkedin': row[4],
                        'github': row[5],
                        'portfolio': row[6],
                        'summary': row[7],
                        'target_role': row[8],
                        'target_category': row[9],
                        'education': row[10],
                        'experience': row[11],
                        'projects': row[12],
                        'skills': row[13],
                        'template': row[14],
                        'created_at': row[15]
                    })
                
                return {'success': True, 'resumes': resumes, 'count': len(resumes)}
        except Exception as e:
            return {'success': False, 'error': str(e), 'resumes': [], 'count': 0}
    
    @staticmethod
    def get_user_analyses(user_id):
        """Get all resume analyses for user"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        ra.id, ra.resume_id, ra.ats_score, ra.keyword_match_score,
                        ra.format_score, ra.section_score, ra.missing_skills,
                        ra.recommendations, ra.created_at, ra.pdf_report_path,
                        rd.name, rd.target_role
                    FROM resume_analysis ra
                    LEFT JOIN resume_data rd ON ra.resume_id = rd.id
                    WHERE ra.user_id = %s
                    ORDER BY ra.created_at DESC
                """, (user_id,))
                
                analyses = []
                for row in cursor.fetchall():
                    analyses.append({
                        'id': row[0],
                        'resume_id': row[1],
                        'ats_score': row[2],
                        'keyword_match_score': row[3],
                        'format_score': row[4],
                        'section_score': row[5],
                        'missing_skills': row[6],
                        'recommendations': row[7],
                        'created_at': row[8],
                        'pdf_report_path': row[9],
                        'resume_name': row[10],
                        'target_role': row[11]
                    })
                
                return {'success': True, 'analyses': analyses, 'count': len(analyses)}
        except Exception as e:
            return {'success': False, 'error': str(e), 'analyses': [], 'count': 0}
    
    @staticmethod
    def get_user_ai_analyses(user_id):
        """Get all AI analyses for user"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        aa.id, aa.resume_id, aa.model_used, aa.resume_score,
                        aa.job_role, aa.created_at, aa.pdf_report_path,
                        rd.name
                    FROM ai_analysis aa
                    LEFT JOIN resume_data rd ON aa.resume_id = rd.id
                    WHERE aa.user_id = %s
                    ORDER BY aa.created_at DESC
                """, (user_id,))
                
                ai_analyses = []
                for row in cursor.fetchall():
                    ai_analyses.append({
                        'id': row[0],
                        'resume_id': row[1],
                        'model_used': row[2],
                        'resume_score': row[3],
                        'job_role': row[4],
                        'created_at': row[5],
                        'pdf_report_path': row[6],
                        'resume_name': row[7]
                    })
                
                return {'success': True, 'ai_analyses': ai_analyses, 'count': len(ai_analyses)}
        except Exception as e:
            return {'success': False, 'error': str(e), 'ai_analyses': [], 'count': 0}
    
    @staticmethod
    def get_user_uploaded_files(user_id):
        """Get all files uploaded by user"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        id, filename, original_name, file_path, file_size,
                        file_type, upload_source, timestamp
                    FROM uploaded_files
                    WHERE user_id = %s
                    ORDER BY timestamp DESC
                """, (user_id,))
                
                files = []
                for row in cursor.fetchall():
                    files.append({
                        'id': row[0],
                        'filename': row[1],
                        'original_name': row[2],
                        'file_path': row[3],
                        'file_size': row[4],
                        'file_type': row[5],
                        'upload_source': row[6],
                        'uploaded_at': row[7]  # Map timestamp to uploaded_at
                    })
                
                return {'success': True, 'files': files, 'count': len(files)}
        except Exception as e:
            return {'success': False, 'error': str(e), 'files': [], 'count': 0}
    
    @staticmethod
    def get_user_deployments(user_id):
        """Get all portfolio deployments for user"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                # Check if deployments table exists, create if not
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio_deployments (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        portfolio_name TEXT,
                        deployment_url TEXT,
                        admin_url TEXT,
                        site_id TEXT,
                        deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active'
                    )
                """)
                
                cursor.execute("""
                    SELECT 
                        id, portfolio_name, deployment_url, admin_url,
                        site_id, deployed_at, status
                    FROM portfolio_deployments
                    WHERE user_id = %s
                    ORDER BY deployed_at DESC
                """, (user_id,))
                
                deployments = []
                for row in cursor.fetchall():
                    deployments.append({
                        'id': row[0],
                        'portfolio_name': row[1],
                        'deployment_url': row[2],
                        'admin_url': row[3],
                        'site_id': row[4],
                        'deployed_at': row[5],
                        'status': row[6]
                    })
                
                return {'success': True, 'deployments': deployments, 'count': len(deployments)}
        except Exception as e:
            return {'success': False, 'error': str(e), 'deployments': [], 'count': 0}
    
    @staticmethod
    def save_deployment(user_id, portfolio_name, deployment_url, admin_url, site_id):
        """Save a portfolio deployment for user"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                # Ensure table exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio_deployments (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        portfolio_name TEXT,
                        deployment_url TEXT,
                        admin_url TEXT,
                        site_id TEXT,
                        deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active'
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO portfolio_deployments 
                    (user_id, portfolio_name, deployment_url, admin_url, site_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (user_id, portfolio_name, deployment_url, admin_url, site_id))
                
                deployment_id = cursor.fetchone()[0]
                conn.commit()
                
                return {'success': True, 'deployment_id': deployment_id}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_user_statistics(user_id):
        """Get comprehensive statistics for user"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total resumes
                cursor.execute("SELECT COUNT(*) FROM resume_data WHERE user_id = %s", (user_id,))
                stats['total_resumes'] = cursor.fetchone()[0]
                
                # Total analyses
                cursor.execute("SELECT COUNT(*) FROM resume_analysis WHERE user_id = %s", (user_id,))
                stats['total_analyses'] = cursor.fetchone()[0]
                
                # Total AI analyses
                cursor.execute("SELECT COUNT(*) FROM ai_analysis WHERE user_id = %s", (user_id,))
                stats['total_ai_analyses'] = cursor.fetchone()[0]
                
                # Average ATS score
                cursor.execute("""
                    SELECT AVG(ats_score) 
                    FROM resume_analysis 
                    WHERE user_id = %s AND ats_score > 0
                """, (user_id,))
                avg_score = cursor.fetchone()[0]
                stats['avg_ats_score'] = round(float(avg_score), 2) if avg_score else 0
                
                # Average AI score
                cursor.execute("""
                    SELECT AVG(resume_score) 
                    FROM ai_analysis 
                    WHERE user_id = %s AND resume_score > 0
                """, (user_id,))
                avg_ai_score = cursor.fetchone()[0]
                stats['avg_ai_score'] = round(float(avg_ai_score), 2) if avg_ai_score else 0
                
                # Total uploaded files
                cursor.execute("SELECT COUNT(*) FROM uploaded_files WHERE user_id = %s", (user_id,))
                stats['total_uploads'] = cursor.fetchone()[0]
                
                # Total deployments (check if table exists first)
                try:
                    cursor.execute("""
                        SELECT COUNT(*) FROM portfolio_deployments 
                        WHERE user_id = %s
                    """, (user_id,))
                    stats['total_deployments'] = cursor.fetchone()[0]
                except:
                    stats['total_deployments'] = 0
                
                # Most recent activity
                cursor.execute("""
                    SELECT created_at 
                    FROM resume_data 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (user_id,))
                recent = cursor.fetchone()
                stats['last_activity'] = recent[0] if recent else None
                
                return {'success': True, 'statistics': stats}
        except Exception as e:
            return {'success': False, 'error': str(e), 'statistics': {}}
    
    @staticmethod
    def get_user_activity_timeline(user_id, limit=20):
        """Get recent activity timeline for user"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                # Combine all activities
                cursor.execute("""
                    SELECT 'Resume Created' as activity_type, name as details, created_at as timestamp
                    FROM resume_data WHERE user_id = %s
                    UNION ALL
                    SELECT 'Analysis Completed' as activity_type, 
                           CONCAT('Score: ', ats_score::text) as details, created_at as timestamp
                    FROM resume_analysis WHERE user_id = %s
                    UNION ALL
                    SELECT 'AI Analysis' as activity_type,
                           CONCAT(model_used, ' - Score: ', resume_score::text) as details, created_at as timestamp
                    FROM ai_analysis WHERE user_id = %s
                    UNION ALL
                    SELECT 'File Uploaded' as activity_type, original_name as details, timestamp
                    FROM uploaded_files WHERE user_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (user_id, user_id, user_id, user_id, limit))
                
                activities = []
                for row in cursor.fetchall():
                    activities.append({
                        'activity_type': row[0],
                        'details': row[1],
                        'timestamp': row[2]
                    })
                
                return {'success': True, 'activities': activities, 'count': len(activities)}
        except Exception as e:
            return {'success': False, 'error': str(e), 'activities': [], 'count': 0}
