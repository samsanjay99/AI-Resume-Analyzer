"""
Test Enhanced Dashboard Features
Tests the new multi-user dashboard features and SSL connection fixes
"""
from dashboard.dashboard import DashboardManager
from config.database import get_database_connection
import sys

def test_connection_retry():
    """Test the retry logic for database connections"""
    print("Testing connection retry logic...")
    dashboard = DashboardManager()
    
    # Test execute_with_retry
    def test_query():
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return cursor.fetchone()[0]
    
    result = dashboard.execute_with_retry(test_query)
    if result == 1:
        print("✅ Connection retry logic working")
        return True
    else:
        print("❌ Connection retry logic failed")
        return False

def test_quick_stats():
    """Test get_quick_stats with retry logic"""
    print("\nTesting quick stats with retry logic...")
    dashboard = DashboardManager()
    
    try:
        stats = dashboard.get_quick_stats()
        if stats:
            print("✅ Quick stats retrieved successfully")
            print(f"   Total Resumes: {stats.get('Total Resumes', 'N/A')}")
            print(f"   Avg ATS Score: {stats.get('Avg ATS Score', 'N/A')}")
            return True
        else:
            print("⚠️ Quick stats returned empty")
            return False
    except Exception as e:
        print(f"❌ Quick stats failed: {e}")
        return False

def test_user_management():
    """Test multi-user management features"""
    print("\nTesting user management features...")
    dashboard = DashboardManager()
    
    try:
        users = dashboard.get_all_users_stats()
        print(f"✅ Retrieved {len(users)} users")
        if users:
            print(f"   Sample user: {users[0].get('email', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ User management failed: {e}")
        return False

def test_system_analytics():
    """Test system-wide analytics"""
    print("\nTesting system analytics...")
    dashboard = DashboardManager()
    
    try:
        stats = dashboard.get_system_wide_stats()
        if stats:
            print("✅ System analytics retrieved successfully")
            print(f"   Total Users: {stats.get('total_users', 0)}")
            print(f"   Active Users: {stats.get('active_users', 0)}")
            print(f"   Total Resumes: {stats.get('total_resumes', 0)}")
            print(f"   Total Analyses: {stats.get('total_standard_analyses', 0) + stats.get('total_ai_analyses', 0)}")
            return True
        else:
            print("⚠️ System analytics returned empty")
            return False
    except Exception as e:
        print(f"❌ System analytics failed: {e}")
        return False

def test_engagement_metrics():
    """Test user engagement metrics"""
    print("\nTesting engagement metrics...")
    dashboard = DashboardManager()
    
    try:
        metrics = dashboard.get_user_engagement_metrics()
        if metrics:
            print("✅ Engagement metrics retrieved successfully")
            if metrics.get('activity_distribution'):
                print(f"   Activity levels: {len(metrics['activity_distribution'])} categories")
            if metrics.get('top_users'):
                print(f"   Top users: {len(metrics['top_users'])} users")
            return True
        else:
            print("⚠️ Engagement metrics returned empty")
            return False
    except Exception as e:
        print(f"❌ Engagement metrics failed: {e}")
        return False

def test_resume_data_with_retry():
    """Test resume data retrieval with retry logic"""
    print("\nTesting resume data with retry logic...")
    dashboard = DashboardManager()
    
    try:
        data = dashboard.get_resume_data()
        print(f"✅ Retrieved {len(data)} resume records")
        return True
    except Exception as e:
        print(f"❌ Resume data retrieval failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ENHANCED DASHBOARD TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Connection Retry", test_connection_retry),
        ("Quick Stats", test_quick_stats),
        ("User Management", test_user_management),
        ("System Analytics", test_system_analytics),
        ("Engagement Metrics", test_engagement_metrics),
        ("Resume Data Retry", test_resume_data_with_retry)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Dashboard is ready for multi-user use.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
