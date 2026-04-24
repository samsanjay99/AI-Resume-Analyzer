"""
User Profile Management Page - LinkedIn Style
Complete profile viewing and editing interface with stunning design
"""
import streamlit as st
from config.profile_manager import ProfileManager
from auth.auth_manager import AuthManager
from config.database import get_resume_stats, get_database_connection
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd


@st.cache_data(ttl=60)
def get_cached_profile(user_id: int):
    """Get profile with caching"""
    return ProfileManager.get_profile(user_id)


@st.cache_data(ttl=60)
def get_cached_stats(user_id: int):
    """Get profile stats with caching"""
    return ProfileManager.get_profile_stats(user_id)


def render_profile_page():
    """Render stunning LinkedIn-style profile page"""
    
    if not AuthManager.is_authenticated():
        st.warning("⚠️ Please login to view your profile")
        return
    
    user_id = AuthManager.get_current_user_id()
    user_email = AuthManager.get_current_user_email()
    user_name = AuthManager.get_current_user_name()
    
    # Custom CSS for stunning profile
    st.markdown("""
    <style>
    .profile-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border-radius: 20px;
        padding: 2.5rem;
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
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(0,255,136,0.15) 0%, transparent 70%);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
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
        margin: 0 auto 1rem;
        box-shadow: 0 0 40px rgba(0,255,136,0.5);
        border: 4px solid rgba(0,255,136,0.3);
        animation: pulse-glow 3s ease-in-out infinite;
        position: relative;
        z-index: 1;
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 40px rgba(0,255,136,0.4); }
        50% { box-shadow: 0 0 60px rgba(0,255,136,0.7); }
    }
    
    .profile-name {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00ff88, #00b4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.5rem 0;
        text-align: center;
        position: relative;
        z-index: 1;
    }
    
    .profile-email {
        color: #a0a0c0;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
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
        transition: all 0.3s ease;
    }
    
    .profile-badge:hover {
        background: rgba(0,255,136,0.2);
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0,255,136,0.3);
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
        padding: 1.2rem;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
    }
    
    .achievement-card:hover {
        transform: translateX(10px);
        border-color: rgba(0,255,136,0.4);
        box-shadow: 0 4px 20px rgba(0,255,136,0.2);
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00ff88;
        margin-bottom: 1.5rem;
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
    
    .timeline-item {
        position: relative;
        padding-left: 2.5rem;
        padding-bottom: 1.5rem;
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
    </style>
    """, unsafe_allow_html=True)
    
    # Get profile data
    profile = get_cached_profile(user_id) or {}
    
    if not profile:
        result = ProfileManager.create_profile(user_id, user_name)
        if result['success']:
            profile = ProfileManager.get_profile(user_id) or {}
            get_cached_profile.clear()
    
    # Ensure stats is always defined
    stats = {}
    
    # Profile Header
    st.markdown(f"""
    <div class="profile-header">
        <div class="profile-avatar">👤</div>
        <h1 class="profile-name">{profile.get('full_name', user_name)}</h1>
        <p class="profile-email">📧 {user_email}</p>
        <p style="text-align:center;color:#a0a0c0;margin:0.3rem 0;">
            {('🎯 ' + profile['target_job_role']) if profile.get('target_job_role') else ''}
            {'&nbsp;&nbsp;|&nbsp;&nbsp;' if profile.get('target_job_role') and profile.get('location') else ''}
            {('📍 ' + profile['location']) if profile.get('location') else ''}
        </p>
        <div style="text-align: center; margin-top: 1rem;">
            <span class="profile-badge">🎯 Active Member</span>
            <span class="profile-badge">⭐ Verified</span>
            <span class="profile-badge">🚀 Pro User</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance Dashboard
    st.markdown('<p style="font-size:1.4rem;font-weight:700;color:#00ff88;margin-bottom:1rem;">📊 Your Performance Dashboard</p>', unsafe_allow_html=True)
    
    SCARD = "background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:15px;padding:1.5rem;text-align:center;"
    SVAL = "font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#00ff88,#00b4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0.4rem 0;"
    SLBL = "color:#a0a0c0;font-size:0.85rem;text-transform:uppercase;letter-spacing:1px;"

    try:
        stats = get_resume_stats(user_id) or {}
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'<div style="{SCARD}"><div style="font-size:2rem;">📄</div><div style="{SVAL}">{stats.get("total_resumes", 0)}</div><div style="{SLBL}">Resumes</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="{SCARD}"><div style="font-size:2rem;">🔍</div><div style="{SVAL}">{stats.get("total_analyses", 0)}</div><div style="{SLBL}">Analyses</div></div>', unsafe_allow_html=True)
        with col3:
            avg_score = stats.get('avg_score', 0)
            st.markdown(f'<div style="{SCARD}"><div style="font-size:2rem;">⭐</div><div style="{SVAL}">{f"{avg_score}%" if avg_score else "N/A"}</div><div style="{SLBL}">Avg Score</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div style="{SCARD}"><div style="font-size:2rem;">🌐</div><div style="{SVAL}">{stats.get("total_portfolios", 0)}</div><div style="{SLBL}">Portfolios</div></div>', unsafe_allow_html=True)
    except:
        st.info("Start using the platform to see your statistics!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📝 Edit Profile", "🏆 Achievements", "⚙️ Settings"])
    
    with tab1:
        render_overview_tab(user_id, profile, stats)
    
    with tab2:
        render_edit_tab(user_id, profile)
    
    with tab3:
        render_achievements_tab(user_id, stats)
    
    with tab4:
        render_settings_tab(user_id, user_email)


def render_overview_tab(user_id, profile, stats):
    """Render overview tab with activity and skills"""
    
    CARD = "background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:15px;padding:1.2rem;margin-bottom:1rem;"
    TITLE = "font-size:1rem;font-weight:700;color:#00ff88;margin-bottom:0.5rem;"
    VAL = "color:#f0f0ff;font-size:1rem;"

    # Info cards row
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f'<div style="{CARD}"><div style="{TITLE}">📍 Location</div><div style="{VAL}">{profile.get("location") or "—"}</div></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div style="{CARD}"><div style="{TITLE}">💼 Experience</div><div style="{VAL}">{profile.get("experience_level") or "—"}</div></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown(f'<div style="{CARD}"><div style="{TITLE}">🎯 Target Role</div><div style="{VAL}">{profile.get("target_job_role") or "—"}</div></div>', unsafe_allow_html=True)

    # Bio
    if profile.get('bio'):
        st.markdown(f'<div style="{CARD}"><div style="{TITLE}">📝 About</div><div style="color:#d0d0e0;line-height:1.7;font-size:0.95rem;">{profile.get("bio")}</div></div>', unsafe_allow_html=True)

    # Education
    if profile.get('education'):
        st.markdown(f'<div style="{CARD}"><div style="{TITLE}">🎓 Education</div><div style="color:#d0d0e0;font-size:0.95rem;">{profile.get("education")}</div></div>', unsafe_allow_html=True)

    # Social links
    linkedin = profile.get('linkedin_url')
    github = profile.get('github_url')
    portfolio_url = profile.get('portfolio_url')
    if linkedin or github or portfolio_url:
        links = ''
        if linkedin:
            links += f'<a href="{linkedin}" target="_blank" style="background:rgba(0,180,255,0.1);color:#00b4ff;padding:0.5rem 1.2rem;border-radius:50px;border:1px solid rgba(0,180,255,0.3);text-decoration:none;font-weight:600;margin:0.3rem;display:inline-block;">🔗 LinkedIn</a>'
        if github:
            links += f'<a href="{github}" target="_blank" style="background:rgba(168,85,247,0.1);color:#a855f7;padding:0.5rem 1.2rem;border-radius:50px;border:1px solid rgba(168,85,247,0.3);text-decoration:none;font-weight:600;margin:0.3rem;display:inline-block;">💻 GitHub</a>'
        if portfolio_url:
            links += f'<a href="{portfolio_url}" target="_blank" style="background:rgba(0,255,136,0.1);color:#00ff88;padding:0.5rem 1.2rem;border-radius:50px;border:1px solid rgba(0,255,136,0.3);text-decoration:none;font-weight:600;margin:0.3rem;display:inline-block;">🌐 Portfolio</a>'
        st.markdown(f'<div style="{CARD}"><div style="{TITLE}">🔗 Connect</div><div style="flex-wrap:wrap;">{links}</div></div>', unsafe_allow_html=True)

    # Skills
    skills = profile.get('skills') or get_user_top_skills(user_id)
    if skills:
        badges = ''.join(f'<span style="display:inline-block;background:rgba(0,255,136,0.1);color:#00ff88;border:1px solid rgba(0,255,136,0.3);padding:0.4rem 0.9rem;border-radius:50px;font-size:0.82rem;font-weight:600;margin:0.25rem;">{s}</span>' for s in skills[:15])
        st.markdown(f'<div style="{CARD}"><div style="{TITLE}">💡 Skills</div>{badges}</div>', unsafe_allow_html=True)

    # Activity chart + recent activity
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("#### 📈 Activity Timeline")
        activity_data = get_user_activity(user_id)
        if activity_data:
            st.plotly_chart(create_activity_chart(activity_data), use_container_width=True)
        else:
            st.info("Start using the platform to see your activity!")

    with col2:
        st.markdown("#### ⏱️ Recent Activity")
        recent = get_recent_activities(user_id)
        if recent:
            for activity in recent:
                st.markdown(f"""
                <div style="position:relative;padding-left:2rem;padding-bottom:1.2rem;border-left:2px solid rgba(0,255,136,0.2);">
                    <div style="position:absolute;left:-6px;top:0;width:12px;height:12px;border-radius:50%;background:#00ff88;box-shadow:0 0 10px rgba(0,255,136,0.5);"></div>
                    <div style="font-weight:600;color:#f0f0ff;margin-bottom:0.2rem;">{activity['icon']} {activity['title']}</div>
                    <div style="color:#a0a0c0;font-size:0.82rem;">{activity['time']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent activity yet!")


def render_edit_tab(user_id, profile):
    """Render edit profile tab"""
    
    st.markdown("### 📝 Edit Your Profile")
    
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Basic Information")
            full_name = st.text_input("Full Name", value=profile.get('full_name', '') or '')
            username = st.text_input("Username", value=profile.get('username', '') or '')
            location = st.text_input("Location", value=profile.get('location', '') or '')
            
        with col2:
            st.markdown("#### 💼 Career Information")
            experience_level = st.selectbox(
                "Experience Level",
                ["", "Entry Level", "Junior", "Mid-Level", "Senior", "Lead", "Executive"],
                index=0 if not profile.get('experience_level') else
                      ["", "Entry Level", "Junior", "Mid-Level", "Senior", "Lead", "Executive"].index(profile.get('experience_level', ''))
            )
            target_job_role = st.text_input("Target Job Role", value=profile.get('target_job_role', '') or '')
            education = st.text_input("Education", value=profile.get('education', '') or '')
        
        bio = st.text_area("Bio", value=profile.get('bio', '') or '', height=100, max_chars=500)
        skills_input = st.text_input(
            "Skills (comma-separated)",
            value=", ".join(profile.get('skills', [])) if profile.get('skills') else ''
        )
        
        col3, col4, col5 = st.columns(3)
        with col3:
            linkedin_url = st.text_input("LinkedIn", value=profile.get('linkedin_url', '') or '')
        with col4:
            github_url = st.text_input("GitHub", value=profile.get('github_url', '') or '')
        with col5:
            portfolio_url = st.text_input("Portfolio", value=profile.get('portfolio_url', '') or '')
        
        submit = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
        
        if submit:
            if username and username != profile.get('username'):
                if not ProfileManager.check_username_available(username, user_id):
                    st.error("❌ Username already taken")
                    return
            
            skills_list = [s.strip() for s in skills_input.split(',') if s.strip()]
            
            update_data = {
                'full_name': full_name,
                'username': username if username else None,
                'bio': bio,
                'location': location,
                'education': education,
                'experience_level': experience_level if experience_level else None,
                'target_job_role': target_job_role,
                'skills': skills_list,
                'linkedin_url': linkedin_url,
                'github_url': github_url,
                'portfolio_url': portfolio_url
            }
            
            result = ProfileManager.update_profile(user_id, update_data)
            
            if result['success']:
                get_cached_profile.clear()
                get_cached_stats.clear()
                st.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                st.error(f"❌ {result['message']}")


def render_achievements_tab(user_id, stats):
    """Render achievements tab"""
    
    st.markdown("### 🏆 Your Achievements")
    CARD = "background:linear-gradient(135deg,rgba(0,255,136,0.05),rgba(0,180,255,0.05));border:1px solid rgba(0,255,136,0.2);border-radius:15px;padding:1.2rem;margin:0.8rem 0;"
    
    achievements = get_user_achievements(stats)
    for achievement in achievements:
        st.markdown(f"""
        <div style="{CARD}">
            <div style="font-size:2rem;margin-bottom:0.4rem;">{achievement['icon']}</div>
            <div style="font-weight:600;color:#00ff88;margin-bottom:0.3rem;font-size:1.05rem;">{achievement['title']}</div>
            <div style="color:#a0a0c0;font-size:0.88rem;">{achievement['description']}</div>
        </div>
        """, unsafe_allow_html=True)


def render_settings_tab(user_id, user_email):
    """Render settings tab"""
    
    st.markdown("### ⚙️ Account Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Change Password", use_container_width=True):
            st.session_state['show_change_password'] = True
    
    with col2:
        if st.button("📥 Download My Data", use_container_width=True):
            st.info("Feature coming soon!")
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            AuthManager.logout_user()
            st.success("✅ Logged out successfully!")
            st.rerun()
    
    if st.session_state.get('show_change_password', False):
        st.markdown("---")
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


# Helper functions
def get_user_activity(user_id):
    """Get user activity data"""
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
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
    except:
        pass
    return None


def create_activity_chart(activity_data):
    """Create activity chart"""
    df = pd.DataFrame(activity_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['count'],
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
    """Get user achievements"""
    achievements = []
    total_resumes = stats.get('total_resumes', 0)
    total_analyses = stats.get('total_analyses', 0)
    avg_score = stats.get('avg_score', 0)
    
    if total_resumes >= 1:
        achievements.append({'icon': '🎯', 'title': 'First Resume', 'description': 'Created your first resume'})
    if total_resumes >= 5:
        achievements.append({'icon': '📚', 'title': 'Resume Master', 'description': 'Created 5+ resumes'})
    if total_analyses >= 10:
        achievements.append({'icon': '🔍', 'title': 'Analysis Pro', 'description': 'Completed 10+ analyses'})
    if avg_score >= 80:
        achievements.append({'icon': '⭐', 'title': 'High Achiever', 'description': '80+ average score'})
    
    if not achievements:
        achievements.append({'icon': '🚀', 'title': 'Getting Started', 'description': 'Begin your journey!'})
    
    return achievements


def get_user_top_skills(user_id):
    """Get user top skills"""
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
    except:
        pass
    return None


def get_recent_activities(user_id):
    """Get recent activities"""
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
    except:
        pass
    return None


if __name__ == "__main__":
    render_profile_page()
