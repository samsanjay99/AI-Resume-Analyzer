"""Test dashboard with PostgreSQL"""
from dashboard.dashboard import DashboardManager

print("=" * 60)
print("Dashboard PostgreSQL Test")
print("=" * 60)

dm = DashboardManager()

# Test 1: Quick Stats
print("\n1. Testing quick stats...")
stats = dm.get_quick_stats()
print(f"   ✅ Total Resumes: {stats['Total Resumes']}")
print(f"   ✅ Avg ATS Score: {stats['Avg ATS Score']}")
print(f"   ✅ High Performing: {stats['High Performing']}")
print(f"   ✅ Success Rate: {stats['Success Rate']}")

# Test 2: Resume Metrics
print("\n2. Testing resume metrics...")
metrics = dm.get_resume_metrics()
print(f"   ✅ Metrics retrieved for {len(metrics)} time periods")

# Test 3: Skill Distribution
print("\n3. Testing skill distribution...")
categories, counts = dm.get_skill_distribution()
print(f"   ✅ Found {len(categories)} skill categories")

# Test 4: Weekly Trends
print("\n4. Testing weekly trends...")
dates, submissions = dm.get_weekly_trends()
print(f"   ✅ Weekly data for {len(dates)} days")

# Test 5: Job Category Stats
print("\n5. Testing job category stats...")
categories, rates = dm.get_job_category_stats()
print(f"   ✅ Found {len(categories)} job categories")

# Test 6: Database Stats
print("\n6. Testing database stats...")
db_stats = dm.get_database_stats()
print(f"   ✅ Total resumes: {db_stats['total_resumes']}")
print(f"   ✅ Today's submissions: {db_stats['today_submissions']}")
print(f"   ✅ Storage: {db_stats['storage_size']}")

# Test 7: Admin Logs
print("\n7. Testing admin logs...")
logs = dm.get_admin_logs()
print(f"   ✅ Retrieved {len(logs)} admin log entries")

print("\n" + "=" * 60)
print("✅ All dashboard tests passed!")
print("=" * 60)
