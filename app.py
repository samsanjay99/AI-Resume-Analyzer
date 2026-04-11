"""
Smart Resume AI - Main Application
"""
import os
import time
import threading
import tempfile
import json
from dotenv import load_dotenv

# Load environment variables from .env file FIRST so NETLIFY_TOKEN etc. are available
load_dotenv()
from PIL import Image
from jobs.job_search import render_job_search
from datetime import datetime, timedelta
from utils.ui_components import (
    apply_modern_styles, hero_section, feature_card, about_section,
    page_header, render_analytics_section, render_activity_section,
    render_suggestions_section
)
from feedback.feedback import FeedbackManager
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx import Document
import io
import base64
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
from dashboard.dashboard import DashboardManager
from config.courses import COURSES_BY_CATEGORY, RESUME_VIDEOS, INTERVIEW_VIDEOS, get_courses_for_role, get_category_for_role
from config.job_roles import JOB_ROLES
from config.database import (
    get_database_connection, save_resume_data, save_analysis_data,
    init_database, verify_admin, log_admin_action, save_ai_analysis_data,
    get_ai_analysis_stats, reset_ai_analysis_stats, get_all_resume_data, 
    get_admin_analytics, get_resume_stats
)
from utils.ai_resume_analyzer import AIResumeAnalyzer
from utils.resume_builder import ResumeBuilder
from utils.resume_analyzer import ResumeAnalyzer
from utils.portfolio_generator import PortfolioGenerator
from auth.auth_manager import AuthManager
from auth.login_page import render_login_page, render_signup_page
import traceback
import plotly.express as px
import pandas as pd
import json
import streamlit as st

# Set page config at the very beginning
st.set_page_config(
    page_title="Smart Resume AI",
    page_icon="🚀",
    layout="wide"
)


# ========================================================================================
# NETLIFY DEPLOYMENT (Simple & Reliable)
# ========================================================================================

def save_portfolio_to_folder(files_dict):
    """Convert portfolio files dict to a real folder"""
    temp_dir = tempfile.mkdtemp(prefix="portfolio_")
    
    for path, content in files_dict.items():
        full_path = os.path.join(temp_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    return temp_dir


def deploy_to_netlify(folder_path):
    """Deploy portfolio folder to Netlify and return instant live URL.
    Uses the correct 2-step API: create site → upload zip deploy.
    """
    import requests
    import zipfile
    import io

    token = os.getenv("NETLIFY_TOKEN")
    if not token:
        return {
            "success": False,
            "error": "NETLIFY_TOKEN not found in environment. Add it to your .env file."
        }

    try:
        # ── Step 1: Build a ZIP of the folder in memory ────────────────
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, folder_path)
                    z.write(full_path, rel_path)
        zip_buffer.seek(0)
        zip_bytes = zip_buffer.read()

        auth_headers = {"Authorization": f"Bearer {token}"}

        # ── Step 2: Create a new Netlify site ──────────────────────────
        site_resp = requests.post(
            "https://api.netlify.com/api/v1/sites",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={},
            timeout=30
        )
        if site_resp.status_code not in (200, 201):
            return {
                "success": False,
                "error": f"Could not create Netlify site: {site_resp.status_code} – {site_resp.text[:300]}"
            }
        site_data = site_resp.json()
        site_id = site_data.get("id")
        if not site_id:
            return {"success": False, "error": "Netlify did not return a site ID."}

        # ── Step 3: Upload the ZIP as a deploy ─────────────────────────
        deploy_resp = requests.post(
            f"https://api.netlify.com/api/v1/sites/{site_id}/deploys",
            headers={**auth_headers, "Content-Type": "application/zip"},
            data=zip_bytes,
            timeout=120
        )
        if deploy_resp.status_code not in (200, 201):
            return {
                "success": False,
                "error": f"Netlify deploy failed: {deploy_resp.status_code} – {deploy_resp.text[:300]}"
            }

        deploy_data = deploy_resp.json()
        # Prefer HTTPS url
        live_url = (
            deploy_data.get("ssl_url")
            or deploy_data.get("url")
            or site_data.get("ssl_url")
            or site_data.get("url")
            or ""
        )
        return {
            "success": True,
            "live_url": live_url,
            "admin_url": site_data.get("admin_url", ""),
            "site_id": site_id,
            "message": "Portfolio deployed successfully!"
        }

    except Exception as e:
        return {"success": False, "error": f"Deployment error: {str(e)}"}


# ========================================================================================



class ResumeApp:
    def __init__(self):
        """Initialize the application"""
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {
                'personal_info': {
                    'full_name': '',
                    'email': '',
                    'phone': '',
                    'location': '',
                    'linkedin': '',
                    'portfolio': ''
                },
                'summary': '',
                'experiences': [],
                'education': [],
                'projects': [],
                'skills_categories': {
                    'technical': [],
                    'soft': [],
                    'languages': [],
                    'tools': []
                }
            }

        # Initialize navigation state
        if 'page' not in st.session_state:
            st.session_state.page = 'home'

        # Initialize admin state
        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False
        
        # Initialize deployment state (simple)
        if 'deployment_result' not in st.session_state:
            st.session_state.deployment_result = None

        # Main pages for all users (Dashboard removed - admin only)
        self.pages = {
            "🏠 HOME": self.render_home,
            "🔍 RESUME ANALYZER": self.render_analyzer,
            "📝 RESUME BUILDER": self.render_builder,
            "🌐 PORTFOLIO GENERATOR": self.render_portfolio_generator,
            "📚 MY HISTORY": self.render_user_history,
            "🎓 LEARNING": self.render_learning_dashboard,
            "🎤 MOCK INTERVIEW": self.render_mock_interview,
            "🎯 JOB SEARCH": self.render_job_search,
            "💬 FEEDBACK": self.render_feedback_page,
            "ℹ️ ABOUT": self.render_about
        }

        # Initialize dashboard manager
        self.dashboard_manager = DashboardManager()

        self.analyzer = ResumeAnalyzer()
        self.ai_analyzer = AIResumeAnalyzer()
        self.builder = ResumeBuilder()
        self.portfolio_generator = PortfolioGenerator()
        self.job_roles = JOB_ROLES
        
        # Initialize database and create default admin
        init_database()
        
        # Debug admin table
        from config.database import debug_admin_table
        debug_admin_table()

        # Initialize session state
        if 'user_id' not in st.session_state:
            st.session_state.user_id = 'default_user'
        if 'selected_role' not in st.session_state:
            st.session_state.selected_role = None

        # Load external CSS
        with open('style/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

        # Load Google Fonts
        st.markdown("""
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        """, unsafe_allow_html=True)

        if 'resume_data' not in st.session_state:
            st.session_state.resume_data = []
        if 'ai_analysis_stats' not in st.session_state:
            st.session_state.ai_analysis_stats = {
                'score_distribution': {},
                'total_analyses': 0,
                'average_score': 0
            }

    def load_lottie_url(self, url: str):
        """Load Lottie animation from URL"""
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return None
            return r.json()
        except Exception as e:
            print(f"Could not load Lottie animation: {e}")
            return None

    def apply_global_styles(self):
        st.markdown("""
        <style>
        /* Hide Streamlit's auto-generated pages nav (we use custom sidebar) */
        [data-testid="stSidebarNav"] { display: none !important; }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #1a1a1a;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: #4CAF50;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #45a049;
        }

        /* Global Styles */
        .main-header {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, transparent 0%, rgba(255,255,255,0.1) 100%);
            z-index: 1;
        }

        .main-header h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: 600;
            margin: 0;
            position: relative;
            z-index: 2;
        }

        /* Template Card Styles */
        .template-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
            padding: 1rem;
        }

        .template-card {
            background: rgba(45, 45, 45, 0.9);
            border-radius: 20px;
            padding: 2rem;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .template-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            border-color: #4CAF50;
        }

        .template-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, transparent 0%, rgba(76,175,80,0.1) 100%);
            z-index: 1;
        }

        .template-icon {
            font-size: 3rem;
            color: #4CAF50;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;
        }

        .template-title {
            font-size: 1.8rem;
            font-weight: 600;
            color: white;
            margin-bottom: 1rem;
            position: relative;
            z-index: 2;
        }

        .template-description {
            color: #aaa;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;
            line-height: 1.6;
        }

        /* Feature List Styles */
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 1.5rem 0;
            position: relative;
            z-index: 2;
        }

        .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            color: #ddd;
            font-size: 0.95rem;
        }

        .feature-icon {
            color: #4CAF50;
            margin-right: 0.8rem;
            font-size: 1.1rem;
        }

        /* Button Styles */
        .action-button {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            border: none;
            font-weight: 500;
            cursor: pointer;
            width: 100%;
            text-align: center;
            position: relative;
            overflow: hidden;
            z-index: 2;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(76,175,80,0.3);
        }

        .action-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);
            transition: all 0.6s ease;
        }

        .action-button:hover::before {
            left: 100%;
        }

        /* Form Section Styles */
        .form-section {
            background: rgba(45, 45, 45, 0.9);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }

        .form-section-title {
            font-size: 1.8rem;
            font-weight: 600;
            color: white;
            margin-bottom: 1.5rem;
            padding-bottom: 0.8rem;
            border-bottom: 2px solid #4CAF50;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-label {
            color: #ddd;
            font-weight: 500;
            margin-bottom: 0.8rem;
            display: block;
        }

        .form-input {
            width: 100%;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(30, 30, 30, 0.9);
            color: white;
            transition: all 0.3s ease;
        }

        .form-input:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 2px rgba(76,175,80,0.2);
            outline: none;
        }

        /* Skill Tags */
        .skill-tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .skill-tag {
            background: rgba(76,175,80,0.1);
            color: #4CAF50;
            padding: 0.6rem 1.2rem;
            border-radius: 50px;
            border: 1px solid #4CAF50;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .skill-tag:hover {
            background: #4CAF50;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76,175,80,0.2);
        }

        /* Progress Circle */
        .progress-container {
            position: relative;
            width: 150px;
            height: 150px;
            margin: 2rem auto;
        }

        .progress-circle {
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
        }

        .progress-circle circle {
            fill: none;
            stroke-width: 8;
            stroke-linecap: round;
            stroke: #4CAF50;
            transform-origin: 50% 50%;
            transition: all 0.3s ease;
        }

        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.5rem;
            font-weight: 600;
            color: white;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .feature-card {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Animations */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .animate-slide-in {
            animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .template-container {
                grid-template-columns: 1fr;
            }

            .main-header {
                padding: 1.5rem;
            }

            .main-header h1 {
                font-size: 2rem;
            }

            .template-card {
                padding: 1.5rem;
            }

            .action-button {
                padding: 0.8rem 1.6rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
    def add_footer(self):
        """Add a footer to all pages"""
        st.markdown("<hr style='margin-top: 50px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col2:
            # GitHub star button with lottie animation
            st.markdown("""
            <div style='display: flex; justify-content: center; align-items: center; margin-bottom: 10px;'>
                <a href='https://github.com/samsanjay99/AI-Resume-Analyzer-And-Enhancement-system' target='_blank' style='text-decoration: none;'>
                    <div style='display: flex; align-items: center; background-color: #24292e; padding: 5px 10px; border-radius: 5px; transition: all 0.3s ease;'>
                        <svg height="16" width="16" viewBox="0 0 16 16" version="1.1" style='margin-right: 5px;'>
                            <path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z" fill="gold"></path>
                        </svg>
                        <span style='color: white; font-size: 14px;'>Star this repo</span>
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            # Footer text
            st.markdown("""
            <p style='text-align: center;'>
                Powered by <b>Streamlit</b> and <b>Google Gemini AI</b> | Developed by 
                <a href="https://github.com/samsanjay99" target="_blank" style='text-decoration: none; color: #FFFFFF'>
                    <b>Sanjay (samsanjay99)</b>
                </a>
            </p>
            <p style='text-align: center; font-size: 12px; color: #888888;'>
                "Every star counts! If you find this project helpful, please consider starring the repo to help it reach more people."
            </p>
            """, unsafe_allow_html=True)

    def load_image(self, image_name):
        """Load image from static directory"""
        try:
            image_path = os.path.join(os.path.dirname(__file__), "assets", image_name)
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            encoded = base64.b64encode(image_bytes).decode()
            return f"data:image/png;base64,{encoded}"
        except Exception as e:
            print(f"Error loading image {image_name}: {e}")
            return None

    def export_to_excel(self):
        """Export resume data to Excel"""
        conn = get_database_connection()

        # Get resume data with analysis
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
            # Read data into DataFrame
            df = pd.read_sql_query(query, conn)

            # Create Excel writer object
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Resume Data')

            return output.getvalue()
        except Exception as e:
            print(f"Error exporting to Excel: {str(e)}")
            return None
        finally:
            conn.close()

    def render_dashboard(self):
        """Render the dashboard page"""
        self.dashboard_manager.render_dashboard()
        
        # Add admin section if logged in
        if st.session_state.get('is_admin', False):
            st.markdown("---")
            self.render_admin_dashboard()


    def render_admin_dashboard(self):
        """Render comprehensive admin dashboard"""
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        
        st.markdown("## 👑 Admin Dashboard")
        st.markdown("*Welcome to the administrative control panel*")
        
        # Add refresh button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Refresh Data", type="secondary", use_container_width=True):
                st.rerun()
        
        # Admin tabs
        admin_tabs = st.tabs([
            "📊 Analytics Overview", 
            "👥 User Data", 
            "📄 Resume Files", 
            "💬 Feedback & Ratings",
            "📈 Detailed Charts"
        ])
        
        # Get admin analytics data
        analytics = get_admin_analytics()
        all_resume_data = get_all_resume_data()
        
        # Debug information (can be removed later)
        if st.checkbox("🔍 Show Debug Info", key="admin_debug"):
            st.write("**Debug - Analytics Data:**", analytics)
            st.write("**Debug - Resume Data Count:**", len(all_resume_data))
        
        with admin_tabs[0]:  # Analytics Overview
            st.subheader("📊 System Overview")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Users", analytics.get('total_users', 0))
            with col2:
                st.metric("Total Resumes", analytics.get('total_resumes', 0))
            with col3:
                st.metric("Average Score", f"{analytics.get('avg_score', 0)}%")
            with col4:
                st.metric("Admin Status", "Active ✅")
            
            # Quick stats
            if analytics.get('role_distribution'):
                st.subheader("🎯 Top Predicted Roles")
                role_df = pd.DataFrame(analytics['role_distribution'], columns=['Role', 'Count'])
                st.dataframe(role_df.head(10), use_container_width=True)
        
        with admin_tabs[1]:  # User Data
            st.subheader("👥 All User Data")
            
            if all_resume_data:
                # Convert to DataFrame
                columns = [
                    'ID', 'Name', 'Email', 'Phone', 'LinkedIn', 'GitHub', 'Portfolio',
                    'Summary', 'Target Role', 'Target Category', 'Education', 'Experience',
                    'Projects', 'Skills', 'Template', 'Created At', 'Score', 'ATS Score',
                    'Predicted Role', 'Experience Level', 'Analysis Date', 'Model Used'
                ]
                
                df = pd.DataFrame(all_resume_data, columns=columns)
                
                # Display data with filters
                st.write(f"**Total Records:** {len(df)}")
                
                # Filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    if 'Target Role' in df.columns and not df['Target Role'].isna().all():
                        role_filter = st.selectbox("Filter by Role", 
                                                 ['All'] + list(df['Target Role'].dropna().unique()))
                    else:
                        role_filter = 'All'
                
                with col2:
                    if 'Experience Level' in df.columns and not df['Experience Level'].isna().all():
                        exp_filter = st.selectbox("Filter by Experience", 
                                                ['All'] + list(df['Experience Level'].dropna().unique()))
                    else:
                        exp_filter = 'All'
                
                with col3:
                    score_filter = st.slider("Minimum Score", 0, 100, 0)
                
                # Apply filters
                filtered_df = df.copy()
                if role_filter != 'All':
                    filtered_df = filtered_df[filtered_df['Target Role'] == role_filter]
                if exp_filter != 'All':
                    filtered_df = filtered_df[filtered_df['Experience Level'] == exp_filter]
                if score_filter > 0:
                    filtered_df = filtered_df[filtered_df['Score'] >= score_filter]
                
                # Display filtered data
                st.dataframe(filtered_df, use_container_width=True)
                
                # Download CSV
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"resume_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No user data available yet.")
        
        with admin_tabs[2]:  # Resume Files
            st.subheader("📄 Uploaded Resume Files")
            
            # Get uploaded files from database
            from config.database import get_all_uploaded_files
            uploaded_files = get_all_uploaded_files()
            
            if uploaded_files:
                st.write(f"**Found {len(uploaded_files)} uploaded files:**")
                
                # Convert to DataFrame for better display
                files_df = pd.DataFrame(uploaded_files, columns=[
                    'ID', 'Filename', 'Original Name', 'File Path', 'Size (bytes)', 
                    'File Type', 'Upload Source', 'Timestamp'
                ])
                
                # Add size in KB column
                files_df['Size (KB)'] = (files_df['Size (bytes)'] / 1024).round(1)
                
                # Display filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    source_filter = st.selectbox("Filter by Source", 
                                               ['All'] + list(files_df['Upload Source'].unique()))
                with col2:
                    file_type_filter = st.selectbox("Filter by Type", 
                                                   ['All'] + list(files_df['File Type'].unique()))
                with col3:
                    show_count = st.selectbox("Show Files", [10, 25, 50, 100], index=1)
                
                # Apply filters
                filtered_files = files_df.copy()
                if source_filter != 'All':
                    filtered_files = filtered_files[filtered_files['Upload Source'] == source_filter]
                if file_type_filter != 'All':
                    filtered_files = filtered_files[filtered_files['File Type'] == file_type_filter]
                
                filtered_files = filtered_files.head(show_count)
                
                # Display files table
                display_columns = ['Original Name', 'Upload Source', 'File Type', 'Size (KB)', 'Timestamp']
                st.dataframe(filtered_files[display_columns], use_container_width=True)
                
                # File download section
                st.subheader("📥 Download Files")
                
                for i, (_, file_info) in enumerate(filtered_files.iterrows()):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"📄 {file_info['Original Name']}")
                        st.caption(f"Source: {file_info['Upload Source']} | {file_info['Timestamp']}")
                    
                    with col2:
                        st.write(f"{file_info['Size (KB)']} KB")
                    
                    with col3:
                        st.write(file_info['File Type'].split('/')[-1].upper())
                    
                    with col4:
                        try:
                            if os.path.exists(file_info['File Path']):
                                with open(file_info['File Path'], "rb") as f:
                                    file_data = f.read()
                                st.download_button(
                                    "⬇️ Download",
                                    file_data,
                                    file_name=file_info['Original Name'],
                                    mime=file_info['File Type'],
                                    key=f"download_file_{i}"
                                )
                            else:
                                st.error("File not found")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # Download CSV of file list
                csv = filtered_files.to_csv(index=False)
                st.download_button(
                    label="📥 Download File List CSV",
                    data=csv,
                    file_name=f"uploaded_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.info("No files uploaded yet.")
                st.write("💡 **Note:** Resume files will appear here when users upload them for analysis.")
                
                # Show directory status for debugging
                uploads_dir = "uploads"
                if os.path.exists(uploads_dir):
                    files_in_dir = os.listdir(uploads_dir)
                    if files_in_dir:
                        st.warning(f"Found {len(files_in_dir)} files in uploads directory but not in database. This may indicate files were uploaded before the database tracking was implemented.")
                        
                        # Option to sync existing files
                        if st.button("🔄 Sync Existing Files to Database"):
                            from config.database import save_uploaded_file_info
                            synced_count = 0
                            for file in files_in_dir:
                                file_path = os.path.join(uploads_dir, file)
                                if os.path.isfile(file_path):
                                    file_size = os.path.getsize(file_path)
                                    file_type = "application/pdf" if file.lower().endswith('.pdf') else "application/octet-stream"
                                    
                                    result = save_uploaded_file_info(
                                        filename=file,
                                        original_name=file,
                                        file_path=file_path,
                                        file_size=file_size,
                                        file_type=file_type,
                                        upload_source="Legacy Upload"
                                    )
                                    if result:
                                        synced_count += 1
                            
                            if synced_count > 0:
                                st.success(f"✅ Synced {synced_count} files to database!")
                                st.rerun()
                            else:
                                st.error("Failed to sync files to database.")
        
        with admin_tabs[3]:  # Feedback & Ratings
            st.subheader("💬 User Feedback & Ratings")
            
            # Get feedback data
            from config.database import get_all_feedback, get_feedback_stats
            feedback_data = get_all_feedback()
            feedback_stats = get_feedback_stats()
            
            # Display feedback statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Feedback", feedback_stats['total_responses'])
            with col2:
                st.metric("Avg Rating", f"{feedback_stats['avg_rating']}/5.0")
            with col3:
                st.metric("Usability Score", f"{feedback_stats['avg_usability']}/5.0")
            with col4:
                st.metric("Satisfaction", f"{feedback_stats['avg_satisfaction']}/5.0")
            
            # Display feedback data
            if feedback_data:
                st.subheader("📝 Recent Feedback")
                
                # Convert to DataFrame for better display
                feedback_df = pd.DataFrame(feedback_data, columns=[
                    'ID', 'Rating', 'Usability', 'Satisfaction', 
                    'Missing Features', 'Improvements', 'Experience', 'Timestamp'
                ])
                
                # Display with filters
                col1, col2 = st.columns(2)
                with col1:
                    min_rating = st.selectbox("Minimum Rating", [1, 2, 3, 4, 5], index=0)
                with col2:
                    show_count = st.selectbox("Show Records", [10, 25, 50, 100], index=0)
                
                # Filter data
                filtered_feedback = feedback_df[feedback_df['Rating'] >= min_rating].head(show_count)
                
                # Display data
                st.dataframe(filtered_feedback, use_container_width=True)
                
                # Download CSV
                csv = filtered_feedback.to_csv(index=False)
                st.download_button(
                    label="📥 Download Feedback CSV",
                    data=csv,
                    file_name=f"feedback_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Show detailed feedback
                if st.checkbox("Show Detailed Feedback"):
                    for _, feedback in filtered_feedback.iterrows():
                        with st.expander(f"Feedback #{feedback['ID']} - Rating: {feedback['Rating']}/5"):
                            st.write(f"**Usability Score:** {feedback['Usability']}/5")
                            st.write(f"**Satisfaction:** {feedback['Satisfaction']}/5")
                            st.write(f"**Timestamp:** {feedback['Timestamp']}")
                            
                            if feedback['Missing Features']:
                                st.write(f"**Missing Features:** {feedback['Missing Features']}")
                            if feedback['Improvements']:
                                st.write(f"**Improvement Suggestions:** {feedback['Improvements']}")
                            if feedback['Experience']:
                                st.write(f"**User Experience:** {feedback['Experience']}")
            else:
                st.info("No feedback received yet. Encourage users to submit feedback!")
        
        with admin_tabs[4]:  # Detailed Charts
            st.subheader("📈 Detailed Analytics Charts")
            
            if analytics:
                # Role Distribution Pie Chart
                if analytics.get('role_distribution'):
                    st.subheader("🎯 Predicted Roles Distribution")
                    role_df = pd.DataFrame(analytics['role_distribution'], columns=['Role', 'Count'])
                    
                    fig_roles = px.pie(role_df, values='Count', names='Role', 
                                     title="Distribution of Predicted Job Roles")
                    st.plotly_chart(fig_roles, use_container_width=True)
                
                # Experience Level Distribution
                if analytics.get('experience_distribution'):
                    st.subheader("💼 Experience Level Distribution")
                    exp_df = pd.DataFrame(analytics['experience_distribution'], columns=['Level', 'Count'])
                    
                    fig_exp = px.bar(exp_df, x='Level', y='Count', 
                                   title="Distribution by Experience Level")
                    st.plotly_chart(fig_exp, use_container_width=True)
                
                # Score Distribution
                if analytics.get('score_distribution'):
                    st.subheader("📊 Resume Score Distribution")
                    score_df = pd.DataFrame(analytics['score_distribution'], columns=['Range', 'Count'])
                    
                    fig_score = px.pie(score_df, values='Count', names='Range',
                                     title="Resume Score Ranges")
                    st.plotly_chart(fig_score, use_container_width=True)
                
                # User Registration Timeline (if we have date data)
                if all_resume_data:
                    st.subheader("📅 User Registration Timeline")
                    df = pd.DataFrame(all_resume_data, columns=[
                        'ID', 'Name', 'Email', 'Phone', 'LinkedIn', 'GitHub', 'Portfolio',
                        'Summary', 'Target Role', 'Target Category', 'Education', 'Experience',
                        'Projects', 'Skills', 'Template', 'Created At', 'Score', 'ATS Score',
                        'Predicted Role', 'Experience Level', 'Analysis Date', 'Model Used'
                    ])
                    
                    if 'Created At' in df.columns:
                        df['Created At'] = pd.to_datetime(df['Created At'])
                        df['Date'] = df['Created At'].dt.date
                        
                        daily_users = df.groupby('Date').size().reset_index(name='Count')
                        
                        fig_timeline = px.line(daily_users, x='Date', y='Count',
                                             title="Daily User Registrations")
                        st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                st.info("No analytics data available yet.")

    def render_empty_state(self, icon, message):
        """Render an empty state with icon and message"""
        return f"""
            <div style='text-align: center; padding: 2rem; color: #666;'>
                <i class='{icon}' style='font-size: 2rem; margin-bottom: 1rem; color: #00bfa5;'></i>
                <p style='margin: 0;'>{message}</p>
            </div>
        """

    def analyze_resume(self, resume_text):
        """Analyze resume and store results"""
        analytics = self.analyzer.analyze_resume(resume_text)
        st.session_state.analytics_data = analytics
        return analytics

    def handle_resume_upload(self):
        """Handle resume upload and analysis"""
        uploaded_file = st.file_uploader(
            "Upload your resume", type=['pdf', 'docx'])

        if uploaded_file is not None:
            try:
                # Extract text from resume
                if uploaded_file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = extract_text_from_docx(uploaded_file)

                # Store resume data
                st.session_state.resume_data = {
                    'filename': uploaded_file.name,
                    'content': resume_text,
                    'upload_time': datetime.now().isoformat()
                }

                # Analyze resume
                analytics = self.analyze_resume(resume_text)

                return True
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
                return False
        return False

    def render_builder(self):
        st.title("Resume Builder 📝")
        st.write("Create your professional resume")

        # Template selection
        template_options = ["Modern", "Professional", "Minimal", "Creative"]
        selected_template = st.selectbox(
    "Select Resume Template", template_options)
        st.success(f"🎨 Currently using: {selected_template} Template")

        # Personal Information
        st.subheader("Personal Information")

        col1, col2 = st.columns(2)
        with col1:
            # Get existing values from session state
            existing_name = st.session_state.form_data['personal_info']['full_name']
            existing_email = st.session_state.form_data['personal_info']['email']
            existing_phone = st.session_state.form_data['personal_info']['phone']

            # Input fields with existing values
            full_name = st.text_input("Full Name", value=existing_name)
            email = st.text_input(
    "Email",
    value=existing_email,
     key="email_input")
            phone = st.text_input("Phone", value=existing_phone)

            # Immediately update session state after email input
            if 'email_input' in st.session_state:
                st.session_state.form_data['personal_info']['email'] = st.session_state.email_input

        with col2:
            # Get existing values from session state
            existing_location = st.session_state.form_data['personal_info']['location']
            existing_linkedin = st.session_state.form_data['personal_info']['linkedin']
            existing_portfolio = st.session_state.form_data['personal_info']['portfolio']

            # Input fields with existing values
            location = st.text_input("Location", value=existing_location)
            linkedin = st.text_input("LinkedIn URL", value=existing_linkedin)
            portfolio = st.text_input(
    "Portfolio Website", value=existing_portfolio)

        # Update personal info in session state
        st.session_state.form_data['personal_info'] = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'location': location,
            'linkedin': linkedin,
            'portfolio': portfolio
        }

        # Professional Summary
        st.subheader("Professional Summary")
        summary = st.text_area("Professional Summary", value=st.session_state.form_data.get('summary', ''), height=150,
                             help="Write a brief summary highlighting your key skills and experience")

        # Experience Section
        st.subheader("Work Experience")
        if 'experiences' not in st.session_state.form_data:
            st.session_state.form_data['experiences'] = []

        if st.button("Add Experience"):
            st.session_state.form_data['experiences'].append({
                'company': '',
                'position': '',
                'start_date': '',
                'end_date': '',
                'description': '',
                'responsibilities': [],
                'achievements': []
            })

        for idx, exp in enumerate(st.session_state.form_data['experiences']):
            with st.expander(f"Experience {idx + 1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    exp['company'] = st.text_input(
    "Company Name",
    key=f"company_{idx}",
    value=exp.get(
        'company',
         ''))
                    exp['position'] = st.text_input(
    "Position", key=f"position_{idx}", value=exp.get(
        'position', ''))
                with col2:
                    exp['start_date'] = st.text_input(
    "Start Date", key=f"start_date_{idx}", value=exp.get(
        'start_date', ''))
                    exp['end_date'] = st.text_input(
    "End Date", key=f"end_date_{idx}", value=exp.get(
        'end_date', ''))

                exp['description'] = st.text_area("Role Overview", key=f"desc_{idx}",
                                                value=exp.get(
                                                    'description', ''),
                                                help="Brief overview of your role and impact")

                # Responsibilities
                st.markdown("##### Key Responsibilities")
                resp_text = st.text_area("Enter responsibilities (one per line)",
                                       key=f"resp_{idx}",
                                       value='\n'.join(
                                           exp.get('responsibilities', [])),
                                       height=100,
                                       help="List your main responsibilities, one per line")
                exp['responsibilities'] = [r.strip()
                                                   for r in resp_text.split('\n') if r.strip()]

                # Achievements
                st.markdown("##### Key Achievements")
                achv_text = st.text_area("Enter achievements (one per line)",
                                       key=f"achv_{idx}",
                                       value='\n'.join(
                                           exp.get('achievements', [])),
                                       height=100,
                                       help="List your notable achievements, one per line")
                exp['achievements'] = [a.strip()
                                               for a in achv_text.split('\n') if a.strip()]

                if st.button("Remove Experience", key=f"remove_exp_{idx}"):
                    st.session_state.form_data['experiences'].pop(idx)
                    st.rerun()

        # Projects Section
        st.subheader("Projects")
        if 'projects' not in st.session_state.form_data:
            st.session_state.form_data['projects'] = []

        if st.button("Add Project"):
            st.session_state.form_data['projects'].append({
                'name': '',
                'technologies': '',
                'description': '',
                'responsibilities': [],
                'achievements': [],
                'link': ''
            })

        for idx, proj in enumerate(st.session_state.form_data['projects']):
            with st.expander(f"Project {idx + 1}", expanded=True):
                proj['name'] = st.text_input(
    "Project Name",
    key=f"proj_name_{idx}",
    value=proj.get(
        'name',
         ''))
                proj['technologies'] = st.text_input("Technologies Used", key=f"proj_tech_{idx}",
                                                   value=proj.get(
                                                       'technologies', ''),
                                                   help="List the main technologies, frameworks, and tools used")

                proj['description'] = st.text_area("Project Overview", key=f"proj_desc_{idx}",
                                                 value=proj.get(
                                                     'description', ''),
                                                 help="Brief overview of the project and its goals")

                # Project Responsibilities
                st.markdown("##### Key Responsibilities")
                proj_resp_text = st.text_area("Enter responsibilities (one per line)",
                                            key=f"proj_resp_{idx}",
                                            value='\n'.join(
                                                proj.get('responsibilities', [])),
                                            height=100,
                                            help="List your main responsibilities in the project")
                proj['responsibilities'] = [r.strip()
                                                    for r in proj_resp_text.split('\n') if r.strip()]

                # Project Achievements
                st.markdown("##### Key Achievements")
                proj_achv_text = st.text_area("Enter achievements (one per line)",
                                            key=f"proj_achv_{idx}",
                                            value='\n'.join(
                                                proj.get('achievements', [])),
                                            height=100,
                                            help="List the project's key achievements and your contributions")
                proj['achievements'] = [a.strip()
                                                for a in proj_achv_text.split('\n') if a.strip()]

                proj['link'] = st.text_input("Project Link (optional)", key=f"proj_link_{idx}",
                                           value=proj.get('link', ''),
                                           help="Link to the project repository, demo, or documentation")

                if st.button("Remove Project", key=f"remove_proj_{idx}"):
                    st.session_state.form_data['projects'].pop(idx)
                    st.rerun()

        # Education Section
        st.subheader("Education")
        if 'education' not in st.session_state.form_data:
            st.session_state.form_data['education'] = []

        if st.button("Add Education"):
            st.session_state.form_data['education'].append({
                'school': '',
                'degree': '',
                'field': '',
                'graduation_date': '',
                'gpa': '',
                'achievements': []
            })

        for idx, edu in enumerate(st.session_state.form_data['education']):
            with st.expander(f"Education {idx + 1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    edu['school'] = st.text_input(
    "School/University",
    key=f"school_{idx}",
    value=edu.get(
        'school',
         ''))
                    edu['degree'] = st.text_input(
    "Degree", key=f"degree_{idx}", value=edu.get(
        'degree', ''))
                with col2:
                    edu['field'] = st.text_input(
    "Field of Study",
    key=f"field_{idx}",
    value=edu.get(
        'field',
         ''))
                    edu['graduation_date'] = st.text_input("Graduation Date", key=f"grad_date_{idx}",
                                                         value=edu.get('graduation_date', ''))

                edu['gpa'] = st.text_input(
    "GPA (optional)",
    key=f"gpa_{idx}",
    value=edu.get(
        'gpa',
         ''))

                # Educational Achievements
                st.markdown("##### Achievements & Activities")
                edu_achv_text = st.text_area("Enter achievements (one per line)",
                                           key=f"edu_achv_{idx}",
                                           value='\n'.join(
                                               edu.get('achievements', [])),
                                           height=100,
                                           help="List academic achievements, relevant coursework, or activities")
                edu['achievements'] = [a.strip()
                                               for a in edu_achv_text.split('\n') if a.strip()]

                if st.button("Remove Education", key=f"remove_edu_{idx}"):
                    st.session_state.form_data['education'].pop(idx)
                    st.rerun()

        # Skills Section
        st.subheader("Skills")
        if 'skills_categories' not in st.session_state.form_data:
            st.session_state.form_data['skills_categories'] = {
                'technical': [],
                'soft': [],
                'languages': [],
                'tools': []
            }

        col1, col2 = st.columns(2)
        with col1:
            tech_skills = st.text_area("Technical Skills (one per line)",
                                     value='\n'.join(
    st.session_state.form_data['skills_categories']['technical']),
                                     height=150,
                                     help="Programming languages, frameworks, databases, etc.")
            st.session_state.form_data['skills_categories']['technical'] = [
                s.strip() for s in tech_skills.split('\n') if s.strip()]

            soft_skills = st.text_area("Soft Skills (one per line)",
                                     value='\n'.join(
    st.session_state.form_data['skills_categories']['soft']),
                                     height=150,
                                     help="Leadership, communication, problem-solving, etc.")
            st.session_state.form_data['skills_categories']['soft'] = [
                s.strip() for s in soft_skills.split('\n') if s.strip()]

        with col2:
            languages = st.text_area("Languages (one per line)",
                                   value='\n'.join(
    st.session_state.form_data['skills_categories']['languages']),
                                   height=150,
                                   help="Programming or human languages with proficiency level")
            st.session_state.form_data['skills_categories']['languages'] = [
                l.strip() for l in languages.split('\n') if l.strip()]

            tools = st.text_area("Tools & Technologies (one per line)",
                               value='\n'.join(
    st.session_state.form_data['skills_categories']['tools']),
                               height=150,
                               help="Development tools, software, platforms, etc.")
            st.session_state.form_data['skills_categories']['tools'] = [
                t.strip() for t in tools.split('\n') if t.strip()]

        # Update form data in session state
        st.session_state.form_data.update({
            'summary': summary
        })

        # Generate Resume button
        if st.button("Generate Resume 📄", type="primary"):
            print("Validating form data...")
            print(f"Session state form data: {st.session_state.form_data}")
            print(f"Email input value: {st.session_state.get('email_input', '')}")

            # Get the current values from form
            current_name = st.session_state.form_data['personal_info']['full_name'].strip(
            )
            current_email = st.session_state.email_input if 'email_input' in st.session_state else ''

            print(f"Current name: {current_name}")
            print(f"Current email: {current_email}")

            # Validate required fields
            if not current_name:
                st.error("⚠️ Please enter your full name.")
                return

            if not current_email:
                st.error("⚠️ Please enter your email address.")
                return

            # Update email in form data one final time
            st.session_state.form_data['personal_info']['email'] = current_email

            try:
                print("Preparing resume data...")
                # Prepare resume data with current form values
                resume_data = {
                    "personal_info": st.session_state.form_data['personal_info'],
                    "summary": st.session_state.form_data.get('summary', '').strip(),
                    "experience": st.session_state.form_data.get('experiences', []),
                    "education": st.session_state.form_data.get('education', []),
                    "projects": st.session_state.form_data.get('projects', []),
                    "skills": st.session_state.form_data.get('skills_categories', {
                        'technical': [],
                        'soft': [],
                        'languages': [],
                        'tools': []
                    }),
                    "template": selected_template
                }

                print(f"Resume data prepared: {resume_data}")

                try:
                    # Generate resume
                    resume_buffer = self.builder.generate_resume(resume_data)
                    if resume_buffer:
                        try:
                            # Save resume data to database with user_id
                            user_id = AuthManager.get_current_user_id()
                            save_resume_data(resume_data, user_id)

                            # Offer the resume for download
                            st.success("✅ Resume generated successfully!")

                            # Show snowflake effect
                            st.snow()

                            st.download_button(
                                label="Download Resume 📥",
                                data=resume_buffer,
                                file_name=f"{current_name.replace(' ', '_')}_resume.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                on_click=lambda: st.balloons()
                            )
                        except Exception as db_error:
                            print(f"Warning: Failed to save to database: {str(db_error)}")
                            # Still allow download even if database save fails
                            st.warning(
                                "⚠️ Resume generated but couldn't be saved to database")
                            
                            # Show balloons effect
                            st.balloons()

                            st.download_button(
                                label="Download Resume 📥",
                                data=resume_buffer,
                                file_name=f"{current_name.replace(' ', '_')}_resume.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                on_click=lambda: st.balloons()
                            )
                    else:
                        st.error(
                            "❌ Failed to generate resume. Please try again.")
                        print("Resume buffer was None")
                except Exception as gen_error:
                    print(f"Error during resume generation: {str(gen_error)}")
                    print(f"Full traceback: {traceback.format_exc()}")
                    st.error(f"❌ Error generating resume: {str(gen_error)}")

            except Exception as e:
                print(f"Error preparing resume data: {str(e)}")
                print(f"Full traceback: {traceback.format_exc()}")
                st.error(f"❌ Error preparing resume data: {str(e)}")

    def render_portfolio_generator(self):
        """Render the portfolio generator page"""
        from utils.ui_components import apply_modern_styles, page_header
        apply_modern_styles()
        
        # Inject targeted CSS for Portfolio Generator page content only
        st.markdown("""
        <style>
        /* Portfolio Generator Page Specific Styles - Targeting main content only */
        .portfolio-page {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%) !important;
            color: #ffffff !important;
            position: relative;
            overflow: hidden;
            border-radius: 10px;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Animated background pattern - only for portfolio page */
        .portfolio-page::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 25% 25%, #00d4ff22 0%, transparent 50%),
                radial-gradient(circle at 75% 75%, #4ecdc422 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, #ff6b6b11 0%, transparent 50%);
            animation: float 20s ease-in-out infinite;
            z-index: -1;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            33% { transform: translateY(-20px) rotate(1deg); }
            66% { transform: translateY(10px) rotate(-1deg); }
        }
        
        /* Page header styling with tech glow - scoped to portfolio page */
        .portfolio-page .page-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
            color: #00d4ff !important;
            border: 2px solid #00d4ff !important;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3) !important;
            border-radius: 15px !important;
            position: relative;
            overflow: hidden;
        }
        
        .portfolio-page .page-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.1), transparent);
            animation: shimmer 3s infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .portfolio-page .header-title {
            color: #00d4ff !important;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5) !important;
            font-weight: 700 !important;
        }
        
        .portfolio-page .header-subtitle, 
        .portfolio-page .header-description {
            color: #b0b0b0 !important;
        }
        
        /* Content sections with tech styling - scoped to portfolio page only */
        .portfolio-page div[data-testid="stMarkdownContainer"] {
            color: #ffffff !important;
        }
        
        /* Instructions box with cyber styling - scoped to portfolio page */
        .portfolio-page div[style*="background-color: #1e1e1e"] {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
            color: #ffffff !important;
            border: 2px solid #4ecdc4 !important;
            border-radius: 15px !important;
            box-shadow: 0 0 20px rgba(78, 205, 196, 0.2) !important;
            position: relative;
            overflow: hidden;
        }
        
        .portfolio-page div[style*="background-color: #1e1e1e"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #00d4ff, #4ecdc4, #ff6b6b, #00d4ff);
            animation: borderGlow 2s linear infinite;
        }
        
        @keyframes borderGlow {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        /* File uploader with tech styling - scoped to portfolio page */
        .portfolio-page .stFileUploader {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
            border: 2px dashed #00d4ff !important;
            border-radius: 15px !important;
            color: #ffffff !important;
            transition: all 0.3s ease !important;
        }
        
        .portfolio-page .stFileUploader:hover {
            border-color: #4ecdc4 !important;
            box-shadow: 0 0 25px rgba(0, 212, 255, 0.3) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Buttons with cyber glow - scoped to portfolio page */
        .portfolio-page .stButton > button {
            background: linear-gradient(135deg, #00d4ff 0%, #4ecdc4 100%) !important;
            color: #0a0a0a !important;
            border: none !important;
            border-radius: 25px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .portfolio-page .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: all 0.5s ease;
        }
        
        .portfolio-page .stButton > button:hover {
            background: linear-gradient(135deg, #4ecdc4 0%, #00d4ff 100%) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 25px rgba(0, 212, 255, 0.4) !important;
        }
        
        .portfolio-page .stButton > button:hover::before {
            left: 100%;
        }
        
        /* Success/Info messages with tech styling - scoped to portfolio page */
        .portfolio-page .stSuccess {
            background: linear-gradient(135deg, #1a4d3a 0%, #2e7d32 100%) !important;
            color: #4caf50 !important;
            border: 2px solid #4caf50 !important;
            border-radius: 10px !important;
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.3) !important;
        }
        
        .portfolio-page .stInfo {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
            color: #00d4ff !important;
            border: 2px solid #00d4ff !important;
            border-radius: 10px !important;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.3) !important;
        }
        
        /* Tabs with cyber styling - scoped to portfolio page */
        .portfolio-page .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
            border-radius: 15px !important;
            border: 2px solid #333 !important;
            padding: 5px !important;
        }
        
        .portfolio-page .stTabs [data-baseweb="tab"] {
            color: #b0b0b0 !important;
            background-color: transparent !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
        }
        
        .portfolio-page .stTabs [data-baseweb="tab"]:hover {
            color: #00d4ff !important;
            background-color: rgba(0, 212, 255, 0.1) !important;
        }
        
        .portfolio-page .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #00d4ff 0%, #4ecdc4 100%) !important;
            color: #0a0a0a !important;
            font-weight: 600 !important;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.4) !important;
        }
        
        /* Preview and download sections - scoped to portfolio page */
        .portfolio-page div[style*="background-color: #2d2d2d"] {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
            color: #ffffff !important;
            border: 2px solid #4ecdc4 !important;
            border-radius: 15px !important;
            box-shadow: 0 0 20px rgba(78, 205, 196, 0.2) !important;
        }
        
        .portfolio-page div[style*="background-color: #1a4d3a"] {
            background: linear-gradient(135deg, #1a4d3a 0%, #2e7d32 100%) !important;
            color: #4caf50 !important;
            border: 2px solid #4caf50 !important;
            border-radius: 15px !important;
            box-shadow: 0 0 20px rgba(76, 175, 80, 0.3) !important;
        }
        
        /* Subheaders with glow effect - scoped to portfolio page */
        .portfolio-page .stSubheader {
            color: #00d4ff !important;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5) !important;
            font-weight: 600 !important;
        }
        
        /* Text elements with better contrast - scoped to portfolio page */
        .portfolio-page h1, .portfolio-page h2, .portfolio-page h3, 
        .portfolio-page h4, .portfolio-page h5, .portfolio-page h6 {
            color: #00d4ff !important;
            text-shadow: 0 0 5px rgba(0, 212, 255, 0.3) !important;
        }
        
        .portfolio-page p, .portfolio-page li, .portfolio-page span {
            color: #e0e0e0 !important;
        }
        
        /* Code elements with tech styling - scoped to portfolio page */
        .portfolio-page code {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
            color: #4ecdc4 !important;
            border: 1px solid #4ecdc4 !important;
            border-radius: 5px !important;
            padding: 2px 6px !important;
            font-family: 'JetBrains Mono', monospace !important;
        }
        
        /* Spinner with tech colors - scoped to portfolio page */
        .portfolio-page .stSpinner {
            color: #00d4ff !important;
        }
        
        /* Download button with special styling - scoped to portfolio page */
        .portfolio-page .stDownloadButton > button {
            background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%) !important;
            color: white !important;
            border-radius: 25px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            transition: all 0.3s ease !important;
        }
        
        .portfolio-page .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 25px rgba(76, 175, 80, 0.4) !important;
        }
        
        /* Columns with subtle borders - scoped to portfolio page */
        .portfolio-page .stColumn {
            background-color: transparent !important;
            border-radius: 10px !important;
        }
        
        /* Markdown content styling - scoped to portfolio page */
        .portfolio-page .stMarkdown {
            color: #ffffff !important;
        }
        
        .portfolio-page .stMarkdown h3 {
            color: #00d4ff !important;
            text-shadow: 0 0 8px rgba(0, 212, 255, 0.4) !important;
        }
        
        .portfolio-page .stMarkdown p {
            color: #e0e0e0 !important;
            line-height: 1.6 !important;
        }
        
        .portfolio-page .stMarkdown li {
            color: #e0e0e0 !important;
        }
        
        /* Scrollbar styling - scoped to portfolio page content */
        .portfolio-page ::-webkit-scrollbar {
            width: 8px;
        }
        
        .portfolio-page ::-webkit-scrollbar-track {
            background: #1a1a2e;
            border-radius: 4px;
        }
        
        .portfolio-page ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #00d4ff, #4ecdc4);
            border-radius: 4px;
        }
        
        .portfolio-page ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #4ecdc4, #00d4ff);
        }
        
        /* Responsive adjustments - scoped to portfolio page */
        @media (max-width: 768px) {
            .portfolio-page {
                padding: 0.5rem !important;
            }
            
            .portfolio-page .page-header {
                margin: 0.5rem !important;
            }
        }
        
        /* Loading animation for tech feel */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .tech-pulse {
            animation: pulse 2s infinite;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Wrap the entire portfolio content in a scoped div
        st.markdown('<div class="portfolio-page">', unsafe_allow_html=True)
        
        page_header(
            "Portfolio Generator",
            "Transform your resume into a stunning portfolio website"
        )
        
        # Instructions with enhanced tech styling
        st.markdown("""
        <div style='background-color: #1e1e1e; padding: 25px; border-radius: 15px; margin: 15px 0; position: relative; overflow: hidden;'>
            <div style='position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #00d4ff, #4ecdc4, #ff6b6b, #00d4ff); animation: borderGlow 2s linear infinite;'></div>
            <h3 style='color: #00d4ff; text-shadow: 0 0 10px rgba(0, 212, 255, 0.5); margin-bottom: 15px; font-weight: 700;'>
                🚀 AI-Powered Portfolio Generator
            </h3>
            <p style='color: #e0e0e0; font-size: 16px; line-height: 1.6; margin-bottom: 20px;'>
                Transform your resume into a stunning, professional portfolio website with the power of AI! 
                Our intelligent system extracts your information and creates a beautiful, responsive portfolio 
                that showcases your skills and experience.
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 20px;'>
                <div style='background: rgba(0, 212, 255, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #00d4ff;'>
                    <strong style='color: #00d4ff;'>🤖 AI Intelligence</strong><br>
                    <span style='color: #b0b0b0; font-size: 14px;'>Smart data extraction and missing field inference</span>
                </div>
                <div style='background: rgba(78, 205, 196, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #4ecdc4;'>
                    <strong style='color: #4ecdc4;'>🎨 Modern Design</strong><br>
                    <span style='color: #b0b0b0; font-size: 14px;'>Responsive, mobile-friendly tech portfolio</span>
                </div>
                <div style='background: rgba(255, 107, 107, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #ff6b6b;'>
                    <strong style='color: #ff6b6b;'>⚡ Instant Deploy</strong><br>
                    <span style='color: #b0b0b0; font-size: 14px;'>Ready-to-host complete website package</span>
                </div>
            </div>
            <div style='margin-top: 20px; padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1);'>
                <h4 style='color: #4ecdc4; margin-bottom: 10px; font-size: 16px;'>✨ Key Features:</h4>
                <ul style='color: #e0e0e0; margin: 0; padding-left: 20px; line-height: 1.8;'>
                    <li><strong>Smart Extraction:</strong> AI analyzes your resume content intelligently</li>
                    <li><strong>Missing Data Inference:</strong> Generates professional content for incomplete sections</li>
                    <li><strong>Live Preview:</strong> See your portfolio before downloading</li>
                    <li><strong>Complete Package:</strong> Download as .zip with all files included</li>
                    <li><strong>Host Anywhere:</strong> Works with GitHub Pages, Netlify, Vercel, and more</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload section — only shown when no portfolio has been generated yet
        if 'portfolio_result' not in st.session_state:
            st.subheader("📄 Upload Your Resume")
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                        padding: 1.5rem; border-radius: 15px; text-align: center;
                        border: 2px solid #00d4ff; margin-bottom: 1.5rem;'>
                <h4 style='color: #00d4ff; margin-bottom: 0.5rem;'>🎨 Professional Tech Portfolio</h4>
                <p style='color: #b0b0b0; font-size: 0.9rem;'>Modern, responsive design optimized for developers and tech professionals</p>
            </div>
            """, unsafe_allow_html=True)
            
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume in PDF, DOCX, or TXT format",
            disabled='portfolio_result' in st.session_state  # hide after generation
        )
        
        if uploaded_file and 'portfolio_result' not in st.session_state:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Template Selection Section
            st.markdown("---")
            st.subheader("🎨 Choose Your Portfolio Style")
            
            # Get available templates
            available_templates = self.portfolio_generator.get_available_templates()
            
            # Create template selection cards
            template_cols = st.columns(4)
            
            # Initialize selected template in session state if not exists
            if 'selected_template' not in st.session_state:
                st.session_state.selected_template = 'tech-style'
            
            for idx, (template_key, template_info) in enumerate(available_templates.items()):
                with template_cols[idx]:
                    # Create card for each template
                    is_selected = st.session_state.selected_template == template_key
                    border_color = "#00d4ff" if is_selected else "#333"
                    bg_color = "rgba(0, 212, 255, 0.1)" if is_selected else "rgba(255, 255, 255, 0.05)"
                    
                    st.markdown(f"""
                    <div style='background: {bg_color}; 
                                padding: 15px; 
                                border-radius: 12px; 
                                border: 2px solid {border_color};
                                text-align: center;
                                margin-bottom: 10px;
                                transition: all 0.3s;'>
                        <h4 style='color: #00d4ff; margin: 0 0 8px 0; font-size: 16px;'>{template_info['name']}</h4>
                        <p style='color: #b0b0b0; font-size: 12px; margin: 0;'>{template_info['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(
                        "✓ Selected" if is_selected else "Select",
                        key=f"template_{template_key}",
                        type="primary" if is_selected else "secondary",
                        use_container_width=True,
                        disabled=is_selected
                    ):
                        st.session_state.selected_template = template_key
                        st.rerun()
            
            st.markdown("---")
            
            # Save uploaded file to uploads directory
            uploads_dir = "uploads"
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
            
            # Create unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = uploaded_file.name.split('.')[-1]
            saved_filename = f"portfolio_{timestamp}.{file_extension}"
            file_path = os.path.join(uploads_dir, saved_filename)
            
            # Save the file
            try:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Save file info to database
                from config.database import save_uploaded_file_info
                from auth.auth_manager import AuthManager
                
                # Get user_id - use authenticated user or default
                user_id = AuthManager.get_current_user_id() if AuthManager.is_authenticated() else None
                
                if not user_id:
                    st.warning("⚠️ You are not logged in. File uploaded but not saved to your history. Please log in to track your activities.")
                
                file_size = len(uploaded_file.getbuffer())
                save_uploaded_file_info(
                    filename=saved_filename,
                    original_name=uploaded_file.name,
                    file_path=file_path,
                    file_size=file_size,
                    file_type=uploaded_file.type,
                    upload_source="Portfolio Generator",
                    user_id=user_id
                )
            except Exception as e:
                st.warning(f"Could not save file: {str(e)}")
            
            # Generate portfolio button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                generate_portfolio = st.button(
                    "🚀 Generate Portfolio",
                    type="primary",
                    use_container_width=True,
                    help="Click to generate your portfolio website"
                )
            
            if generate_portfolio:
                with st.spinner("🔄 Generating your portfolio..."):
                    try:
                        # Initialize result variable to avoid UnboundLocalError
                        result = None
                        
                        # Extract text from uploaded file
                        if uploaded_file.type == "application/pdf":
                            resume_text = self.ai_analyzer.extract_text_from_pdf(uploaded_file)
                        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                            resume_text = self.ai_analyzer.extract_text_from_docx(uploaded_file)
                        else:
                            resume_text = uploaded_file.getvalue().decode('utf-8')
                        
                        if not resume_text or resume_text.strip() == "":
                            st.error("❌ Could not extract text from the uploaded file. Please try a different file.")
                            return
                        
                        # Check if API key is available for AI portfolio generation
                        if not hasattr(self.ai_analyzer, 'google_api_key') or not self.ai_analyzer.google_api_key:
                            st.warning("🔑 **Google API Key Required for AI Portfolio Generation**")
                            st.info("""
                            **To generate AI-powered portfolios, you need a Google Gemini API key.**
                            
                            **For Streamlit Cloud:**
                            1. Go to your app settings → Secrets
                            2. Add: `GOOGLE_API_KEY = "your_api_key_here"`
                            3. Get your free API key from: [Google AI Studio](https://aistudio.google.com/app/apikey)
                            
                            **Alternative:** The portfolio will be generated with basic extracted data.
                            """)
                        
                        # Generate portfolio using AI with selected template
                        selected_template = st.session_state.get('selected_template', 'tech-style')
                        result = self.portfolio_generator.generate_portfolio_with_ai(
                            resume_text, 
                            self.ai_analyzer,
                            user_id=f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            template_style=selected_template
                        )
                        
                        if result and result.get('success', False):
                            # Store result in session state
                            st.session_state.portfolio_result = result
                            st.success("🎉 Portfolio generated successfully! Preparing preview...")
                            # Rerun to show the portfolio with download/host buttons
                            st.rerun()
                        
                        elif result:
                            st.error(f"❌ {result.get('message', 'Portfolio generation failed')}")
                            if 'error' in result:
                                st.error(f"Error details: {result['error']}")
                        else:
                            st.error("❌ Portfolio generation failed - no result returned")
                    
                    except Exception as e:
                        st.error(f"❌ An error occurred while generating the portfolio: {str(e)}")
                        print(f"Portfolio generation error: {str(e)}")
                        return  # Exit the function to prevent further execution
        
        # ── PRIORITY: if a portfolio was already generated, show results ───────
        # MUST come before `if uploaded_file` because Streamlit persists the
        # file-uploader value across reruns, which would block this elif branch
        # from ever executing (including the deployment + purple-box logic).
        if 'portfolio_result' in st.session_state:

            try:
                result = st.session_state.portfolio_result
                
                # Validate that result has required keys and is properly structured
                required_keys = ['html_content', 'portfolio_data', 'zip_path', 'success']
                if not isinstance(result, dict) or not all(key in result for key in required_keys):
                    st.warning("⚠️ Previous portfolio data is incomplete. Please generate a new portfolio.")
                    if st.button("🗑️ Clear Incomplete Data"):
                        del st.session_state.portfolio_result
                        st.rerun()
                    return
                
                # Check if the result indicates success
                if not result.get('success', False):
                    st.error(f"❌ Previous portfolio generation failed: {result.get('message', 'Unknown error')}")
                    if st.button("🗑️ Clear Failed Data"):
                        del st.session_state.portfolio_result
                        st.rerun()
                    return
                
                st.subheader("🎯 Your Previously Generated Portfolio")
                
                # Show template info
                template_style = result.get('template_style', 'tech-style')
                template_info = self.portfolio_generator.get_available_templates().get(template_style, {})
                template_name = template_info.get('name', 'Tech Style')
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 12px 20px; border-radius: 10px; text-align: center;
                            margin-bottom: 15px;'>
                    <span style='color: white; font-size: 14px;'>
                        🎨 Template: <strong>{template_name}</strong>
                    </span>
                </div>
                """, unsafe_allow_html=True)

                # ══════════════════════════════════════════════════════════════
                # DEPLOYMENT SECTION — lives ABOVE the tabs so it is always
                # visible even after a rerun (reruns reset the active tab to
                # the first one, so anything inside a tab becomes invisible).
                # ══════════════════════════════════════════════════════════════

                zip_path_top = result.get('zip_path', '')
                # Store portfolio data in session state for deployment
                st.session_state.portfolio_data_for_deploy = result.get('portfolio_data', {})

                # Step 1 – run the actual deploy when the flag is set
                if st.session_state.get('do_deploy', False):
                    st.session_state.do_deploy = False   # consume flag immediately
                    with st.spinner("🚀 Uploading your portfolio to Netlify… please wait (up to 60 s)"):
                        try:
                            import zipfile as _zf
                            import shutil as _sh
                            netlify_token = os.getenv("NETLIFY_TOKEN")
                            if not netlify_token:
                                raise ValueError("NETLIFY_TOKEN not found in .env. Add it and restart the app.")
                            if not zip_path_top or not os.path.exists(zip_path_top):
                                raise FileNotFoundError(f"Portfolio ZIP not found: {zip_path_top}")
                            _tmp = tempfile.mkdtemp(prefix="netlify_")
                            try:
                                with _zf.ZipFile(zip_path_top, 'r') as _z:
                                    _z.extractall(_tmp)
                                _deploy_result = deploy_to_netlify(_tmp)
                            finally:
                                _sh.rmtree(_tmp, ignore_errors=True)
                            if _deploy_result.get("success"):
                                st.session_state.deployment_live_url = _deploy_result.get("live_url", "")
                                st.session_state.show_deployment_link = True
                                st.session_state.deploy_error = None
                                
                                # Save deployment to database
                                try:
                                    from config.user_data_manager import UserDataManager
                                    from auth.auth_manager import AuthManager
                                    
                                    # Check if user is authenticated
                                    if not AuthManager.is_authenticated():
                                        st.warning("⚠️ You are not logged in. Deployment successful but not saved to your history. Please log in to track your deployments.")
                                        print("WARNING: User not authenticated - deployment not saved to history")
                                    else:
                                        user_id = AuthManager.get_current_user_id()
                                        portfolio_data = st.session_state.get('portfolio_data_for_deploy', {})
                                        portfolio_name = portfolio_data.get('FULL_NAME', 'Portfolio')
                                        
                                        print(f"DEBUG: Saving deployment - user_id={user_id}, portfolio_name={portfolio_name}")
                                        
                                        save_result = UserDataManager.save_deployment(
                                            user_id=user_id,
                                            portfolio_name=portfolio_name,
                                            deployment_url=_deploy_result.get("live_url", ""),
                                            admin_url=_deploy_result.get("admin_url", ""),
                                            site_id=_deploy_result.get("site_id", "")
                                        )
                                        
                                        if save_result.get('success'):
                                            print(f"DEBUG: Deployment saved successfully with ID: {save_result.get('deployment_id')}")
                                            st.success("✅ Deployment saved to your history!")
                                        else:
                                            print(f"DEBUG: Failed to save deployment: {save_result.get('error')}")
                                            st.warning(f"⚠️ Deployment successful but could not save to history: {save_result.get('error')}")
                                        
                                except Exception as db_err:
                                    print(f"ERROR: Could not save deployment to database: {db_err}")
                                    import traceback
                                    traceback.print_exc()
                                    st.warning(f"⚠️ Deployment successful but could not save to history: {str(db_err)}")
                            else:
                                st.session_state.deploy_error = _deploy_result.get("error", "Deployment failed – check your Netlify token.")
                                st.session_state.show_deployment_link = False
                                st.session_state.deployment_live_url = None
                        except Exception as _ex:
                            st.session_state.deploy_error = str(_ex)
                            st.session_state.show_deployment_link = False
                            st.session_state.deployment_live_url = None

                # Step 2 – HOST button (sets flag + reruns; deploy runs above on next render)
                col_dl, col_host = st.columns(2)
                portfolio_data = st.session_state.get('portfolio_data_for_deploy', {})
                with col_dl:
                    if zip_path_top and os.path.exists(zip_path_top):
                        with open(zip_path_top, 'rb') as _f:
                            _zd = _f.read()
                        st.download_button(
                            label="📥 Download Portfolio (.zip)",
                            data=_zd,
                            file_name=f"{portfolio_data.get('FULL_NAME', 'Portfolio').replace(' ', '_')}_portfolio.zip",
                            mime="application/zip",
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        st.warning("⚠️ ZIP file not found.")

                with col_host:
                    if st.button("🚀 Host Portfolio Online", type="primary",
                                 use_container_width=True, key="host_portfolio_btn"):
                        st.session_state.do_deploy = True
                        st.session_state.deploy_error = None
                        st.session_state.show_deployment_link = False
                        st.session_state.deployment_live_url = None
                        st.rerun()

                # Step 3 – show deploy error (if any)
                if st.session_state.get('deploy_error'):
                    st.error(f"❌ {st.session_state.deploy_error}")

                # Step 4 – PURPLE BOX (always visible, above the tabs)
                if st.session_state.get('show_deployment_link') and st.session_state.get('deployment_live_url'):
                    _live_url = st.session_state.deployment_live_url
                    st.markdown("---")
                    st.success("🎉 Portfolio deployed and is now LIVE!")
                    st.balloons()
                    st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px 24px; border-radius: 16px; text-align: center;
                        margin: 16px 0; box-shadow: 0 8px 36px rgba(102,126,234,0.45);
                    '>
                        <h3 style='color:white; margin:0 0 10px; font-size:1.5rem;'>🌐 Your Portfolio is LIVE!</h3>
                        <p style='color:#ddd6fe; margin-bottom:20px; font-size:15px;'>
                            Your portfolio has been published. Click below to view it:
                        </p>
                        <a href="{_live_url}" target="_blank" rel="noopener noreferrer"
                           style='background:white; color:#667eea; padding:14px 40px;
                                  border-radius:32px; text-decoration:none; font-weight:700;
                                  font-size:16px; display:inline-block;
                                  box-shadow:0 4px 18px rgba(0,0,0,0.25);'>
                            🔗 Open My Portfolio →
                        </a>
                        <br><br>
                        <div style='background:rgba(255,255,255,0.12); color:#e0e7ff;
                                    padding:10px 18px; border-radius:10px; font-size:14px;
                                    word-break:break-all; display:inline-block; max-width:100%;'>
                            {_live_url}
                        </div>
                        <p style='color:#c4b5fd; margin-top:16px; font-size:13px;'>
                            Share this URL with recruiters, employers, and clients!
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🔄 Re-deploy", key="reset_deployment_url"):
                        st.session_state.deployment_live_url = None
                        st.session_state.show_deployment_link = False
                        st.session_state.deploy_error = None
                        st.rerun()

                st.markdown("---")

                # ══════════════════════════════════════════════════════════════
                # TABS — preview and info only (no deployment logic inside)
                # ══════════════════════════════════════════════════════════════
                preview_tab, download_tab = st.tabs(["🖥️ Preview", "ℹ️ Portfolio Info"])

                with preview_tab:
                    st.markdown("### 👀 Portfolio Preview")
                    st.markdown("""
                    <div style='background-color: #1a1a2e; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #00d4ff;'>
                        <p style='color: #e0e0e0; margin: 0;'>
                            💡 <strong>Preview Mode:</strong> Click navigation links to scroll to sections. External links show preview alerts.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    html_content = result.get('html_content', '')
                    if html_content:
                        st.components.v1.html(html_content, height=800, scrolling=True)
                    else:
                        st.error("❌ Portfolio preview not available")

                with download_tab:
                    portfolio_data = result.get('portfolio_data', {})
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Name:** {portfolio_data.get('FULL_NAME', 'Unknown')}")
                        st.info(f"**Role:** {portfolio_data.get('JOB_TITLE', 'Professional')}")
                        st.info(f"**Email:** {portfolio_data.get('EMAIL', 'Not provided')}")
                    with col2:
                        st.info(f"**Experience:** {portfolio_data.get('YEARS_EXPERIENCE', 'N/A')} years")
                        st.info(f"**Projects:** {portfolio_data.get('PROJECT_COUNT', 'N/A')} projects")
                        st.info(f"**Skills:** {portfolio_data.get('SKILL_COUNT', 'N/A')} skills")

                    st.markdown("---")
                    if st.button("🗑️ Clear Generated Files", key="clear_portfolio_files"):
                        try:
                            user_id = result.get('user_id')
                            if user_id:
                                self.portfolio_generator.cleanup_generated_portfolio(user_id)
                            del st.session_state.portfolio_result
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error during cleanup: {str(e)}")
                            del st.session_state.portfolio_result
                            st.rerun()

            
            except Exception as e:
                st.error(f"❌ Error displaying previous portfolio: {str(e)}")
                st.info("💡 Try generating a new portfolio.")
                if st.button("🗑️ Clear Error Data"):
                    del st.session_state.portfolio_result
                    st.rerun()
        
        # Enhanced feature showcase with tech styling
        st.markdown("""
        <div style='margin: 40px 0; padding: 2px; background: linear-gradient(90deg, #00d4ff, #4ecdc4, #ff6b6b, #00d4ff); border-radius: 15px;'>
            <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; border-radius: 13px;'>
                <h2 style='text-align: center; color: #00d4ff; text-shadow: 0 0 15px rgba(0, 212, 255, 0.5); margin-bottom: 30px; font-weight: 700;'>
                    ✨ Portfolio Features & Benefits
                </h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #00d4ff; box-shadow: 0 0 20px rgba(0, 212, 255, 0.2); transition: all 0.3s ease; height: 200px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 3rem; color: #00d4ff; margin-bottom: 15px; text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);'>🎨</div>
                <h4 style='color: #00d4ff; margin-bottom: 10px; font-weight: 600;'>Modern Tech Design</h4>
                <p style='color: #e0e0e0; font-size: 14px; line-height: 1.5;'>Cutting-edge UI with animations, gradients, and responsive layouts</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #4ecdc4; box-shadow: 0 0 20px rgba(78, 205, 196, 0.2); transition: all 0.3s ease; height: 200px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 3rem; color: #4ecdc4; margin-bottom: 15px; text-shadow: 0 0 10px rgba(78, 205, 196, 0.5);'>🤖</div>
                <h4 style='color: #4ecdc4; margin-bottom: 10px; font-weight: 600;'>AI-Powered Content</h4>
                <p style='color: #e0e0e0; font-size: 14px; line-height: 1.5;'>Smart content generation and professional data inference</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #ff6b6b; box-shadow: 0 0 20px rgba(255, 107, 107, 0.2); transition: all 0.3s ease; height: 200px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size: 3rem; color: #ff6b6b; margin-bottom: 15px; text-shadow: 0 0 10px rgba(255, 107, 107, 0.5);'>⚡</div>
                <h4 style='color: #ff6b6b; margin-bottom: 10px; font-weight: 600;'>Instant Deployment</h4>
                <p style='color: #e0e0e0; font-size: 14px; line-height: 1.5;'>Ready-to-host package with optimized performance</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional tech features section
        st.markdown("""
        <div style='margin: 30px 0; padding: 25px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 15px; border: 2px solid rgba(255, 255, 255, 0.1);'>
            <h3 style='color: #00d4ff; text-align: center; margin-bottom: 20px; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);'>
                🚀 Technical Specifications
            </h3>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;'>
                <div style='text-align: center; padding: 15px;'>
                    <div style='color: #4ecdc4; font-size: 1.5rem; margin-bottom: 8px;'>📱</div>
                    <strong style='color: #4ecdc4;'>Responsive Design</strong><br>
                    <span style='color: #b0b0b0; font-size: 13px;'>Mobile-first approach</span>
                </div>
                <div style='text-align: center; padding: 15px;'>
                    <div style='color: #00d4ff; font-size: 1.5rem; margin-bottom: 8px;'>🎯</div>
                    <strong style='color: #00d4ff;'>SEO Optimized</strong><br>
                    <span style='color: #b0b0b0; font-size: 13px;'>Meta tags & structure</span>
                </div>
                <div style='text-align: center; padding: 15px;'>
                    <div style='color: #ff6b6b; font-size: 1.5rem; margin-bottom: 8px;'>⚡</div>
                    <strong style='color: #ff6b6b;'>Fast Loading</strong><br>
                    <span style='color: #b0b0b0; font-size: 13px;'>Optimized assets</span>
                </div>
                <div style='text-align: center; padding: 15px;'>
                    <div style='color: #4ecdc4; font-size: 1.5rem; margin-bottom: 8px;'>🔧</div>
                    <strong style='color: #4ecdc4;'>Easy Hosting</strong><br>
                    <span style='color: #b0b0b0; font-size: 13px;'>Deploy anywhere</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Close the portfolio page wrapper
        st.markdown('</div>', unsafe_allow_html=True)

    def render_about(self):
        """Render the about page"""
        from utils.ui_components import apply_modern_styles
        import base64

        def get_image_as_base64(file_path):
            try:
                with open(file_path, "rb") as f:
                    return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
            except:
                return None

        image_base64 = get_image_as_base64(
            os.path.join(os.path.dirname(__file__), "assets", "124852522.jpeg"))

        apply_modern_styles()

        st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
        .about-hero{text-align:center;padding:3rem 1rem 2rem;background:linear-gradient(135deg,#0f172a,#1e293b);
          border-radius:16px;margin-bottom:2rem;border:1px solid rgba(76,175,80,.2)}
        .about-hero h1{font-size:2.6rem;color:#4CAF50;margin-bottom:.5rem}
        .about-hero p{color:#aaa;font-size:1.1rem}
        .profile-card{text-align:center;padding:2rem;background:rgba(30,41,59,.8);
          border-radius:16px;margin-bottom:2rem;border:1px solid rgba(76,175,80,.15)}
        .profile-img{width:160px;height:160px;border-radius:50%;object-fit:cover;
          border:4px solid #4CAF50;margin:0 auto 1rem;display:block}
        .profile-name{font-size:1.8rem;color:white;margin-bottom:.3rem}
        .profile-role{color:#4CAF50;font-size:1rem;margin-bottom:1.2rem}
        .social-row{display:flex;justify-content:center;gap:1rem;margin:1rem 0}
        .social-btn{width:48px;height:48px;border-radius:50%;background:rgba(76,175,80,.1);
          color:#4CAF50;display:flex;align-items:center;justify-content:center;
          font-size:1.3rem;text-decoration:none;transition:all .3s}
        .social-btn:hover{background:#4CAF50;color:white;transform:translateY(-3px)}
        .bio{color:#ccc;line-height:1.8;font-size:.95rem;text-align:left;margin-top:1rem}
        .features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
          gap:1.2rem;margin:1.5rem 0}
        .feat-card{background:rgba(30,41,59,.8);border:1px solid rgba(76,175,80,.15);
          border-radius:12px;padding:1.5rem;transition:border-color .3s}
        .feat-card:hover{border-color:#4CAF50}
        .feat-icon{font-size:2rem;color:#4CAF50;margin-bottom:.8rem}
        .feat-title{color:white;font-size:1.05rem;font-weight:700;margin-bottom:.5rem}
        .feat-desc{color:#aaa;font-size:.85rem;line-height:1.6}
        .tech-stack{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1rem;justify-content:center}
        .tech-badge{background:rgba(76,175,80,.1);color:#4CAF50;border:1px solid rgba(76,175,80,.3);
          padding:4px 12px;border-radius:20px;font-size:.78rem;font-weight:600}
        .section-title{color:white;font-size:1.4rem;font-weight:700;margin:2rem 0 1rem;
          padding-bottom:.5rem;border-bottom:2px solid rgba(76,175,80,.3)}
        </style>
        """, unsafe_allow_html=True)

        # Hero
        st.markdown("""
        <div class="about-hero">
          <h1>🚀 Smart Resume AI</h1>
          <p>Your all-in-one AI-powered career platform — from resume analysis to live mock interviews</p>
        </div>
        """, unsafe_allow_html=True)

        # Profile
        img_src = image_base64 or "https://avatars.githubusercontent.com/samsanjay99"
        st.markdown(f"""
        <div class="profile-card">
          <img src="{img_src}" class="profile-img"
               onerror="this.src='https://avatars.githubusercontent.com/samsanjay99'">
          <div class="profile-name">Sanjay Kumar CP</div>
          <div class="profile-role">AI/ML Developer · Full Stack Engineer</div>
          <div class="social-row">
            <a href="https://github.com/samsanjay99" class="social-btn" target="_blank">
              <i class="fab fa-github"></i></a>
            <a href="https://www.linkedin.com/in/sanjay-kumar-cp-174198329" class="social-btn" target="_blank">
              <i class="fab fa-linkedin"></i></a>
            <a href="mailto:sanjaykumarcp9900@gmail.com" class="social-btn" target="_blank">
              <i class="fas fa-envelope"></i></a>
          </div>
          <p class="bio">
            Hi, I'm Sanjay — a passionate AI/ML developer who built Smart Resume AI to help job seekers
            stand out in a competitive market. This platform combines resume intelligence, voice AI interviews,
            personalized learning, and portfolio generation into one seamless experience.
            Every feature is designed to give you a real edge in your career journey.
          </p>
        </div>
        """, unsafe_allow_html=True)

        # Features
        st.markdown('<div class="section-title">✨ Platform Features</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="features-grid">
          <div class="feat-card">
            <div class="feat-icon"><i class="fas fa-file-alt"></i></div>
            <div class="feat-title">AI Resume Analysis</div>
            <div class="feat-desc">Deep analysis of your resume with ATS scoring, keyword optimization,
            skill gap detection, and actionable improvement suggestions powered by Gemini AI.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon"><i class="fas fa-microphone"></i></div>
            <div class="feat-title">AI Mock Interviews</div>
            <div class="feat-desc">Live voice interviews with VAPI's Clara AI or free browser-based voice mode.
            Get scored on communication, technical knowledge, problem-solving, and more with a full PDF report.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon"><i class="fas fa-graduation-cap"></i></div>
            <div class="feat-title">Learning Dashboard</div>
            <div class="feat-desc">Personalized course recommendations based on your skill gaps from resume analysis
            and mock interviews. Track your learning progress across all topics.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon"><i class="fas fa-globe"></i></div>
            <div class="feat-title">Portfolio Generator</div>
            <div class="feat-desc">Instantly transform your resume into a professional web portfolio with multiple
            design templates. Deploy to Netlify with one click and share your personal URL.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon"><i class="fas fa-chart-bar"></i></div>
            <div class="feat-title">Analytics Dashboard</div>
            <div class="feat-desc">Track your resume analysis history, interview scores over time, skill progression,
            and get insights into your career development journey.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon"><i class="fas fa-search"></i></div>
            <div class="feat-title">Job Search</div>
            <div class="feat-desc">Search for relevant job opportunities based on your skills and target role.
            Get matched with positions that align with your resume profile.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon"><i class="fas fa-user-circle"></i></div>
            <div class="feat-title">Profile Management</div>
            <div class="feat-desc">Manage your professional profile, track all your resume analyses, interview
            history, and download your PDF reports anytime.</div>
          </div>
          <div class="feat-card">
            <div class="feat-icon"><i class="fas fa-shield-alt"></i></div>
            <div class="feat-title">Secure & Private</div>
            <div class="feat-desc">Your data is stored securely in a PostgreSQL database. All API keys are
            environment-protected and your personal information is never shared.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Tech stack
        st.markdown('<div class="section-title">🛠️ Built With</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="tech-stack">
          <span class="tech-badge">Python</span>
          <span class="tech-badge">Streamlit</span>
          <span class="tech-badge">Google Gemini AI</span>
          <span class="tech-badge">VAPI Voice AI</span>
          <span class="tech-badge">PostgreSQL (Neon)</span>
          <span class="tech-badge">Vercel Serverless</span>
          <span class="tech-badge">GitHub Pages</span>
          <span class="tech-badge">ReportLab PDF</span>
          <span class="tech-badge">Web Speech API</span>
          <span class="tech-badge">Netlify</span>
        </div>
        """, unsafe_allow_html=True)

        # Add Font Awesome icons and custom CSS
        st.markdown("""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                .profile-section, .vision-section, .feature-card {
                    text-align: center;
                    padding: 2rem;
                    background: rgba(45, 45, 45, 0.9);
                    border-radius: 20px;
                    margin: 2rem auto;
                    max-width: 800px;
                }

                .profile-image {
                    width: 200px;
                    height: 200px;
                    border-radius: 50%;
                    margin: 0 auto 1.5rem;
                    display: block;
                    object-fit: cover;
                    border: 4px solid #4CAF50;
                }

                .profile-name {
                    font-size: 2.5rem;
                    color: white;
                    margin-bottom: 0.5rem;
                }

                .profile-title {
                    font-size: 1.2rem;
                    color: #4CAF50;
                    margin-bottom: 1.5rem;
                }

                .social-links {
                    display: flex;
                    justify-content: center;
                    gap: 1.5rem;
                    margin: 2rem 0;
                }

                .social-link {
                    font-size: 2rem;
                    color: #4CAF50;
                    transition: all 0.3s ease;
                    padding: 0.5rem;
                    border-radius: 50%;
                    background: rgba(76, 175, 80, 0.1);
                    width: 60px;
                    height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-decoration: none;
                }

                .social-link:hover {
                    transform: translateY(-5px);
                    background: #4CAF50;
                    color: white;
                    box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
                }

                .bio-text {
                    color: #ddd;
                    line-height: 1.8;
                    font-size: 1.1rem;
                    margin-top: 2rem;
                    text-align: left;
                }

                .vision-text {
                    color: #ddd;
                    line-height: 1.8;
                    font-size: 1.1rem;
                    font-style: italic;
                    margin: 1.5rem 0;
                    text-align: left;
                }

                .vision-icon {
                    font-size: 2.5rem;
                    color: #4CAF50;
                    margin-bottom: 1rem;
                }

                .vision-title {
                    font-size: 2rem;
                    color: white;
                    margin-bottom: 1rem;
                }

                .features-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 2rem;
                    margin: 2rem auto;
                    max-width: 1200px;
                }

                .feature-card {
                    padding: 2rem;
                    margin: 0;
                }

                .feature-icon {
                    font-size: 2.5rem;
                    color: #4CAF50;
                    margin-bottom: 1rem;
                }

                .feature-title {
                    font-size: 1.5rem;
                    color: white;
                    margin: 1rem 0;
                }

                .feature-description {
                    color: #ddd;
                    line-height: 1.6;
                }
            </style>
        """, unsafe_allow_html=True)

        # Hero Section
        st.markdown("""
            <div class="hero-section">
                <h1 class="hero-title">About Smart Resume AI</h1>
                <p class="hero-subtitle">A powerful AI-driven platform for optimizing your resume</p>
            </div>
        """, unsafe_allow_html=True)

        # Profile Section
        st.markdown(f"""
            <div class="profile-section">
                <img src="{image_base64 if image_base64 else 'https://avatars.githubusercontent.com/samsanjay99'}"
                     alt="Sanjay Kumar CP"
                     class="profile-image"
                     onerror="this.onerror=null; this.src='https://avatars.githubusercontent.com/samsanjay99';">
                <h2 class="profile-name">Sanjay Kumar CP (samsanjay99)</h2>
                <p class="profile-title">AI/ML Developer & Resume Optimization Expert</p>
                <div class="social-links">
                    <a href="https://github.com/samsanjay99" class="social-link" target="_blank">
                        <i class="fab fa-github"></i>
                    </a>
                    <a href="https://www.linkedin.com/in/sanjay-kumar-cp-174198329" class="social-link" target="_blank">
                        <i class="fab fa-linkedin"></i>
        """, unsafe_allow_html=True)

    def render_analyzer(self):
        """Render the resume analyzer page"""
        apply_modern_styles()

        # Page Header
        page_header(
            "Resume Analyzer",
            "Get instant AI-powered feedback to optimize your resume"
        )

        # Create tabs for Normal Analyzer and AI Analyzer
        analyzer_tabs = st.tabs(["Standard Analyzer", "AI Analyzer"])

        with analyzer_tabs[0]:
            # Job Role Selection
            categories = list(self.job_roles.keys())
            selected_category = st.selectbox(
    "Job Category", categories, key="standard_category")

            roles = list(self.job_roles[selected_category].keys())
            selected_role = st.selectbox(
    "Specific Role", roles, key="standard_role")

            role_info = self.job_roles[selected_category][selected_role]

            # Display role information
            st.markdown(f"""
            <div style='background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h3>{selected_role}</h3>
                <p>{role_info['description']}</p>
                <h4>Required Skills:</h4>
                <p>{', '.join(role_info['required_skills'])}</p>
            </div>
            """, unsafe_allow_html=True)

            # File Upload
            uploaded_file = st.file_uploader(
    "Upload your resume", type=[
        'pdf', 'docx'], key="standard_file")

            if not uploaded_file:
                # Display empty state with a prominent upload button
                st.markdown(
                    self.render_empty_state(
                    "fas fa-cloud-upload-alt",
                    "Upload your resume to get started with standard analysis"
                    ),
                    unsafe_allow_html=True
                )
                # Add a prominent upload button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown("""
                    <style>
                    .upload-button {
                        background: linear-gradient(90deg, #4b6cb7, #182848);
                        color: white;
                        border: none;
                        border-radius: 10px;
                        padding: 15px 25px;
                        font-size: 18px;
                        font-weight: bold;
                        cursor: pointer;
                        width: 100%;
                        text-align: center;
                        margin: 20px 0;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                        transition: all 0.3s ease;
                    }
                    .upload-button:hover {
                        transform: translateY(-3px);
                        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
                    }

                    """, unsafe_allow_html=True)

            if uploaded_file:
                # Save uploaded file to uploads directory
                
                uploads_dir = "uploads"
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)
                
                # Create unique filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_extension = uploaded_file.name.split('.')[-1]
                saved_filename = f"standard_{timestamp}.{file_extension}"
                file_path = os.path.join(uploads_dir, saved_filename)
                
                # Save the file
                try:
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Save file info to database
                    from config.database import save_uploaded_file_info
                    from auth.auth_manager import AuthManager
                    file_size = len(uploaded_file.getbuffer())
                    save_uploaded_file_info(
                        filename=saved_filename,
                        original_name=uploaded_file.name,
                        file_path=file_path,
                        file_size=file_size,
                        file_type=uploaded_file.type,
                        upload_source="Standard Analysis",
                        user_id=AuthManager.get_current_user_id()
                    )
                except Exception as e:
                    st.warning(f"Could not save file: {str(e)}")
                
                # Add a prominent analyze button
                analyze_standard = st.button("🔍 Analyze My Resume",
                                    type="primary",
                                    use_container_width=True,
                                    key="analyze_standard_button")

                if analyze_standard:
                    with st.spinner("Analyzing your document..."):
                        # Get file content
                        text = ""
                        try:
                            if uploaded_file.type == "application/pdf":
                                try:
                                    text = self.analyzer.extract_text_from_pdf(uploaded_file)
                                except Exception as pdf_error:
                                    st.error(f"PDF extraction failed: {str(pdf_error)}")
                                    st.info("Trying alternative PDF extraction method...")
                                    # Try AI analyzer as backup
                                    try:
                                        text = self.ai_analyzer.extract_text_from_pdf(uploaded_file)
                                    except Exception as backup_error:
                                        st.error(f"All PDF extraction methods failed: {str(backup_error)}")
                                        return
                            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                try:
                                    text = self.analyzer.extract_text_from_docx(uploaded_file)
                                except Exception as docx_error:
                                    st.error(f"DOCX extraction failed: {str(docx_error)}")
                                    # Try AI analyzer as backup
                                    try:
                                        text = self.ai_analyzer.extract_text_from_docx(uploaded_file)
                                    except Exception as backup_error:
                                        st.error(f"All DOCX extraction methods failed: {str(backup_error)}")
                                        return
                            else:
                                text = uploaded_file.getvalue().decode()
                                
                            if not text or text.strip() == "":
                                st.error("Could not extract any text from the uploaded file. Please try a different file.")
                                return
                        except Exception as e:
                            st.error(f"Error reading file: {str(e)}")
                            return

                        # Analyze the document
                        analysis = self.analyzer.analyze_resume({'raw_text': text}, role_info)
                        
                        # Check if analysis returned an error
                        if 'error' in analysis:
                            st.error(analysis['error'])
                            return

                        # Show snowflake effect
                        st.snow()

                        # Save resume data to database
                        resume_data = {
                            'personal_info': {
                                'name': analysis.get('name', ''),
                                'email': analysis.get('email', ''),
                                'phone': analysis.get('phone', ''),
                                'linkedin': analysis.get('linkedin', ''),
                                'github': analysis.get('github', ''),
                                'portfolio': analysis.get('portfolio', '')
                            },
                            'summary': analysis.get('summary', ''),
                            'target_role': selected_role,
                            'target_category': selected_category,
                            'education': analysis.get('education', []),
                            'experience': analysis.get('experience', []),
                            'projects': analysis.get('projects', []),
                            'skills': analysis.get('skills', []),
                            'template': ''
                        }

                        # Save to database with user_id
                        try:
                            user_id = AuthManager.get_current_user_id()
                            resume_id = save_resume_data(resume_data, user_id)

                            # Save analysis data (old system)
                            analysis_data = {
                                'resume_id': resume_id,
                                'ats_score': analysis['ats_score'],
                                'keyword_match_score': analysis['keyword_match']['score'],
                                'format_score': analysis['format_score'],
                                'section_score': analysis['section_score'],
                                'missing_skills': ','.join(analysis['keyword_match']['missing_skills']),
                                'recommendations': ','.join(analysis['suggestions'])
                            }
                            save_analysis_data(resume_id, analysis_data, user_id)
                            
                            # Also save to new analysis storage system
                            from config.analysis_manager import AnalysisManager
                            
                            # Save resume to new system
                            resume_result = AnalysisManager.save_resume(
                                user_id=user_id,
                                file_name=uploaded_file.name,
                                parsed_text=text,
                                file_url=file_path if 'file_path' in locals() else None,
                                file_type=uploaded_file.type
                            )
                            
                            if resume_result['success']:
                                new_resume_id = resume_result['resume_id']
                                
                                # Update resume status with detected role
                                AnalysisManager.update_resume_status(
                                    new_resume_id, 
                                    'completed', 
                                    selected_role
                                )
                                
                                # Save analysis to new system
                                new_analysis_data = {
                                    'detected_skills': analysis.get('skills', []),
                                    'experience_years': len(analysis.get('experience', [])),
                                    'education_detected': ', '.join([str(edu) for edu in analysis.get('education', [])]) if analysis.get('education') else 'Not specified',
                                    'projects_detected': analysis.get('projects', []),
                                    'certifications_detected': [],
                                    'resume_score': analysis['ats_score'],
                                    'analysis_summary': f"ATS Score: {analysis['ats_score']}%, Format: {analysis['format_score']}%, Sections: {analysis['section_score']}%",
                                    'ai_feedback': ', '.join(analysis.get('suggestions', []))
                                }
                                
                                AnalysisManager.save_analysis(user_id, new_resume_id, new_analysis_data)
                            
                            # Generate course recommendations based on missing skills
                            missing_skills = analysis['keyword_match'].get('missing_skills', [])
                            
                            # Debug: Show what skills were detected
                            st.info(f"🔍 Detected {len(missing_skills)} missing skills: {', '.join(missing_skills[:5])}")
                            
                            if missing_skills:
                                from config.course_recommendation_manager import CourseRecommendationManager
                                
                                try:
                                    course_result = CourseRecommendationManager.save_recommendations_for_user(
                                        user_id=user_id,
                                        resume_id=resume_id,
                                        analysis_id=resume_id,  # Using resume_id as analysis_id for now
                                        missing_skills=missing_skills
                                    )
                                    
                                    if course_result['success']:
                                        st.success(f"✅ Resume data saved! Generated {course_result['count']} course recommendations")
                                        st.info("📚 Check the Learning Dashboard to see your personalized courses!")
                                    else:
                                        st.warning(f"⚠️ Resume saved but course recommendations failed: {course_result.get('message', 'Unknown error')}")
                                except Exception as course_error:
                                    st.warning(f"⚠️ Resume saved but course recommendations failed: {str(course_error)}")
                                    print(f"Course recommendation error: {course_error}")
                            else:
                                st.success("✅ Resume data saved successfully!")
                                st.info("ℹ️ No skill gaps detected - your resume looks great!")
                        except Exception as e:
                            st.error(f"Error saving to database: {str(e)}")
                            print(f"Database error: {e}")

                        # Show results based on document type
                        if analysis.get('document_type') != 'resume':
                            st.error(f"⚠️ This appears to be a {analysis['document_type']} document, not a resume!")
                            st.warning(
                                "Please upload a proper resume for ATS analysis.")
                            return
                        # Display results in a modern card layout
                    col1, col2 = st.columns(2)

                    with col1:
                        # ATS Score Card with circular progress
                        st.markdown("""
                        <div class="feature-card">
                            <h2>ATS Score</h2>
                            <div style="position: relative; width: 150px; height: 150px; margin: 0 auto;">
                                <div style="
                                    position: absolute;
                                    width: 150px;
                                    height: 150px;
                                    border-radius: 50%;
                                    background: conic-gradient(
                                        #4CAF50 0% {score}%,
                                        #2c2c2c {score}% 100%
                                    );
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                ">
                                    <div style="
                                        width: 120px;
                                        height: 120px;
                                        background: #1a1a1a;
                                        border-radius: 50%;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        font-size: 24px;
                                        font-weight: bold;
                                        color: {color};
                                    ">
                                        {score}
                                    </div>
                                </div>
                            </div>
                            <div style="text-align: center; margin-top: 10px;">
                                <span style="
                                    font-size: 1.2em;
                                    color: {color};
                                    font-weight: bold;
                                ">
                                    {status}
                                </span>
                            </div>
                        """.format(
                            score=analysis['ats_score'],
                            color='#4CAF50' if analysis['ats_score'] >= 80 else '#FFA500' if analysis[
                                'ats_score'] >= 60 else '#FF4444',
                            status='Excellent' if analysis['ats_score'] >= 80 else 'Good' if analysis[
                                'ats_score'] >= 60 else 'Needs Improvement'
                        ), unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)

                        # self.display_analysis_results(analysis_results)

                        # Skills Match Card
                        st.markdown("""
                        <div class="feature-card">
                            <h2>Skills Match</h2>
                        """, unsafe_allow_html=True)

                        st.metric(
                            "Keyword Match", f"{int(analysis.get('keyword_match', {}).get('score', 0))}%")

                        if analysis['keyword_match']['missing_skills']:
                            st.markdown("#### Missing Skills:")
                            for skill in analysis['keyword_match']['missing_skills']:
                                st.markdown(f"- {skill}")

                        st.markdown("</div>", unsafe_allow_html=True)

                    with col2:
                        # Format Score Card
                        st.markdown("""
                        <div class="feature-card">
                            <h2>Format Analysis</h2>
                        """, unsafe_allow_html=True)

                        st.metric("Format Score",
                                  f"{int(analysis.get('format_score', 0))}%")
                        st.metric("Section Score",
                                  f"{int(analysis.get('section_score', 0))}%")

                        st.markdown("</div>", unsafe_allow_html=True)

                        # Suggestions Card with improved UI
                        st.markdown("""
                        <div class="feature-card">
                            <h2>📋 Resume Improvement Suggestions</h2>
                        """, unsafe_allow_html=True)

                            # Contact Section
                        if analysis.get('contact_suggestions'):
                                st.markdown("""
                                <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                                    <h3 style='color: #4CAF50; margin-bottom: 10px;'>📞 Contact Information</h3>
                                    <ul style='list-style-type: none; padding-left: 0;'>
                                """, unsafe_allow_html=True)
                                for suggestion in analysis.get(
                                    'contact_suggestions', []):
                                    st.markdown(
    f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>",
     unsafe_allow_html=True)
                                st.markdown(
    "</ul></div>", unsafe_allow_html=True)

                            # Summary Section
                        if analysis.get('summary_suggestions'):
                                st.markdown("""
                                <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                                    <h3 style='color: #4CAF50; margin-bottom: 10px;'>📝 Professional Summary</h3>
                                    <ul style='list-style-type: none; padding-left: 0;'>
                                """, unsafe_allow_html=True)
                                for suggestion in analysis.get(
                                    'summary_suggestions', []):
                                    st.markdown(
    f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>",
     unsafe_allow_html=True)
                                st.markdown(
    "</ul></div>", unsafe_allow_html=True)

                            # Skills Section
                        if analysis.get(
                            'skills_suggestions') or analysis['keyword_match']['missing_skills']:
                                st.markdown("""
                                <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                                    <h3 style='color: #4CAF50; margin-bottom: 10px;'>🎯 Skills</h3>
                                    <ul style='list-style-type: none; padding-left: 0;'>
                                """, unsafe_allow_html=True)
                                for suggestion in analysis.get(
                                    'skills_suggestions', []):
                                    st.markdown(
    f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>",
     unsafe_allow_html=True)
                                if analysis['keyword_match']['missing_skills']:
                                    st.markdown(
    "<li style='margin-bottom: 8px;'>✓ Consider adding these relevant skills:</li>",
     unsafe_allow_html=True)
                                    for skill in analysis['keyword_match']['missing_skills']:
                                        st.markdown(
    f"<li style='margin-left: 20px; margin-bottom: 4px;'>• {skill}</li>",
     unsafe_allow_html=True)
                                st.markdown(
    "</ul></div>", unsafe_allow_html=True)
                                
                                # Add learning dashboard link if missing skills exist
                                if analysis['keyword_match']['missing_skills']:
                                    st.markdown("""
                                    <div style='background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); 
                                                padding: 1rem; border-radius: 10px; margin: 10px 0; text-align: center;'>
                                        <p style='color: white; margin: 0; font-size: 1.1rem; font-weight: 600;'>
                                            🎓 Want to learn these skills?
                                        </p>
                                        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                                            We've generated personalized YouTube course recommendations for you!
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if st.button("📚 View Learning Recommendations", use_container_width=True, type="primary"):
                                        st.session_state.page = 'learning'
                                        st.rerun()

                            # Experience Section
                        if analysis.get('experience_suggestions'):
                                st.markdown("""
                                <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                                    <h3 style='color: #4CAF50; margin-bottom: 10px;'>💼 Work Experience</h3>
                                    <ul style='list-style-type: none; padding-left: 0;'>
                                """, unsafe_allow_html=True)
                                for suggestion in analysis.get(
                                    'experience_suggestions', []):
                                    st.markdown(
    f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>",
     unsafe_allow_html=True)
                                st.markdown(
    "</ul></div>", unsafe_allow_html=True)

                            # Education Section
                        if analysis.get('education_suggestions'):
                                st.markdown("""
                                <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                                    <h3 style='color: #4CAF50; margin-bottom: 10px;'>🎓 Education</h3>
                                    <ul style='list-style-type: none; padding-left: 0;'>
                                """, unsafe_allow_html=True)
                                for suggestion in analysis.get(
                                    'education_suggestions', []):
                                    st.markdown(
    f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>",
     unsafe_allow_html=True)
                                st.markdown(
    "</ul></div>", unsafe_allow_html=True)

                            # General Formatting Suggestions
                        if analysis.get('format_suggestions'):
                                st.markdown("""
                                <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                                    <h3 style='color: #4CAF50; margin-bottom: 10px;'>📄 Formatting</h3>
                                    <ul style='list-style-type: none; padding-left: 0;'>
                                """, unsafe_allow_html=True)
                                for suggestion in analysis.get(
                                    'format_suggestions', []):
                                    st.markdown(
    f"<li style='margin-bottom: 8px;'>✓ {suggestion}</li>",
     unsafe_allow_html=True)
                                st.markdown(
    "</ul></div>", unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)

                        # Course Recommendations
                    st.markdown("""
                        <div class="feature-card">
                            <h2>📚 Recommended Courses</h2>
                        """, unsafe_allow_html=True)

                        # Get courses based on role and category
                    courses = get_courses_for_role(selected_role)
                    if not courses:
                            category = get_category_for_role(selected_role)
                            courses = COURSES_BY_CATEGORY.get(
                                category, {}).get(selected_role, [])

                        # Display courses in a grid
                    cols = st.columns(2)
                    for i, course in enumerate(
                        courses[:6]):  # Show top 6 courses
                            with cols[i % 2]:
                                st.markdown(f"""
                                <div style='background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                                    <h4>{course[0]}</h4>
                                    <a href='{course[1]}' target='_blank'>View Course</a>
                                </div>
                                """, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                        # Learning Resources
                    st.markdown("""
                        <div class="feature-card">
                            <h2>📺 Helpful Videos</h2>
                        """, unsafe_allow_html=True)

                    tab1, tab2 = st.tabs(["Resume Tips", "Interview Tips"])

                    with tab1:
                            # Resume Videos
                            for category, videos in RESUME_VIDEOS.items():
                                st.subheader(category)
                                cols = st.columns(2)
                                for i, video in enumerate(videos):
                                    with cols[i % 2]:
                                        st.video(video[1])

                    with tab2:
                            # Interview Videos
                            for category, videos in INTERVIEW_VIDEOS.items():
                                st.subheader(category)
                                cols = st.columns(2)
                                for i, video in enumerate(videos):
                                    with cols[i % 2]:
                                        st.video(video[1])

                    st.markdown("</div>", unsafe_allow_html=True)

        with analyzer_tabs[1]:
            st.markdown("""
            <div style='background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h3>AI-Powered Resume Analysis</h3>
                <p>Choose between our proprietary analysis algorithms for comprehensive resume evaluation.</p>
            </div>
            """, unsafe_allow_html=True)

            # Analysis Type Selection - Smart vs Deep
            st.markdown("### Choose Analysis Type")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="template-card" style="background: rgba(45, 45, 45, 0.9); border-radius: 20px; padding: 2rem; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="font-size: 3rem; color: #4CAF50; margin-bottom: 1.5rem; text-align: center;">⚡</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: white; margin-bottom: 1rem; text-align: center;">Smart Analysis</div>
                    <div style="color: #aaa; margin-bottom: 1.5rem; line-height: 1.6;">
                        Fast, efficient analysis using our proprietary Lightweight Semantic Evaluation (LSE) Algorithm
                    </div>
                    <ul style="list-style: none; padding: 0; margin: 1.5rem 0;">
                        <li style="display: flex; align-items: center; margin-bottom: 1rem; color: #ddd; font-size: 0.95rem;">
                            <span style="color: #4CAF50; margin-right: 0.8rem; font-size: 1.1rem;">✓</span>
                            Processing Time: 1-2 seconds
                        </li>
                        <li style="display: flex; align-items: center; margin-bottom: 1rem; color: #ddd; font-size: 0.95rem;">
                            <span style="color: #4CAF50; margin-right: 0.8rem; font-size: 1.1rem;">✓</span>
                            Accuracy: 87%
                        </li>
                        <li style="display: flex; align-items: center; margin-bottom: 1rem; color: #ddd; font-size: 0.95rem;">
                            <span style="color: #4CAF50; margin-right: 0.8rem; font-size: 1.1rem;">✓</span>
                            Best for: Quick assessments
                        </li>
                        <li style="display: flex; align-items: center; margin-bottom: 1rem; color: #ddd; font-size: 0.95rem;">
                            <span style="color: #4CAF50; margin-right: 0.8rem; font-size: 1.1rem;">✓</span>
                            Technology: TF-IDF + NLP Engine
                        </li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("⚡ Use Smart Analysis", key="smart_analysis_btn", use_container_width=True, type="primary"):
                    st.session_state.selected_analysis_type = 'smart'
                    st.success("✓ Smart Analysis selected")
            
            with col2:
                st.markdown("""
                <div class="template-card" style="background: rgba(45, 45, 45, 0.9); border-radius: 20px; padding: 2rem; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="font-size: 3rem; color: #4CAF50; margin-bottom: 1.5rem; text-align: center;">🧠</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: white; margin-bottom: 1rem; text-align: center;">Deep Analysis</div>
                    <div style="color: #aaa; margin-bottom: 1.5rem; line-height: 1.6;">
                        Comprehensive analysis using our advanced Advanced Contextual Understanding (ACU) Algorithm
                    </div>
                    <ul style="list-style: none; padding: 0; margin: 1.5rem 0;">
                        <li style="display: flex; align-items: center; margin-bottom: 1rem; color: #ddd; font-size: 0.95rem;">
                            <span style="color: #4CAF50; margin-right: 0.8rem; font-size: 1.1rem;">✓</span>
                            Processing Time: 5-15 seconds
                        </li>
                        <li style="display: flex; align-items: center; margin-bottom: 1rem; color: #ddd; font-size: 0.95rem;">
                            <span style="color: #4CAF50; margin-right: 0.8rem; font-size: 1.1rem;">✓</span>
                            Accuracy: 94%
                        </li>
                        <li style="display: flex; align-items: center; margin-bottom: 1rem; color: #ddd; font-size: 0.95rem;">
                            <span style="color: #4CAF50; margin-right: 0.8rem; font-size: 1.1rem;">✓</span>
                            Best for: Detailed insights
                        </li>
                        <li style="display: flex; align-items: center; margin-bottom: 1rem; color: #ddd; font-size: 0.95rem;">
                            <span style="color: #4CAF50; margin-right: 0.8rem; font-size: 1.1rem;">✓</span>
                            Technology: Transformer + Attention
                        </li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🧠 Use Deep Analysis", key="deep_analysis_btn", use_container_width=True, type="primary"):
                    st.session_state.selected_analysis_type = 'deep'
                    st.success("✓ Deep Analysis selected")
            
            # Initialize analysis type if not set
            if 'selected_analysis_type' not in st.session_state:
                st.info("👆 Please select an analysis type above to continue")
                return
            
            # Show selected analysis type
            analysis_type = st.session_state.selected_analysis_type
            analysis_name = "🚀 Smart Analysis" if analysis_type == 'smart' else "🔬 Deep Analysis"
            algorithm_name = "Lightweight Semantic Evaluation (LSE)" if analysis_type == 'smart' else "Advanced Contextual Understanding (ACU)"
            st.success(f"✓ Using: **{analysis_name}** - {algorithm_name} Algorithm")
            
            # Show algorithm information
            with st.expander("ℹ️ Algorithm Information", expanded=False):
                if analysis_type == 'smart':
                    st.markdown("""
                    **Lightweight Semantic Evaluation (LSE) Algorithm**
                    
                    Our proprietary LSE Algorithm uses:
                    - TF-IDF Vectorization for keyword extraction
                    - Advanced Pattern Recognition v1.5
                    - Rule-based Heuristic Scoring
                    - Multi-factor Evaluation System
                    
                    **Processing Pipeline:**
                    1. Text Preprocessing & Tokenization
                    2. Feature Extraction using TF-IDF
                    3. Pattern Matching for Structure Analysis
                    4. Multi-factor Scoring (ATS 30%, Keywords 35%, Structure 20%, Completeness 15%)
                    5. Rule-based Recommendations
                    
                    **Performance:**
                    - Speed: 1-2 seconds
                    - Accuracy: 87%
                    - Memory: < 100MB
                    - Throughput: 1800+ resumes/hour
                    """)
                else:
                    st.markdown("""
                    **Advanced Contextual Understanding (ACU) Algorithm**
                    
                    Our advanced ACU Algorithm uses:
                    - Transformer-based Semantic Embeddings (768-dimensional)
                    - Multi-head Attention Mechanisms
                    - Four-layer Analysis System
                    - Advanced Reasoning Engine
                    
                    **Processing Layers:**
                    1. **Layer 1**: Structural Analysis & Document Mapping
                    2. **Layer 2**: Content Quality & Writing Style Assessment
                    3. **Layer 3**: Role-Fit & Skill Alignment Analysis
                    4. **Layer 4**: Career Trajectory & Growth Evaluation
                    5. Attention Mechanism for Context Understanding
                    6. Comprehensive Skill Gap Analysis
                    7. Personalized Learning Roadmap Generation
                    
                    **Performance:**
                    - Speed: 5-15 seconds
                    - Accuracy: 94%
                    - Memory: < 500MB
                    - Throughput: 300+ resumes/hour
                    """)
            
            # Set ai_model variable for compatibility with rest of code
            ai_model = analysis_name
             
            # Add job description input option
            use_custom_job_desc = st.checkbox("Use custom job description", value=False, 
                                             help="Enable this to provide a specific job description for more targeted analysis")
            
            custom_job_description = ""
            if use_custom_job_desc:
                custom_job_description = st.text_area(
                    "Paste the job description here",
                    height=200,
                    placeholder="Paste the full job description from the company here for more targeted analysis...",
                    help="Providing the actual job description will help the AI analyze your resume specifically for this position"
                )
                
                st.markdown("""
                <div style='background-color: #2e7d32; padding: 15px; border-radius: 10px; margin: 10px 0;'>
                    <p><i class="fas fa-lightbulb"></i> <strong>Pro Tip:</strong> Including the actual job description significantly improves the accuracy of the analysis and provides more relevant recommendations tailored to the specific position.</p>
                </div>
                """, unsafe_allow_html=True)
             
                        # Add AI Analyzer Stats in an expander
            with st.expander("📊 AI Analyzer Statistics", expanded=False):
                try:
                    # Add a reset button for admin users
                    if st.session_state.get('is_admin', False):
                        if st.button(
    "🔄 Reset AI Analysis Statistics",
    type="secondary",
     key="reset_ai_stats_button_2"):
                            from config.database import reset_ai_analysis_stats
                            result = reset_ai_analysis_stats()
                            if result["success"]:
                                st.success(result["message"])
                            else:
                                st.error(result["message"])
                            # Refresh the page to show updated stats
                            st.rerun()

                    # Get detailed AI analysis statistics
                    from config.database import get_detailed_ai_analysis_stats
                    ai_stats = get_detailed_ai_analysis_stats()

                    if ai_stats["total_analyses"] > 0:
                        # Create a more visually appealing layout
                        st.markdown("""
                        <style>
                        .stats-card {
                            background: linear-gradient(135deg, #1e3c72, #2a5298);
                            border-radius: 10px;
                            padding: 15px;
                            margin-bottom: 15px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            text-align: center;
                        }
                        .stats-value {
                            font-size: 28px;
                            font-weight: bold;
                            color: white;
                            margin: 10px 0;
                        }
                        .stats-label {
                            font-size: 14px;
                            color: rgba(255, 255, 255, 0.8);
                            text-transform: uppercase;
                            letter-spacing: 1px;
                        }
                        .score-card {
                            background: linear-gradient(135deg, #11998e, #38ef7d);
                            border-radius: 10px;
                            padding: 15px;
                            margin-bottom: 15px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            text-align: center;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"""
                            <div class="stats-card">
                                <div class="stats-label">Total AI Analyses</div>
                                <div class="stats-value">{ai_stats["total_analyses"]}</div>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            # Determine color based on score
                            score_color = "#38ef7d" if ai_stats["average_score"] >= 80 else "#FFEB3B" if ai_stats[
                                "average_score"] >= 60 else "#FF5252"
                            st.markdown(f"""
                            <div class="stats-card" style="background: linear-gradient(135deg, #2c3e50, {score_color});">
                                <div class="stats-label">Average Resume Score</div>
                                <div class="stats-value">{ai_stats["average_score"]}/100</div>
                            </div>
                            """, unsafe_allow_html=True)

                        with col3:
                            # Create a gauge chart for average score
                            import plotly.graph_objects as go
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=ai_stats["average_score"],
                                domain={'x': [0, 1], 'y': [0, 1]},
                                title={
    'text': "Score", 'font': {
        'size': 14, 'color': 'white'}},
                                gauge={
                                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                                    'bar': {'color': "#38ef7d" if ai_stats["average_score"] >= 80 else "#FFEB3B" if ai_stats["average_score"] >= 60 else "#FF5252"},
                                    'bgcolor': "rgba(0,0,0,0)",
                                    'borderwidth': 2,
                                    'bordercolor': "white",
                                    'steps': [
                                        {'range': [
                                            0, 40], 'color': 'rgba(255, 82, 82, 0.3)'},
                                        {'range': [
                                            40, 70], 'color': 'rgba(255, 235, 59, 0.3)'},
                                        {'range': [
                                            70, 100], 'color': 'rgba(56, 239, 125, 0.3)'}
                                    ],
                                }
                            ))

                            fig.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font={'color': "white"},
                                height=150,
                                margin=dict(l=10, r=10, t=30, b=10)
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # Display model usage with enhanced visualization
                        if ai_stats["model_usage"]:
                            st.markdown("### 🤖 Model Usage")
                            model_data = pd.DataFrame(ai_stats["model_usage"])

                            # Create a more colorful pie chart
                            import plotly.express as px
                            fig = px.pie(
                                model_data,
                                values="count",
                                names="model",
                                color_discrete_sequence=px.colors.qualitative.Bold,
                                hole=0.4
                            )

                            fig.update_traces(
                                textposition='inside',
                                textinfo='percent+label',
                                marker=dict(
    line=dict(
        color='#000000',
         width=1.5))
                            )

                            fig.update_layout(
                                margin=dict(l=20, r=20, t=30, b=20),
                                height=300,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color="#ffffff", size=14),
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=-0.1,
                                    xanchor="center",
                                    x=0.5
                                ),
                                title={
                                    'text': 'AI Model Distribution',
                                    'y': 0.95,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font': {'size': 18, 'color': 'white'}
                                }
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # Display top job roles with enhanced visualization
                        if ai_stats["top_job_roles"]:
                            st.markdown("### 🎯 Top Job Roles")
                            roles_data = pd.DataFrame(
                                ai_stats["top_job_roles"])

                            # Create a more colorful bar chart
                            fig = px.bar(
                                roles_data,
                                x="role",
                                y="count",
                                color="count",
                                color_continuous_scale=px.colors.sequential.Viridis,
                                labels={
    "role": "Job Role", "count": "Number of Analyses"}
                            )

                            fig.update_traces(
                                marker_line_width=1.5,
                                marker_line_color="white",
                                opacity=0.9
                            )

                            fig.update_layout(
                                margin=dict(l=20, r=20, t=50, b=30),
                                height=350,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color="#ffffff", size=14),
                                title={
                                    'text': 'Most Analyzed Job Roles',
                                    'y': 0.95,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font': {'size': 18, 'color': 'white'}
                                },
                                xaxis=dict(
                                    title="",
                                    tickangle=-45,
                                    tickfont=dict(size=12)
                                ),
                                yaxis=dict(
                                    title="Number of Analyses",
                                    gridcolor="rgba(255, 255, 255, 0.1)"
                                ),
                                coloraxis_showscale=False
                            )

                            st.plotly_chart(fig, use_container_width=True)

                            # Add a timeline chart for analysis over time (mock
                            # data for now)
                            st.markdown("### 📈 Analysis Trend")
                            st.info(
                                "This is a conceptual visualization. To implement actual time-based analysis, additional data collection would be needed.")

                            # Create mock data for timeline
                            import numpy as np

                            today = datetime.now()
                            dates = [
    (today -
    timedelta(
        days=i)).strftime('%Y-%m-%d') for i in range(7)]
                            dates.reverse()

                            # Generate some random data that sums to
                            # total_analyses
                            total = ai_stats["total_analyses"]
                            if total > 7:
                                values = np.random.dirichlet(
                                    np.ones(7)) * total
                                values = [round(v) for v in values]
                                # Adjust to make sure sum equals total
                                diff = total - sum(values)
                                values[-1] += diff
                            else:
                                values = [0] * 7
                                for i in range(total):
                                    values[-(i % 7) - 1] += 1

                            trend_data = pd.DataFrame({
                                'Date': dates,
                                'Analyses': values
                            })

                            fig = px.line(
                                trend_data,
                                x='Date',
                                y='Analyses',
                                markers=True,
                                line_shape='spline',
                                color_discrete_sequence=["#38ef7d"]
                            )

                            fig.update_traces(
                                line=dict(width=3),
                                marker=dict(
    size=8, line=dict(
        width=2, color='white'))
                            )

                            fig.update_layout(
                                margin=dict(l=20, r=20, t=50, b=30),
                                height=300,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color="#ffffff", size=14),
                                title={
                                    'text': 'Analysis Activity (Last 7 Days)',
                                    'y': 0.95,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font': {'size': 18, 'color': 'white'}
                                },
                                xaxis=dict(
                                    title="",
                                    gridcolor="rgba(255, 255, 255, 0.1)"
                                ),
                                yaxis=dict(
                                    title="Number of Analyses",
                                    gridcolor="rgba(255, 255, 255, 0.1)"
                                )
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # Display score distribution if available
                        if ai_stats["score_distribution"]:
                            st.markdown("""
                            <h3 style='text-align: center; margin-bottom: 20px; background: linear-gradient(90deg, #4b6cb7, #182848); padding: 15px; border-radius: 10px; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>
                                📊 Score Distribution Analysis
                            </h3>
                            """, unsafe_allow_html=True)

                            score_data = pd.DataFrame(
                                ai_stats["score_distribution"])

                            # Create a more visually appealing bar chart for
                            # score distribution
                            fig = px.bar(
                                score_data,
                                x="range",
                                y="count",
                                color="range",
                                color_discrete_map={
                                    "0-20": "#FF5252",
                                    "21-40": "#FF7043",
                                    "41-60": "#FFEB3B",
                                    "61-80": "#8BC34A",
                                    "81-100": "#38ef7d"
                                },
                                labels={
    "range": "Score Range",
     "count": "Number of Resumes"},
                                text="count"  # Display count values on bars
                            )

                            fig.update_traces(
                                marker_line_width=2,
                                marker_line_color="white",
                                opacity=0.9,
                                textposition='outside',
                                textfont=dict(
    color="white", size=14, family="Arial, sans-serif"),
                                hovertemplate="<b>Score Range:</b> %{x}<br><b>Number of Resumes:</b> %{y}<extra></extra>"
                            )

                            # Add a gradient background to the chart
                            fig.update_layout(
                                margin=dict(l=20, r=20, t=50, b=30),
                                height=400,  # Increase height for better visibility
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(
    color="#ffffff", size=14, family="Arial, sans-serif"),
                                # title={
                                #     # 'text': 'Resume Score Distribution',
                                #     'y': 0.95,
                                #     'x': 0.5,
                                #     'xanchor': 'center',
                                #     'yanchor': 'top',
                                #     'font': {'size': 22, 'color': 'white', 'family': 'Arial, sans-serif', 'weight': 'bold'}
                                # },
                                xaxis=dict(
                                    title=dict(
    text="Score Range", font=dict(
        size=16, color="white")),
                                    categoryorder="array",
                                    categoryarray=[
    "0-20", "21-40", "41-60", "61-80", "81-100"],
                                    tickfont=dict(size=14, color="white"),
                                    gridcolor="rgba(255, 255, 255, 0.1)"
                                ),
                                yaxis=dict(
                                    title=dict(
    text="Number of Resumes", font=dict(
        size=16, color="white")),
                                    tickfont=dict(size=14, color="white"),
                                    gridcolor="rgba(255, 255, 255, 0.1)",
                                    zeroline=False
                                ),
                                showlegend=False,
                                bargap=0.2,  # Adjust gap between bars
                                shapes=[
                                    # Add gradient background
                                    dict(
                                        type="rect",
                                        xref="paper",
                                        yref="paper",
                                        x0=0,
                                        y0=0,
                                        x1=1,
                                        y1=1,
                                        fillcolor="rgba(26, 26, 44, 0.5)",
                                        layer="below",
                                        line_width=0,
                                    )
                                ]
                            )

                            # Add annotations for insights
                            if len(score_data) > 0:
                                max_count_idx = score_data["count"].idxmax()
                                max_range = score_data.iloc[max_count_idx]["range"]
                                max_count = score_data.iloc[max_count_idx]["count"]

                                fig.add_annotation(
                                    x=0.5,
                                    y=1.12,
                                    xref="paper",
                                    yref="paper",
                                    text=f"Most resumes fall in the {max_range} score range",
                                    showarrow=False,
                                    font=dict(size=14, color="#FFEB3B"),
                                    bgcolor="rgba(0,0,0,0.5)",
                                    bordercolor="#FFEB3B",
                                    borderwidth=1,
                                    borderpad=4,
                                    opacity=0.8
                                )

                            # Display the chart in a styled container
                            st.markdown("""
                            <div style='background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 20px; border-radius: 15px; margin: 10px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2);'>
                            """, unsafe_allow_html=True)

                            st.plotly_chart(fig, use_container_width=True)

                            # Add descriptive text below the chart
                            st.markdown("""
                            <p style='color: white; text-align: center; font-style: italic; margin-top: 10px;'>
                                This chart shows the distribution of resume scores across different ranges, helping identify common performance levels.
                            </p>
                            </div>
                            """, unsafe_allow_html=True)

                        # Display recent analyses if available
                        if ai_stats["recent_analyses"]:
                            st.markdown("""
                            <h3 style='text-align: center; margin-bottom: 20px; background: linear-gradient(90deg, #4b6cb7, #182848); padding: 15px; border-radius: 10px; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>
                                🕒 Recent Resume Analyses
                            </h3>
                            """, unsafe_allow_html=True)

                            # Create a more modern styled table for recent
                            # analyses
                            st.markdown("""
                            <style>
                            .modern-analyses-table {
                                width: 100%;
                                border-collapse: separate;
                                border-spacing: 0 8px;
                                margin-bottom: 20px;
                                font-family: 'Arial', sans-serif;
                            }
                            .modern-analyses-table th {
                                background: linear-gradient(135deg, #1e3c72, #2a5298);
                                color: white;
                                padding: 15px;
                                text-align: left;
                                font-weight: bold;
                                font-size: 14px;
                                text-transform: uppercase;
                                letter-spacing: 1px;
                                border-radius: 8px;
                            }
                            .modern-analyses-table td {
                                padding: 15px;
                                background-color: rgba(30, 30, 30, 0.7);
                                border-top: 1px solid rgba(255, 255, 255, 0.05);
                                border-bottom: 1px solid rgba(0, 0, 0, 0.2);
                                color: white;
                            }
                            .modern-analyses-table tr td:first-child {
                                border-top-left-radius: 8px;
                                border-bottom-left-radius: 8px;
                            }
                            .modern-analyses-table tr td:last-child {
                                border-top-right-radius: 8px;
                                border-bottom-right-radius: 8px;
                            }
                            .modern-analyses-table tr:hover td {
                                background-color: rgba(60, 60, 60, 0.7);
                                transform: translateY(-2px);
                                transition: all 0.2s ease;
                                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                            }
                            .model-badge {
                                display: inline-block;
                                padding: 6px 12px;
                                border-radius: 20px;
                                font-weight: bold;
                                text-align: center;
                                font-size: 12px;
                                letter-spacing: 0.5px;
                                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                            }
                            .model-gemini {
                                background: linear-gradient(135deg, #4e54c8, #8f94fb);
                                color: white;
                            }
                            .model-claude {
                                background: linear-gradient(135deg, #834d9b, #d04ed6);
                                color: white;
                            }
                            .score-pill {
                                display: inline-block;
                                padding: 8px 15px;
                                border-radius: 20px;
                                font-weight: bold;
                                text-align: center;
                                min-width: 70px;
                                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                            }
                            .score-high {
                                background: linear-gradient(135deg, #11998e, #38ef7d);
                                color: white;
                            }
                            .score-medium {
                                background: linear-gradient(135deg, #f2994a, #f2c94c);
                                color: white;
                            }
                            .score-low {
                                background: linear-gradient(135deg, #cb2d3e, #ef473a);
                                color: white;
                            }
                            .date-badge {
                                display: inline-block;
                                padding: 6px 12px;
                                border-radius: 20px;
                                background-color: rgba(255, 255, 255, 0.1);
                                color: #e0e0e0;
                                font-size: 12px;
                            }
                            .role-badge {
                                display: inline-block;
                                padding: 6px 12px;
                                border-radius: 8px;
                                background-color: rgba(33, 150, 243, 0.2);
                                color: #90caf9;
                                font-size: 13px;
                                max-width: 200px;
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
                            }
                            </style>

                            <div style='background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 20px; border-radius: 15px; margin: 10px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.2);'>
                            <table class="modern-analyses-table">
                                <tr>
                                    <th>AI Model</th>
                                    <th>Score</th>
                                    <th>Job Role</th>
                                    <th>Date</th>
                                </tr>
                            """, unsafe_allow_html=True)

                            for analysis in ai_stats["recent_analyses"]:
                                score = analysis["score"]
                                score_class = "score-high" if score >= 80 else "score-medium" if score >= 60 else "score-low"

                                # Determine model class
                                model_name = analysis["model"]
                                model_class = "model-gemini" if "Gemini" in model_name else "model-claude" if "Claude" in model_name else ""

                                # Format the date
                                try:
                                    date_obj = datetime.strptime(
                                        analysis["date"], "%Y-%m-%d %H:%M:%S")
                                    formatted_date = date_obj.strftime(
                                        "%b %d, %Y")
                                except:
                                    formatted_date = analysis["date"]

                                st.markdown(f"""
                                <tr>
                                    <td><div class="model-badge {model_class}">{model_name}</div></td>
                                    <td><div class="score-pill {score_class}">{score}/100</div></td>
                                    <td><div class="role-badge">{analysis["job_role"]}</div></td>
                                    <td><div class="date-badge">{formatted_date}</div></td>
                                </tr>
                                """, unsafe_allow_html=True)

                            st.markdown("""
                            </table>

                            <p style='color: white; text-align: center; font-style: italic; margin-top: 15px;'>
                                These are the most recent resume analyses performed by our AI models.
                            </p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info(
                            "No AI analysis data available yet. Upload and analyze resumes to see statistics here.")
                except Exception as e:
                    st.error(f"Error loading AI analysis statistics: {str(e)}")

            # Job Role Selection for AI Analysis
            categories = list(self.job_roles.keys())
            selected_category = st.selectbox(
    "Job Category", categories, key="ai_category")

            roles = list(self.job_roles[selected_category].keys())
            selected_role = st.selectbox("Specific Role", roles, key="ai_role")

            role_info = self.job_roles[selected_category][selected_role]

            # Display role information
            st.markdown(f"""
            <div style='background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                <h3>{selected_role}</h3>
                <p>{role_info['description']}</p>
                <h4>Required Skills:</h4>
                <p>{', '.join(role_info['required_skills'])}</p>
            </div>
            """, unsafe_allow_html=True)

            # File Upload for AI Analysis
            uploaded_file = st.file_uploader(
    "Upload your resume", type=[
        'pdf', 'docx'], key="ai_file")

            if not uploaded_file:
            # Display empty state with a prominent upload button
                st.markdown(
                self.render_empty_state(
            "fas fa-robot",
                        "Upload your resume to get AI-powered analysis and recommendations"
        ),
        unsafe_allow_html=True
    )
            else:
                # Add a prominent analyze button
                analyze_ai = st.button("🤖 Analyze with AI",
                                type="primary",
                                use_container_width=True,
                                key="analyze_ai_button")

                if analyze_ai:
                    with st.spinner(f"Analyzing your resume with {ai_model}..."):
                        # Save uploaded file to uploads directory
                        
                        uploads_dir = "uploads"
                        if not os.path.exists(uploads_dir):
                            os.makedirs(uploads_dir)
                        
                        # Create unique filename with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_extension = uploaded_file.name.split('.')[-1]
                        saved_filename = f"resume_{timestamp}.{file_extension}"
                        file_path = os.path.join(uploads_dir, saved_filename)
                        
                        # Save the file
                        try:
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Save file info to database
                            from config.database import save_uploaded_file_info
                            from auth.auth_manager import AuthManager
                            file_size = len(uploaded_file.getbuffer())
                            save_uploaded_file_info(
                                filename=saved_filename,
                                original_name=uploaded_file.name,
                                file_path=file_path,
                                file_size=file_size,
                                file_type=uploaded_file.type,
                                upload_source="AI Analysis",
                                user_id=AuthManager.get_current_user_id()
                            )
                        except Exception as e:
                            st.warning(f"Could not save file: {str(e)}")
                        
                        # Get file content
                        text = ""
                        try:
                            if uploaded_file.type == "application/pdf":
                                text = self.analyzer.extract_text_from_pdf(
                                    uploaded_file)
                            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                text = self.analyzer.extract_text_from_docx(
                                    uploaded_file)
                            else:
                                text = uploaded_file.getvalue().decode()
                        except Exception as e:
                            st.error(f"Error reading file: {str(e)}")
                            st.stop()

                        # Analyze with AI
                        try:
                            # Show a loading animation
                            with st.spinner("🧠 AI is analyzing your resume..."):
                                progress_bar = st.progress(0)
                                
                                # Get the selected model
                                selected_model = "Google Gemini"
                                
                                # Update progress
                                progress_bar.progress(10)
                                
                                # Extract text from the resume
                                analyzer = AIResumeAnalyzer()
                                if uploaded_file.type == "application/pdf":
                                    resume_text = analyzer.extract_text_from_pdf(
                                        uploaded_file)
                                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                    resume_text = analyzer.extract_text_from_docx(
                                        uploaded_file)
                                else:
                                    # For text files or other formats
                                    resume_text = uploaded_file.getvalue().decode('utf-8')
                                
                                # Initialize the AI analyzer (moved after text extraction)
                                progress_bar.progress(30)
                                
                                # Get the job role
                                job_role = selected_role if selected_role else "Not specified"
                                
                                # Update progress
                                progress_bar.progress(50)
                                
                                # Get role info if available
                                role_info = None
                                if selected_role and selected_role != "Not specified":
                                    # Try to get role info from JOB_ROLES
                                    from config.job_roles import JOB_ROLES
                                    for category, roles in JOB_ROLES.items():
                                        if selected_role in roles:
                                            role_info = roles[selected_role]
                                            break
                                
                                # Analyze the resume with selected analysis mode
                                # The analyze_resume method handles both Smart and Deep analysis internally
                                analysis_result = analyzer.analyze_resume(
                                    resume_text=resume_text,
                                    job_role=job_role,
                                    role_info=role_info,
                                    model=ai_model  # This will be "🚀 Smart Analysis" or "🔬 Deep Analysis"
                                )
                                
                                # Mark if custom job description was used
                                st.session_state['used_custom_job_desc'] = use_custom_job_desc and bool(custom_job_description)

                                
                                # Update progress
                                progress_bar.progress(80)
                                
                                # Save the analysis to the database
                                if analysis_result and "error" not in analysis_result:
                                    # Extract the resume score
                                    resume_score = analysis_result.get(
                                        "resume_score", 0)
                                    
                                    # Extract basic info from resume text for database
                                    try:
                                        # Simple extraction of email and name from resume text
                                        import re
                                        
                                        # Extract email
                                        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                                        emails = re.findall(email_pattern, resume_text)
                                        email = emails[0] if emails else "unknown@example.com"
                                        
                                        # Extract phone number (improved pattern)
                                        phone_patterns = [
                                            r'(?:Phone|Tel|Mobile|Cell):\s*([+]?[\d\s\-\(\)\.]{10,})',
                                            r'([+]?[\d]{1,3}[-.\s]?[\(]?[\d]{3}[\)]?[-.\s]?[\d]{3}[-.\s]?[\d]{4})',
                                            r'([+]?[\d\s\-\(\)\.]{10,})'
                                        ]
                                        phone = "Not provided"
                                        for pattern in phone_patterns:
                                            phones = re.findall(pattern, resume_text, re.IGNORECASE)
                                            if phones:
                                                phone = phones[0].strip()
                                                break
                                        
                                        # Extract LinkedIn
                                        linkedin_patterns = [
                                            r'(?:LinkedIn|linkedin):\s*(https?://[^\s]+)',
                                            r'(https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9-]+)',
                                            r'linkedin\.com/in/([A-Za-z0-9-]+)'
                                        ]
                                        linkedin = ""
                                        for pattern in linkedin_patterns:
                                            matches = re.findall(pattern, resume_text, re.IGNORECASE)
                                            if matches:
                                                if matches[0].startswith('http'):
                                                    linkedin = matches[0]
                                                else:
                                                    linkedin = f"https://linkedin.com/in/{matches[0]}"
                                                break
                                        
                                        # Extract GitHub
                                        github_patterns = [
                                            r'(?:GitHub|github):\s*(https?://[^\s]+)',
                                            r'(https?://(?:www\.)?github\.com/[A-Za-z0-9-]+)',
                                            r'github\.com/([A-Za-z0-9-]+)'
                                        ]
                                        github = ""
                                        for pattern in github_patterns:
                                            matches = re.findall(pattern, resume_text, re.IGNORECASE)
                                            if matches:
                                                if matches[0].startswith('http'):
                                                    github = matches[0]
                                                else:
                                                    github = f"https://github.com/{matches[0]}"
                                                break
                                        
                                        # Extract Portfolio
                                        portfolio_patterns = [
                                            r'(?:Portfolio|Website|Site):\s*(https?://[^\s]+)',
                                            r'(https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?)'
                                        ]
                                        portfolio = ""
                                        for pattern in portfolio_patterns:
                                            matches = re.findall(pattern, resume_text, re.IGNORECASE)
                                            if matches:
                                                # Skip common sites that are not portfolios
                                                excluded_domains = ['linkedin.com', 'github.com', 'gmail.com', 'yahoo.com', 'outlook.com']
                                                for match in matches:
                                                    if not any(domain in match.lower() for domain in excluded_domains):
                                                        portfolio = match
                                                        break
                                                if portfolio:
                                                    break
                                        
                                        # Extract name (improved logic)
                                        lines = resume_text.split('\n')
                                        name = "Unknown"
                                        for line in lines[:10]:  # Check first 10 lines
                                            line = line.strip()
                                            # Look for lines that could be names
                                            if (len(line) > 2 and len(line) < 50 and 
                                                not '@' in line and 
                                                not 'http' in line.lower() and
                                                not line.lower().startswith(('phone', 'email', 'address', 'linkedin', 'github')) and
                                                line.lower() not in ['resume', 'cv', 'curriculum vitae', 'profile', 'summary', 'objective']):
                                                # Check if it looks like a name (contains letters and possibly spaces)
                                                if re.match(r'^[A-Za-z\s\.]+$', line) and len(line.split()) <= 4:
                                                    name = line
                                                    break
                                        
                                        # Create resume data
                                        resume_data = {
                                            'personal_info': {
                                                'full_name': name,
                                                'email': email,
                                                'phone': phone,
                                                'linkedin': linkedin,
                                                'github': github,
                                                'portfolio': portfolio
                                            },
                                            'summary': resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,
                                            'target_role': job_role,
                                            'target_category': selected_category,
                                            'education': [],
                                            'experience': [],
                                            'projects': [],
                                            'skills': [],
                                            'template': 'AI Analysis'
                                        }
                                        
                                        # Save resume data first with user_id
                                        user_id = AuthManager.get_current_user_id()
                                        resume_id = save_resume_data(resume_data, user_id)
                                        
                                        if resume_id:
                                            # Now save AI analysis with proper resume_id and user_id and PDF path
                                            save_ai_analysis_data(
                                                resume_id,
                                                {
                                                    "model_used": ai_model,
                                                    "resume_score": resume_score,
                                                    "job_role": job_role
                                                },
                                                user_id,
                                                pdf_file_path if 'pdf_file_path' in locals() else None
                                            )
                                            
                                            # Also save basic analysis data with user_id and PDF path
                                            analysis_data = {
                                                'resume_id': resume_id,
                                                'ats_score': resume_score,
                                                'keyword_match_score': resume_score,
                                                'format_score': resume_score,
                                                'section_score': resume_score,
                                                'missing_skills': '',
                                                'recommendations': f'AI Analysis completed with {ai_model}'
                                            }
                                            save_analysis_data(resume_id, analysis_data, user_id, pdf_file_path if 'pdf_file_path' in locals() else None)
                                            
                                            # Also save to new analysis storage system
                                            from config.analysis_manager import AnalysisManager
                                            
                                            # Save resume to new system
                                            resume_result = AnalysisManager.save_resume(
                                                user_id=user_id,
                                                file_name=uploaded_file.name if 'uploaded_file' in locals() else 'AI_Analysis.pdf',
                                                parsed_text=resume_text if 'resume_text' in locals() else '',
                                                file_url=None,
                                                file_type='application/pdf'
                                            )
                                            
                                            if resume_result['success']:
                                                new_resume_id = resume_result['resume_id']
                                                
                                                # Update resume status with detected role
                                                AnalysisManager.update_resume_status(
                                                    new_resume_id, 
                                                    'completed', 
                                                    job_role
                                                )
                                                
                                                # Save analysis to new system with PDF path
                                                new_analysis_data = {
                                                    'detected_skills': analysis_result.get('skills', []),
                                                    'experience_years': analysis_result.get('experience_years', 0),
                                                    'education_detected': analysis_result.get('education', 'Not specified'),
                                                    'projects_detected': analysis_result.get('projects', []),
                                                    'certifications_detected': analysis_result.get('certifications', []),
                                                    'resume_score': resume_score,
                                                    'analysis_summary': f"AI Analysis using {ai_model}: Score {resume_score}%",
                                                    'ai_feedback': analysis_result.get('feedback', '')
                                                }
                                                
                                                AnalysisManager.save_analysis(user_id, new_resume_id, new_analysis_data, pdf_file_path if 'pdf_file_path' in locals() else None)
                                        
                                    except Exception as e:
                                        print(f"Error saving resume data: {e}")
                                        # Fallback: save AI analysis without resume link but with user_id
                                        save_ai_analysis_data(
                                            None,
                                            {
                                                "model_used": ai_model,
                                                "resume_score": resume_score,
                                                "job_role": job_role
                                            },
                                            user_id
                                        )
                                # show snowflake effect
                                st.snow()

                                # Complete the progress
                                progress_bar.progress(100)
                                
                                # Display the analysis result
                                if analysis_result and "error" not in analysis_result:
                                    st.success("✅ Analysis complete!")
                                    
                                    # Extract data from the analysis
                                    full_response = analysis_result.get(
                                        "analysis", "")
                                    resume_score = analysis_result.get(
                                        "resume_score", 0)
                                    ats_score = analysis_result.get(
                                        "ats_score", 0)
                                    model_used = analysis_result.get(
                                        "model_used", selected_model)
                                    
                                    # Store the full response in session state for download
                                    st.session_state['full_analysis'] = full_response
                                    
                                    # Display the analysis in a nice format
                                    st.markdown("## Full Analysis Report")
                                    
                                    # Get current date
                                    current_date = datetime.now().strftime("%B %d, %Y")
                                    
                                    # Create a modern styled header for the report
                                    st.markdown(f"""
                                    <div style="background-color: #262730; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                                        <h2 style="color: #ffffff; margin-bottom: 10px;">AI Resume Analysis Report</h2>
                                        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                                            <div style="flex: 1; min-width: 200px;">
                                                <p style="color: #ffffff;"><strong>Job Role:</strong> {job_role if job_role else "Not specified"}</p>
                                                <p style="color: #ffffff;"><strong>Analysis Date:</strong> {current_date}</p>                                                                                                                                        </div>
                                            <div style="flex: 1; min-width: 200px;">
                                                <p style="color: #ffffff;"><strong>AI Model:</strong> {model_used}</p>
                                                <p style="color: #ffffff;"><strong>Overall Score:</strong> {resume_score}/100 - {"Excellent" if resume_score >= 80 else "Good" if resume_score >= 60 else "Needs Improvement"}</p>
                                                {f'<p style="color: #4CAF50;"><strong>✓ Custom Job Description Used</strong></p>' if st.session_state.get('used_custom_job_desc', False) else ''}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Add gauge charts for scores
                                    import plotly.graph_objects as go
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        # Resume Score Gauge
                                        fig1 = go.Figure(go.Indicator(
                                            mode="gauge+number",
                                            value=resume_score,
                                            domain={'x': [0, 1], 'y': [0, 1]},
                                            title={'text': "Resume Score", 'font': {'size': 16}},
                                            gauge={
                                                'axis': {'range': [0, 100], 'tickwidth': 1},
                                                'bar': {'color': "#4CAF50" if resume_score >= 80 else "#FFA500" if resume_score >= 60 else "#FF4444"},
                                                'bgcolor': "white",
                                                'borderwidth': 2,
                                                'bordercolor': "gray",
                                                'steps': [
                                                    {'range': [0, 40], 'color': 'rgba(255, 68, 68, 0.2)'},
                                                    {'range': [40, 60], 'color': 'rgba(255, 165, 0, 0.2)'},
                                                    {'range': [60, 80], 'color': 'rgba(255, 214, 0, 0.2)'},
                                                    {'range': [80, 100], 'color': 'rgba(76, 175, 80, 0.2)'}
                                                ],
                                                'threshold': {
                                                    'line': {'color': "red", 'width': 4},
                                                    'thickness': 0.75,
                                                    'value': 60
                                                }
                                            }
                                        ))
                                        
                                        fig1.update_layout(
                                            height=250,
                                            margin=dict(l=20, r=20, t=50, b=20),
                                        )
                                        
                                        st.plotly_chart(fig1, use_container_width=True)
                                        
                                        status = "Excellent" if resume_score >= 80 else "Good" if resume_score >= 60 else "Needs Improvement"
                                        st.markdown(f"<div style='text-align: center; font-weight: bold;'>{status}</div>", unsafe_allow_html=True)
                                    
                                    with col2:
                                        # ATS Score Gauge
                                        fig2 = go.Figure(go.Indicator(
                                            mode="gauge+number",
                                            value=ats_score,
                                            domain={'x': [0, 1], 'y': [0, 1]},
                                            title={'text': "ATS Optimization Score", 'font': {'size': 16}},
                                            gauge={
                                                'axis': {'range': [0, 100], 'tickwidth': 1},
                                                'bar': {'color': "#4CAF50" if ats_score >= 80 else "#FFA500" if ats_score >= 60 else "#FF4444"},
                                                'bgcolor': "white",
                                                'borderwidth': 2,
                                                'bordercolor': "gray",
                                                'steps': [
                                                    {'range': [0, 40], 'color': 'rgba(255, 68, 68, 0.2)'},
                                                    {'range': [40, 60], 'color': 'rgba(255, 165, 0, 0.2)'},
                                                    {'range': [60, 80], 'color': 'rgba(255, 214, 0, 0.2)'},
                                                    {'range': [80, 100], 'color': 'rgba(76, 175, 80, 0.2)'}
                                                ],
                                                'threshold': {
                                                    'line': {'color': "red", 'width': 4},
                                                    'thickness': 0.75,
                                                    'value': 60
                                                }
                                            }
                                        ))
                                        
                                        fig2.update_layout(
                                            height=250,
                                            margin=dict(l=20, r=20, t=50, b=20),
                                        )
                                        
                                        st.plotly_chart(fig2, use_container_width=True)
                                        
                                        status = "Excellent" if ats_score >= 80 else "Good" if ats_score >= 60 else "Needs Improvement"
                                        st.markdown(f"<div style='text-align: center; font-weight: bold;'>{status}</div>", unsafe_allow_html=True)

                                    # Add Job Description Match Score if custom job description was used
                                    if st.session_state.get('used_custom_job_desc', False) and custom_job_description:
                                        # Extract job match score from analysis result or calculate it
                                        job_match_score = analysis_result.get("job_match_score", 0)
                                        if not job_match_score and "job_match" in analysis_result:
                                            job_match_score = analysis_result["job_match"].get("score", 0)
                                        
                                        # If we have a job match score, display it
                                        if job_match_score:
                                            st.markdown("""
                                            <h3 style="background: linear-gradient(90deg, #4d7c0f, #84cc16); color: white; padding: 10px; border-radius: 5px; margin-top: 20px;">
                                                <i class="fas fa-handshake"></i> Job Description Match Analysis
                                            </h3>
                                            """, unsafe_allow_html=True)
                                            
                                            col1, col2 = st.columns(2)
                                            
                                            with col1:
                                                # Job Match Score Gauge
                                                fig3 = go.Figure(go.Indicator(
                                                    mode="gauge+number",
                                                    value=job_match_score,
                                                    domain={'x': [0, 1], 'y': [0, 1]},
                                                    title={'text': "Job Match Score", 'font': {'size': 16}},
                                                    gauge={
                                                        'axis': {'range': [0, 100], 'tickwidth': 1},
                                                        'bar': {'color': "#4CAF50" if job_match_score >= 80 else "#FFA500" if job_match_score >= 60 else "#FF4444"},
                                                        'bgcolor': "white",
                                                        'borderwidth': 2,
                                                        'bordercolor': "gray",
                                                        'steps': [
                                                            {'range': [0, 40], 'color': 'rgba(255, 68, 68, 0.2)'},
                                                            {'range': [40, 60], 'color': 'rgba(255, 165, 0, 0.2)'},
                                                            {'range': [60, 80], 'color': 'rgba(255, 214, 0, 0.2)'},
                                                            {'range': [80, 100], 'color': 'rgba(76, 175, 80, 0.2)'}
                                                        ],
                                                        'threshold': {
                                                            'line': {'color': "red", 'width': 4},
                                                            'thickness': 0.75,
                                                            'value': 60
                                                        }
                                                    }
                                                ))
                                                
                                                fig3.update_layout(
                                                    height=250,
                                                    margin=dict(l=20, r=20, t=50, b=20),
                                                )
                                                
                                                st.plotly_chart(fig3, use_container_width=True)
                                                
                                                match_status = "Excellent Match" if job_match_score >= 80 else "Good Match" if job_match_score >= 60 else "Low Match"
                                                st.markdown(f"<div style='text-align: center; font-weight: bold;'>{match_status}</div>", unsafe_allow_html=True)
                                            
                                            with col2:
                                                st.markdown("""
                                                <div style="background-color: #262730; padding: 20px; border-radius: 10px; height: 100%;">
                                                    <h4 style="color: #ffffff; margin-bottom: 15px;">What This Means</h4>
                                                    <p style="color: #ffffff;">This score represents how well your resume matches the specific job description you provided.</p>
                                                    <ul style="color: #ffffff; padding-left: 20px;">
                                                        <li><strong>80-100:</strong> Excellent match - your resume is highly aligned with this job</li>
                                                        <li><strong>60-79:</strong> Good match - your resume matches many requirements</li>
                                                        <li><strong>Below 60:</strong> Consider tailoring your resume more specifically to this job</li>
                                                    </ul>
                                                </div>
                                                """, unsafe_allow_html=True)
                                    

                                    # Format the full response with better styling
                                    formatted_analysis = full_response
                                    
                                    # Replace section headers with styled headers
                                    section_styles = {
                                        "## Overall Assessment": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-chart-line"></i> Overall Assessment
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Professional Profile Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #047857, #10b981); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-user-tie"></i> Professional Profile Analysis
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Skills Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #4f46e5, #818cf8); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-tools"></i> Skills Analysis
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Experience Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #9f1239, #e11d48); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-briefcase"></i> Experience Analysis
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Education Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #854d0e, #eab308); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-graduation-cap"></i> Education Analysis
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Key Strengths": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #166534, #22c55e); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-check-circle"></i> Key Strengths
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Areas for Improvement": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #9f1239, #fb7185); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-exclamation-circle"></i> Areas for Improvement
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## ATS Optimization Assessment": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #0e7490, #06b6d4); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-robot"></i> ATS Optimization Assessment
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Recommended Courses": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #5b21b6, #8b5cf6); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-book"></i> Recommended Courses
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Resume Score": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #0369a1, #0ea5e9); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-star"></i> Resume Score
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Role Alignment Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #7c2d12, #ea580c); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-bullseye"></i> Role Alignment Analysis
                                            </h3>
                                            <div class="section-content">""",
                                            
                                        "## Job Match Analysis": """<div class="report-section">
                                            <h3 style="background: linear-gradient(90deg, #4d7c0f, #84cc16); color: white; padding: 10px; border-radius: 5px;">
                                                <i class="fas fa-handshake"></i> Job Match Analysis
                                            </h3>
                                            <div class="section-content">""",
                                    }
                                    
                                    # Apply the styling to each section
                                    for section, style in section_styles.items():
                                        if section in formatted_analysis:
                                            formatted_analysis = formatted_analysis.replace(
                                                section, style)
                                            # Add closing div tags
                                            next_section = False
                                            for next_sec in section_styles.keys():
                                                if next_sec != section and next_sec in formatted_analysis.split(style)[1]:
                                                    split_text = formatted_analysis.split(style)[1].split(next_sec)
                                                    formatted_analysis = formatted_analysis.split(style)[0] + style + split_text[0] + "</div></div>" + next_sec + "".join(split_text[1:])
                                                    next_section = True
                                                    break
                                            if not next_section:
                                                formatted_analysis = formatted_analysis + "</div></div>"
                                    
                                    # Remove any extra closing div tags that might have been added
                                    formatted_analysis = formatted_analysis.replace("</div></div></div></div>", "</div></div>")
                                    
                                    # Ensure we don't have any orphaned closing tags at the end
                                    if formatted_analysis.endswith("</div>"):
                                        # Count opening and closing div tags
                                        open_tags = formatted_analysis.count("<div")
                                        close_tags = formatted_analysis.count("</div>")
                                        
                                        # If we have more closing than opening tags, remove the extras
                                        if close_tags > open_tags:
                                            excess = close_tags - open_tags
                                            formatted_analysis = formatted_analysis[:-6 * excess]
                                    
                                    # Clean up any visible HTML tags that might appear in the text
                                    formatted_analysis = formatted_analysis.replace("&lt;/div&gt;", "")
                                    formatted_analysis = formatted_analysis.replace("&lt;div&gt;", "")
                                    formatted_analysis = formatted_analysis.replace("<div>", "<div>")  # Ensure proper opening
                                    formatted_analysis = formatted_analysis.replace("</div>", "</div>")  # Ensure proper closing
                                    
                                    # Add CSS for the report
                                    st.markdown("""
                                    <style>
                                        .report-section {
                                            margin-bottom: 25px;
                                            border: 1px solid #4B4B4B;
                                            border-radius: 8px;
                                            overflow: hidden;
                                        }
                                        .section-content {
                                            padding: 15px;
                                            background-color: #262730;
                                            color: #ffffff;
                                        }
                                        .report-section h3 {
                                            margin-top: 0;
                                            font-weight: 600;
                                        }
                                        .report-section ul {
                                            padding-left: 20px;
                                        }
                                        .report-section p {
                                            color: #ffffff;
                                            margin-bottom: 10px;
                                        }
                                        .report-section li {
                                            color: #ffffff;
                                            margin-bottom: 5px;
                                        }
                                    </style>
                                    """, unsafe_allow_html=True)

                                    # Display the formatted analysis
                                    st.markdown(f"""
                                    <div style="background-color: #262730; padding: 20px; border-radius: 10px; border: 1px solid #4B4B4B; color: #ffffff;">
                                        {formatted_analysis}
                                    </div>
                                    """, unsafe_allow_html=True)

                                    # Create a PDF report
                                    pdf_buffer = self.ai_analyzer.generate_pdf_report(
                                        analysis_result={
                                            "score": resume_score,
                                            "ats_score": ats_score,
                                            "model_used": model_used,
                                            "full_response": full_response,
                                            "strengths": analysis_result.get("strengths", []),
                                            "weaknesses": analysis_result.get("weaknesses", []),
                                            "used_custom_job_desc": st.session_state.get('used_custom_job_desc', False),
                                            "custom_job_description": custom_job_description if st.session_state.get('used_custom_job_desc', False) else ""
                                        },
                                        candidate_name=st.session_state.get(
                                            'candidate_name', 'Candidate'),
                                        job_role=selected_role
                                    )

                                    # Save PDF to file system
                                    pdf_file_path = None
                                    if pdf_buffer:
                                        try:
                                            # Create unique filename
                                            pdf_filename = f"ai_analysis_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                            pdf_file_path = os.path.join('analysis_reports', pdf_filename)
                                            
                                            # Save PDF to file
                                            with open(pdf_file_path, 'wb') as f:
                                                f.write(pdf_buffer.getvalue())
                                            
                                            print(f"✅ PDF saved to: {pdf_file_path}")
                                        except Exception as pdf_save_error:
                                            print(f"Error saving PDF file: {pdf_save_error}")
                                            pdf_file_path = None

                                    # PDF download button
                                    if pdf_buffer:
                                        st.download_button(
                                            label="📊 Download PDF Report",
                                            data=pdf_buffer,
                                            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                            mime="application/pdf",
                                            use_container_width=True,
                                            on_click=lambda: st.balloons()
                                        )
                                        
                                        # ============ LEARNING RECOMMENDATIONS SECTION ============
                                        st.markdown("<br>", unsafe_allow_html=True)
                                        
                                        # Extract missing skills from the analysis text
                                        missing_skills = []
                                        analysis_text = analysis_result.get('analysis', '')
                                        
                                        # Extract missing skills from the "Missing Skills" section
                                        if "Missing Skills" in analysis_text:
                                            try:
                                                missing_section = analysis_text.split("Missing Skills")[1]
                                                # Stop at the next section
                                                if "##" in missing_section:
                                                    missing_section = missing_section.split("##")[0]
                                                
                                                # Extract skills from bullet points
                                                for line in missing_section.split("\n"):
                                                    line = line.strip()
                                                    if line and ("-" in line or "*" in line or "•" in line):
                                                        # Remove bullet points and clean up
                                                        skill = line.replace("-", "").replace("*", "").replace("•", "").strip()
                                                        # Take only the skill name (before colon if present)
                                                        if ":" in skill:
                                                            skill = skill.split(":")[0].strip()
                                                        if skill and len(skill) > 2:  # Avoid empty or very short strings
                                                            missing_skills.append(skill)
                                            except Exception as e:
                                                st.warning(f"⚠️ Error extracting skills: {e}")
                                        
                                        # Debug: Show extracted skills
                                        if missing_skills:
                                            st.success(f"✅ Extracted {len(missing_skills)} missing skills")
                                        else:
                                            st.info("ℹ️ No missing skills found in analysis")
                                        
                                        # Store in session state for Learning Dashboard
                                        if missing_skills:
                                            st.session_state["missing_skills"] = missing_skills
                                            
                                            # Save course recommendations to database
                                            try:
                                                from config.course_recommendation_manager import CourseRecommendationManager
                                                
                                                # Save recommendations
                                                current_resume_id = resume_id if resume_id else 0
                                                
                                                course_result = CourseRecommendationManager.save_recommendations_for_user(
                                                    user_id=user_id,
                                                    resume_id=current_resume_id,
                                                    analysis_id=None,  # Set to None to avoid foreign key constraint issues
                                                    missing_skills=missing_skills
                                                )
                                                
                                                # Only show message if there's an issue
                                                if not course_result['success']:
                                                    st.warning(f"⚠️ Course recommendations not saved: {course_result.get('message')}")
                                            except Exception as course_error:
                                                st.error(f"⚠️ Error saving course recommendations: {course_error}")
                                                import traceback
                                                st.code(traceback.format_exc())
                                        
                                        if missing_skills and len(missing_skills) > 0:
                                            # Beautiful card for learning recommendations
                                            st.markdown("""
                                            <div style="
                                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                                padding: 2rem;
                                                border-radius: 16px;
                                                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
                                                margin: 2rem 0;
                                                text-align: center;
                                            ">
                                                <h2 style="color: white; margin: 0 0 1rem 0; font-size: 1.8rem;">
                                                    🎓 Boost Your Skills!
                                                </h2>
                                                <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0 0 1.5rem 0;">
                                                    We found <strong>{}</strong> skill gaps in your resume. 
                                                    Get personalized YouTube courses to level up!
                                                </p>
                                            </div>
                                            """.format(len(missing_skills)), unsafe_allow_html=True)
                                            
                                            # Show preview of missing skills
                                            st.markdown("### 📋 Skills to Improve:")
                                            skill_cols = st.columns(min(len(missing_skills), 5))
                                            for idx, skill in enumerate(missing_skills[:5]):
                                                with skill_cols[idx]:
                                                    st.markdown(f"""
                                                    <div style="
                                                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                                                        padding: 0.8rem;
                                                        border-radius: 12px;
                                                        text-align: center;
                                                        color: white;
                                                        font-weight: 600;
                                                        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
                                                    ">
                                                        {skill}
                                                    </div>
                                                    """, unsafe_allow_html=True)
                                            
                                            if len(missing_skills) > 5:
                                                st.info(f"+ {len(missing_skills) - 5} more skills")
                                            
                                            st.markdown("<br>", unsafe_allow_html=True)
                                            
                                            # Big CTA button to Learning Dashboard
                                            col1, col2, col3 = st.columns([1, 2, 1])
                                            with col2:
                                                if st.button(
                                                    "🚀 View My Personalized Courses",
                                                    key="view_courses_btn",
                                                    type="primary",
                                                    use_container_width=True
                                                ):
                                                    st.session_state.page = 'learning_dashboard'
                                                    st.rerun()
                                        else:
                                            # No skill gaps - show congratulations
                                            st.markdown("""
                                            <div style="
                                                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                                                padding: 2rem;
                                                border-radius: 16px;
                                                box-shadow: 0 10px 30px rgba(17, 153, 142, 0.3);
                                                margin: 2rem 0;
                                                text-align: center;
                                            ">
                                                <h2 style="color: white; margin: 0 0 1rem 0; font-size: 1.8rem;">
                                                    🎉 Excellent Resume!
                                                </h2>
                                                <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0;">
                                                    Your resume looks great! No major skill gaps detected.
                                                    Keep learning to stay ahead!
                                                </p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                        
                                        # ============ END LEARNING RECOMMENDATIONS ============
                                        
                                    else:
                                        st.error("PDF generation failed. Please try again later.")
                                else:
                                    st.error(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}")
                        except Exception as ai_error:
                            st.error(f"Error during AI analysis: {str(ai_error)}")
                            import traceback as tb
                            st.code(tb.format_exc())


    def render_user_history(self):
        """Render user history page"""
        from pages.user_history import render_user_history
        render_user_history()
    
    def render_learning_dashboard(self):
        """Render learning dashboard with course recommendations"""
        from pages.learning_dashboard import render_learning_dashboard
        render_learning_dashboard()

    def render_home(self):
        apply_modern_styles()
        
        # Hero Section
        hero_section(
            "Smart Resume AI",
            "Transform your career with AI-powered resume analysis and building. Get personalized insights and create professional resumes that stand out."
        )
        
        # Features Section
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        
        feature_card(
            "fas fa-robot",
            "AI-Powered Analysis",
            "Get instant feedback on your resume with advanced AI analysis that identifies strengths and areas for improvement."
        )
        
        feature_card(
            "fas fa-magic",
            "Smart Resume Builder",
            "Create professional resumes with our intelligent builder that suggests optimal content and formatting."
        )
        
        feature_card(
            "fas fa-chart-line",
            "Career Insights",
            "Access detailed analytics and personalized recommendations to enhance your career prospects."
        )
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Call-to-Action with Streamlit navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Get Started", key="get_started_btn", 
                        help="Click to start analyzing your resume",
                        type="primary",
                        use_container_width=True):
                cleaned_name = "🔍 RESUME ANALYZER".lower().replace(" ", "_").replace("🔍", "").strip()
                st.session_state.page = cleaned_name
                st.rerun()

    def render_mock_interview(self):
        """Render the AI Mock Interview page"""
        from pages.mock_interview import render_mock_interview
        render_mock_interview()

    def render_job_search(self):
        """Render the job search page"""
        render_job_search()


    def render_feedback_page(self):
        """Render the feedback page"""
        apply_modern_styles()
        
        # Page Header
        page_header(
            "Feedback & Suggestions",
            "Help us improve by sharing your thoughts"
        )
        
        # Initialize feedback manager
        feedback_manager = FeedbackManager()
        
        # Create tabs for form and stats
        form_tab, stats_tab = st.tabs(["Submit Feedback", "Feedback Stats"])
        
        with form_tab:
            feedback_manager.render_feedback_form()
            
        with stats_tab:
            feedback_manager.render_feedback_stats()





    def main(self):
        """Main application entry point"""

        # ── Instant dark overlay — eliminates white flash on ALL page transitions ──
        from auth.login_page import pre_inject_dark_overlay
        pre_inject_dark_overlay()

        # ============ AUTHENTICATION CHECK ============
        # Check if user is authenticated
        if not AuthManager.is_authenticated():
            # Show login or signup page
            if st.session_state.get('show_signup', False):
                render_signup_page()
            else:
                render_login_page()
            return  # Stop here if not authenticated
        # ============================================
        
        self.apply_global_styles()

        # ── Handle interview completion (cloud mode) ──────────────────────
        # On cloud, the interview page navigates window.opener to
        # /?iv_done=ID&iv_data=TRANSCRIPT. If session state is intact
        # (opener tab), render_live() catches it. If session was lost,
        # we restore minimal state here so evaluation still runs.
        _params = st.query_params
        if "iv_done" in _params and "iv_data" in _params:
            import json as _json
            try:
                _iv_id = int(_params["iv_done"])
                _transcript = _json.loads(_params["iv_data"])
                if _transcript:
                    # Restore session state if missing (fresh session after redirect)
                    if st.session_state.get("iv_id") != _iv_id:
                        from utils.interview_manager import InterviewManager
                        _iv_data = InterviewManager.get_interview_by_id(_iv_id)
                        if _iv_data:
                            st.session_state.iv_id     = _iv_id
                            st.session_state.iv_q      = _iv_data.get("questions", [])
                            st.session_state.iv_exp    = _iv_data.get("expected_answers", [])
                            st.session_state.iv_skills = _iv_data.get("skills_to_test", [])
                            st.session_state.iv_cfg    = {
                                "job_role":       _iv_data.get("job_role", "Unknown"),
                                "difficulty":     _iv_data.get("difficulty", "medium"),
                                "interview_type": _iv_data.get("interview_type", "mixed"),
                                "question_count": _iv_data.get("question_count", 5),
                            }
                    st.session_state.iv_transcript = _transcript
                    st.session_state.iv_phase      = "evaluating"
                    st.session_state.page          = "mock_interview"
                    st.query_params.clear()
                    st.rerun()
            except Exception as _e:
                print(f"iv_done intercept error: {_e}")
                st.query_params.clear()
        # ─────────────────────────────────────────────────────────────────
        
        # Admin login/logout in sidebar
        with st.sidebar:
            # Load Lottie animation with fallback
            lottie_animation = self.load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_xyadoh9h.json")
            if lottie_animation:
                st_lottie(lottie_animation, height=200, key="sidebar_animation")
            else:
                # Fallback when animation can't be loaded
                st.markdown("""
                    <div style="text-align: center; padding: 20px;">
                        <h1 style="color: #4CAF50; font-size: 3em;">🚀</h1>
                        <p style="color: #E0E0E0;">Smart Resume AI</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Show logged in user info
            st.markdown(f"""
            <div style='background: rgba(76,175,80,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                <p style='margin: 0; color: #4CAF50; font-weight: 600;'>👤 {AuthManager.get_current_user_name()}</p>
                <p style='margin: 0; color: #aaa; font-size: 0.85rem;'>{AuthManager.get_current_user_email()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.title("Smart Resume AI")
            st.markdown("---")
            
            # Navigation buttons
            for page_name in self.pages.keys():
                if st.button(page_name, use_container_width=True):
                    cleaned_name = page_name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "").replace("📊", "").replace("🎯", "").replace("💬", "").replace("ℹ️", "").replace("🎤", "").replace("📚", "").replace("🎓", "").replace("🌐", "").strip()
                    st.session_state.page = cleaned_name
                    st.rerun()

            # Add Profile and Logout buttons
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👤 Profile", use_container_width=True):
                    st.session_state.page = 'profile'
                    st.rerun()
            with col2:
                if st.button("🚪 Logout", use_container_width=True, type="primary"):
                    AuthManager.logout_user()
                    st.success("✅ Logged out!")
                    st.rerun()
            
            # Add some space before admin login
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("---")

            # Admin Login/Logout section at bottom
            if st.session_state.get('is_admin', False):
                st.success(f"👑 Admin: {st.session_state.get('current_admin_email')}")
                
                # Admin Dashboard button (only visible when admin is logged in)
                if st.button("📊 ADMIN DASHBOARD", use_container_width=True, type="primary"):
                    st.session_state.page = 'admin_dashboard'
                    st.rerun()
                
                # Admin Logout button
                if st.button("🚪 Admin Logout", use_container_width=True):
                    try:
                        log_admin_action(st.session_state.get('current_admin_email'), "logout")
                        st.session_state.is_admin = False
                        st.session_state.current_admin_email = None
                        st.success("✅ Admin logged out successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error during logout: {str(e)}")
            else:
                with st.expander("🔐 Admin Login"):
                    admin_email_input = st.text_input("Email", key="admin_email_input")
                    admin_password = st.text_input("Password", type="password", key="admin_password_input")
                    if st.button("Login", key="login_button"):
                            try:
                                if verify_admin(admin_email_input, admin_password):
                                    st.session_state.is_admin = True
                                    st.session_state.current_admin_email = admin_email_input
                                    log_admin_action(admin_email_input, "login")
                                    st.success("✅ Admin logged in successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid admin credentials")
                            except Exception as e:
                                st.error(f"Error during login: {str(e)}")
        


        # Force home page on first load
        if 'initial_load' not in st.session_state:
            st.session_state.initial_load = True
            st.session_state.page = 'home'
            st.rerun()
        
        # Get current page and render it
        current_page = st.session_state.get('page', 'home')
        
        # Handle profile page
        if current_page == 'profile':
            from pages.profile_management import render_profile_page
            render_profile_page()
            self.add_footer()
            return
        
        # Handle admin dashboard page (only if admin is logged in)
        if current_page == 'admin_dashboard':
            if st.session_state.get('is_admin', False):
                self.render_dashboard()
                self.add_footer()
                return
            else:
                st.error("⛔ Access Denied: Admin login required")
                st.info("Please login as admin using the 'Admin Login' section in the sidebar")
                self.add_footer()
                return
        
        # Create a mapping of cleaned page names to original names
        page_mapping = {name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "").replace("📊", "").replace("🎯", "").replace("💬", "").replace("ℹ️", "").replace("🎤", "").replace("📚", "").replace("🎓", "").replace("🌐", "").strip(): name 
                       for name in self.pages.keys()}
        
        # Render the appropriate page
        if current_page in page_mapping:
            self.pages[page_mapping[current_page]]()
        else:
            # Default to home page if invalid page
            self.render_home()
    
        # Add footer to every page
        self.add_footer()

if __name__ == "__main__":
    app = ResumeApp()
    app.main()