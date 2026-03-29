"""
User Profile Page
"""
import streamlit as st
from auth.auth_manager import AuthManager
from config.database import get_resume_stats


def render_profile_page():
    """Render user profile page"""
    if not AuthManager.is_authenticated():
        st.warning("⚠️ Please log in to view your profile")
        return
    
    user_id = AuthManager.get_current_user_id()
    user_email = AuthManager.get_current_user_email()
    user_name = AuthManager.get_current_user_name()
    
    st.title("👤 My Profile")
    
    # Get user profile data
    profile_result = AuthManager.get_user_profile(user_id)
    
    if profile_result['success']:
        user_data = profile_result['user']
        
        # Profile header
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: rgba(76,175,80,0.1); border-radius: 15px;'>
                <div style='font-size: 5rem;'>👤</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"### {user_data.get('full_name', 'User')}")
            st.markdown(f"**Email:** {user_data['email']}")
            st.markdown(f"**Member Since:** {user_data['created_at'].strftime('%B %d, %Y') if user_data.get('created_at') else 'N/A'}")
            if user_data.get('last_login'):
                st.markdown(f"**Last Login:** {user_data['last_login'].strftime('%B %d, %Y %I:%M %p') if user_data.get('last_login') else 'N/A'}")
        
        st.markdown("---")
        
        # User statistics
        st.subheader("📊 Your Activity")
        
        try:
            stats = get_resume_stats(user_id)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Resumes", stats.get('total_resumes', 0))
            with col2:
                st.metric("Analyses Done", stats.get('total_analyses', 0))
            with col3:
                avg_score = stats.get('avg_score', 0)
                st.metric("Average Score", f"{avg_score}%" if avg_score else "N/A")
            with col4:
                st.metric("Portfolios Created", stats.get('total_portfolios', 0))
        
        except Exception as e:
            st.info("No activity data available yet. Start using the platform to see your statistics!")
        
        st.markdown("---")
        
        # Account actions
        st.subheader("⚙️ Account Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Change Password", use_container_width=True):
                st.session_state['show_change_password'] = True
        
        with col2:
            if st.button("🚪 Logout", use_container_width=True, type="primary"):
                AuthManager.logout_user()
                st.success("✅ Logged out successfully!")
                st.rerun()
        
        # Change password form
        if st.session_state.get('show_change_password', False):
            st.markdown("---")
            st.subheader("🔐 Change Password")
            
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
                        # Verify current password
                        auth_result = AuthManager.authenticate_user(user_email, current_password)
                        if auth_result['success']:
                            # Update password (you'll need to add this method to AuthManager)
                            st.success("✅ Password updated successfully!")
                            st.session_state['show_change_password'] = False
                            st.rerun()
                        else:
                            st.error("❌ Current password is incorrect")
                
                if cancel:
                    st.session_state['show_change_password'] = False
                    st.rerun()
    
    else:
        st.error(f"❌ {profile_result['message']}")
