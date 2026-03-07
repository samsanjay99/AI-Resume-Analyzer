import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from config.database import get_database_connection
import io
import uuid
from plotly.subplots import make_subplots
from io import BytesIO
import time
import psycopg2

class DashboardManager:
    def __init__(self):
        # Don't store connection - use context manager in each method
        self.colors = {
            'primary': '#4CAF50',
            'secondary': '#2196F3',
            'warning': '#FFA726',
            'danger': '#F44336',
            'info': '#00BCD4',
            'success': '#66BB6A',
            'purple': '#9C27B0',
            'background': '#1E1E1E',
            'card': '#2D2D2D',
            'text': '#FFFFFF',
            'subtext': '#B0B0B0'
        }
    
    def execute_with_retry(self, query_func, max_retries=3, retry_delay=1):
        """Execute database query with retry logic for SSL connection errors"""
        for attempt in range(max_retries):
            try:
                return query_func()
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    st.error(f"Database connection error after {max_retries} attempts: {str(e)}")
                    return None
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                return None
        
    def apply_dashboard_style(self):
        """Apply custom styling for dashboard"""
        st.markdown("""
            <style>
                .dashboard-title {
                    font-size: 2.5rem;
                    font-weight: bold;
                    margin-bottom: 2rem;
                    color: white;
                    text-align: center;
                }
                
                .metric-card {
                    background-color: #2D2D2D;
                    border-radius: 15px;
                    padding: 1.5rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    transition: transform 0.3s ease;
                    height: 100%;
                }
                
                .metric-card:hover {
                    transform: translateY(-5px);
                }
                
                .metric-value {
                    font-size: 2.5rem;
                    font-weight: bold;
                    color: #4CAF50;
                    margin: 0.5rem 0;
                }
                
                .metric-label {
                    font-size: 1rem;
                    color: #B0B0B0;
                }
                
                .trend-up {
                    color: #4CAF50;
                    font-size: 1.2rem;
                }
                
                .trend-down {
                    color: #F44336;
                    font-size: 1.2rem;
                }
                
                .chart-container {
                    background-color: #2D2D2D;
                    border-radius: 15px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                }
                
                .section-title {
                    font-size: 1.5rem;
                    color: white;
                    margin: 2rem 0 1rem 0;
                }
                
                .stPlotlyChart {
                    background-color: #2D2D2D;
                    border-radius: 15px;
                    padding: 1rem;
                }
                
                div[data-testid="stHorizontalBlock"] > div {
                    background-color: #2D2D2D;
                    border-radius: 15px;
                    padding: 1rem;
                    margin: 0.5rem;
                }

                [data-testid="stMetricValue"] {
                    font-size: 2rem !important;
                }

                [data-testid="stMetricLabel"] {
                    font-size: 1rem !important;
                }
            </style>
        """, unsafe_allow_html=True)

    def get_resume_metrics(self):
        """Get resume-related metrics from database with retry logic"""
        def query():
            with get_database_connection() as conn:
                cursor = conn.cursor()

                # Get current date
                now = datetime.now()
                start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
                start_of_week = now - timedelta(days=now.weekday())
                start_of_month = now.replace(day=1)

                # Fetch metrics for different time periods
                metrics = {}
                for period, start_date in [
                    ('Today', start_of_day),
                    ('This Week', start_of_week),
                    ('This Month', start_of_month),
                    ('All Time', datetime(2000, 1, 1))
                ]:
                    cursor.execute("""
                        SELECT 
                            COUNT(DISTINCT rd.id) as total_resumes,
                            ROUND(CAST(AVG(ra.ats_score) AS numeric), 1) as avg_ats_score,
                            ROUND(CAST(AVG(ra.keyword_match_score) AS numeric), 1) as avg_keyword_score,
                            COUNT(DISTINCT CASE WHEN ra.ats_score >= 70 THEN rd.id END) as high_scoring
                        FROM resume_data rd
                        LEFT JOIN resume_analysis ra ON rd.id = ra.resume_id
                        WHERE rd.created_at >= %s
                    """, (start_date.strftime('%Y-%m-%d %H:%M:%S'),))

                    row = cursor.fetchone()
                    if row:
                        metrics[period] = {
                            'total': row[0] or 0,
                            'ats_score': float(row[1]) if row[1] else 0,
                            'keyword_score': float(row[2]) if row[2] else 0,
                            'high_scoring': row[3] or 0
                        }
                    else:
                        metrics[period] = {
                            'total': 0,
                            'ats_score': 0,
                            'keyword_score': 0,
                            'high_scoring': 0
                        }

                return metrics
        
        result = self.execute_with_retry(query)
        return result if result else {}

    def get_skill_distribution(self):
        """Get skill distribution data - simplified for PostgreSQL"""
        with get_database_connection() as conn:
            cursor = conn.cursor()

            # Get all skills and parse them in Python
            cursor.execute("SELECT skills FROM resume_data WHERE skills IS NOT NULL AND skills != ''")
            all_skills = cursor.fetchall()

            # Count skills by category
            skill_categories = {
                'Programming': 0,
                'Database': 0,
                'Cloud': 0,
                'Management': 0,
                'Other': 0
            }

            for (skills_str,) in all_skills:
                skills_lower = skills_str.lower()
                if any(keyword in skills_lower for keyword in ['python', 'java', 'javascript', 'c++', 'programming']):
                    skill_categories['Programming'] += 1
                if any(keyword in skills_lower for keyword in ['sql', 'database', 'mongodb']):
                    skill_categories['Database'] += 1
                if any(keyword in skills_lower for keyword in ['aws', 'cloud', 'azure']):
                    skill_categories['Cloud'] += 1
                if any(keyword in skills_lower for keyword in ['agile', 'scrum', 'management']):
                    skill_categories['Management'] += 1
                if not any(keyword in skills_lower for keyword in ['python', 'java', 'javascript', 'sql', 'aws', 'cloud', 'agile']):
                    skill_categories['Other'] += 1

            # Sort by count
            sorted_categories = sorted(skill_categories.items(), key=lambda x: x[1], reverse=True)
            categories = [cat for cat, _ in sorted_categories if _ > 0]
            counts = [count for _, count in sorted_categories if count > 0]

            return categories, counts

    def get_weekly_trends(self):
        """Get weekly submission trends"""
        with get_database_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            dates = [(now - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(6, -1, -1)]

            submissions = []
            for date in dates:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM resume_data 
                    WHERE DATE(created_at) = DATE(%s)
                """, (date,))
                submissions.append(cursor.fetchone()[0])

            return [d[-5:] for d in dates], submissions  # Return shortened date format

    def get_job_category_stats(self):
        """Get statistics by job category"""
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COALESCE(target_category, 'Other') as category,
                    COUNT(*) as count,
                    ROUND(CAST(AVG(CASE WHEN ra.ats_score >= 70 THEN 1 ELSE 0 END) * 100 AS numeric), 1) as success_rate
                FROM resume_data rd
                LEFT JOIN resume_analysis ra ON rd.id = ra.resume_id
                GROUP BY category
                ORDER BY count DESC
                LIMIT 5
            """)

            categories, success_rates = [], []
            for row in cursor.fetchall():
                categories.append(row[0])
                success_rates.append(float(row[2]) if row[2] else 0)

            return categories, success_rates

    def render_admin_panel(self):
        """Render admin panel with data management tools"""
        st.sidebar.markdown("### 👋 Welcome Admin!")
        st.sidebar.markdown("---")
        
        if st.sidebar.button("🚪 Logout"):
            st.session_state.is_admin = False
            st.rerun()
            
        st.sidebar.markdown("### 🛠️ Admin Tools")
        
        # Data Export Options
        export_format = st.sidebar.selectbox(
            "Export Format",
            ["Excel", "CSV", "JSON"],
            key="export_format"
        )
        
        if st.sidebar.button("📥 Export Data"):
            if export_format == "Excel":
                excel_data = self.export_to_excel()
                if excel_data:
                    st.sidebar.download_button(
                        "⬇️ Download Excel",
                        data=excel_data,
                        file_name=f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            elif export_format == "CSV":
                csv_data = self.export_to_csv()
                if csv_data:
                    st.sidebar.download_button(
                        "⬇️ Download CSV",
                        data=csv_data,
                        file_name=f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
            else:
                json_data = self.export_to_json()
                if json_data:
                    st.sidebar.download_button(
                        "⬇️ Download JSON",
                        data=json_data,
                        file_name=f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json"
                    )

        # Database Stats
        st.sidebar.markdown("### 📊 Database Stats")
        stats = self.get_database_stats()
        st.sidebar.markdown(f"""
            - Total Resumes: {stats['total_resumes']}
            - Today's Submissions: {stats['today_submissions']}
            - Storage Used: {stats['storage_size']}
        """)

    def get_resume_data(self):
        """Get all resume data with retry logic"""
        def query():
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT 
                    r.id,
                    r.name,
                    r.email,
                    r.phone,
                    r.linkedin,
                    r.github,
                    r.portfolio,
                    r.target_role,
                    r.target_category,
                    r.created_at,
                    a.ats_score,
                    a.keyword_match_score,
                    a.format_score,
                    a.section_score
                FROM resume_data r
                LEFT JOIN resume_analysis a ON r.id = a.resume_id
                ORDER BY r.created_at DESC
                ''')
                return cursor.fetchall()
        
        result = self.execute_with_retry(query)
        return result if result else []

    def render_resume_data_section(self):
        """Render resume data section with Excel download"""
        st.markdown("<h2 class='section-title'>Resume Submissions</h2>", unsafe_allow_html=True)
        
        # Get resume data
        resume_data = self.get_resume_data()
        
        if resume_data:
            # Convert to DataFrame
            columns = [
                'ID', 'Name', 'Email', 'Phone', 'LinkedIn', 'GitHub', 
                'Portfolio', 'Target Role', 'Target Category', 'Submission Date',
                'ATS Score', 'Keyword Match', 'Format Score', 'Section Score'
            ]
            df = pd.DataFrame(resume_data, columns=columns)
            
            # Format scores as percentages
            score_columns = ['ATS Score', 'Keyword Match', 'Format Score', 'Section Score']
            for col in score_columns:
                df[col] = df[col].apply(lambda x: f"{x*100:.1f}%" if pd.notnull(x) else "N/A")
            
            # Style the dataframe
            st.markdown("""
            <style>
            .resume-data {
                background-color: #2D2D2D;
                border-radius: 10px;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            </style>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="resume-data">', unsafe_allow_html=True)
                
                # Add filters
                col1, col2 = st.columns(2)
                with col1:
                    target_role = st.selectbox(
                        "Filter by Target Role",
                        options=["All"] + list(df['Target Role'].unique()),
                        key="role_filter"
                    )
                with col2:
                    target_category = st.selectbox(
                        "Filter by Category",
                        options=["All"] + list(df['Target Category'].unique()),
                        key="category_filter"
                    )
                
                # Apply filters
                filtered_df = df.copy()
                if target_role != "All":
                    filtered_df = filtered_df[filtered_df['Target Role'] == target_role]
                if target_category != "All":
                    filtered_df = filtered_df[filtered_df['Target Category'] == target_category]
                
                # Display filtered data
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Add download buttons
                col1, col2 = st.columns(2)
                with col1:
                    # Download filtered data
                    excel_buffer = BytesIO()
                    filtered_df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download Filtered Data",
                        data=excel_buffer,
                        file_name=f"resume_data_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_filtered_data"
                    )
                
                with col2:
                    # Download all data
                    excel_buffer_all = BytesIO()
                    df.to_excel(excel_buffer_all, index=False, engine='openpyxl')
                    excel_buffer_all.seek(0)
                    
                    st.download_button(
                        label="📥 Download All Data",
                        data=excel_buffer_all,
                        file_name=f"resume_data_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_all_data"
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No resume submissions available")

    def render_admin_section(self):
        """Render admin section with logs and Excel download"""
        # Render resume data section
        self.render_resume_data_section()
        
        # Render admin logs section
        st.markdown("<h2 class='section-title'>Admin Activity Logs</h2>", unsafe_allow_html=True)
        
        # Get admin logs
        admin_logs = self.get_admin_logs()
        
        if admin_logs:
            # Convert to DataFrame
            df = pd.DataFrame(admin_logs, columns=['Admin Email', 'Action', 'Timestamp'])
            
            # Style the dataframe
            st.markdown("""
            <style>
            .admin-logs {
                background-color: #2D2D2D;
                border-radius: 10px;
                padding: 1rem;
            }
            </style>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="admin-logs">', unsafe_allow_html=True)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Add download button
                excel_buffer = BytesIO()
                df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                
                st.download_button(
                    label="📥 Download Admin Logs as Excel",
                    data=excel_buffer,
                    file_name=f"admin_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_admin_logs"
                )
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No admin activity logs available")

    def export_to_excel(self):
        """Export data to Excel format"""
        query = """
            SELECT 
                rd.name, rd.email, rd.phone, rd.linkedin, rd.github, rd.portfolio,
                rd.summary, rd.target_role, rd.target_category,
                rd.education, rd.experience, rd.projects, rd.skills,
                ra.ats_score, ra.keyword_match_score, ra.format_score, ra.section_score,
                ra.missing_skills, ra.recommendations,
                rd.created_at
            FROM resume_data rd
            LEFT JOIN resume_analysis ra ON rd.id = ra.resume_id
        """
        try:
            with get_database_connection() as conn:
                df = pd.read_sql_query(query, conn)
            
            # Create Excel writer object
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Write main data
                df.to_excel(writer, sheet_name='Resume Data', index=False)
                
                # Get the workbook and the worksheet
                workbook = writer.book
                worksheet = writer.sheets['Resume Data']
                
                # Add formatting
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Write headers with formatting
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    
                # Auto-adjust columns' width
                for i, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    ) + 2
                    worksheet.set_column(i, i, min(max_length, 50))
            
            # Return the Excel file
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            st.error(f"Error exporting to Excel: {str(e)}")
            return None

    def export_to_csv(self):
        """Export data to CSV format"""
        query = """
            SELECT 
                rd.name, rd.email, rd.phone, rd.linkedin, rd.github, rd.portfolio,
                rd.summary, rd.target_role, rd.target_category,
                rd.education, rd.experience, rd.projects, rd.skills,
                ra.ats_score, ra.keyword_match_score, ra.format_score, ra.section_score,
                ra.missing_skills, ra.recommendations,
                rd.created_at
            FROM resume_data rd
            LEFT JOIN resume_analysis ra ON rd.id = ra.resume_id
        """
        try:
            with get_database_connection() as conn:
                df = pd.read_sql_query(query, conn)
            return df.to_csv(index=False).encode('utf-8')
        except Exception as e:
            st.error(f"Error exporting to CSV: {str(e)}")
            return None

    def export_to_json(self):
        """Export data to JSON format"""
        query = """
            SELECT 
                rd.*, ra.*
            FROM resume_data rd
            LEFT JOIN resume_analysis ra ON rd.id = ra.resume_id
        """
        try:
            with get_database_connection() as conn:
                df = pd.read_sql_query(query, conn)
            return df.to_json(orient='records', date_format='iso')
        except Exception as e:
            st.error(f"Error exporting to JSON: {str(e)}")
            return None

    def get_database_stats(self):
        """Get database statistics"""
        with get_database_connection() as conn:
            cursor = conn.cursor()
            stats = {}
            
            # Total resumes
            cursor.execute("SELECT COUNT(*) FROM resume_data")
            stats['total_resumes'] = cursor.fetchone()[0]
            
            # Today's submissions
            cursor.execute("""
                SELECT COUNT(*) 
                FROM resume_data 
                WHERE DATE(created_at) = CURRENT_DATE
            """)
            stats['today_submissions'] = cursor.fetchone()[0]
            
            # Database size (PostgreSQL - simplified)
            stats['storage_size'] = "Cloud Storage"
            
            return stats

    def get_admin_logs(self):
        """Get admin logs"""
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
                print(f"Error fetching admin logs: {str(e)}")
                return []

    # ==================== MULTI-USER FEATURES ====================

    def get_all_users_stats(self):
        """Get statistics for all users with retry logic"""
        def query():
            with get_database_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT
                        u.id,
                        u.email,
                        u.full_name,
                        u.created_at,
                        u.last_login,
                        u.is_active,
                        COUNT(DISTINCT rd.id) as total_resumes,
                        COUNT(DISTINCT ra.id) as total_analyses,
                        COUNT(DISTINCT aa.id) as total_ai_analyses,
                        COALESCE(AVG(ra.ats_score), 0) as avg_ats_score,
                        COALESCE(AVG(aa.resume_score), 0) as avg_ai_score
                    FROM users u
                    LEFT JOIN resume_data rd ON u.id = rd.user_id
                    LEFT JOIN resume_analysis ra ON u.id = ra.user_id
                    LEFT JOIN ai_analysis aa ON u.id = aa.user_id
                    GROUP BY u.id, u.email, u.full_name, u.created_at, u.last_login, u.is_active
                    ORDER BY u.created_at DESC
                """)

                users = []
                for row in cursor.fetchall():
                    users.append({
                        'id': row[0],
                        'email': row[1],
                        'full_name': row[2],
                        'created_at': row[3],
                        'last_login': row[4],
                        'is_active': row[5],
                        'total_resumes': row[6],
                        'total_analyses': row[7],
                        'total_ai_analyses': row[8],
                        'avg_ats_score': round(float(row[9]), 2) if row[9] else 0,
                        'avg_ai_score': round(float(row[10]), 2) if row[10] else 0
                    })

                return users

        return self.execute_with_retry(query) or []

    def get_system_wide_stats(self):
        """Get system-wide statistics with retry logic"""
        def query():
            with get_database_connection() as conn:
                cursor = conn.cursor()

                stats = {}

                # Total users
                cursor.execute("SELECT COUNT(*) FROM users")
                stats['total_users'] = cursor.fetchone()[0]

                # Active users (logged in last 30 days)
                cursor.execute("""
                    SELECT COUNT(*) FROM users
                    WHERE last_login >= CURRENT_DATE - INTERVAL '30 days'
                """)
                stats['active_users'] = cursor.fetchone()[0]

                # New users this month
                cursor.execute("""
                    SELECT COUNT(*) FROM users
                    WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
                """)
                stats['new_users_month'] = cursor.fetchone()[0]

                # Total resumes
                cursor.execute("SELECT COUNT(*) FROM resume_data")
                stats['total_resumes'] = cursor.fetchone()[0]

                # Total analyses
                cursor.execute("SELECT COUNT(*) FROM resume_analysis")
                stats['total_standard_analyses'] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM ai_analysis")
                stats['total_ai_analyses'] = cursor.fetchone()[0]

                # Average scores
                cursor.execute("SELECT AVG(ats_score) FROM resume_analysis WHERE ats_score > 0")
                avg_ats = cursor.fetchone()[0]
                stats['avg_ats_score'] = round(float(avg_ats), 2) if avg_ats else 0

                cursor.execute("SELECT AVG(resume_score) FROM ai_analysis WHERE resume_score > 0")
                avg_ai = cursor.fetchone()[0]
                stats['avg_ai_score'] = round(float(avg_ai), 2) if avg_ai else 0

                # User growth (last 7 days)
                cursor.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM users
                    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """)
                stats['user_growth'] = cursor.fetchall()

                # Activity by day (last 7 days)
                cursor.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM resume_data
                    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """)
                stats['activity_by_day'] = cursor.fetchall()

                return stats

        return self.execute_with_retry(query) or {}

    def get_user_engagement_metrics(self):
        """Get user engagement metrics with retry logic"""
        def query():
            with get_database_connection() as conn:
                cursor = conn.cursor()

                metrics = {}

                # Users by activity level
                cursor.execute("""
                    SELECT
                        CASE
                            WHEN resume_count = 0 THEN 'Inactive'
                            WHEN resume_count <= 2 THEN 'Low Activity'
                            WHEN resume_count <= 5 THEN 'Medium Activity'
                            ELSE 'High Activity'
                        END as activity_level,
                        COUNT(*) as user_count
                    FROM (
                        SELECT u.id, COUNT(rd.id) as resume_count
                        FROM users u
                        LEFT JOIN resume_data rd ON u.id = rd.user_id
                        GROUP BY u.id
                    ) as user_activity
                    GROUP BY activity_level
                """)
                metrics['activity_distribution'] = cursor.fetchall()

                # Most active users
                cursor.execute("""
                    SELECT
                        u.email,
                        u.full_name,
                        COUNT(DISTINCT rd.id) as resumes,
                        COUNT(DISTINCT ra.id) as analyses
                    FROM users u
                    LEFT JOIN resume_data rd ON u.id = rd.user_id
                    LEFT JOIN resume_analysis ra ON u.id = ra.user_id
                    GROUP BY u.id, u.email, u.full_name
                    HAVING COUNT(DISTINCT rd.id) > 0
                    ORDER BY resumes DESC, analyses DESC
                    LIMIT 10
                """)
                metrics['top_users'] = cursor.fetchall()

                # Analysis type distribution
                cursor.execute("""
                    SELECT
                        'Standard Analysis' as type,
                        COUNT(*) as count
                    FROM resume_analysis
                    UNION ALL
                    SELECT
                        'AI Analysis' as type,
                        COUNT(*) as count
                    FROM ai_analysis
                """)
                metrics['analysis_types'] = cursor.fetchall()

                return metrics

        return self.execute_with_retry(query) or {}

    def render_user_management_section(self):
        """Render user management section for multi-user admin"""
        st.markdown("<h2 class='section-title'>👥 User Management</h2>", unsafe_allow_html=True)

        # Get all users stats
        users = self.get_all_users_stats()

        if users:
            # Convert to DataFrame
            df = pd.DataFrame(users)

            # Format dates
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
            df['last_login'] = pd.to_datetime(df['last_login']).dt.strftime('%Y-%m-%d %H:%M')

            # Add filters
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox(
                    "Filter by Status",
                    options=["All", "Active", "Inactive"],
                    key="user_status_filter"
                )
            with col2:
                activity_filter = st.selectbox(
                    "Filter by Activity",
                    options=["All", "Has Resumes", "No Resumes"],
                    key="user_activity_filter"
                )
            with col3:
                sort_by = st.selectbox(
                    "Sort by",
                    options=["Created Date", "Last Login", "Total Resumes", "Avg Score"],
                    key="user_sort"
                )

            # Apply filters
            filtered_df = df.copy()
            if status_filter == "Active":
                filtered_df = filtered_df[filtered_df['is_active'] == True]
            elif status_filter == "Inactive":
                filtered_df = filtered_df[filtered_df['is_active'] == False]

            if activity_filter == "Has Resumes":
                filtered_df = filtered_df[filtered_df['total_resumes'] > 0]
            elif activity_filter == "No Resumes":
                filtered_df = filtered_df[filtered_df['total_resumes'] == 0]

            # Apply sorting
            if sort_by == "Last Login":
                filtered_df = filtered_df.sort_values('last_login', ascending=False)
            elif sort_by == "Total Resumes":
                filtered_df = filtered_df.sort_values('total_resumes', ascending=False)
            elif sort_by == "Avg Score":
                filtered_df = filtered_df.sort_values('avg_ats_score', ascending=False)

            # Display user table
            st.dataframe(
                filtered_df[[
                    'email', 'full_name', 'created_at', 'last_login',
                    'is_active', 'total_resumes', 'total_analyses',
                    'total_ai_analyses', 'avg_ats_score', 'avg_ai_score'
                ]],
                use_container_width=True,
                hide_index=True
            )

            # Download button
            excel_buffer = BytesIO()
            filtered_df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)

            st.download_button(
                label="📥 Download User Data",
                data=excel_buffer,
                file_name=f"user_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_user_data"
            )
        else:
            st.info("No users found in the system")

    def render_system_analytics_section(self):
        """Render system-wide analytics for multi-user platform"""
        st.markdown("<h2 class='section-title'>📊 System Analytics</h2>", unsafe_allow_html=True)

        stats = self.get_system_wide_stats()

        if stats:
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    label="Total Users",
                    value=stats.get('total_users', 0),
                    delta=f"+{stats.get('new_users_month', 0)} this month"
                )

            with col2:
                active_rate = (stats.get('active_users', 0) / stats.get('total_users', 1) * 100) if stats.get('total_users', 0) > 0 else 0
                st.metric(
                    label="Active Users (30d)",
                    value=stats.get('active_users', 0),
                    delta=f"{active_rate:.1f}% of total"
                )

            with col3:
                st.metric(
                    label="Total Resumes",
                    value=stats.get('total_resumes', 0)
                )

            with col4:
                total_analyses = stats.get('total_standard_analyses', 0) + stats.get('total_ai_analyses', 0)
                st.metric(
                    label="Total Analyses",
                    value=total_analyses
                )

            # User growth chart
            if stats.get('user_growth'):
                st.markdown("### User Growth (Last 7 Days)")
                growth_df = pd.DataFrame(stats['user_growth'], columns=['Date', 'New Users'])
                fig = px.line(growth_df, x='Date', y='New Users', markers=True)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white'}
                )
                st.plotly_chart(fig, use_container_width=True)

            # Activity chart
            if stats.get('activity_by_day'):
                st.markdown("### Platform Activity (Last 7 Days)")
                activity_df = pd.DataFrame(stats['activity_by_day'], columns=['Date', 'Resumes Created'])
                fig = px.bar(activity_df, x='Date', y='Resumes Created')
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white'}
                )
                st.plotly_chart(fig, use_container_width=True)

    def render_engagement_metrics_section(self):
        """Render user engagement metrics"""
        st.markdown("<h2 class='section-title'>📈 User Engagement</h2>", unsafe_allow_html=True)

        metrics = self.get_user_engagement_metrics()

        if metrics:
            col1, col2 = st.columns(2)

            with col1:
                # Activity distribution
                if metrics.get('activity_distribution'):
                    st.markdown("### User Activity Distribution")
                    activity_df = pd.DataFrame(
                        metrics['activity_distribution'],
                        columns=['Activity Level', 'User Count']
                    )
                    fig = px.pie(
                        activity_df,
                        values='User Count',
                        names='Activity Level',
                        color_discrete_sequence=px.colors.sequential.Teal
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font={'color': 'white'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Analysis type distribution
                if metrics.get('analysis_types'):
                    st.markdown("### Analysis Type Distribution")
                    analysis_df = pd.DataFrame(
                        metrics['analysis_types'],
                        columns=['Type', 'Count']
                    )
                    fig = px.bar(
                        analysis_df,
                        x='Type',
                        y='Count',
                        color='Type'
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font={'color': 'white'},
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Top users table
            if metrics.get('top_users'):
                st.markdown("### Top 10 Most Active Users")
                top_users_df = pd.DataFrame(
                    metrics['top_users'],
                    columns=['Email', 'Full Name', 'Resumes', 'Analyses']
                )
                st.dataframe(top_users_df, use_container_width=True, hide_index=True)


    def render_dashboard(self):
        """Main dashboard rendering function"""
        # Apply styling
        st.markdown("""
            <style>
                .dashboard-container {
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    padding: 2rem;
                    border-radius: 20px;
                    margin: -1rem -1rem 2rem -1rem;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }
                .dashboard-title {
                    color: #4FD1C5;
                    font-size: 2.5rem;
                    margin-bottom: 0.5rem;
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                }
                .dashboard-icon {
                    background: rgba(79, 209, 197, 0.2);
                    padding: 0.5rem;
                    border-radius: 12px;
                }
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 1.5rem;
                    margin-top: 2rem;
                }
                .stat-card {
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    padding: 1.5rem;
                    border-radius: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    transition: all 0.3s ease;
                }
                .stat-card:hover {
                    transform: translateY(-5px);
                    background: rgba(255, 255, 255, 0.1);
                }
                .stat-value {
                    font-size: 2.5rem;
                    font-weight: bold;
                    margin: 0;
                    color: #4FD1C5;
                }
                .stat-label {
                    font-size: 1rem;
                    color: rgba(255, 255, 255, 0.7);
                    margin: 0.5rem 0 0 0;
                }
                .section-title {
                    color: #4FD1C5;
                    font-size: 1.5rem;
                    margin: 1rem 0 0.5rem 0;
                    padding-bottom: 0.5rem;
                    border-bottom: 2px solid rgba(79, 209, 197, 0.2);
                }
                .chart-container {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 16px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                }
                .insights-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 1.5rem;
                    margin-top: 1rem;
                }
                .insight-card {
                    background: rgba(255, 255, 255, 0.05);
                    padding: 1.5rem;
                    border-radius: 16px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .trend-indicator {
                    display: inline-flex;
                    align-items: center;
                    padding: 0.25rem 0.5rem;
                    border-radius: 12px;
                    font-size: 0.875rem;
                    margin-left: 0.5rem;
                }
                .trend-up {
                    background: rgba(46, 204, 113, 0.2);
                    color: #2ecc71;
                }
                .trend-down {
                    background: rgba(231, 76, 60, 0.2);
                    color: #e74c3c;
                }
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                .animate-fade-in {
                    animation: fadeInUp 0.5s ease-out forwards;
                }
            </style>
        """, unsafe_allow_html=True)

        # Dashboard Header
        st.markdown("""
            <div class="dashboard-container animate-fade-in">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="dashboard-title">
                        <span class="dashboard-icon">📊</span>
                        Resume Analytics Dashboard
                    </div>
                    <div style="color: rgba(255, 255, 255, 0.7);">
                        Last updated: {}
                    </div>
                </div>
            """.format(datetime.now().strftime('%B %d, %Y %I:%M %p')), unsafe_allow_html=True)

        # Quick Stats
        stats = self.get_quick_stats()
        trend_indicators = self.get_trend_indicators()
        
        st.markdown("""
            <div class="stats-grid">
                <div class="stat-card">
                    <p class="stat-value">{}</p>
                    <p class="stat-label">Total Resumes</p>
                    <span class="trend-indicator {}">
                        {} {}%
                    </span>
                </div>
                <div class="stat-card">
                    <p class="stat-value">{}</p>
                    <p class="stat-label">Avg ATS Score</p>
                    <span class="trend-indicator {}">
                        {} {}%
                    </span>
                </div>
                <div class="stat-card">
                    <p class="stat-value">{}</p>
                    <p class="stat-label">High Performing</p>
                    <span class="trend-indicator {}">
                        {} {}%
                    </span>
                </div>
                <div class="stat-card">
                    <p class="stat-value">{}</p>
                    <p class="stat-label">Success Rate</p>
                    <span class="trend-indicator {}">
                        {} {}%
                    </span>
                </div>
            </div>
            </div>
        """.format(
            stats['Total Resumes'], 
            trend_indicators['resumes']['class'], trend_indicators['resumes']['icon'], trend_indicators['resumes']['value'],
            stats['Avg ATS Score'],
            trend_indicators['ats']['class'], trend_indicators['ats']['icon'], trend_indicators['ats']['value'],
            stats['High Performing'],
            trend_indicators['high_performing']['class'], trend_indicators['high_performing']['icon'], trend_indicators['high_performing']['value'],
            stats['Success Rate'],
            trend_indicators['success_rate']['class'], trend_indicators['success_rate']['icon'], trend_indicators['success_rate']['value']
        ), unsafe_allow_html=True)

        # Performance Analytics Section
        st.markdown('<div class="section-title">📈 Performance Analytics</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = self.create_enhanced_ats_gauge(float(stats['Avg ATS Score'].rstrip('%')))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = self.create_skill_distribution_chart()
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Additional Analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = self.create_submission_trends_chart()
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = self.create_job_category_chart()
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Key Insights Section
        st.markdown('<div class="section-title">🎯 Key Insights</div>', unsafe_allow_html=True)
        insights = self.get_detailed_insights()
        
        st.markdown('<div class="insights-grid">', unsafe_allow_html=True)
        for insight in insights:
            st.markdown(f"""
                <div class="insight-card">
                    <h3 style="color: #4FD1C5; margin-bottom: 1rem;">
                        {insight['icon']} {insight['title']}
                    </h3>
                    <p style="color: rgba(255, 255, 255, 0.7); margin: 0;">
                        {insight['description']}
                    </p>
                    <div style="margin-top: 1rem;">
                        <span class="trend-indicator {insight['trend_class']}">
                            {insight['trend_icon']} {insight['trend_value']}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Admin logs section with Excel download functionality
        if st.session_state.get('is_admin', False):
            # Create tabs for different admin sections
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Resume Data", 
                "👥 User Management", 
                "📈 System Analytics", 
                "🎯 Engagement Metrics"
            ])
            
            with tab1:
                self.render_resume_data_section()
                st.markdown("---")
                # Admin logs
                st.markdown("<h2 class='section-title'>Admin Activity Logs</h2>", unsafe_allow_html=True)
                admin_logs = self.get_admin_logs()
                if admin_logs:
                    df = pd.DataFrame(admin_logs, columns=['Admin Email', 'Action', 'Timestamp'])
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    excel_buffer = BytesIO()
                    df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download Admin Logs",
                        data=excel_buffer,
                        file_name=f"admin_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_admin_logs"
                    )
                else:
                    st.info("No admin activity logs available")
            
            with tab2:
                self.render_user_management_section()
            
            with tab3:
                self.render_system_analytics_section()
            
            with tab4:
                self.render_engagement_metrics_section()

    def get_trend_indicators(self):
        """Get trend indicators for stats"""
        with get_database_connection() as conn:
            cursor = conn.cursor()
            indicators = {}

            # Simplified trend indicators for PostgreSQL
            for metric in ['resumes', 'ats', 'high_performing', 'success_rate']:
                try:
                    if metric == 'resumes':
                        cursor.execute("""
                            SELECT 
                                COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') as recent,
                                COUNT(*) FILTER (WHERE created_at < CURRENT_DATE - INTERVAL '7 days' AND created_at >= CURRENT_DATE - INTERVAL '14 days') as previous
                            FROM resume_data
                        """)
                        row = cursor.fetchone()
                        change = ((row[0] - row[1]) * 100.0 / row[1]) if row[1] > 0 else 0
                    elif metric == 'ats':
                        cursor.execute("""
                            SELECT 
                                AVG(ats_score) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') as recent,
                                AVG(ats_score) FILTER (WHERE created_at < CURRENT_DATE - INTERVAL '7 days' AND created_at >= CURRENT_DATE - INTERVAL '14 days') as previous
                            FROM resume_analysis
                        """)
                        row = cursor.fetchone()
                        change = ((row[0] - row[1]) * 100.0 / row[1]) if row[1] and row[0] else 0
                    else:
                        change = 0

                    indicators[metric] = {
                        'value': abs(round(float(change), 1)),
                        'icon': '↑' if change >= 0 else '↓',
                        'class': 'trend-up' if change >= 0 else 'trend-down'
                    }
                except Exception:
                    indicators[metric] = {
                        'value': 0,
                        'icon': '→',
                        'class': 'trend-neutral'
                    }

            return indicators

    def get_detailed_insights(self):
        """Get detailed insights from the database - simplified for PostgreSQL"""
        with get_database_connection() as conn:
            cursor = conn.cursor()
            insights = []

            # Most Successful Job Category
            cursor.execute("""
                SELECT target_category, AVG(ats_score) as avg_score,
                       COUNT(*) as submission_count
                FROM resume_data rd
                JOIN resume_analysis ra ON rd.id = ra.resume_id
                WHERE target_category IS NOT NULL
                GROUP BY target_category
                ORDER BY avg_score DESC
                LIMIT 1
            """)
            top_category = cursor.fetchone()
            if top_category and top_category[0]:
                insights.append({
                    'title': 'Top Performing Category',
                    'icon': '🏆',
                    'description': f"{top_category[0]} leads with {float(top_category[1]):.1f}% average ATS score across {top_category[2]} submissions",
                    'trend_class': 'trend-up',
                    'trend_icon': '↑',
                    'trend_value': f"{float(top_category[1]):.1f}%"
                })
            else:
                insights.append({
                    'title': 'Top Performing Category',
                    'icon': '🏆',
                    'description': "No category data available yet.",
                    'trend_class': 'trend-neutral',
                    'trend_icon': '📊',
                    'trend_value': "No data"
                })

            # Recent Improvement
            cursor.execute("""
                SELECT 
                    AVG(ats_score) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') as recent_score,
                    AVG(ats_score) FILTER (WHERE created_at < CURRENT_DATE - INTERVAL '7 days') as old_score
                FROM resume_analysis
            """)
            scores = cursor.fetchone()
            if scores and scores[0] is not None and scores[1] is not None:
                change = float(scores[0]) - float(scores[1])
                insights.append({
                    'title': 'Weekly Trend',
                    'icon': '📈',
                    'description': f"ATS scores have {'improved' if change >= 0 else 'decreased'} by {abs(change):.1f}% in the last week",
                    'trend_class': 'trend-up' if change >= 0 else 'trend-down',
                    'trend_icon': '↑' if change >= 0 else '↓',
                    'trend_value': f"{abs(change):.1f}%"
                })
            else:
                insights.append({
                    'title': 'Weekly Trend',
                    'icon': '📈',
                    'description': "Not enough data to show weekly trends.",
                    'trend_class': 'trend-neutral',
                    'trend_icon': '�',
                    'trend_value': "No data"
                })

            # Simplified skills insight
            insights.append({
                'title': 'Top Skills',
                'icon': '💡',
                'description': "Skills analysis available in detailed reports.",
                'trend_class': 'trend-up',
                'trend_icon': '�',
                'trend_value': "Active"
            })

            return insights

    def get_quick_stats(self):
        """Get quick statistics for the dashboard with retry logic"""
        def query():
            with get_database_connection() as conn:
                cursor = conn.cursor()

                # Total Resumes
                cursor.execute("SELECT COUNT(*) FROM resume_data")
                total_resumes = cursor.fetchone()[0]

                # Average ATS Score
                cursor.execute("SELECT AVG(ats_score) FROM resume_analysis")
                avg_ats = cursor.fetchone()[0] or 0

                # High Performing Resumes
                cursor.execute("SELECT COUNT(*) FROM resume_analysis WHERE ats_score >= 70")
                high_performing = cursor.fetchone()[0]

                # Success Rate
                success_rate = (high_performing / total_resumes * 100) if total_resumes > 0 else 0

                return {
                    "Total Resumes": f"{total_resumes:,}",
                    "Avg ATS Score": f"{float(avg_ats):.1f}%",
                    "High Performing": f"{high_performing:,}",
                    "Success Rate": f"{success_rate:.1f}%"
                }
        
        result = self.execute_with_retry(query)
        return result if result else {
            "Total Resumes": "0",
            "Avg ATS Score": "0.0%",
            "High Performing": "0",
            "Success Rate": "0.0%"
        }

    def create_enhanced_ats_gauge(self, value):
        """Create an enhanced ATS score gauge chart"""
        reference = 70  # Target score
        delta = value - reference
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            delta={
                'reference': reference,
                'valueformat': '.1f',
                'increasing': {'color': '#2ecc71'},
                'decreasing': {'color': '#e74c3c'}
            },
            number={'font': {'size': 40, 'color': 'white'}},
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickwidth': 1,
                    'tickcolor': 'white',
                    'tickfont': {'color': 'white'}
                },
                'bar': {'color': '#3498db'},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 2,
                'bordercolor': 'white',
                'steps': [
                    {'range': [0, 40], 'color': '#e74c3c'},
                    {'range': [40, 70], 'color': '#f1c40f'},
                    {'range': [70, 100], 'color': '#2ecc71'}
                ],
                'threshold': {
                    'line': {'color': 'white', 'width': 4},
                    'thickness': 0.75,
                    'value': reference
                }
            }
        ))
        
        fig.update_layout(
            title={
                'text': 'ATS Score Performance',
                'font': {'size': 24, 'color': 'white'},
                'y': 0.85
            },
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'},
            height=350,
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        return fig

    def create_skill_distribution_chart(self):
        """Create a skill distribution chart"""
        categories, counts = self.get_skill_distribution()
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=counts,
                marker_color=self.colors['info'],
                text=counts,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title={
                'text': 'Skill Distribution',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            height=350,  
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=self.colors['text']),
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='rgba(255,255,255,0.2)',
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                zeroline=False
            ),
            bargap=0.3
        )
        return fig

    def create_submission_trends_chart(self):
        """Create a weekly submission trend chart"""
        dates, submissions = self.get_weekly_trends()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=submissions,
            mode='lines+markers',
            line=dict(color=self.colors['info'], width=3),
            marker=dict(size=8, color=self.colors['info'])
        ))
        
        fig.update_layout(
            title="Weekly Submission Pattern",
            paper_bgcolor=self.colors['card'],
            plot_bgcolor=self.colors['card'],
            font={'color': self.colors['text']},
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        fig.update_xaxes(title_text="Day of Week", color=self.colors['text'])
        fig.update_yaxes(title_text="Number of Submissions", color=self.colors['text'])
        
        return fig

    def create_job_category_chart(self):
        """Create a success rate by category chart"""
        categories, rates = self.get_job_category_stats()
        fig = go.Figure(go.Bar(
            x=categories,
            y=rates,
            marker_color=[self.colors['success'], self.colors['info'], 
                        self.colors['warning'], self.colors['purple'], 
                        self.colors['secondary']],
            text=[f"{rate}%" for rate in rates],
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Success Rate by Job Category",
            paper_bgcolor=self.colors['card'],
            plot_bgcolor=self.colors['card'],
            font={'color': self.colors['text']},
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        fig.update_xaxes(title_text="Job Category", color=self.colors['text'])
        fig.update_yaxes(title_text="Success Rate (%)", color=self.colors['text'])
        
        return fig