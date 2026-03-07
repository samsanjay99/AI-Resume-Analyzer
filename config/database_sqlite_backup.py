import sqlite3
from datetime import datetime

def get_database_connection():
    """Create and return a database connection"""
    import os
    db_path = 'resume_data.db'
    
    # Debug: Check if database file exists
    if os.path.exists(db_path):
        print(f"Database file exists at: {os.path.abspath(db_path)}")
        print(f"Database file size: {os.path.getsize(db_path)} bytes")
    else:
        print(f"Database file does not exist, will be created at: {os.path.abspath(db_path)}")
    
    conn = sqlite3.connect(db_path)
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Create resume_data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_email TEXT NOT NULL,
        action TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create admin table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    
    # Create default admin if none exists
    create_default_admin()
    
    # Setup additional tables
    setup_feedback_table()
    setup_uploaded_files_table()

def save_resume_data(data):
    """Save resume data to database"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        personal_info = data.get('personal_info', {})
        
        cursor.execute('''
        INSERT INTO resume_data (
            name, email, phone, linkedin, github, portfolio,
            summary, target_role, target_category, education, 
            experience, projects, skills, template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            data.get('template', '')
        ))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving resume data: {str(e)}")
        conn.rollback()
        return None
    finally:
        conn.close()

def save_analysis_data(resume_id, analysis):
    """Save resume analysis data"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO resume_analysis (
            resume_id, ats_score, keyword_match_score,
            format_score, section_score, missing_skills,
            recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume_id,
            float(analysis.get('ats_score', 0)),
            float(analysis.get('keyword_match_score', 0)),
            float(analysis.get('format_score', 0)),
            float(analysis.get('section_score', 0)),
            analysis.get('missing_skills', ''),
            analysis.get('recommendations', '')
        ))
        
        conn.commit()
    except Exception as e:
        print(f"Error saving analysis data: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def get_resume_stats():
    """Get statistics about resumes"""
    conn = get_database_connection()
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
        
        return {
            'total_resumes': total_resumes,
            'avg_ats_score': round(avg_ats_score, 2),
            'recent_activity': recent_activity
        }
    except Exception as e:
        print(f"Error getting resume stats: {str(e)}")
        return None
    finally:
        conn.close()

def log_admin_action(admin_email, action):
    """Log admin login/logout actions"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO admin_logs (admin_email, action)
        VALUES (?, ?)
        ''', (admin_email, action))
        conn.commit()
    except Exception as e:
        print(f"Error logging admin action: {str(e)}")
    finally:
        conn.close()

def get_admin_logs():
    """Get all admin login/logout logs"""
    conn = get_database_connection()
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
    finally:
        conn.close()

def get_all_resume_data():
    """Get all resume data for admin dashboard"""
    conn = get_database_connection()
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
    finally:
        conn.close()

def verify_admin(email, password):
    """Verify admin credentials"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Debug: Print what we're looking for
        print(f"Verifying admin - Email: '{email}', Password: '{password}'")
        
        # Check all admins first
        cursor.execute('SELECT email, password FROM admin')
        all_admins = cursor.fetchall()
        print(f"All admins in database: {all_admins}")
        
        # Now check for exact match
        cursor.execute('SELECT * FROM admin WHERE email = ? AND password = ?', (email, password))
        result = cursor.fetchone()
        print(f"Query result: {result}")
        
        return bool(result)
    except Exception as e:
        print(f"Error verifying admin: {str(e)}")
        return False
    finally:
        conn.close()

def add_admin(email, password):
    """Add a new admin"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO admin (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding admin: {str(e)}")
        return False
    finally:
        conn.close()

def create_default_admin():
    """Create default admin if no admin exists"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Ensure admin table exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            cursor.execute('INSERT INTO admin (email, password) VALUES (?, ?)', 
                         ('sam@gmail.com', 'sanjay2026'))
            conn.commit()
            print("✅ Default admin created: sam@gmail.com")
            
            # Verify the admin was created
            cursor.execute('SELECT email, password FROM admin WHERE email = ?', ('sam@gmail.com',))
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
    finally:
        conn.close()

def debug_admin_table():
    """Debug function to check admin table contents"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if admin table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin'")
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
            cursor.execute("PRAGMA table_info(admin)")
            schema = cursor.fetchall()
            print(f"🏗️ Admin table schema:")
            for col in schema:
                print(f"   - {col[1]} ({col[2]})")
        
        return True
    except Exception as e:
        print(f"❌ Error debugging admin table: {str(e)}")
        return False
    finally:
        conn.close()

def reset_admin_credentials():
    """Reset admin credentials to default"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Delete all existing admins
        cursor.execute('DELETE FROM admin')
        
        # Create default admin
        cursor.execute('INSERT INTO admin (email, password) VALUES (?, ?)', 
                     ('sam@gmail.com', 'sanjay2026'))
        conn.commit()
        
        print("✅ Admin credentials reset to default: sam@gmail.com / sanjay2026")
        return True
    except Exception as e:
        print(f"❌ Error resetting admin credentials: {str(e)}")
        return False
    finally:
        conn.close()



def get_admin_analytics():
    """Get analytics data for admin dashboard"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        analytics = {}
        
        # Total users (distinct emails)
        cursor.execute('SELECT COUNT(DISTINCT email) FROM resume_data WHERE email IS NOT NULL AND email != ""')
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
            )
        ''')
        result = cursor.fetchone()[0]
        analytics['avg_score'] = round(result, 2) if result else 0
        
        # Role distribution from both target_role and ai_analysis job_role
        cursor.execute('''
            SELECT role, COUNT(*) as count FROM (
                SELECT target_role as role FROM resume_data WHERE target_role IS NOT NULL AND target_role != ""
                UNION ALL
                SELECT job_role as role FROM ai_analysis WHERE job_role IS NOT NULL AND job_role != ""
            ) GROUP BY role ORDER BY count DESC
        ''')
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
            )
            GROUP BY score_range
        ''')
        analytics['score_distribution'] = cursor.fetchall()
        
        return analytics
    except Exception as e:
        print(f"Error getting analytics: {str(e)}")
        return {}
    finally:
        conn.close()

def save_ai_analysis_data(resume_id, analysis_data):
    """Save AI analysis data to the database"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the ai_analysis table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER,
                model_used TEXT,
                resume_score INTEGER,
                job_role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resume_data (id)
            )
        """)
        
        # Insert the analysis data
        cursor.execute("""
            INSERT INTO ai_analysis (
                resume_id, model_used, resume_score, job_role
            ) VALUES (?, ?, ?, ?)
        """, (
            resume_id,
            analysis_data.get('model_used', ''),
            analysis_data.get('resume_score', 0),
            analysis_data.get('job_role', '')
        ))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving AI analysis data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_ai_analysis_stats():
    """Get statistics about AI analyzer usage"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the ai_analysis table exists
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
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
            "average_score": round(average_score, 1),
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
    finally:
        conn.close()

def get_detailed_ai_analysis_stats():
    """Get detailed statistics about AI analyzer usage including daily trends"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the ai_analysis table exists
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
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
            WHERE created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        daily_trend = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
        
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
                WHERE resume_score >= ? AND resume_score <= ?
            """, (range_info["min"], range_info["max"]))
            count = cursor.fetchone()[0]
            score_distribution.append({"range": range_info["range"], "count": count})
        
        # Get recent analyses
        cursor.execute("""
            SELECT model_used, resume_score, job_role, datetime(created_at) as date
            FROM ai_analysis
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_analyses = [
            {
                "model": row[0],
                "score": row[1],
                "job_role": row[2],
                "date": row[3]
            } for row in cursor.fetchall()
        ]
        
        return {
            "total_analyses": total_analyses,
            "model_usage": model_usage,
            "average_score": round(average_score, 1),
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
    finally:
        conn.close()

def reset_ai_analysis_stats():
    """Reset AI analysis statistics by truncating the ai_analysis table"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if the ai_analysis table exists
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='ai_analysis'
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
    finally:
        conn.close()

def reset_all_dashboard_data():
    """Reset all dashboard data except admin credentials"""
    conn = get_database_connection()
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
                    SELECT name FROM sqlite_master WHERE type='table' AND name=?
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
    finally:
        conn.close()

def get_database_status():
    """Get current status of all collections"""
    conn = get_database_connection()
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
                    SELECT name FROM sqlite_master WHERE type='table' AND name=?
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
        
        return {
            "success": True,
            "tables": status,
            "total_records": total_records
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error getting database status: {str(e)}"}
    finally:
        conn.close()

def clear_specific_table(table_name):
    """Clear a specific table"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Don't allow clearing admin table through this function
        if table_name == 'admin':
            return {"success": False, "message": "Cannot clear admin table. Use reset_admin_credentials() instead."}
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name=?
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
    finally:
        conn.close()

def reset_sequence_counters():
    """Reset SQLite sequence counters to start from 1"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Reset the sequences to start from 0 (next insert will be 1)
        cursor.execute('UPDATE sqlite_sequence SET seq = 0 WHERE name = "resume_data"')
        cursor.execute('UPDATE sqlite_sequence SET seq = 0 WHERE name = "resume_analysis"')
        cursor.execute('UPDATE sqlite_sequence SET seq = 0 WHERE name = "ai_analysis"')
        conn.commit()
        
        return {"success": True, "message": "Sequence counters reset to start from 1"}
        
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Error resetting sequences: {str(e)}"}
    finally:
        conn.close()

def setup_feedback_table():
    """Create feedback table in main database"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rating INTEGER,
                usability_score INTEGER,
                feature_satisfaction INTEGER,
                missing_features TEXT,
                improvement_suggestions TEXT,
                user_experience TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating feedback table: {e}")
        return False
    finally:
        conn.close()

def save_feedback_to_main_db(feedback_data):
    """Save feedback to main database"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO feedback (
                rating, usability_score, feature_satisfaction,
                missing_features, improvement_suggestions,
                user_experience
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            feedback_data['rating'],
            feedback_data['usability_score'],
            feedback_data['feature_satisfaction'],
            feedback_data['missing_features'],
            feedback_data['improvement_suggestions'],
            feedback_data['user_experience']
        ))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving feedback: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_all_feedback():
    """Get all feedback from main database"""
    conn = get_database_connection()
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
    finally:
        conn.close()

def get_feedback_stats():
    """Get feedback statistics from main database"""
    conn = get_database_connection()
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
                'avg_rating': round(result[1], 1) if result[1] else 0,
                'avg_usability': round(result[2], 1) if result[2] else 0,
                'avg_satisfaction': round(result[3], 1) if result[3] else 0
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
    finally:
        conn.close()

def setup_uploaded_files_table():
    """Create uploaded files table in main database"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploaded_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                upload_source TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating uploaded_files table: {e}")
        return False
    finally:
        conn.close()

def save_uploaded_file_info(filename, original_name, file_path, file_size, file_type, upload_source):
    """Save uploaded file information to database"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO uploaded_files (
                filename, original_name, file_path, file_size, file_type, upload_source
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (filename, original_name, file_path, file_size, file_type, upload_source))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving file info: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_all_uploaded_files():
    """Get all uploaded files information"""
    conn = get_database_connection()
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
    finally:
        conn.close()