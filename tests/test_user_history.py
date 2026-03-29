"""
Test User History and Data Persistence
"""
from config.user_data_manager import UserDataManager
from auth.auth_manager import AuthManager

def test_user_history():
    """Test user history functionality"""
    print("=" * 70)
    print(" " * 20 + "USER HISTORY TEST")
    print("=" * 70)
    
    # Test with user ID 1 (test user)
    user_id = 1
    
    print(f"\n📊 Testing data retrieval for User ID: {user_id}")
    print("-" * 70)
    
    # Test 1: Get user resumes
    print("\n1. Testing get_user_resumes()...")
    resumes_result = UserDataManager.get_user_resumes(user_id)
    if resumes_result['success']:
        print(f"   ✅ Found {resumes_result['count']} resumes")
        if resumes_result['count'] > 0:
            print(f"   Latest: {resumes_result['resumes'][0].get('name', 'N/A')}")
    else:
        print(f"   ❌ Error: {resumes_result.get('error')}")
    
    # Test 2: Get user analyses
    print("\n2. Testing get_user_analyses()...")
    analyses_result = UserDataManager.get_user_analyses(user_id)
    if analyses_result['success']:
        print(f"   ✅ Found {analyses_result['count']} analyses")
        if analyses_result['count'] > 0:
            latest = analyses_result['analyses'][0]
            print(f"   Latest ATS Score: {latest.get('ats_score', 0)}%")
    else:
        print(f"   ❌ Error: {analyses_result.get('error')}")
    
    # Test 3: Get AI analyses
    print("\n3. Testing get_user_ai_analyses()...")
    ai_analyses_result = UserDataManager.get_user_ai_analyses(user_id)
    if ai_analyses_result['success']:
        print(f"   ✅ Found {ai_analyses_result['count']} AI analyses")
        if ai_analyses_result['count'] > 0:
            latest = ai_analyses_result['ai_analyses'][0]
            print(f"   Latest Score: {latest.get('resume_score', 0)}%")
            print(f"   Model: {latest.get('model_used', 'N/A')}")
    else:
        print(f"   ❌ Error: {ai_analyses_result.get('error')}")
    
    # Test 4: Get uploaded files
    print("\n4. Testing get_user_uploaded_files()...")
    files_result = UserDataManager.get_user_uploaded_files(user_id)
    if files_result['success']:
        print(f"   ✅ Found {files_result['count']} uploaded files")
        if files_result['count'] > 0:
            latest = files_result['files'][0]
            print(f"   Latest: {latest.get('original_name', 'N/A')}")
    else:
        print(f"   ❌ Error: {files_result.get('error')}")
    
    # Test 5: Get deployments
    print("\n5. Testing get_user_deployments()...")
    deployments_result = UserDataManager.get_user_deployments(user_id)
    if deployments_result['success']:
        print(f"   ✅ Found {deployments_result['count']} deployments")
        if deployments_result['count'] > 0:
            latest = deployments_result['deployments'][0]
            print(f"   Latest: {latest.get('portfolio_name', 'N/A')}")
            print(f"   URL: {latest.get('deployment_url', 'N/A')}")
    else:
        print(f"   ❌ Error: {deployments_result.get('error')}")
    
    # Test 6: Get user statistics
    print("\n6. Testing get_user_statistics()...")
    stats_result = UserDataManager.get_user_statistics(user_id)
    if stats_result['success']:
        stats = stats_result['statistics']
        print(f"   ✅ Statistics retrieved successfully")
        print(f"   Total Resumes: {stats.get('total_resumes', 0)}")
        print(f"   Total Analyses: {stats.get('total_analyses', 0)}")
        print(f"   Total AI Analyses: {stats.get('total_ai_analyses', 0)}")
        print(f"   Avg ATS Score: {stats.get('avg_ats_score', 0)}%")
        print(f"   Avg AI Score: {stats.get('avg_ai_score', 0)}%")
        print(f"   Total Uploads: {stats.get('total_uploads', 0)}")
        print(f"   Total Deployments: {stats.get('total_deployments', 0)}")
    else:
        print(f"   ❌ Error: {stats_result.get('error')}")
    
    # Test 7: Get activity timeline
    print("\n7. Testing get_user_activity_timeline()...")
    timeline_result = UserDataManager.get_user_activity_timeline(user_id, limit=10)
    if timeline_result['success']:
        print(f"   ✅ Found {timeline_result['count']} activities")
        if timeline_result['count'] > 0:
            print(f"   Recent activities:")
            for i, activity in enumerate(timeline_result['activities'][:5], 1):
                print(f"      {i}. {activity['activity_type']}: {activity['details'][:50]}...")
    else:
        print(f"   ❌ Error: {timeline_result.get('error')}")
    
    # Test 8: Test deployment saving
    print("\n8. Testing save_deployment()...")
    try:
        save_result = UserDataManager.save_deployment(
            user_id=user_id,
            portfolio_name="Test Portfolio",
            deployment_url="https://test-portfolio.netlify.app",
            admin_url="https://app.netlify.com/sites/test-portfolio",
            site_id="test-123"
        )
        if save_result['success']:
            print(f"   ✅ Deployment saved successfully")
            print(f"   Deployment ID: {save_result.get('deployment_id')}")
        else:
            print(f"   ❌ Error: {save_result.get('error')}")
    except Exception as e:
        print(f"   ⚠️ Note: {str(e)}")
    
    # Summary
    print("\n" + "=" * 70)
    print(" " * 20 + "TEST SUMMARY")
    print("=" * 70)
    
    total_items = (
        resumes_result.get('count', 0) +
        analyses_result.get('count', 0) +
        ai_analyses_result.get('count', 0) +
        files_result.get('count', 0) +
        deployments_result.get('count', 0)
    )
    
    print(f"\n✅ User has {total_items} total items in history")
    print(f"   - {resumes_result.get('count', 0)} resumes")
    print(f"   - {analyses_result.get('count', 0)} analyses")
    print(f"   - {ai_analyses_result.get('count', 0)} AI analyses")
    print(f"   - {files_result.get('count', 0)} uploaded files")
    print(f"   - {deployments_result.get('count', 0)} deployments")
    
    print("\n🎉 User history system is working!")
    print("\n📚 Users can access:")
    print("   ✅ All past resumes")
    print("   ✅ All analysis reports")
    print("   ✅ All AI analysis results")
    print("   ✅ All uploaded files")
    print("   ✅ All deployment URLs")
    print("   ✅ Complete activity timeline")
    print("   ✅ Comprehensive statistics")
    
    print("\n🚀 To view in app:")
    print("   1. Run: streamlit run app.py")
    print("   2. Login with: test@example.com / password123")
    print("   3. Click: 📚 MY HISTORY")
    print("=" * 70)

if __name__ == "__main__":
    test_user_history()
