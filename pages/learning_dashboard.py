"""
Learning Dashboard - Personalized YouTube Course Recommendations
Modern educational dashboard with video previews
"""
import streamlit as st
from config.course_recommendation_manager import CourseRecommendationManager
from auth.auth_manager import AuthManager

def render_video_card(course: dict, show_preview: bool = False):
    """Render a modern YouTube video card with preview"""
    
    video_id = course['youtube_video_id']
    thumbnail_url = course['thumbnail_url']
    
    # Unique key for this card
    card_key = f"card_{course['id']}"
    
    # Card styling
    st.markdown(f"""
    <style>
        .video-card-{course['id']} {{
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            border-radius: 16px;
            overflow: hidden;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
            height: 100%;
        }}
        
        .video-card-{course['id']}:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(76, 175, 80, 0.3);
            border-color: rgba(76, 175, 80, 0.5);
        }}
        
        .thumbnail-container-{course['id']} {{
            position: relative;
            width: 100%;
            padding-top: 56.25%; /* 16:9 Aspect Ratio */
            overflow: hidden;
            cursor: pointer;
        }}
        
        .thumbnail-container-{course['id']} img {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .play-overlay-{course['id']} {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 68px;
            height: 48px;
            background: rgba(255, 0, 0, 0.9);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }}
        
        .play-overlay-{course['id']}:hover {{
            background: rgba(255, 0, 0, 1);
            transform: translate(-50%, -50%) scale(1.1);
        }}
        
        .play-icon-{course['id']} {{
            width: 0;
            height: 0;
            border-left: 20px solid white;
            border-top: 12px solid transparent;
            border-bottom: 12px solid transparent;
            margin-left: 4px;
        }}
        
        .duration-badge-{course['id']} {{
            position: absolute;
            bottom: 8px;
            right: 8px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .card-content-{course['id']} {{
            padding: 1rem;
        }}
        
        .course-title-{course['id']} {{
            color: white;
            font-size: 1rem;
            font-weight: 600;
            margin: 0 0 0.5rem 0;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .channel-name-{course['id']} {{
            color: #aaa;
            font-size: 0.875rem;
            margin: 0 0 0.5rem 0;
        }}
        
        .skill-badge-{course['id']} {{
            display: inline-block;
            background: rgba(76, 175, 80, 0.2);
            color: #4CAF50;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }}
        
        .watch-button-{course['id']} {{
            width: 100%;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            text-decoration: none;
            display: block;
        }}
        
        .watch-button-{course['id']}:hover {{
            background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
            transform: scale(1.02);
        }}
        
        .bookmark-icon-{course['id']} {{
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0, 0, 0, 0.7);
            color: {'#FFD700' if course.get('is_bookmarked') else 'white'};
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            z-index: 10;
        }}
        
        .bookmark-icon-{course['id']}:hover {{
            background: rgba(0, 0, 0, 0.9);
            transform: scale(1.1);
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Card HTML
    st.markdown(f"""
    <div class="video-card-{course['id']}">
        <div class="thumbnail-container-{course['id']}">
            <img src="{thumbnail_url}" alt="{course['course_title']}" loading="lazy">
            <div class="play-overlay-{course['id']}">
                <div class="play-icon-{course['id']}"></div>
            </div>
            <div class="duration-badge-{course['id']}">{course['video_duration']}</div>
            <div class="bookmark-icon-{course['id']}" title="{'Bookmarked' if course.get('is_bookmarked') else 'Bookmark'}">
                {'★' if course.get('is_bookmarked') else '☆'}
            </div>
        </div>
        <div class="card-content-{course['id']}">
            <h3 class="course-title-{course['id']}">{course['course_title']}</h3>
            <p class="channel-name-{course['id']}">{course['channel_name']}</p>
            <span class="skill-badge-{course['id']}">Skill: {course['skill_covered']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Buttons below card
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button(f"▶ Watch on YouTube", key=f"watch_{course['id']}", use_container_width=True):
            # Mark as watched
            CourseRecommendationManager.mark_as_watched(
                course['id'], 
                AuthManager.get_current_user_id()
            )
            # Open in new tab
            st.markdown(f'<meta http-equiv="refresh" content="0;url={course["course_url"]}">', 
                       unsafe_allow_html=True)
            st.success("Opening YouTube...")
    
    with col2:
        bookmark_label = "★" if course.get('is_bookmarked') else "☆"
        if st.button(bookmark_label, key=f"bookmark_{course['id']}", use_container_width=True):
            CourseRecommendationManager.toggle_bookmark(
                course['id'],
                AuthManager.get_current_user_id()
            )
            st.rerun()
    
    # Show embedded preview if requested
    if show_preview:
        st.markdown(f"""
        <iframe 
            width="100%" 
            height="200" 
            src="https://www.youtube.com/embed/{video_id}" 
            title="YouTube video preview" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen
            loading="lazy">
        </iframe>
        """, unsafe_allow_html=True)

def render_learning_dashboard():
    """Main learning dashboard page"""
    
    # Check authentication
    if not AuthManager.is_authenticated():
        st.error("Please login to access learning recommendations")
        return
    
    user_id = AuthManager.get_current_user_id()
    
    # Page styling
    st.markdown("""
    <style>
        .dashboard-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .dashboard-title {
            color: white;
            font-size: 2.5rem;
            margin: 0;
            font-weight: 700;
        }
        
        .dashboard-subtitle {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
        }
        
        .section-header {
            color: #4CAF50;
            font-size: 1.5rem;
            margin: 2rem 0 1rem 0;
            font-weight: 600;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            margin: 2rem 0;
        }
        
        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h1 class="dashboard-title">📚 Learning Dashboard</h1>
        <p class="dashboard-subtitle">Personalized YouTube courses based on your skill gaps</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user's course recommendations
    recommendations = CourseRecommendationManager.get_user_recommendations(user_id)
    
    if not recommendations:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🎓</div>
            <h2>No Course Recommendations Yet</h2>
            <p>Complete a resume analysis to get personalized learning recommendations!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Go to Resume Analyzer", use_container_width=True, type="primary"):
            st.session_state.page = 'resume_analyzer'
            st.rerun()
        return
    
    # Filter options
    st.markdown('<p class="section-header">Filter Courses</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Get unique skills
        skills = list(set([r['skill_covered'] for r in recommendations]))
        selected_skill = st.selectbox("Filter by Skill", ["All Skills"] + skills)
    
    with col2:
        show_watched = st.checkbox("Show Watched", value=True)
    
    with col3:
        show_bookmarked_only = st.checkbox("Bookmarked Only", value=False)
    
    # Filter recommendations
    filtered_recs = recommendations
    
    if selected_skill != "All Skills":
        filtered_recs = [r for r in filtered_recs if r['skill_covered'] == selected_skill]
    
    if not show_watched:
        filtered_recs = [r for r in filtered_recs if not r['is_watched']]
    
    if show_bookmarked_only:
        filtered_recs = [r for r in filtered_recs if r['is_bookmarked']]
    
    # Display count
    st.markdown(f'<p class="section-header">📺 {len(filtered_recs)} Courses Available</p>', 
               unsafe_allow_html=True)
    
    if not filtered_recs:
        st.info("No courses match your filters")
        return
    
    # Display courses in grid (3 columns)
    for i in range(0, len(filtered_recs), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(filtered_recs):
                with col:
                    render_video_card(filtered_recs[i + j])
                    st.markdown("<br>", unsafe_allow_html=True)
