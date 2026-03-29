"""Test database performance with connection pooling"""
import time
import config.database as db

print("=" * 70)
print("DATABASE PERFORMANCE TEST")
print("=" * 70)

# Test 1: Multiple database calls
print("\n1. Testing multiple database status calls...")
times = []
for i in range(5):
    start = time.time()
    status = db.get_database_status()
    elapsed = time.time() - start
    times.append(elapsed)
    print(f"   Call {i+1}: {elapsed:.3f} seconds")

avg_time = sum(times) / len(times)
print(f"\n   Average time: {avg_time:.3f} seconds")
print(f"   First call: {times[0]:.3f}s (establishes pool)")
print(f"   Subsequent calls: {sum(times[1:])/len(times[1:]):.3f}s (uses pool + cache)")

# Test 2: Admin verification
print("\n2. Testing admin verification...")
times = []
for i in range(3):
    start = time.time()
    result = db.verify_admin('sam@gmail.com', 'sanjay2026')
    elapsed = time.time() - start
    times.append(elapsed)
    print(f"   Call {i+1}: {elapsed:.3f} seconds - Result: {result}")

avg_time = sum(times) / len(times)
print(f"\n   Average time: {avg_time:.3f} seconds")

# Test 3: Resume stats
print("\n3. Testing resume stats...")
start = time.time()
stats = db.get_resume_stats()
elapsed = time.time() - start
print(f"   Time: {elapsed:.3f} seconds")
print(f"   Total resumes: {stats['total_resumes']}")

print("\n" + "=" * 70)
print("PERFORMANCE IMPROVEMENTS:")
print("- Connection pooling: Reuses connections (faster)")
print("- Caching: Reduces database calls for 30 seconds")
print("- Indexes: Speeds up queries")
print("=" * 70)
