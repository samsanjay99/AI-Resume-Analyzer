"""
User History Page - View all past activities, analyses, and deployments
"""
import streamlit as st
from auth.auth_manager import AuthManager
from config.user_data_manager import UserDataManager
from config.analysis_manager import AnalysisManager
import pandas as pd
from datetime import datetime
import os


def render_user_history():
    """Render comprehensive user history page"""
    
    # Check authentication
    if not AuthManager.is_authenticated():
        st.warning("⚠️ Please log in to view your history")
        return
    
    user_id = AuthManager.get_current_user_id()
    user_name = AuthManager.get_current_user_name()
    
    st.title("📚 My History")
    st.markdown(f"*Complete activity history for {user_name}*")
    
    # Get user statistics
    stats_result = UserDataManager.get_user_statistics(user_id)
    
    if stats_result['success']:
        stats = stats_result['statistics']
        
        # Display key metrics
        st.markdown("### 📊 Overview")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Resumes", stats.get('total_resumes', 0))
        with col2:
            st.metric("Analyses", stats.get('total_analyses', 0))
        with col3:
            st.metric("AI Analyses", stats.get('total_ai_analyses', 0))
        with col4:
            st.metric("Avg Score", f"{stats.get('avg_ats_score', 0)}%")
        with col5:
            st.metric("Deployments", stats.get('total_deployments', 0))
        
        st.markdown("---")
    
    # Tabs for different history sections
    tabs = st.tabs([
        "📝 Resumes", 
        "🔍 Analyses", 
        "🤖 AI Analyses", 
        "🎤 Mock Interviews",
        "🌐 Deployments",
        "📁 Uploaded Files",
        "⏱️ Activity Timeline"
    ])
    
    # Tab 1: Resumes
    with tabs[0]:
        st.subheader("📝 My Resumes")
        resumes_result = UserDataManager.get_user_resumes(user_id)
        
        if resumes_result['success'] and resumes_result['count'] > 0:
            st.write(f"**Total: {resumes_result['count']} resumes**")
            
            for idx, resume in enumerate(resumes_result['resumes']):
                with st.expander(f"📄 {resume['name']} - {resume.get('target_role', 'N/A')} ({resume['created_at'].strftime('%b %d, %Y')})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Name:** {resume['name']}")
                        st.write(f"**Email:** {resume['email']}")
                        st.write(f"**Phone:** {resume['phone']}")
                        st.write(f"**Template:** {resume['template']}")
                    
                    with col2:
                        st.write(f"**Target Role:** {resume.get('target_role', 'N/A')}")
                        st.write(f"**Category:** {resume.get('target_category', 'N/A')}")
                        st.write(f"**Created:** {resume['created_at'].strftime('%B %d, %Y %I:%M %p')}")
                    
                    if resume.get('summary'):
                        st.write(f"**Summary:** {resume['summary'][:200]}...")
                    
                    if resume.get('linkedin'):
                        st.write(f"**LinkedIn:** {resume['linkedin']}")
                    if resume.get('github'):
                        st.write(f"**GitHub:** {resume['github']}")
                    if resume.get('portfolio'):
                        st.write(f"**Portfolio:** {resume['portfolio']}")
        else:
            st.info("No resumes created yet. Visit the Resume Builder to create your first resume!")
    
    # Tab 2: Analyses
    with tabs[1]:
        st.subheader("🔍 Resume Analyses")
        analyses_result = UserDataManager.get_user_analyses(user_id)
        
        if analyses_result['success'] and analyses_result['count'] > 0:
            st.write(f"**Total: {analyses_result['count']} analyses**")
            
            # Create DataFrame for better visualization
            df_data = []
            for analysis in analyses_result['analyses']:
                df_data.append({
                    'Date': analysis['created_at'].strftime('%Y-%m-%d %H:%M'),
                    'Resume': analysis.get('resume_name', 'N/A'),
                    'Role': analysis.get('target_role', 'N/A'),
                    'ATS Score': f"{analysis['ats_score']}%",
                    'Keyword Match': f"{analysis['keyword_match_score']}%",
                    'Format Score': f"{analysis['format_score']}%",
                    'Section Score': f"{analysis['section_score']}%"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Detailed view
            st.markdown("#### Detailed Analysis Reports")
            for idx, analysis in enumerate(analyses_result['analyses']):
                with st.expander(f"📊 Analysis #{idx+1} - {analysis.get('resume_name', 'N/A')} ({analysis['created_at'].strftime('%b %d, %Y')})"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("ATS Score", f"{analysis['ats_score']}%")
                    with col2:
                        st.metric("Keyword Match", f"{analysis['keyword_match_score']}%")
                    with col3:
                        st.metric("Format Score", f"{analysis['format_score']}%")
                    with col4:
                        st.metric("Section Score", f"{analysis['section_score']}%")
                    
                    if analysis.get('missing_skills'):
                        st.write("**Missing Skills:**")
                        st.write(analysis['missing_skills'])
                    
                    if analysis.get('recommendations'):
                        st.write("**Recommendations:**")
                        st.write(analysis['recommendations'])
                    
                    # Add PDF download button ONLY if stored PDF exists
                    st.markdown("---")
                    if analysis.get('pdf_report_path') and os.path.exists(analysis['pdf_report_path']):
                        try:
                            with open(analysis['pdf_report_path'], 'rb') as pdf_file:
                                pdf_data = pdf_file.read()
                                st.download_button(
                                    label="📄 Download Analysis Report (PDF)",
                                    data=pdf_data,
                                    file_name=f"analysis_report_{analysis['id']}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True,
                                    key=f"download_std_{analysis['id']}"
                                )
                        except Exception as e:
                            st.error(f"Error loading PDF: {str(e)}")
                    else:
                        st.info("📄 PDF report not available for this analysis. PDF reports are only available for analyses performed after the latest update.")
        else:
            st.info("No analyses yet. Visit the Resume Analyzer to analyze your resume!")
    
    # Tab 3: AI Analyses
    with tabs[2]:
        st.subheader("🤖 AI-Powered Analyses")
        
        # Get AI analyses from both old and new systems
        ai_analyses_result = UserDataManager.get_user_ai_analyses(user_id)
        new_analyses = AnalysisManager.get_user_all_analyses(user_id)
        
        # Combine and display
        total_ai_analyses = ai_analyses_result['count'] + len(new_analyses)
        
        if total_ai_analyses > 0:
            st.write(f"**Total: {total_ai_analyses} AI analyses**")
            
            # Display new system analyses first (more detailed)
            if new_analyses:
                st.markdown("#### 📊 Detailed AI Analyses (New System)")
                for idx, analysis in enumerate(new_analyses):
                    with st.expander(f"🤖 AI Analysis #{idx+1} - {analysis.get('file_name', 'N/A')} ({analysis['created_at'].strftime('%b %d, %Y')})"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Resume Score", f"{analysis.get('resume_score', 0)}%")
                        with col2:
                            st.metric("Experience", f"{analysis.get('experience_years', 0)} years")
                        with col3:
                            skills_count = len(analysis.get('detected_skills', [])) if isinstance(analysis.get('detected_skills'), list) else 0
                            st.metric("Skills Detected", skills_count)
                        with col4:
                            projects_count = len(analysis.get('projects_detected', [])) if isinstance(analysis.get('projects_detected'), list) else 0
                            st.metric("Projects", projects_count)
                        
                        # Show detailed information
                        if analysis.get('detected_skills'):
                            st.write("**Detected Skills:**")
                            skills = analysis['detected_skills']
                            if isinstance(skills, list):
                                st.write(", ".join(skills[:15]))
                        
                        if analysis.get('education_detected'):
                            st.write(f"**Education:** {analysis['education_detected']}")
                        
                        if analysis.get('analysis_summary'):
                            st.info(f"**Summary:** {analysis['analysis_summary']}")
                        
                        if analysis.get('ai_feedback'):
                            st.success(f"**AI Feedback:** {analysis['ai_feedback']}")
                        
                        # Add PDF download button ONLY if stored PDF exists
                        st.markdown("---")
                        if analysis.get('pdf_report_path') and os.path.exists(analysis['pdf_report_path']):
                            try:
                                with open(analysis['pdf_report_path'], 'rb') as pdf_file:
                                    pdf_data = pdf_file.read()
                                    st.download_button(
                                        label="📄 Download Analysis Report (PDF)",
                                        data=pdf_data,
                                        file_name=f"ai_analysis_{analysis['id']}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True,
                                        key=f"download_ai_new_{analysis['id']}"
                                    )
                            except Exception as e:
                                st.error(f"Error loading PDF: {str(e)}")
                        else:
                            st.info("📄 PDF report not available for this analysis. PDF reports are only available for analyses performed after the latest update.")
            
            # Display old system analyses
            if ai_analyses_result['success'] and ai_analyses_result['count'] > 0:
                st.markdown("#### 🤖 AI Analyses (Legacy System)")
                
                # Create DataFrame
                df_data = []
                for ai_analysis in ai_analyses_result['ai_analyses']:
                    df_data.append({
                        'Date': ai_analysis['created_at'].strftime('%Y-%m-%d %H:%M'),
                        'Resume': ai_analysis.get('resume_name', 'N/A'),
                        'Model': ai_analysis['model_used'],
                        'Score': f"{ai_analysis['resume_score']}%",
                        'Predicted Role': ai_analysis.get('job_role', 'N/A')
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
                
                # Detailed view
                for idx, ai_analysis in enumerate(ai_analyses_result['ai_analyses']):
                    with st.expander(f"🤖 Legacy AI Analysis #{idx+1} - {ai_analysis.get('resume_name', 'N/A')} ({ai_analysis['created_at'].strftime('%b %d, %Y')})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Resume Score", f"{ai_analysis['resume_score']}%")
                        with col2:
                            st.write(f"**Model Used:** {ai_analysis['model_used']}")
                        with col3:
                            st.write(f"**Predicted Role:** {ai_analysis.get('job_role', 'N/A')}")
                        
                        st.write(f"**Analysis Date:** {ai_analysis['created_at'].strftime('%B %d, %Y %I:%M %p')}")
                        
                        # Add PDF download button ONLY if stored PDF exists
                        st.markdown("---")
                        if ai_analysis.get('pdf_report_path') and os.path.exists(ai_analysis['pdf_report_path']):
                            try:
                                with open(ai_analysis['pdf_report_path'], 'rb') as pdf_file:
                                    pdf_data = pdf_file.read()
                                    st.download_button(
                                        label="📄 Download Analysis Report (PDF)",
                                        data=pdf_data,
                                        file_name=f"ai_analysis_{ai_analysis['id']}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True,
                                        key=f"download_ai_legacy_{ai_analysis['id']}"
                                    )
                            except Exception as e:
                                st.error(f"Error loading PDF: {str(e)}")
                        else:
                            st.info("📄 PDF report not available for this analysis. PDF reports are only available for analyses performed after the latest update.")
        else:
            st.info("No AI analyses yet. Try the Smart or Deep Analysis modes!")
    
    # Tab 4: Mock Interviews
    with tabs[3]:
        st.subheader("🎤 Mock Interview History")
        try:
            from pages.mock_interview import render_interview_history
            render_interview_history()
        except Exception as e:
            st.error(f"Could not load interview history: {e}")

    # Tab 5: Deployments
    with tabs[4]:
        st.subheader("🌐 Portfolio Deployments")
        deployments_result = UserDataManager.get_user_deployments(user_id)
        
        if deployments_result['success'] and deployments_result['count'] > 0:
            st.write(f"**Total: {deployments_result['count']} deployments**")
            
            # Create a nice card layout for deployments
            for idx, deployment in enumerate(deployments_result['deployments']):
                # Status color
                status_color = '#4CAF50' if deployment['status'] == 'active' else '#FFA500'
                
                st.markdown(f"""
                <div style='background: rgba(45, 45, 45, 0.9); padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; border-left: 4px solid {status_color};'>
                    <h3 style='color: #4CAF50; margin: 0 0 1rem 0;'>🌐 {deployment['portfolio_name']}</h3>
                    <p style='color: #ddd; margin: 0.5rem 0;'><strong>Status:</strong> <span style='color: {status_color};'>{deployment['status'].upper()}</span></p>
                    <p style='color: #ddd; margin: 0.5rem 0;'><strong>Deployed:</strong> {deployment['deployed_at'].strftime('%B %d, %Y %I:%M %p')}</p>
                    <p style='color: #ddd; margin: 0.5rem 0;'><strong>Site ID:</strong> {deployment['site_id']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if deployment['deployment_url']:
                        st.link_button(
                            "🌐 Visit Live Site", 
                            deployment['deployment_url'], 
                            use_container_width=True
                        )
                
                with col2:
                    if deployment['admin_url']:
                        st.link_button(
                            "⚙️ Manage Site", 
                            deployment['admin_url'], 
                            use_container_width=True
                        )
                
                with col3:
                    if deployment['deployment_url']:
                        # Copy URL button
                        st.code(deployment['deployment_url'], language=None)
                
                # Expandable details
                with st.expander(f"📋 View Full Details"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**Portfolio Name:** {deployment['portfolio_name']}")
                        st.write(f"**Status:** {deployment['status'].upper()}")
                        st.write(f"**Deployed:** {deployment['deployed_at'].strftime('%B %d, %Y %I:%M %p')}")
                    
                    with col_b:
                        if deployment['deployment_url']:
                            st.write(f"**Live URL:**")
                            st.code(deployment['deployment_url'])
                        if deployment['admin_url']:
                            st.write(f"**Admin URL:**")
                            st.code(deployment['admin_url'])
                        st.write(f"**Site ID:** {deployment['site_id']}")
                
                st.markdown("---")
        else:
            st.info("No deployments yet. Visit the Portfolio Generator to create and deploy your portfolio!")
    
    # Tab 6: Uploaded Files
    with tabs[5]:
        st.subheader("📁 Uploaded Files")
        files_result = UserDataManager.get_user_uploaded_files(user_id)
        
        if files_result['success'] and files_result['count'] > 0:
            st.write(f"**Total: {files_result['count']} files**")
            
            # Create DataFrame
            df_data = []
            for file in files_result['files']:
                df_data.append({
                    'Date': file['uploaded_at'].strftime('%Y-%m-%d %H:%M'),
                    'File Name': file['original_name'],
                    'Size (KB)': round(file['file_size'] / 1024, 2),
                    'Type': file['file_type'].split('/')[-1].upper(),
                    'Source': file['upload_source']
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No files uploaded yet.")
    
    # Tab 7: Activity Timeline
    with tabs[6]:
        st.subheader("⏱️ Recent Activity")
        timeline_result = UserDataManager.get_user_activity_timeline(user_id, limit=50)
        
        if timeline_result['success'] and timeline_result['count'] > 0:
            st.write(f"**Showing {timeline_result['count']} recent activities**")
            
            for activity in timeline_result['activities']:
                # Icon based on activity type
                icon = {
                    'Resume Created': '📝',
                    'Analysis Completed': '🔍',
                    'AI Analysis': '🤖',
                    'File Uploaded': '📁'
                }.get(activity['activity_type'], '📌')
                
                # Format timestamp
                time_str = activity['timestamp'].strftime('%b %d, %Y %I:%M %p')
                
                st.markdown(f"""
                <div style='background: rgba(45, 45, 45, 0.5); padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; border-left: 3px solid #4CAF50;'>
                    <p style='margin: 0; color: #4CAF50; font-weight: 600;'>{icon} {activity['activity_type']}</p>
                    <p style='margin: 0; color: #ddd;'>{activity['details']}</p>
                    <p style='margin: 0; color: #888; font-size: 0.85rem;'>{time_str}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No activity yet. Start using the platform to see your activity timeline!")
    
    # Export options
    st.markdown("---")
    st.subheader("📥 Export Your Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Analyses (CSV)", use_container_width=True):
            analyses_result = UserDataManager.get_user_analyses(user_id)
            if analyses_result['success'] and analyses_result['count'] > 0:
                df_data = []
                for analysis in analyses_result['analyses']:
                    df_data.append({
                        'Date': analysis['created_at'],
                        'Resume': analysis.get('resume_name', 'N/A'),
                        'ATS Score': analysis['ats_score'],
                        'Keyword Match': analysis['keyword_match_score'],
                        'Format Score': analysis['format_score'],
                        'Section Score': analysis['section_score']
                    })
                df = pd.DataFrame(df_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    f"my_analyses_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
    
    with col2:
        if st.button("🌐 Export Deployments (CSV)", use_container_width=True):
            deployments_result = UserDataManager.get_user_deployments(user_id)
            if deployments_result['success'] and deployments_result['count'] > 0:
                df_data = []
                for deployment in deployments_result['deployments']:
                    df_data.append({
                        'Date': deployment['deployed_at'],
                        'Portfolio': deployment['portfolio_name'],
                        'URL': deployment['deployment_url'],
                        'Status': deployment['status']
                    })
                df = pd.DataFrame(df_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    f"my_deployments_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
    
    with col3:
        if st.button("⏱️ Export Timeline (CSV)", use_container_width=True):
            timeline_result = UserDataManager.get_user_activity_timeline(user_id, limit=1000)
            if timeline_result['success'] and timeline_result['count'] > 0:
                df_data = []
                for activity in timeline_result['activities']:
                    df_data.append({
                        'Timestamp': activity['timestamp'],
                        'Activity': activity['activity_type'],
                        'Details': activity['details']
                    })
                df = pd.DataFrame(df_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    f"my_activity_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
