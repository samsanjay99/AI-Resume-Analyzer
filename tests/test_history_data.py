"""
Test script to check if history data is being saved correctly
"""
from config.user_data_manager import UserDataManager
from auth.auth_manager import AuthManager

def test_history_data():
    """Test if user history data exists"""
    print("=" * 60)
    print("Testing User History Data")
    print("=" * 60)
    
    # Check if user is authenticated
    print("\n1. Checking authentication...")
    if AuthManager.is_authenticated():
        user_id = AuthManager.get_current_user_id()
        user_name = AuthManager.get_current_user_name()
        print(f"   ✅ Authenticated as: {user_name} (ID: {user_id})")
    else:
        print("   ❌ Not authenticated - using default user")
        user_id = 'default_user'
    
    # Check statistics
    print("\n2. Checking user statistics...")
    stats_result = UserDataManager.get_user_statistics(user_id)
    if stats_result['success']:
        stats = stats_result['statistics']
        print(f"   ✅ Statistics retrieved:")
        print(f"      - Total Resumes: {stats.get('total_resumes', 0)}")
        print(f"      - Total Analyses: {stats.get('total_analyses', 0)}")
        print(f"      - Total AI Analyses: {stats.get('total_ai_analyses', 0)}")
        print(f"      - Total Deployments: {stats.get('total_deployments', 0)}")
        print(f"      - Total Files: {stats.get('total_files', 0)}")
    else:
        print(f"   ❌ Failed to get statistics: {stats_result.get('message')}")
    
    # Check uploaded files
    print("\n3. Checking uploaded files...")
    files_result = UserDataManager.get_user_uploaded_files(user_id)
    if files_result['success']:
        print(f"   ✅ Found {files_result['count']} uploaded files")
        if files_result['count'] > 0:
            for i, file in enumerate(files_result['files'][:3], 1):
                print(f"      {i}. {file['original_name']} - {file['upload_source']}")
    else:
        print(f"   ❌ Failed to get files: {files_result.get('message')}")
    
    # Check deployments
    print("\n4. Checking deployments...")
    deployments_result = UserDataManager.get_user_deployments(user_id)
    if deployments_result['success']:
        print(f"   ✅ Found {deployments_result['count']} deployments")
        if deployments_result['count'] > 0:
            for i, deployment in enumerate(deployments_result['deployments'][:3], 1):
                print(f"      {i}. {deployment['portfolio_name']} - {deployment['status']}")
    else:
        print(f"   ❌ Failed to get deployments: {deployments_result.get('message')}")
    
    # Check activity timeline
    print("\n5. Checking activity timeline...")
    timeline_result = UserDataManager.get_user_activity_timeline(user_id, limit=10)
    if timeline_result['success']:
        print(f"   ✅ Found {timeline_result['count']} activities")
        if timeline_result['count'] > 0:
            for i, activity in enumerate(timeline_result['activities'][:5], 1):
                print(f"      {i}. {activity['activity_type']} - {activity['timestamp'].strftime('%Y-%m-%d %H:%M')}")
    else:
        print(f"   ❌ Failed to get timeline: {timeline_result.get('message')}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    if not AuthManager.is_authenticated():
        print("   ⚠️  You are not logged in. Please log in to see your personal history.")
        print("   ⚠️  Data saved while not logged in goes to 'default_user'")
    
    if stats_result['success']:
        total_items = (stats.get('total_resumes', 0) + 
                      stats.get('total_analyses', 0) + 
                      stats.get('total_files', 0) + 
                      stats.get('total_deployments', 0))
        
        if total_items == 0:
            print("   ⚠️  No data found. Try:")
            print("      1. Upload a resume in Resume Analyzer")
            print("      2. Generate a portfolio in Portfolio Generator")
            print("      3. Deploy a portfolio to Netlify")
        else:
            print(f"   ✅ Found {total_items} total items in your history!")

if __name__ == "__main__":
    test_history_data()
