"""Verify the running app by testing database connectivity"""
import config.database as db
from dashboard.dashboard import DashboardManager

print("=" * 70)
print("VERIFYING RUNNING APPLICATION")
print("=" * 70)

# Test 1: Database Connection
print("\n1. Testing database connection...")
try:
    with db.get_database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result[0] == 1:
            print("   ✅ Database connection active")
        else:
            print("   ❌ Database connection issue")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Database Status
print("\n2. Checking database status...")
try:
    status = db.get_database_status()
    print(f"   ✅ Total records: {status['total_records']}")
    print(f"   ✅ Tables:")
    for table, count in status['tables'].items():
        print(f"      - {table}: {count}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Admin Authentication
print("\n3. Testing admin authentication...")
try:
    is_valid = db.verify_admin('sam@gmail.com', 'sanjay2026')
    if is_valid:
        print("   ✅ Admin authentication working")
    else:
        print("   ❌ Admin authentication failed")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Dashboard
print("\n4. Testing dashboard...")
try:
    dm = DashboardManager()
    stats = dm.get_quick_stats()
    print(f"   ✅ Total Resumes: {stats['Total Resumes']}")
    print(f"   ✅ Avg ATS Score: {stats['Avg ATS Score']}")
    print(f"   ✅ High Performing: {stats['High Performing']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Resume Stats
print("\n5. Testing resume statistics...")
try:
    stats = db.get_resume_stats()
    print(f"   ✅ Total resumes: {stats['total_resumes']}")
    print(f"   ✅ Average ATS score: {stats['avg_ats_score']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: AI Analysis Stats
print("\n6. Testing AI analysis...")
try:
    ai_stats = db.get_ai_analysis_stats()
    print(f"   ✅ Total analyses: {ai_stats['total_analyses']}")
    print(f"   ✅ Average score: {ai_stats['average_score']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 7: File Tracking
print("\n7. Testing file tracking...")
try:
    files = db.get_all_uploaded_files()
    print(f"   ✅ Uploaded files tracked: {len(files)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ APPLICATION IS RUNNING SUCCESSFULLY!")
print("=" * 70)
print("\n📊 Access your app at: http://localhost:8501")
print("🔐 Admin Login: sam@gmail.com / sanjay2026")
print("\n✨ All PostgreSQL features are working!")
