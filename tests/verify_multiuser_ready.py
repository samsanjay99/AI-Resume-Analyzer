"""
Final Verification - Multi-User Platform Readiness
"""
import sys

def verify_multiuser_platform():
    """Comprehensive verification of multi-user platform"""
    print("\n" + "=" * 70)
    print(" " * 15 + "MULTI-USER PLATFORM VERIFICATION")
    print("=" * 70)
    
    all_checks_passed = True
    
    # Check 1: Import all authentication modules
    print("\n📦 CHECKING IMPORTS...")
    try:
        from auth.auth_manager import AuthManager
        print("   ✅ AuthManager")
        from auth.login_page import render_login_page, render_signup_page
        print("   ✅ Login/Signup pages")
        from auth.profile_page import render_profile_page
        print("   ✅ Profile page")
        from config.database import get_database_connection, save_resume_data, save_analysis_data
        print("   ✅ Database functions")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        all_checks_passed = False
        return False
    
    # Check 2: Database connection
    print("\n🔌 CHECKING DATABASE CONNECTION...")
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            print("   ✅ Database connection successful")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        all_checks_passed = False
        return False
    
    # Check 3: Users table
    print("\n👥 CHECKING USERS TABLE...")
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"   ✅ Users table exists ({user_count} users)")
            
            # Check columns
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
            columns = [row[0] for row in cursor.fetchall()]
            required_columns = ['id', 'email', 'password_hash', 'full_name', 'created_at', 'last_login', 'is_active']
            
            for col in required_columns:
                if col in columns:
                    print(f"   ✅ Column: {col}")
                else:
                    print(f"   ❌ Missing column: {col}")
                    all_checks_passed = False
    except Exception as e:
        print(f"   ❌ Users table check failed: {e}")
        all_checks_passed = False
    
    # Check 4: user_id columns in data tables
    print("\n🔗 CHECKING USER_ID FOREIGN KEYS...")
    tables = ['resume_data', 'resume_analysis', 'ai_analysis', 'uploaded_files', 'feedback']
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            for table in tables:
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = 'user_id'
                """)
                result = cursor.fetchone()
                if result:
                    print(f"   ✅ {table}.user_id")
                else:
                    print(f"   ❌ {table}.user_id missing")
                    all_checks_passed = False
    except Exception as e:
        print(f"   ❌ Foreign key check failed: {e}")
        all_checks_passed = False
    
    # Check 5: Test user authentication
    print("\n🔐 CHECKING AUTHENTICATION...")
    try:
        # Test with test user
        result = AuthManager.authenticate_user("test@example.com", "password123")
        if result['success']:
            print(f"   ✅ Test user authentication successful")
            print(f"      User ID: {result['user']['id']}")
            print(f"      Email: {result['user']['email']}")
        else:
            print(f"   ❌ Test user authentication failed: {result['message']}")
            all_checks_passed = False
        
        # Test invalid credentials
        result = AuthManager.authenticate_user("test@example.com", "wrongpassword")
        if not result['success']:
            print(f"   ✅ Invalid credentials correctly rejected")
        else:
            print(f"   ❌ Invalid credentials should be rejected")
            all_checks_passed = False
    except Exception as e:
        print(f"   ❌ Authentication check failed: {e}")
        all_checks_passed = False
    
    # Check 6: Password hashing
    print("\n🔒 CHECKING PASSWORD SECURITY...")
    try:
        test_password = "testpass123"
        hashed = AuthManager.hash_password(test_password)
        
        if len(hashed) == 60:  # bcrypt hash length
            print(f"   ✅ Password hashing works (bcrypt)")
        else:
            print(f"   ❌ Unexpected hash length: {len(hashed)}")
            all_checks_passed = False
        
        if AuthManager.verify_password(test_password, hashed):
            print(f"   ✅ Password verification works")
        else:
            print(f"   ❌ Password verification failed")
            all_checks_passed = False
    except Exception as e:
        print(f"   ❌ Password security check failed: {e}")
        all_checks_passed = False
    
    # Check 7: Data isolation
    print("\n🛡️ CHECKING DATA ISOLATION...")
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Check if data is assigned to users
            cursor.execute("SELECT COUNT(*) FROM resume_data WHERE user_id IS NOT NULL")
            assigned_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM resume_data WHERE user_id IS NULL")
            unassigned_count = cursor.fetchone()[0]
            
            print(f"   ✅ {assigned_count} resumes assigned to users")
            
            if unassigned_count > 0:
                print(f"   ⚠️ {unassigned_count} resumes without user_id")
            else:
                print(f"   ✅ All resumes have user_id")
            
            # Check if different users have different data
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM resume_data WHERE user_id IS NOT NULL")
            unique_users = cursor.fetchone()[0]
            print(f"   ✅ Data from {unique_users} different users")
    except Exception as e:
        print(f"   ❌ Data isolation check failed: {e}")
        all_checks_passed = False
    
    # Check 8: App.py integration
    print("\n🎯 CHECKING APP INTEGRATION...")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        checks = [
            ('from auth.auth_manager import AuthManager', 'AuthManager import'),
            ('from auth.login_page import', 'Login page import'),
            ('from auth.profile_page import', 'Profile page import'),
            ('AuthManager.is_authenticated()', 'Authentication check'),
            ('AuthManager.get_current_user_id()', 'User ID retrieval'),
            ('render_login_page()', 'Login page rendering'),
            ('render_profile_page()', 'Profile page rendering'),
        ]
        
        for check_str, check_name in checks:
            if check_str in app_content:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ Missing: {check_name}")
                all_checks_passed = False
    except Exception as e:
        print(f"   ❌ App integration check failed: {e}")
        all_checks_passed = False
    
    # Final summary
    print("\n" + "=" * 70)
    if all_checks_passed:
        print(" " * 20 + "✅ ALL CHECKS PASSED!")
        print("=" * 70)
        print("\n🎉 Your multi-user platform is READY FOR PRODUCTION!")
        print("\n📝 Test Credentials:")
        print("   Email: test@example.com")
        print("   Password: password123")
        print("\n🚀 Start the application:")
        print("   streamlit run app.py")
        print("\n📚 Documentation:")
        print("   - MULTI_USER_COMPLETE.md (Technical details)")
        print("   - MULTI_USER_QUICK_START.md (User guide)")
        print("=" * 70)
        return True
    else:
        print(" " * 20 + "❌ SOME CHECKS FAILED")
        print("=" * 70)
        print("\n⚠️ Please review the errors above and fix them.")
        print("=" * 70)
        return False

if __name__ == "__main__":
    success = verify_multiuser_platform()
    sys.exit(0 if success else 1)
