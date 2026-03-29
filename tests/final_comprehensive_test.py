"""Final comprehensive test to catch any potential issues"""
import sys
import traceback

def test_module(name, test_func):
    """Test a module and catch any errors"""
    try:
        test_func()
        print(f"✅ {name}")
        return True
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        traceback.print_exc()
        return False

print("=" * 70)
print("FINAL COMPREHENSIVE TEST - PostgreSQL Migration")
print("=" * 70)

all_passed = True

# Test 1: Database Module Import
def test_db_import():
    import config.database as db
    assert hasattr(db, 'get_database_connection')
    assert hasattr(db, 'init_database')
    assert hasattr(db, 'save_resume_data')

all_passed &= test_module("1. Database module import", test_db_import)

# Test 2: Database Connection
def test_db_connection():
    import config.database as db
    with db.get_database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1

all_passed &= test_module("2. Database connection", test_db_connection)

# Test 3: Database Functions
def test_db_functions():
    import config.database as db
    status = db.get_database_status()
    assert status['success'] == True
    assert 'total_records' in status
    
    stats = db.get_resume_stats()
    assert 'total_resumes' in stats
    
    admin_valid = db.verify_admin('sam@gmail.com', 'sanjay2026')
    assert admin_valid == True

all_passed &= test_module("3. Database functions", test_db_functions)

# Test 4: Dashboard Module Import
def test_dashboard_import():
    from dashboard.dashboard import DashboardManager
    dm = DashboardManager()
    assert hasattr(dm, 'get_quick_stats')
    assert hasattr(dm, 'get_resume_metrics')

all_passed &= test_module("4. Dashboard module import", test_dashboard_import)

# Test 5: Dashboard Functions
def test_dashboard_functions():
    from dashboard.dashboard import DashboardManager
    dm = DashboardManager()
    
    stats = dm.get_quick_stats()
    assert 'Total Resumes' in stats
    
    metrics = dm.get_resume_metrics()
    assert 'Today' in metrics
    assert 'All Time' in metrics
    
    categories, counts = dm.get_skill_distribution()
    assert isinstance(categories, list)
    assert isinstance(counts, list)

all_passed &= test_module("5. Dashboard functions", test_dashboard_functions)

# Test 6: App Module Import
def test_app_import():
    import app
    # Just verify it imports without errors
    assert app is not None

all_passed &= test_module("6. App module import", test_app_import)

# Test 7: Data Integrity
def test_data_integrity():
    import config.database as db
    
    # Check all tables exist and have data
    status = db.get_database_status()
    tables = status['tables']
    
    assert tables['resume_data'] > 0, "resume_data should have records"
    assert tables['admin'] > 0, "admin should have records"
    assert tables['ai_analysis'] > 0, "ai_analysis should have records"

all_passed &= test_module("7. Data integrity", test_data_integrity)

# Test 8: PostgreSQL-specific features
def test_postgres_features():
    import config.database as db
    with db.get_database_connection() as conn:
        cursor = conn.cursor()
        
        # Test PostgreSQL-specific syntax
        cursor.execute("SELECT CURRENT_DATE")
        assert cursor.fetchone() is not None
        
        # Test parameterized queries
        cursor.execute("SELECT COUNT(*) FROM resume_data WHERE id > %s", (0,))
        count = cursor.fetchone()[0]
        assert count >= 0

all_passed &= test_module("8. PostgreSQL-specific features", test_postgres_features)

# Test 9: No SQLite remnants
def test_no_sqlite():
    import config.database as db
    import inspect
    
    source = inspect.getsource(db)
    assert 'sqlite3' not in source, "Should not import sqlite3"
    assert 'sqlite_master' not in source, "Should not reference sqlite_master"
    assert '?' not in source or source.count('?') < 5, "Should not use ? placeholders extensively"

all_passed &= test_module("9. No SQLite remnants", test_no_sqlite)

# Test 10: Environment Configuration
def test_env_config():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv('DATABASE_URL')
    assert db_url is not None, "DATABASE_URL should be set"
    assert 'postgresql' in db_url, "DATABASE_URL should be PostgreSQL"
    assert 'neon' in db_url, "DATABASE_URL should point to Neon"

all_passed &= test_module("10. Environment configuration", test_env_config)

print("\n" + "=" * 70)
if all_passed:
    print("✅ ALL TESTS PASSED - NO ISSUES FOUND!")
    print("=" * 70)
    print("\n🎉 Your application is ready for production!")
    print("   Run: streamlit run app.py")
    sys.exit(0)
else:
    print("❌ SOME TESTS FAILED - PLEASE REVIEW ERRORS ABOVE")
    print("=" * 70)
    sys.exit(1)
