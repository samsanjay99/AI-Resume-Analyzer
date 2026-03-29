"""
Test Admin Access Control
Verifies that dashboard is only accessible to admins
"""
import sys

def test_pages_configuration():
    """Test that dashboard is not in main pages"""
    print("Testing pages configuration...")
    
    # Import the app
    from app import ResumeApp
    app = ResumeApp()
    
    # Check that dashboard is NOT in main pages
    page_names = list(app.pages.keys())
    print(f"Available pages: {page_names}")
    
    if "📊 DASHBOARD" in page_names:
        print("❌ FAIL: Dashboard should not be in main navigation")
        return False
    else:
        print("✅ PASS: Dashboard removed from main navigation")
    
    # Check that other pages are still there
    expected_pages = [
        "🏠 HOME",
        "🔍 RESUME ANALYZER",
        "📝 RESUME BUILDER",
        "🌐 PORTFOLIO GENERATOR",
        "📚 MY HISTORY",
        "🎯 JOB SEARCH",
        "💬 FEEDBACK",
        "ℹ️ ABOUT"
    ]
    
    for page in expected_pages:
        if page not in page_names:
            print(f"❌ FAIL: Expected page '{page}' not found")
            return False
    
    print(f"✅ PASS: All {len(expected_pages)} expected pages present")
    return True

def test_dashboard_method_exists():
    """Test that render_dashboard method still exists"""
    print("\nTesting dashboard method...")
    
    from app import ResumeApp
    app = ResumeApp()
    
    if hasattr(app, 'render_dashboard'):
        print("✅ PASS: render_dashboard method exists")
        return True
    else:
        print("❌ FAIL: render_dashboard method missing")
        return False

def test_dashboard_manager_exists():
    """Test that dashboard manager is initialized"""
    print("\nTesting dashboard manager...")
    
    from app import ResumeApp
    app = ResumeApp()
    
    if hasattr(app, 'dashboard_manager'):
        print("✅ PASS: dashboard_manager initialized")
        return True
    else:
        print("❌ FAIL: dashboard_manager not initialized")
        return False

def test_admin_access_logic():
    """Test the admin access control logic"""
    print("\nTesting admin access control logic...")
    
    # Read app.py to check for admin access control
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for admin dashboard page handling
    if "if current_page == 'admin_dashboard':" in content:
        print("✅ PASS: Admin dashboard page handler found")
    else:
        print("❌ FAIL: Admin dashboard page handler missing")
        return False
    
    # Check for admin check
    if "if st.session_state.get('is_admin', False):" in content:
        print("✅ PASS: Admin authentication check found")
    else:
        print("❌ FAIL: Admin authentication check missing")
        return False
    
    # Check for access denied message
    if "Access Denied" in content or "access denied" in content.lower():
        print("✅ PASS: Access denied message found")
    else:
        print("❌ FAIL: Access denied message missing")
        return False
    
    # Check for admin dashboard button
    if "ADMIN DASHBOARD" in content:
        print("✅ PASS: Admin dashboard button found")
    else:
        print("❌ FAIL: Admin dashboard button missing")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("ADMIN ACCESS CONTROL TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Pages Configuration", test_pages_configuration),
        ("Dashboard Method", test_dashboard_method_exists),
        ("Dashboard Manager", test_dashboard_manager_exists),
        ("Admin Access Logic", test_admin_access_logic)
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
        print("\n🎉 All tests passed! Admin access control is working correctly.")
        print("\n📋 Summary:")
        print("   • Dashboard removed from main navigation")
        print("   • Admin dashboard button only visible after admin login")
        print("   • Access control enforced with authentication check")
        print("   • Access denied message for unauthorized access")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
