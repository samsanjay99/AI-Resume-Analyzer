import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from datetime import datetime
import os
from dotenv import load_dotenv
from functools import lru_cache
import time

# Load environment variables from .env file
load_dotenv()

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

# Create a connection pool for better performance
_connection_pool = None
_cache = {}
_cache_timeout = 300  # Increased cache timeout to 5 minutes for better performance
_database_initialized = False  # Flag to track if database is initialized

def get_connection_pool():
    """Get or create the connection pool with optimized settings"""
    global _connection_pool
    if _connection_pool is None:
        try:
            # Parse DATABASE_URL to add connection optimizations
            import urllib.parse as urlparse
            url = urlparse.urlparse(DATABASE_URL)
            
            # Build optimized connection string with Neon-specific optimizations
            optimized_dsn = (
                f"postgresql://{url.username}:{url.password}@{url.hostname}{url.path}"
                f"?sslmode=require"
                f"&connect_timeout=10"
                f"&keepalives=1"
                f"&keepalives_idle=30"
                f"&keepalives_interval=10"
                f"&keepalives_count=5"
                f"&application_name=smart_resume_ai"
            )
            
            _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,  # Keep 2 connections ready
                maxconn=20,  # Allow up to 20 connections
                dsn=optimized_dsn
            )
            print("✅ Optimized database connection pool created")
        except Exception as e:
            print(f"❌ Error creating connection pool: {e}")
            # Fallback to simple pool
            _connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=DATABASE_URL
            )
    return _connection_pool

@contextmanager
def get_database_connection():
    """Get a connection from the pool"""
    pool = get_connection_pool()
    conn = None
    try:
        conn = pool.getconn()
        yield conn
    finally:
        if conn:
            pool.putconn(conn)

def get_cached(key):
    """Get cached value if not expired"""
    if key in _cache:
        value, timestamp = _cache[key]
        if time.time() - timestamp < _cache_timeout:
            return value
    return None

def set_cache(key, value):
    """Set cache value with timestamp"""
    _cache[key] = (value, time.time())

def clear_cache():
    """Clear all cached data"""
    global _cache
    _cache = {}

def warm_cache():
    """Pre-load frequently accessed data into cache"""
    try:
        print("🔥 Warming up cache...")
        # Pre-load database status
        get_database_status()
        # Pre-load resume stats
        get_resume_stats()
        print("✅ Cache warmed up")
    except Exception as e:
        print(f"⚠️ Cache warm-up warning: {e}")

def init_database():
    """Initialize database tables (runs only once)"""
    global _database_initialized
    
    # Skip if already initialized
    if _database_initialized:
        return
    
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        # Create resume_data table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_data (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            linkedin TEXT,
            github TEXT,
            portfolio TEXT,
            summary TEXT,
            target_role TEXT,
            target_category TEXT,
            education TEXT,
            experience TEXT,
            projects TEXT,
            skills TEXT,
            template TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create resume_skills table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_skills (
            id SERIAL PRIMARY KEY,
            resume_id INTEGER,
            skill_name TEXT NOT NULL,
            skill_category TEXT NOT NULL,
            proficiency_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resume_data (id)
        )
        ''')
        
        # Create resume_analysis table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_analysis (
            id SERIAL PRIMARY KEY,
            resume_id INTEGER,
            ats_score REAL,
            keyword_match_score REAL,
            format_score REAL,
            section_score REAL,
            missing_skills TEXT,
            recommendations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resume_data (id)
        )
        ''')
        
        # Create admin_logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id SERIAL PRIMARY KEY,
            admin_email TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create admin table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        
        # Create indexes for better performance
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_resume_data_email ON resume_data(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_resume_data_created_at ON resume_data(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_resume_analysis_resume_id ON resume_analysis(resume_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_analysis_resume_id ON ai_analysis(resume_id)')
            conn.commit()
            print("✅ Database indexes created")
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
    
    # Create default admin if none exists
    create_default_admin()
    
    # Setup additional tables
    setup_feedback_table()
    setup_uploaded_files_table()
    
    # Mark as initialized
    _database_initialized = True
    print("✅ Database initialized")
    
    # Warm up the cache for better performance
    warm_cache()

def save_resume_data(data, user_id=None):
    """Save resume data to database with user_id"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            personal_info = data.get('personal_info', {})
            
            cursor.execute('''
            INSERT INTO resume_data (
                name, email, phone, linkedin, github, portfolio,
                summary, target_role, target_category, education, 
                experience, projects, skills, template, user_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            ''', (
                personal_info.get('full_name', ''),
                personal_info.get('email', ''),
                personal_info.get('phone', ''),
                personal_info.get('linkedin', ''),
                personal_info.get('github', ''),
                personal_info.get('portfolio', ''),
                data.get('summary', ''),
                data.get('target_role', ''),
                data.get('target_category', ''),
                str(data.get('education', [])),
                str(data.get('experience', [])),
                str(data.get('projects', [])),
                str(data.get('skills', [])),
                data.get('template', ''),
                user_id
            ))
            
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None
        except Exception as e:
            print(f"Error saving resume data: {str(e)}")
            conn.rollback()
            return None

def save_analysis_data(resume_id, analysis, user_id=None, pdf_path=None):
    """Save resume analysis data with user_id and PDF path"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO resume_analysis (
                resume_id, ats_score, keyword_match_score,
                format_score, section_score, missing_skills,
                recommendations, user_id, pdf_report_path
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                resume_id,
                float(analysis.get('ats_score', 0)),
                float(analysis.get('keyword_match_score', 0)),
                float(analysis.get('format_score', 0)),
                float(analysis.get('section_score', 0)),
                analysis.get('missing_skills', ''),
                analysis.get('recommendations', ''),
                user_id,
                pdf_path
            ))
            
            conn.commit()
        except Exception as e:
            print(f"Error saving analysis data: {str(e)}")
            conn.rollback()

def get_resume_stats():
    """Get statistics about resumes (cached for 5 minutes)"""
    # Check cache first
    cached = get_cached('resume_stats')
    if cached:
        return cached
    
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Get total resumes
            cursor.execute('SELECT COUNT(*) FROM resume_data')
            total_resumes = cursor.fetchone()[0]
            
            # Get average ATS score
            cursor.execute('SELECT AVG(ats_score) FROM resume_analysis')
            avg_ats_score = cursor.fetchone()[0] or 0
            
            # Get recent activity
            cursor.execute('''
            SELECT name, target_role, created_at 
            FROM resume_data 
            ORDER BY created_at DESC 
            LIMIT 5
            ''')
            recent_activity = cursor.fetchall()
            
            result = {
                'total_resumes': total_resumes,
                'avg_ats_score': round(float(avg_ats_score), 2),
                'recent_activity': recent_activity
            }
            
            # Cache the result
            set_cache('resume_stats', result)
            return result
        except Exception as e:
            print(f"Error getting resume stats: {str(e)}")
            return None

def log_admin_action(admin_email, action):
    """Log admin login/logout actions"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO admin_logs (admin_email, action)
            VALUES (%s, %s)
            ''', (admin_email, action))
            conn.commit()
        except Exception as e:
            print(f"Error logging admin action: {str(e)}")

def get_admin_logs():
    """Get all admin login/logout logs"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT admin_email, action, timestamp
            FROM admin_logs
            ORDER BY timestamp DESC
            ''')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting admin logs: {str(e)}")
            return []

def get_all_resume_data():
    """Get all resume data for admin dashboard"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Get resume data joined with analysis data and AI analysis data
            cursor.execute('''
            SELECT 
                r.id,
                r.name,
                r.email,
                r.phone,
                r.linkedin,
                r.github,
                r.portfolio,
                r.summary,
                r.target_role,
                r.target_category,
                r.education,
                r.experience,
                r.projects,
                r.skills,
                r.template,
                r.created_at,
                COALESCE(a.ats_score, ai.resume_score, 0) as score,
                COALESCE(a.ats_score, ai.resume_score, 0) as ats_score,
                COALESCE(ai.job_role, r.target_role, 'Unknown') as predicted_role,
                'N/A' as experience_level,
                COALESCE(ai.created_at, a.created_at, r.created_at) as analysis_date,
                COALESCE(ai.model_used, 'Standard Analysis') as model_used
            FROM resume_data r
            LEFT JOIN resume_analysis a ON r.id = a.resume_id
            LEFT JOIN ai_analysis ai ON r.id = ai.resume_id
            ORDER BY r.created_at DESC
            ''')
            
            # Convert to the format expected by the dashboard
            results = cursor.fetchall()
            formatted_results = []
            
            for row in results:
                # Convert to list format expected by dashboard
                formatted_row = [
                    row[0],   # ID
                    row[1],   # Name
                    row[2],   # Email
                    row[3],   # Phone
                    row[4],   # LinkedIn
                    row[5],   # GitHub
                    row[6],   # Portfolio
                    row[7],   # Summary
                    row[8],   # Target Role
                    row[9],   # Target Category
                    row[10],  # Education
                    row[11],  # Experience
                    row[12],  # Projects
                    row[13],  # Skills
                    row[14],  # Template
                    row[15],  # Created At
                    row[16],  # Score
                    row[17],  # ATS Score
                    row[18],  # Predicted Role
                    row[19],  # Experience Level
                    row[20],  # Analysis Date
                    row[21]   # Model Used
                ]
                formatted_results.append(formatted_row)
            
            return formatted_results
        except Exception as e:
            print(f"Error getting resume data: {str(e)}")
            return []

def verify_admin(email, password):
    """Verify admin credentials (cached for 5 minutes)"""
    # Check cache first
    cache_key = f'admin_verify_{email}_{password}'
    cached = get_cached(cache_key)
    if cached is not None:
        return cached
    
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Direct check for exact match (removed debug prints for speed)
            cursor.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (email, password))
            result = cursor.fetchone()
            is_valid = bool(result)
            
            # Cache the result
            set_cache(cache_key, is_valid)
            return is_valid
        except Exception as e:
            print(f"Error verifying admin: {str(e)}")
            return False

def add_admin(email, password):
    """Add a new admin"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO admin (email, password) VALUES (%s, %s)', (email, password))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding admin: {str(e)}")
            return False

def create_default_admin():
    """Create default admin if no admin exists"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Ensure admin table exists
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id SERIAL PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Check if any admin exists
            cursor.execute('SELECT COUNT(*) FROM admin')
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                # Create default admin
                cursor.execute('INSERT INTO admin (email, password) VALUES (%s, %s)', 
                             ('sam@gmail.com', 'sanjay2026'))
                conn.commit()
                print("✅ Default admin created: sam@gmail.com")
                
                # Verify the admin was created
                cursor.execute('SELECT email, password FROM admin WHERE email = %s', ('sam@gmail.com',))
                created_admin = cursor.fetchone()
                if created_admin:
                    print(f"✅ Admin verified in database: {created_admin[0]}")
                else:
                    print("❌ Failed to verify admin creation")
                
                return True
            else:
                # Debug: Show existing admins
                cursor.execute('SELECT id, email, password FROM admin')
                existing_admins = cursor.fetchall()
                print(f"📋 Existing admins in database ({admin_count} total):")
                for admin in existing_admins:
                    print(f"   ID: {admin[0]}, Email: '{admin[1]}', Password: '{admin[2]}'")
            return False
        except Exception as e:
            print(f"❌ Error creating default admin: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def debug_admin_table():
    """Debug function to check admin table contents (cached for 5 minutes)"""
    # Check cache first
    cached = get_cached('debug_admin_table')
    if cached is not None:
        return cached
    
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Check if admin table exists
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename='admin'")
            table_exists = cursor.fetchone()
            print(f"📋 Admin table exists: {bool(table_exists)}")
            
            if table_exists:
                # Get all admins
                cursor.execute('SELECT id, email, password, created_at FROM admin')
                admins = cursor.fetchall()
                print(f"👥 All admins in database ({len(admins)} total):")
                for admin in admins:
                    print(f"   ID: {admin[0]}, Email: '{admin[1]}', Password: '{admin[2]}', Created: {admin[3]}")
                
                # Get table schema
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'admin'
                """)
                schema = cursor.fetchall()
                print(f"🏗️ Admin table schema:")
                for col in schema:
                    print(f"   - {col[0]} ({col[1]})")
            
            # Cache the result
            set_cache('debug_admin_table', True)
            return True
        except Exception as e:
            print(f"❌ Error debugging admin table: {str(e)}")
            return False

def reset_admin_credentials():
    """Reset admin credentials to default"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Delete all existing admins
            cursor.execute('DELETE FROM admin')
            
            # Create default admin
            cursor.execute('INSERT INTO admin (email, password) VALUES (%s, %s)', 
                         ('sam@gmail.com', 'sanjay2026'))
            conn.commit()
            
            print("✅ Admin credentials reset to default: sam@gmail.com / sanjay2026")
            return True
        except Exception as e:
            print(f"❌ Error resetting admin credentials: {str(e)}")
            return False

def get_admin_analytics():
    """Get analytics data for admin dashboard"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            analytics = {}
            
            # Total users (distinct emails)
            cursor.execute('SELECT COUNT(DISTINCT email) FROM resume_data WHERE email IS NOT NULL AND email != %s', ('',))
            analytics['total_users'] = cursor.fetchone()[0]
            
            # Total resumes
            cursor.execute('SELECT COUNT(*) FROM resume_data')
            analytics['total_resumes'] = cursor.fetchone()[0]
            
            # Average score from both resume_analysis and ai_analysis
            cursor.execute('''
                SELECT AVG(score) FROM (
                    SELECT ats_score as score FROM resume_analysis WHERE ats_score > 0
                    UNION ALL
                    SELECT resume_score as score FROM ai_analysis WHERE resume_score > 0
                ) AS combined_scores
            ''')
            result = cursor.fetchone()[0]
            analytics['avg_score'] = round(float(result), 2) if result else 0
            
            # Role distribution from both target_role and ai_analysis job_role
            cursor.execute('''
                SELECT role, COUNT(*) as count FROM (
                    SELECT target_role as role FROM resume_data WHERE target_role IS NOT NULL AND target_role != %s
                    UNION ALL
                    SELECT job_role as role FROM ai_analysis WHERE job_role IS NOT NULL AND job_role != %s
                ) AS combined_roles GROUP BY role ORDER BY count DESC
            ''', ('', ''))
            analytics['role_distribution'] = cursor.fetchall()
            
            # Experience level distribution (placeholder since we don't have this data)
            analytics['experience_distribution'] = [
                ('Entry Level', 0),
                ('Mid Level', 0), 
                ('Senior Level', 0)
            ]
            
            # Score distribution from both analysis tables
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN score >= 80 THEN 'Excellent (80-100)'
                        WHEN score >= 60 THEN 'Good (60-79)'
                        WHEN score >= 40 THEN 'Average (40-59)'
                        ELSE 'Needs Improvement (0-39)'
                    END as score_range,
                    COUNT(*) as count
                FROM (
                    SELECT ats_score as score FROM resume_analysis WHERE ats_score > 0
                    UNION ALL
                    SELECT resume_score as score FROM ai_analysis WHERE resume_score > 0
                ) AS combined_scores
                GROUP BY score_range
            ''')
            analytics['score_distribution'] = cursor.fetchall()
            
            return analytics
        except Exception as e:
            print(f"Error getting analytics: {str(e)}")
            return {}

def save_ai_analysis_data(resume_id, analysis_data, user_id=None, pdf_path=None):
    """Save AI analysis data to the database with user_id and PDF path"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Check if the ai_analysis table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id SERIAL PRIMARY KEY,
                    resume_id INTEGER,
                    model_used TEXT,
                    resume_score INTEGER,
                    job_role TEXT,
                    user_id INTEGER REFERENCES users(id),
                    pdf_report_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resume_id) REFERENCES resume_data (id)
                )
            """)
            
            # Insert the analysis data
            cursor.execute("""
                INSERT INTO ai_analysis (
                    resume_id, model_used, resume_score, job_role, user_id, pdf_report_path
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                resume_id,
                analysis_data.get('model_used', ''),
                analysis_data.get('resume_score', 0),
                analysis_data.get('job_role', ''),
                user_id,
                pdf_path
            ))
            
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None
        except Exception as e:
            print(f"Error saving AI analysis data: {e}")
            conn.rollback()
            raise

def get_ai_analysis_stats():
    """Get statistics about AI analyzer usage"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Check if the ai_analysis table exists
            cursor.execute("""
                SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename='ai_analysis'
            """)
            
            if not cursor.fetchone():
                return {
                    "total_analyses": 0,
                    "model_usage": [],
                    "average_score": 0,
                    "top_job_roles": []
                }
            
            # Get total number of analyses
            cursor.execute("SELECT COUNT(*) FROM ai_analysis")
            total_analyses = cursor.fetchone()[0]
            
            # Get model usage statistics
            cursor.execute("""
                SELECT model_used, COUNT(*) as count
                FROM ai_analysis
                GROUP BY model_used
                ORDER BY count DESC
            """)
            model_usage = [{"model": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Get average resume score
            cursor.execute("SELECT AVG(resume_score) FROM ai_analysis")
            average_score = cursor.fetchone()[0] or 0
            
            # Get top job roles
            cursor.execute("""
                SELECT job_role, COUNT(*) as count
                FROM ai_analysis
                GROUP BY job_role
                ORDER BY count DESC
                LIMIT 5
            """)
            top_job_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            return {
                "total_analyses": total_analyses,
                "model_usage": model_usage,
                "average_score": round(float(average_score), 1),
                "top_job_roles": top_job_roles
            }
        except Exception as e:
            print(f"Error getting AI analysis stats: {e}")
            return {
                "total_analyses": 0,
                "model_usage": [],
                "average_score": 0,
                "top_job_roles": []
            }

def get_detailed_ai_analysis_stats():
    """Get detailed statistics about AI analyzer usage including daily trends"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Check if the ai_analysis table exists
            cursor.execute("""
                SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename='ai_analysis'
            """)
            
            if not cursor.fetchone():
                return {
                    "total_analyses": 0,
                    "model_usage": [],
                    "average_score": 0,
                    "top_job_roles": [],
                    "daily_trend": [],
                    "score_distribution": [],
                    "recent_analyses": []
                }
            
            # Get total number of analyses
            cursor.execute("SELECT COUNT(*) FROM ai_analysis")
            total_analyses = cursor.fetchone()[0]
            
            # Get model usage statistics
            cursor.execute("""
                SELECT model_used, COUNT(*) as count
                FROM ai_analysis
                GROUP BY model_used
                ORDER BY count DESC
            """)
            model_usage = [{"model": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Get average resume score
            cursor.execute("SELECT AVG(resume_score) FROM ai_analysis")
            average_score = cursor.fetchone()[0] or 0
            
            # Get top job roles
            cursor.execute("""
                SELECT job_role, COUNT(*) as count
                FROM ai_analysis
                GROUP BY job_role
                ORDER BY count DESC
                LIMIT 5
            """)
            top_job_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Get daily trend for the last 7 days
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM ai_analysis
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            daily_trend = [{"date": str(row[0]), "count": row[1]} for row in cursor.fetchall()]
            
            # Get score distribution
            score_ranges = [
                {"min": 0, "max": 20, "range": "0-20"},
                {"min": 21, "max": 40, "range": "21-40"},
                {"min": 41, "max": 60, "range": "41-60"},
                {"min": 61, "max": 80, "range": "61-80"},
                {"min": 81, "max": 100, "range": "81-100"}
            ]
            
            score_distribution = []
            for range_info in score_ranges:
                cursor.execute("""
                    SELECT COUNT(*) FROM ai_analysis 
                    WHERE resume_score >= %s AND resume_score <= %s
                """, (range_info["min"], range_info["max"]))
                count = cursor.fetchone()[0]
                score_distribution.append({"range": range_info["range"], "count": count})
            
            # Get recent analyses
            cursor.execute("""
                SELECT model_used, resume_score, job_role, created_at
                FROM ai_analysis
                ORDER BY created_at DESC
                LIMIT 5
            """)
            recent_analyses = [
                {
                    "model": row[0],
                    "score": row[1],
                    "job_role": row[2],
                    "date": str(row[3])
                } for row in cursor.fetchall()
            ]
            
            return {
                "total_analyses": total_analyses,
                "model_usage": model_usage,
                "average_score": round(float(average_score), 1),
                "top_job_roles": top_job_roles,
                "daily_trend": daily_trend,
                "score_distribution": score_distribution,
                "recent_analyses": recent_analyses
            }
        except Exception as e:
            print(f"Error getting detailed AI analysis stats: {e}")
            return {
                "total_analyses": 0,
                "model_usage": [],
                "average_score": 0,
                "top_job_roles": [],
                "daily_trend": [],
                "score_distribution": [],
                "recent_analyses": []
            }

def reset_ai_analysis_stats():
    """Reset AI analysis statistics by truncating the ai_analysis table"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Check if the ai_analysis table exists
            cursor.execute("""
                SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename='ai_analysis'
            """)
            
            if not cursor.fetchone():
                return {"success": False, "message": "AI analysis table does not exist"}
            
            # Delete all records from the ai_analysis table
            cursor.execute("DELETE FROM ai_analysis")
            conn.commit()
            
            return {"success": True, "message": "AI analysis statistics have been reset successfully"}
        except Exception as e:
            conn.rollback()
            print(f"Error resetting AI analysis stats: {e}")
            return {"success": False, "message": f"Error resetting AI analysis statistics: {str(e)}"}

def reset_all_dashboard_data():
    """Reset all dashboard data except admin credentials"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Tables to reset (excluding admin)
            tables_to_reset = [
                'resume_data',
                'resume_skills', 
                'resume_analysis',
                'ai_analysis',
                'admin_logs'
            ]
            
            total_deleted = 0
            reset_details = []
            
            for table_name in tables_to_reset:
                try:
                    # Check if table exists
                    cursor.execute("""
                        SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename=%s
                    """, (table_name,))
                    
                    if cursor.fetchone():
                        # Count records before deletion
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count_before = cursor.fetchone()[0]
                        
                        # Delete all records
                        cursor.execute(f"DELETE FROM {table_name}")
                        
                        reset_details.append(f"{table_name}: {count_before} records deleted")
                        total_deleted += count_before
                    else:
                        reset_details.append(f"{table_name}: Table does not exist")
                        
                except Exception as e:
                    reset_details.append(f"{table_name}: Error - {str(e)}")
            
            conn.commit()
            
            return {
                "success": True,
                "message": f"Dashboard data reset completed. Total records deleted: {total_deleted}",
                "details": reset_details
            }
            
        except Exception as e:
            conn.rollback()
            print(f"Error resetting dashboard data: {e}")
            return {"success": False, "message": f"Error resetting dashboard data: {str(e)}"}

def get_database_status():
    """Get current status of all collections (cached for 30 seconds)"""
    # Check cache first
    cached = get_cached('database_status')
    if cached:
        return cached
    
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            tables = [
                'resume_data',
                'resume_skills', 
                'resume_analysis',
                'ai_analysis',
                'admin',
                'admin_logs'
            ]
            
            status = {}
            total_records = 0
            
            for table_name in tables:
                try:
                    # Check if table exists
                    cursor.execute("""
                        SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename=%s
                    """, (table_name,))
                    
                    if cursor.fetchone():
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        status[table_name] = count
                        total_records += count
                    else:
                        status[table_name] = "Table does not exist"
                except Exception as e:
                    status[table_name] = f"Error: {str(e)}"
            
            result = {
                "success": True,
                "tables": status,
                "total_records": total_records
            }
            
            # Cache the result
            set_cache('database_status', result)
            return result
            
        except Exception as e:
            return {"success": False, "message": f"Error getting database status: {str(e)}"}

def clear_specific_table(table_name):
    """Clear a specific table"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Don't allow clearing admin table through this function
            if table_name == 'admin':
                return {"success": False, "message": "Cannot clear admin table. Use reset_admin_credentials() instead."}
            
            # Check if table exists
            cursor.execute("""
                SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename=%s
            """, (table_name,))
            
            if not cursor.fetchone():
                return {"success": False, "message": f"Table {table_name} does not exist"}
            
            # Count records before deletion
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count_before = cursor.fetchone()[0]
            
            # Delete all records
            cursor.execute(f"DELETE FROM {table_name}")
            conn.commit()
            
            return {
                "success": True,
                "message": f"Cleared {table_name}: {count_before} records deleted"
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"Error clearing {table_name}: {str(e)}"}

def reset_sequence_counters():
    """Reset PostgreSQL sequence counters to start from 1"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Reset the sequences to start from 1
            cursor.execute("SELECT setval('resume_data_id_seq', 1, false)")
            cursor.execute("SELECT setval('resume_analysis_id_seq', 1, false)")
            cursor.execute("SELECT setval('ai_analysis_id_seq', 1, false)")
            conn.commit()
            
            return {"success": True, "message": "Sequence counters reset to start from 1"}
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"Error resetting sequences: {str(e)}"}

def setup_feedback_table():
    """Create feedback table in main database"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    rating INTEGER,
                    usability_score INTEGER,
                    feature_satisfaction INTEGER,
                    missing_features TEXT,
                    improvement_suggestions TEXT,
                    user_experience TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating feedback table: {e}")
            return False

def save_feedback_to_main_db(feedback_data):
    """Save feedback to main database"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO feedback (
                    rating, usability_score, feature_satisfaction,
                    missing_features, improvement_suggestions,
                    user_experience
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                feedback_data['rating'],
                feedback_data['usability_score'],
                feedback_data['feature_satisfaction'],
                feedback_data['missing_features'],
                feedback_data['improvement_suggestions'],
                feedback_data['user_experience']
            ))
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None
        except Exception as e:
            print(f"Error saving feedback: {e}")
            conn.rollback()
            return None

def get_all_feedback():
    """Get all feedback from main database"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, rating, usability_score, feature_satisfaction,
                       missing_features, improvement_suggestions, user_experience,
                       timestamp
                FROM feedback
                ORDER BY timestamp DESC
            ''')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting feedback: {e}")
            return []

def get_feedback_stats():
    """Get feedback statistics from main database"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_responses,
                    AVG(rating) as avg_rating,
                    AVG(usability_score) as avg_usability,
                    AVG(feature_satisfaction) as avg_satisfaction
                FROM feedback
            ''')
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                return {
                    'total_responses': result[0],
                    'avg_rating': round(float(result[1]), 1) if result[1] else 0,
                    'avg_usability': round(float(result[2]), 1) if result[2] else 0,
                    'avg_satisfaction': round(float(result[3]), 1) if result[3] else 0
                }
            else:
                return {
                    'total_responses': 0,
                    'avg_rating': 0,
                    'avg_usability': 0,
                    'avg_satisfaction': 0
                }
        except Exception as e:
            print(f"Error getting feedback stats: {e}")
            return {
                'total_responses': 0,
                'avg_rating': 0,
                'avg_usability': 0,
                'avg_satisfaction': 0
            }

def setup_uploaded_files_table():
    """Create uploaded files table in main database"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS uploaded_files (
                    id SERIAL PRIMARY KEY,
                    filename TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    file_type TEXT,
                    upload_source TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating uploaded_files table: {e}")
            return False

def save_uploaded_file_info(filename, original_name, file_path, file_size, file_type, upload_source, user_id=None):
    """Save uploaded file information to database with user_id"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO uploaded_files (
                    filename, original_name, file_path, file_size, file_type, upload_source, user_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (filename, original_name, file_path, file_size, file_type, upload_source, user_id))
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None
        except Exception as e:
            print(f"Error saving file info: {e}")
            conn.rollback()
            return None

def get_all_uploaded_files():
    """Get all uploaded files information"""
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, filename, original_name, file_path, file_size, 
                       file_type, upload_source, timestamp
                FROM uploaded_files
                ORDER BY timestamp DESC
            ''')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting uploaded files: {e}")
            return []
