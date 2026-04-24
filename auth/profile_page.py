"""
User Profile Page - LinkedIn Style
"""
import streamlit as st
from auth.auth_manager import AuthManager
from config.database import get_resume_stats, get_database_connection
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render_profile_page():
    """Render stunning LinkedIn-style user profile page"""
    if not AuthManager.is_authenticated():
        st.warning("⚠️ Please log in to view your profile")
        return
    
    user_id = AuthManager.get_current_user_id()
    user_email = AuthManager.get_current_user_email()
    user_name = AuthManager.get_current_user_name()
    
    # Custom CSS for profile page
    st.markdown("""
    <style>
    .profile-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(0,255,136,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        position: relative;
        overflow: hidden;
    }
    
    .profile-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(0,255,136,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .profile-avatar {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00ff88, #00b4ff);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4rem;
        margin: 0 auto;
        box-shadow: 0 0 40px rgba(0,255,136,0.4);
        border: 4px solid rgba(0,255,136,0.3);
        animation: pulse-glow 3s ease-in-out infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 40px rgba(0,255,136,0.4); }
        50% { box-shadow: 0 0 60px rgba(0,255,136,0.6); }
    }
    
    .profile-name {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00ff88, #00b4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 1rem 0 0.5rem 0;
        text-align: center;
    }
    
    .profile-email {
        color: #a0a0c0;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .profile-badge {
        display: inline-block;
        background: rgba(0,255,136,0.1);
        color: #00ff88;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(0,255,136,0.3);
        margin: 0.3rem;
    }
    
    .stat-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0,255,136,0.3);
        box-shadow: 0 8px 32px rgba(0,255,136,0.2);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00ff88, #00b4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        color: #a0a0c0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .achievement-card {
        background: linear-gradient(135deg, rgba(0,255,136,0.05), rgba(0,180,255,0.05));
        border: 1px solid rgba(0,255,136,0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .achievement-card:hover {
        transform: translateX(10px);
        border-color: rgba(0,255,136,0.4);
        box-shadow: 0 4px 20px rgba(0,255,136,0.2);
    }
    
    .achievement-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .timeline-item {
        position: relative;
        padding-left: 2.5rem;
        padding-bottom: 2rem;
        border-left: 2px solid rgba(0,255,136,0.2);
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -6px;
        top: 0;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #00ff88;
        box-shadow: 0 0 15px rgba(0,255,136,0.6);
    }
    
    .skill-badge {
        display: inline-block;
        background: rgba(0,255,136,0.1);
        color: #00ff88;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(0,255,136,0.3);
        margin: 0.3rem;
        transition: all 0.2s ease;
    }
    
    .skill-badge:hover {
        background: rgba(0,255,136,0.2);
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0,255,136,0.3);
    }
    
    .section-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00ff88;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get user profile data
    profile_result = AuthManager.get_user_profile(user_id)
    
    if profile_result['success']:
        user_data = profile_result['user']
        
        # Profile Header with Cover
        st.markdown("""
        <div class="profile-header">
            <div style="position: relative; z-index: 1;">
                <div class="profile-avatar">👤</div>
                <h1 class="profile-name">{}</h1>
                <p class="profile-email">📧 {}</p>
                <div style="text-align: center; margin-top: 1rem;">
                    <span class="profile-badge">🎯 Active Member</span>
                    <span class="profile-badge">⭐ Verified</span>
                    <span class="profile-badge">🚀 Pro User</span>
                </div>
            </div>
        </div>
        """.format(user_data.get('full_name', 'User'), user_data['email']), unsafe_allow_html=True)
        
        # Quick Stats Dashboard
        st.markdown('<div class="section-title">📊 Your Performance Dashboard</div>', unsafe_allow_html=True)
        
        try:
            stats = get_resume_stats(user_id)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="stat-card">
                    <div style="font-size: 2rem;">📄</div>
                    <div class="stat-value">{}</div>
                    <div class="stat-label">Resumes</div>
                </div>
                """.format(stats.get('total_resumes', 0)), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="stat-card">
                    <div style="font-size: 2rem;">🔍</div>
                    <div class="stat-value">{}</div>
                    <div class="stat-label">Analyses</div>
                </div>
                """.format(stats.get('total_analyses', 0)), unsafe_allow_html=True)
            
            with col3:
                avg_score = stats.get('avg_score', 0)
                st.markdown("""
                <div class="stat-card">
                    <div style="font-size: 2rem;">⭐</div>
                    <div class="stat-value">{}</div>
                    <div class="stat-label">Avg Score</div>
                </div>
                """.format(f"{avg_score}%" if avg_score else "N/A"), unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="stat-card">
                    <div style="font-size: 2rem;">🌐</div>
                    <div class="stat-value">{}</div>
                    <div class="stat-label">Portfolios</div>
                </div>
                """.format(stats.get('total_portfolios', 0)), unsafe_allow_html=True)
            
            # Activity Chart
            st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📈 Activity Timeline</div>', unsafe_allow_html=True)
                
                # Get activity data
                activity_data = get_user_activity(user_id)
                if activity_data:
                    fig = create_activity_chart(activity_data)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Start using the platform to see your activity timeline!")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🏆 Achievements</div>', unsafe_allow_html=True)
                
                achievements = get_user_achievements(stats)
                for achievement in achievements:
                    st.markdown(f"""
                    <div class="achievement-card">
                        <div class="achievement-icon">{achievement['icon']}</div>
                        <div style="font-weight: 600; color: #00ff88; margin-bottom: 0.3rem;">{achievement['title']}</div>
                        <div style="color: #a0a0c0; font-size: 0.85rem;">{achievement['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        except Exception as e:
            st.info("No activity data available yet. Start using the platform to see your statistics!")
        
        # Skills & Interests Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">💡 Top Skills</div>', unsafe_allow_html=True)
            
            skills = get_user_top_skills(user_id)
            if skills:
                for skill in skills:
                    st.markdown(f'<span class="skill-badge">{skill}</span>', unsafe_allow_html=True)
            else:
                st.info("Upload resumes to discover your top skills!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🎯 Career Interests</div>', unsafe_allow_html=True)
            
            interests = get_user_interests(user_id)
            if interests:
                for interest in interests:
                    st.markdown(f'<span class="skill-badge">{interest}</span>', unsafe_allow_html=True)
            else:
                st.info("Your career interests will appear here based on your activity!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent Activity Timeline
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⏱️ Recent Activity</div>', unsafe_allow_html=True)
        
        recent_activities = get_recent_activities(user_id)
        if recent_activities:
            for activity in recent_activities:
                st.markdown(f"""
                <div class="timeline-item">
                    <div style="font-weight: 600; color: #f0f0ff; margin-bottom: 0.3rem;">
                        {activity['icon']} {activity['title']}
                    </div>
                    <div style="color: #a0a0c0; font-size: 0.85rem;">{activity['time']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Your recent activities will appear here!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Account Information
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">ℹ️ Account Information</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="padding: 1rem; background: rgba(0,255,136,0.05); border-radius: 10px; border: 1px solid rgba(0,255,136,0.2);">
                <div style="color: #a0a0c0; font-size: 0.85rem; margin-bottom: 0.5rem;">Member Since</div>
                <div style="color: #00ff88; font-weight: 600;">
                    {user_data['created_at'].strftime('%B %d, %Y') if user_data.get('created_at') else 'N/A'}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="padding: 1rem; background: rgba(0,180,255,0.05); border-radius: 10px; border: 1px solid rgba(0,180,255,0.2);">
                <div style="color: #a0a0c0; font-size: 0.85rem; margin-bottom: 0.5rem;">Last Login</div>
                <div style="color: #00b4ff; font-weight: 600;">
                    {user_data['last_login'].strftime('%B %d, %Y') if user_data.get('last_login') else 'N/A'}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="padding: 1rem; background: rgba(168,85,247,0.05); border-radius: 10px; border: 1px solid rgba(168,85,247,0.2);">
                <div style="color: #a0a0c0; font-size: 0.85rem; margin-bottom: 0.5rem;">Account Status</div>
                <div style="color: #a855f7; font-weight: 600;">
                    ✅ Active
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Account Actions
        st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Change Password", use_container_width=True):
                st.session_state['show_change_password'] = True
        
        with col2:
            if st.button("📥 Download My Data", use_container_width=True):
                st.info("Feature coming soon! You'll be able to download all your data.")
        
        with col3:
            if st.button("🚪 Logout", use_container_width=True, type="primary"):
                AuthManager.logout_user()
                st.success("✅ Logged out successfully!")
                st.rerun()
        
        # Change password form
        if st.session_state.get('show_change_password', False):
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">🔐 Change Password</div>', unsafe_allow_html=True)
            
            with st.form("change_password_form"):
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submit = st.form_submit_button("Update Password", use_container_width=True)
                with col_b:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)
                
                if submit:
                    if not current_password or not new_password:
                        st.error("⚠️ Please fill in all fields")
                    elif len(new_password) < 6:
                        st.error("⚠️ New password must be at least 6 characters")
                    elif new_password != confirm_password:
                        st.error("⚠️ New passwords do not match")
                    else:
                        auth_result = AuthManager.authenticate_user(user_email, current_password)
                        if auth_result['success']:
                            st.success("✅ Password updated successfully!")
                            st.session_state['show_change_password'] = False
                            st.rerun()
                        else:
                            st.error("❌ Current password is incorrect")
                
                if cancel:
                    st.session_state['show_change_password'] = False
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.error(f"❌ {profile_result['message']}")


def get_user_activity(user_id):
    """Get user activity data for chart"""
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Get activity for last 30 days
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM resume_data
                WHERE user_id = %s AND created_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """, (user_id,))
            
            results = cursor.fetchall()
            if results:
                return [{'date': row[0], 'count': row[1]} for row in results]
            return None
    except:
        return None


def create_activity_chart(activity_data):
    """Create activity timeline chart"""
    df = pd.DataFrame(activity_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['count'],
        mode='lines+markers',
        line=dict(color='#00ff88', width=3),
        marker=dict(size=8, color='#00ff88', line=dict(color='#00b4ff', width=2)),
        fill='tozeroy',
        fillcolor='rgba(0,255,136,0.1)'
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0a0c0'),
        xaxis=dict(showgrid=False, title='Date'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='Activities'),
        margin=dict(l=0, r=0, t=20, b=0),
        height=250
    )
    
    return fig


def get_user_achievements(stats):
    """Get user achievements based on stats"""
    achievements = []
    
    total_resumes = stats.get('total_resumes', 0)
    total_analyses = stats.get('total_analyses', 0)
    avg_score = stats.get('avg_score', 0)
    
    if total_resumes >= 1:
        achievements.append({
            'icon': '🎯',
            'title': 'First Resume',
            'description': 'Created your first resume'
        })
    
    if total_resumes >= 5:
        achievements.append({
            'icon': '📚',
            'title': 'Resume Master',
            'description': 'Created 5+ resumes'
        })
    
    if total_analyses >= 10:
        achievements.append({
            'icon': '🔍',
            'title': 'Analysis Pro',
            'description': 'Completed 10+ analyses'
        })
    
    if avg_score >= 80:
        achievements.append({
            'icon': '⭐',
            'title': 'High Achiever',
            'description': '80+ average score'
        })
    
    if not achievements:
        achievements.append({
            'icon': '🚀',
            'title': 'Getting Started',
            'description': 'Begin your journey!'
        })
    
    return achievements


def get_user_top_skills(user_id):
    """Get user's top skills from resumes"""
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT skills FROM resume_data 
                WHERE user_id = %s AND skills IS NOT NULL 
                ORDER BY created_at DESC LIMIT 5
            """, (user_id,))
            
            results = cursor.fetchall()
            if results:
                all_skills = []
                for row in results:
                    if row[0]:
                        skills = row[0].split(',')
                        all_skills.extend([s.strip() for s in skills[:5]])
                return list(set(all_skills))[:10]
            return None
    except:
        return None


def get_user_interests(user_id):
    """Get user's career interests from target roles"""
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT target_role FROM resume_data 
                WHERE user_id = %s AND target_role IS NOT NULL 
                LIMIT 5
            """, (user_id,))
            
            results = cursor.fetchall()
            if results:
                return [row[0] for row in results if row[0]]
            return None
    except:
        return None


def get_recent_activities(user_id):
    """Get user's recent activities"""
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT created_at, target_role 
                FROM resume_data 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 5
            """, (user_id,))
            
            results = cursor.fetchall()
            if results:
                activities = []
                for row in results:
                    time_diff = datetime.now() - row[0]
                    if time_diff.days == 0:
                        time_str = "Today"
                    elif time_diff.days == 1:
                        time_str = "Yesterday"
                    else:
                        time_str = f"{time_diff.days} days ago"
                    
                    activities.append({
                        'icon': '📄',
                        'title': f"Created resume for {row[1] or 'position'}",
                        'time': time_str
                    })
                return activities
            return None
    except:
        return None
