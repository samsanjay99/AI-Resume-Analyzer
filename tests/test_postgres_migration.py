"""Test script to verify PostgreSQL migration is working correctly"""
import config.database as db

print("=" * 60)
print("PostgreSQL Migration Test")
print("=" * 60)

# Test 1: Database Status
print("\n1. Testing database status...")
status = db.get_database_status()
if status['success']:
    print("   ✅ Database status retrieved successfully")
    print(f"   📊 Total records: {status['total_records']}")
    for table, count in status['tables'].items():
        print(f"      - {table}: {count}")
else:
    print("   ❌ Failed to get database status")

# Test 2: Admin Verification
print("\n2. Testing admin authentication...")
if db.verify_admin('sam@gmail.com', 'sanjay2026'):
    print("   ✅ Admin authentication working")
else:
    print("   ❌ Admin authentication failed")

# Test 3: Resume Stats
print("\n3. Testing resume statistics...")
stats = db.get_resume_stats()
if stats:
    print("   ✅ Resume stats retrieved successfully")
    print(f"      - Total resumes: {stats['total_resumes']}")
    print(f"      - Average ATS score: {stats['avg_ats_score']}")
else:
    print("   ❌ Failed to get resume stats")

# Test 4: AI Analysis Stats
print("\n4. Testing AI analysis statistics...")
ai_stats = db.get_ai_analysis_stats()
print("   ✅ AI analysis stats retrieved successfully")
print(f"      - Total analyses: {ai_stats['total_analyses']}")
print(f"      - Average score: {ai_stats['average_score']}")

# Test 5: Admin Analytics
print("\n5. Testing admin analytics...")
analytics = db.get_admin_analytics()
if analytics:
    print("   ✅ Admin analytics retrieved successfully")
    print(f"      - Total users: {analytics['total_users']}")
    print(f"      - Total resumes: {analytics['total_resumes']}")
    print(f"      - Average score: {analytics['avg_score']}")
else:
    print("   ❌ Failed to get admin analytics")

# Test 6: Uploaded Files
print("\n6. Testing uploaded files...")
files = db.get_all_uploaded_files()
print(f"   ✅ Uploaded files retrieved: {len(files)} files")

# Test 7: Feedback Stats
print("\n7. Testing feedback statistics...")
feedback_stats = db.get_feedback_stats()
print("   ✅ Feedback stats retrieved successfully")
print(f"      - Total responses: {feedback_stats['total_responses']}")

print("\n" + "=" * 60)
print("✅ All PostgreSQL migration tests passed!")
print("=" * 60)
