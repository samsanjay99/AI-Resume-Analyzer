"""
Learning Dashboard - Personalized YouTube Course Recommendations
Modern educational dashboard with video previews
"""
import streamlit as st
from config.course_recommendation_manager import CourseRecommendationManager
from auth.auth_manager import AuthManager

def render_video_card(course: dict, show_preview: bool = False):
    """Render a modern YouTube video card"""

    video_id = course['youtube_video_id']
    thumbnail_url = course['thumbnail_url']
    is_bookmarked = course.get('is_bookmarked', False)
    is_watched = course.get('is_watched', False)
    course_url = course['course_url']

    watched_badge = "<span style='display:inline-block;background:rgba(0,180,255,0.1);color:#00b4ff;border:1px solid rgba(0,180,255,0.25);padding:3px 10px;border-radius:50px;font-size:0.75rem;font-weight:600;margin-left:0.4rem;'>✅ Watched</span>" if is_watched else ""
    bm_icon = "★" if is_bookmarked else "☆"

    st.markdown(f"""<div style='background:linear-gradient(135deg,rgba(15,23,42,0.9),rgba(30,41,59,0.9));border-radius:16px;overflow:hidden;border:1px solid rgba(255,255,255,0.08);transition:all 0.3s ease;margin-bottom:0.5rem;'>
<div style='position:relative;width:100%;padding-top:56.25%;overflow:hidden;background:#0a0a1a;'>
<img src="{thumbnail_url}" alt="{course['course_title']}" loading="lazy" style='position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;'>
<div style='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:56px;height:40px;background:rgba(255,0,0,0.88);border-radius:10px;'></div>
<span style='position:absolute;bottom:8px;right:8px;background:rgba(0,0,0,0.82);color:white;padding:3px 7px;border-radius:4px;font-size:0.72rem;font-weight:600;'>{course['video_duration']}</span>
<span style='position:absolute;top:8px;right:8px;background:rgba(0,0,0,0.7);width:32px;height:32px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:1rem;'>{bm_icon}</span>
</div>
<div style='padding:1rem;'>
<p style='color:#f0f0ff;font-size:0.95rem;font-weight:600;margin:0 0 0.4rem 0;line-height:1.4;'>{course['course_title']}</p>
<p style='color:#a0a0c0;font-size:0.82rem;margin:0 0 0.5rem 0;'>{course['channel_name']}</p>
<span style='display:inline-block;background:rgba(0,255,136,0.1);color:#00ff88;border:1px solid rgba(0,255,136,0.25);padding:3px 10px;border-radius:50px;font-size:0.75rem;font-weight:600;'>{course['skill_covered']}</span>{watched_badge}
</div>
</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        # Opens YouTube in a new tab without navigating away from the app
        st.markdown(
            f"<a href='{course_url}' target='_blank' rel='noopener noreferrer' "
            f"style='display:block;text-align:center;background:linear-gradient(135deg,#00cc6a,#00a855);"
            f"color:#000;font-weight:700;font-size:0.88rem;padding:0.6rem 1rem;border-radius:50px;"
            f"text-decoration:none;width:100%;box-sizing:border-box;'>▶ Watch on YouTube</a>",
            unsafe_allow_html=True
        )
        # Mark as watched when user clicks (tracked separately via a small button)
        if st.button("✓ Mark as Watched", key=f"watched_{course['id']}", use_container_width=True):
            CourseRecommendationManager.mark_as_watched(course['id'], AuthManager.get_current_user_id())
            st.rerun()
    with col2:
        if st.button(bm_icon, key=f"bookmark_{course['id']}", use_container_width=True):
            CourseRecommendationManager.toggle_bookmark(course['id'], AuthManager.get_current_user_id())
            st.rerun()

    if show_preview:
        # Use /embed/ URL — youtube.com/watch is blocked by X-Frame-Options
        st.markdown(
            f"<iframe width='100%' height='200' "
            f"src='https://www.youtube.com/embed/{video_id}' "
            f"frameborder='0' allowfullscreen loading='lazy'></iframe>",
            unsafe_allow_html=True
        )

def render_learning_dashboard():
    """Main learning dashboard page"""
    
    if not AuthManager.is_authenticated():
        st.error("Please login to access learning recommendations")
        return
    
    user_id = AuthManager.get_current_user_id()
    
    # Match app-wide theme
    st.markdown("""
    <style>
    .learn-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(0,255,136,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .learn-header::before {
        content: '';
        position: absolute;
        top: -40%;
        left: 50%;
        transform: translateX(-50%);
        width: 500px; height: 300px;
        background: radial-gradient(ellipse, rgba(0,255,136,0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    .learn-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00ff88, #00b4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.5rem 0;
    }
    .learn-subtitle {
        color: #a0a0c0;
        font-size: 1.05rem;
        margin: 0;
    }
    .stat-pill {
        display: inline-block;
        background: rgba(0,255,136,0.1);
        color: #00ff88;
        border: 1px solid rgba(0,255,136,0.25);
        border-radius: 50px;
        padding: 0.35rem 1rem;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.3rem;
    }
    .video-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,41,59,0.9));
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
        transition: all 0.3s cubic-bezier(.34,1.56,.64,1);
        height: 100%;
    }
    .video-card:hover {
        transform: translateY(-6px);
        border-color: rgba(0,255,136,0.35);
        box-shadow: 0 16px 40px rgba(0,0,0,0.5), 0 0 30px rgba(0,255,136,0.15);
    }
    .thumb-wrap {
        position: relative;
        width: 100%;
        padding-top: 56.25%;
        overflow: hidden;
        background: #0a0a1a;
    }
    .thumb-wrap img {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        object-fit: cover;
        transition: transform 0.4s ease;
    }
    .video-card:hover .thumb-wrap img { transform: scale(1.05); }
    .play-btn {
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 56px; height: 40px;
        background: rgba(255,0,0,0.88);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        transition: all 0.3s ease;
    }
    .play-btn::after {
        content: '';
        width: 0; height: 0;
        border-left: 16px solid white;
        border-top: 10px solid transparent;
        border-bottom: 10px solid transparent;
        margin-left: 4px;
    }
    .dur-badge {
        position: absolute;
        bottom: 8px; right: 8px;
        background: rgba(0,0,0,0.82);
        color: white;
        padding: 3px 7px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .bm-badge {
        position: absolute;
        top: 8px; right: 8px;
        background: rgba(0,0,0,0.7);
        width: 32px; height: 32px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem;
        z-index: 10;
    }
    .card-body {
        padding: 1rem;
    }
    .card-title {
        color: #f0f0ff;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 0 0 0.4rem 0;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .card-channel {
        color: #a0a0c0;
        font-size: 0.82rem;
        margin: 0 0 0.5rem 0;
    }
    .skill-chip {
        display: inline-block;
        background: rgba(0,255,136,0.1);
        color: #00ff88;
        border: 1px solid rgba(0,255,136,0.25);
        padding: 3px 10px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .watched-chip {
        display: inline-block;
        background: rgba(0,180,255,0.1);
        color: #00b4ff;
        border: 1px solid rgba(0,180,255,0.25);
        padding: 3px 10px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.4rem;
    }
    .empty-box {
        text-align: center;
        padding: 4rem 2rem;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="learn-header">
        <h1 class="learn-title">📚 Learning Dashboard</h1>
        <p class="learn-subtitle">Personalized YouTube courses based on your skill gaps</p>
    </div>
    """, unsafe_allow_html=True)
    
    recommendations = CourseRecommendationManager.get_user_recommendations(user_id)
    
    if not recommendations:
        st.markdown("""
        <div class="empty-box">
            <div style="font-size:4rem;margin-bottom:1rem;">🎓</div>
            <h2 style="color:#f0f0ff;">No Course Recommendations Yet</h2>
            <p style="color:#a0a0c0;">Complete a resume analysis to get personalized learning recommendations!</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔍 Go to Resume Analyzer", use_container_width=True, type="primary"):
            st.session_state.page = 'resume_analyzer'
            st.rerun()
        return
    
    # Stats pills
    total = len(recommendations)
    watched = sum(1 for r in recommendations if r.get('is_watched'))
    bookmarked = sum(1 for r in recommendations if r.get('is_bookmarked'))
    skills_count = len(set(r['skill_covered'] for r in recommendations))
    
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <span class="stat-pill">📺 {total} Courses</span>
        <span class="stat-pill">✅ {watched} Watched</span>
        <span class="stat-pill">★ {bookmarked} Bookmarked</span>
        <span class="stat-pill">💡 {skills_count} Skills</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        skills = ["All Skills"] + sorted(set(r['skill_covered'] for r in recommendations))
        selected_skill = st.selectbox("🔍 Filter by Skill", skills)
    with col2:
        show_watched = st.checkbox("Show Watched", value=True)
    with col3:
        show_bookmarked_only = st.checkbox("Bookmarked Only", value=False)
    
    filtered = recommendations
    if selected_skill != "All Skills":
        filtered = [r for r in filtered if r['skill_covered'] == selected_skill]
    if not show_watched:
        filtered = [r for r in filtered if not r.get('is_watched')]
    if show_bookmarked_only:
        filtered = [r for r in filtered if r.get('is_bookmarked')]
    
    st.markdown(f"<p style='color:#a0a0c0;margin:1rem 0;'>Showing <strong style='color:#00ff88;'>{len(filtered)}</strong> courses</p>", unsafe_allow_html=True)
    
    if not filtered:
        st.info("No courses match your filters.")
        return
    
    # Course grid
    for i in range(0, len(filtered), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(filtered):
                with col:
                    render_video_card(filtered[i + j])
                    st.markdown("<br>", unsafe_allow_html=True)

