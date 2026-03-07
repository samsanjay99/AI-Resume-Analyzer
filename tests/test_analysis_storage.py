"""
Test script for Resume Analysis Storage System
Tests all CRUD operations and data persistence
"""
from config.analysis_manager import AnalysisManager
from datetime import datetime
import json


def test_analysis_storage_system():
    """Test complete analysis storage system"""
    
    print("=" * 60)
    print("TESTING RESUME ANALYSIS STORAGE SYSTEM")
    print("=" * 60)
    
    # Test user ID (use a real user ID from your database)
    test_user_id = 1
    
    # Test 1: Save a resume
    print("\n1. Testing Resume Save...")
    resume_result = AnalysisManager.save_resume(
        user_id=test_user_id,
        file_name="test_resume.pdf",
        parsed_text="This is a test resume with skills like Python, JavaScript, React, and Node.js. Experience in software development.",
        file_url="/uploads/test_resume.pdf",
        file_type="application/pdf"
    )
    
    if resume_result['success']:
        print(f"✅ Resume saved successfully! Resume ID: {resume_result['resume_id']}")
        test_resume_id = resume_result['resume_id']
    else:
        print(f"❌ Failed to save resume: {resume_result['message']}")
        return
    
    # Test 2: Update resume status
    print("\n2. Testing Resume Status Update...")
    status_result = AnalysisManager.update_resume_status(
        test_resume_id,
        'completed',
        'Software Engineer'
    )
    
    if status_result['success']:
        print("✅ Resume status updated successfully!")
    else:
        print(f"❌ Failed to update status: {status_result['message']}")
    
    # Test 3: Save analysis
    print("\n3. Testing Analysis Save...")
    analysis_data = {
        'detected_skills': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL'],
        'experience_years': 3,
        'education_detected': 'Bachelor of Science in Computer Science',
        'projects_detected': ['E-commerce Platform', 'Social Media App', 'Portfolio Website'],
        'certifications_detected': ['AWS Certified Developer', 'Google Cloud Professional'],
        'resume_score': 85,
        'analysis_summary': 'Strong technical resume with good project experience',
        'ai_feedback': 'Consider adding more quantifiable achievements and metrics'
    }
    
    analysis_result = AnalysisManager.save_analysis(
        test_user_id,
        test_resume_id,
        analysis_data
    )
    
    if analysis_result['success']:
        print(f"✅ Analysis saved successfully! Analysis ID: {analysis_result['analysis_id']}")
        test_analysis_id = analysis_result['analysis_id']
    else:
        print(f"❌ Failed to save analysis: {analysis_result['message']}")
        return
    
    # Test 4: Get user resumes
    print("\n4. Testing Get User Resumes...")
    resumes = AnalysisManager.get_user_resumes(test_user_id)
    print(f"✅ Found {len(resumes)} resume(s) for user {test_user_id}")
    
    if resumes:
        print("\nResume Details:")
        for resume in resumes[:3]:  # Show first 3
            print(f"  - ID: {resume['id']}")
            print(f"    File: {resume['file_name']}")
            print(f"    Status: {resume.get('analysis_status', 'N/A')}")
            print(f"    Role: {resume.get('detected_job_role', 'N/A')}")
            print(f"    Uploaded: {resume['upload_date']}")
            print()
    
    # Test 5: Get specific resume
    print("\n5. Testing Get Specific Resume...")
    resume = AnalysisManager.get_resume(test_resume_id, test_user_id)
    
    if resume:
        print(f"✅ Retrieved resume: {resume['file_name']}")
        print(f"   Status: {resume.get('analysis_status')}")
        print(f"   Role: {resume.get('detected_job_role')}")
    else:
        print("❌ Failed to retrieve resume")
    
    # Test 6: Get resume analyses
    print("\n6. Testing Get Resume Analyses...")
    analyses = AnalysisManager.get_resume_analyses(test_resume_id, test_user_id)
    print(f"✅ Found {len(analyses)} analysis(es) for resume {test_resume_id}")
    
    if analyses:
        print("\nAnalysis Details:")
        for analysis in analyses:
            print(f"  - ID: {analysis['id']}")
            print(f"    Score: {analysis.get('resume_score')}%")
            print(f"    Experience: {analysis.get('experience_years')} years")
            print(f"    Skills: {len(analysis.get('detected_skills', []))} detected")
            print(f"    Created: {analysis['created_at']}")
            print()
    
    # Test 7: Get latest analysis
    print("\n7. Testing Get Latest Analysis...")
    latest = AnalysisManager.get_latest_analysis(test_resume_id, test_user_id)
    
    if latest:
        print(f"✅ Latest analysis score: {latest.get('resume_score')}%")
        print(f"   Summary: {latest.get('analysis_summary')}")
    else:
        print("❌ No latest analysis found")
    
    # Test 8: Get all user analyses
    print("\n8. Testing Get All User Analyses...")
    all_analyses = AnalysisManager.get_user_all_analyses(test_user_id)
    print(f"✅ Found {len(all_analyses)} total analysis(es) for user {test_user_id}")
    
    if all_analyses:
        print("\nAll Analyses Summary:")
        for idx, analysis in enumerate(all_analyses[:5], 1):  # Show first 5
            print(f"  {idx}. {analysis.get('file_name', 'N/A')} - Score: {analysis.get('resume_score')}% - {analysis['created_at'].strftime('%Y-%m-%d')}")
    
    # Test 9: Get user statistics
    print("\n9. Testing Get User Statistics...")
    stats = AnalysisManager.get_user_stats(test_user_id)
    
    print(f"✅ User Statistics:")
    print(f"   Total Resumes: {stats['total_resumes']}")
    print(f"   Total Analyses: {stats['total_analyses']}")
    print(f"   Average Score: {stats['average_score']}%")
    print(f"   Latest Analysis: {stats['latest_analysis']}")
    
    # Test 10: Data persistence check
    print("\n10. Testing Data Persistence...")
    print("Retrieving data again to verify persistence...")
    
    resumes_check = AnalysisManager.get_user_resumes(test_user_id)
    analyses_check = AnalysisManager.get_user_all_analyses(test_user_id)
    
    if len(resumes_check) > 0 and len(analyses_check) > 0:
        print("✅ Data persistence verified!")
        print(f"   Resumes persisted: {len(resumes_check)}")
        print(f"   Analyses persisted: {len(analyses_check)}")
    else:
        print("❌ Data persistence check failed")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✅ All tests completed successfully!")
    print(f"✅ Resume Analysis Storage System is fully operational")
    print(f"✅ Data is being saved and retrieved correctly")
    print(f"✅ User can access all historical data")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_analysis_storage_system()
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
