"""
User Profile Management Page
Complete profile viewing and editing interface
"""
import streamlit as st
from config.profile_manager import ProfileManager
from auth.auth_manager import AuthManager


@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_cached_profile(user_id: int):
    """Get profile with caching"""
    return ProfileManager.get_profile(user_id)


@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_cached_stats(user_id: int):
    """Get profile stats with caching"""
    return ProfileManager.get_profile_stats(user_id)


def render_profile_page():
    """Render the profile management page"""
    
    # Check authentication using AuthManager
    if not AuthManager.is_authenticated():
        st.warning("⚠️ Please login to view your profile")
        return
    
    # Get user data from session
    user_id = AuthManager.get_current_user_id()
    user_email = AuthManager.get_current_user_email()
    user_name = AuthManager.get_current_user_name()
    
    # Create user dict for compatibility
    user = {
        'id': user_id,
        'email': user_email,
        'full_name': user_name
    }
    
    # Get profile data with caching
    profile = get_cached_profile(user_id)
    
    # If no profile exists, create one
    if not profile:
        result = ProfileManager.create_profile(user_id, user.get('full_name'))
        if result['success']:
            profile = ProfileManager.get_profile(user_id)
            # Clear cache after creating profile
            get_cached_profile.clear()
    
    # Get profile stats with caching
    stats = get_cached_stats(user_id)
    
    st.title("👤 My Profile")
    
    # Profile completion progress
    st.progress(stats['completion_percentage'] / 100)
    st.caption(f"Profile {stats['completion_percentage']}% complete ({stats['completed_fields']}/{stats['total_fields']} fields)")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📝 Edit Profile", "👁️ View Profile", "📊 Profile Stats"])
    
    with tab1:
        render_edit_profile(user_id, profile)
    
    with tab2:
        render_view_profile(profile)
    
    with tab3:
        render_profile_stats(stats, profile)


def render_edit_profile(user_id: int, profile: dict):
    """Render profile editing form"""
    
    st.subheader("Edit Your Profile")
    
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Basic Information")
            full_name = st.text_input(
                "Full Name",
                value=profile.get('full_name', '') or '',
                placeholder="John Doe"
            )
            
            username = st.text_input(
                "Username (Public)",
                value=profile.get('username', '') or '',
                placeholder="johndoe",
                help="Unique username for your public profile"
            )
            
            location = st.text_input(
                "Location",
                value=profile.get('location', '') or '',
                placeholder="San Francisco, CA"
            )
            
            preferred_language = st.selectbox(
                "Preferred Language",
                options=["English", "Spanish", "French", "German", "Chinese", "Japanese", "Other"],
                index=0 if not profile.get('preferred_language') else 
                      ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Other"].index(profile.get('preferred_language', 'English'))
            )
        
        with col2:
            st.markdown("### 💼 Career Information")
            experience_level = st.selectbox(
                "Experience Level",
                options=["", "Entry Level", "Junior", "Mid-Level", "Senior", "Lead", "Executive"],
                index=0 if not profile.get('experience_level') else
                      ["", "Entry Level", "Junior", "Mid-Level", "Senior", "Lead", "Executive"].index(profile.get('experience_level', ''))
            )
            
            target_job_role = st.text_input(
                "Target Job Role",
                value=profile.get('target_job_role', '') or '',
                placeholder="Software Engineer"
            )
            
            education = st.text_area(
                "Education",
                value=profile.get('education', '') or '',
                placeholder="BS Computer Science, Stanford University",
                height=100
            )
        
        st.markdown("### 📝 About You")
        bio = st.text_area(
            "Bio",
            value=profile.get('bio', '') or '',
            placeholder="Tell us about yourself...",
            height=150,
            max_chars=500
        )
        
        st.markdown("### 🎯 Skills")
        skills_input = st.text_input(
            "Skills (comma-separated)",
            value=", ".join(profile.get('skills', [])) if profile.get('skills') else '',
            placeholder="Python, JavaScript, React, Node.js"
        )
        
        st.markdown("### 🔗 Social Links")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            linkedin_url = st.text_input(
                "LinkedIn URL",
                value=profile.get('linkedin_url', '') or '',
                placeholder="https://linkedin.com/in/username"
            )
        
        with col4:
            github_url = st.text_input(
                "GitHub URL",
                value=profile.get('github_url', '') or '',
                placeholder="https://github.com/username"
            )
        
        with col5:
            portfolio_url = st.text_input(
                "Portfolio URL",
                value=profile.get('portfolio_url', '') or '',
                placeholder="https://yourportfolio.com"
            )
        
        # Submit buttons
        col_save, col_cancel = st.columns([1, 1])
        
        with col_save:
            submit = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
        
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submit:
            # Validate username if provided
            if username and username != profile.get('username'):
                if not ProfileManager.check_username_available(username, user_id):
                    st.error("❌ Username already taken")
                    return
            
            # Parse skills
            skills_list = [s.strip() for s in skills_input.split(',') if s.strip()]
            
            # Prepare update data
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
                'portfolio_url': portfolio_url,
                'preferred_language': preferred_language
            }
            
            # Update profile
            result = ProfileManager.update_profile(user_id, update_data)
            
            if result['success']:
                # Clear cache after update
                get_cached_profile.clear()
                get_cached_stats.clear()
                st.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                st.error(f"❌ {result['message']}")
        
        if cancel:
            st.rerun()


def render_view_profile(profile: dict):
    """Render profile view (read-only)"""
    
    st.subheader("Profile Overview")
    
    # Profile header
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if profile.get('profile_picture_url'):
            st.image(profile['profile_picture_url'], width=150)
        else:
            st.markdown("### 👤")
            st.caption("No profile picture")
    
    with col2:
        st.markdown(f"## {profile.get('full_name', 'No name set')}")
        if profile.get('username'):
            st.markdown(f"**@{profile['username']}**")
        if profile.get('target_job_role'):
            st.markdown(f"🎯 {profile['target_job_role']}")
        if profile.get('location'):
            st.markdown(f"📍 {profile['location']}")
    
    st.divider()
    
    # About section
    if profile.get('bio'):
        st.markdown("### 📝 About")
        st.write(profile['bio'])
        st.divider()
    
    # Career details
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 💼 Career Details")
        if profile.get('experience_level'):
            st.write(f"**Experience:** {profile['experience_level']}")
        if profile.get('education'):
            st.write(f"**Education:** {profile['education']}")
    
    with col4:
        st.markdown("### 🎯 Skills")
        if profile.get('skills') and len(profile['skills']) > 0:
            for skill in profile['skills']:
                st.markdown(f"- {skill}")
        else:
            st.caption("No skills added yet")
    
    st.divider()
    
    # Social links
    if any([profile.get('linkedin_url'), profile.get('github_url'), profile.get('portfolio_url')]):
        st.markdown("### 🔗 Connect")
        col5, col6, col7 = st.columns(3)
        
        with col5:
            if profile.get('linkedin_url'):
                st.markdown(f"[🔗 LinkedIn]({profile['linkedin_url']})")
        
        with col6:
            if profile.get('github_url'):
                st.markdown(f"[💻 GitHub]({profile['github_url']})")
        
        with col7:
            if profile.get('portfolio_url'):
                st.markdown(f"[🌐 Portfolio]({profile['portfolio_url']})")


def render_profile_stats(stats: dict, profile: dict):
    """Render profile statistics"""
    
    st.subheader("Profile Statistics")
    
    # Completion metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Completion", f"{stats['completion_percentage']}%")
    
    with col2:
        st.metric("Completed Fields", f"{stats['completed_fields']}/{stats['total_fields']}")
    
    with col3:
        st.metric("Skills Added", len(profile.get('skills', [])))
    
    st.divider()
    
    # Missing fields
    if stats.get('missing_fields'):
        st.markdown("### 📋 Complete Your Profile")
        st.write("Add these fields to improve your profile:")
        for field in stats['missing_fields']:
            field_name = field.replace('_', ' ').title()
            st.markdown(f"- {field_name}")
    
    st.divider()
    
    # Profile metadata
    st.markdown("### ℹ️ Profile Information")
    if profile.get('created_at'):
        st.write(f"**Created:** {profile['created_at'].strftime('%B %d, %Y')}")
    if profile.get('updated_at'):
        st.write(f"**Last Updated:** {profile['updated_at'].strftime('%B %d, %Y at %I:%M %p')}")


if __name__ == "__main__":
    render_profile_page()
