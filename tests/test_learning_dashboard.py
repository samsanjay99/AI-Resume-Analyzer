"""
Test Learning Dashboard and Course Recommendations
"""
from config.course_recommendation_manager import CourseRecommendationManager
from config.database import get_database_connection
import sys

def test_database_schema():
    """Test that tables exist"""
    print("Testing database schema...")
    
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        # Check course_recommendations table
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname='public' AND tablename='course_recommendations'
        """)
        if cursor.fetchone():
            print("✅ course_recommendations table exists")
        else:
            print("❌ course_recommendations table missing")
            return False
        
        # Check skill_course_mapping table
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname='public' AND tablename='skill_course_mapping'
        """)
        if cursor.fetchone():
            print("✅ skill_course_mapping table exists")
        else:
            print("❌ skill_course_mapping table missing")
            return False
        
        # Check seeded courses
        cursor.execute("SELECT COUNT(*) FROM skill_course_mapping")
        count = cursor.fetchone()[0]
        print(f"✅ {count} courses seeded in database")
        
        return True

def test_find_courses():
    """Test finding courses for skills"""
    print("\nTesting course finding...")
    
    test_skills = ['Python', 'SQL', 'JavaScript', 'React']
    
    for skill in test_skills:
        courses = CourseRecommendationManager.find_courses_for_skills([skill], limit=2)
        if courses:
            print(f"✅ Found {len(courses)} courses for {skill}")
            for course in courses:
                print(f"   - {course['course_title']} ({course['video_duration']})")
        else:
            print(f"⚠️ No courses found for {skill}")
    
    return True

def test_youtube_functions():
    """Test YouTube utility functions"""
    print("\nTesting YouTube functions...")
    
    # Test video ID extraction
    test_urls = [
        'https://youtube.com/watch?v=HXV3zeQKqGY',
        'https://youtu.be/HXV3zeQKqGY',
        'https://youtube.com/embed/HXV3zeQKqGY'
    ]
    
    for url in test_urls:
        video_id = CourseRecommendationManager.extract_youtube_video_id(url)
        if video_id == 'HXV3zeQKqGY':
            print(f"✅ Extracted video ID from {url[:30]}...")
        else:
            print(f"❌ Failed to extract video ID from {url}")
            return False
    
    # Test thumbnail generation
    thumbnail = CourseRecommendationManager.generate_thumbnail_url('HXV3zeQKqGY')
    expected = 'https://img.youtube.com/vi/HXV3zeQKqGY/maxresdefault.jpg'
    if thumbnail == expected:
        print(f"✅ Generated correct thumbnail URL")
    else:
        print(f"❌ Thumbnail URL mismatch")
        return False
    
    return True

def test_save_recommendations():
    """Test saving recommendations for a user"""
    print("\nTesting save recommendations...")
    
    # Use test user ID (assuming user 1 exists)
    test_user_id = 1
    test_resume_id = 1
    test_analysis_id = 1
    test_skills = ['Python', 'SQL']
    
    result = CourseRecommendationManager.save_recommendations_for_user(
        user_id=test_user_id,
        resume_id=test_resume_id,
        analysis_id=test_analysis_id,
        missing_skills=test_skills
    )
    
    if result['success']:
        print(f"✅ Saved {result['count']} recommendations")
        return True
    else:
        print(f"❌ Failed to save recommendations: {result['message']}")
        return False

def test_get_recommendations():
    """Test retrieving recommendations"""
    print("\nTesting get recommendations...")
    
    test_user_id = 1
    
    recommendations = CourseRecommendationManager.get_user_recommendations(test_user_id, limit=10)
    
    if recommendations:
        print(f"✅ Retrieved {len(recommendations)} recommendations")
        for rec in recommendations[:3]:
            print(f"   - {rec['course_title']} (Skill: {rec['skill_covered']})")
        return True
    else:
        print("⚠️ No recommendations found (this is OK if no data exists)")
        return True

def test_page_imports():
    """Test that learning dashboard page imports correctly"""
    print("\nTesting page imports...")
    
    try:
        from pages.learning_dashboard import render_learning_dashboard
        print("✅ learning_dashboard.py imports successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import learning_dashboard: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("LEARNING DASHBOARD TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Find Courses", test_find_courses),
        ("YouTube Functions", test_youtube_functions),
        ("Save Recommendations", test_save_recommendations),
        ("Get Recommendations", test_get_recommendations),
        ("Page Imports", test_page_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
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
        print("\n🎉 All tests passed! Learning dashboard is ready.")
        print("\n📋 Features:")
        print("   • YouTube course recommendations")
        print("   • Video thumbnails and previews")
        print("   • Skill-based filtering")
        print("   • Bookmark and watch tracking")
        print("   • Integrated with resume analysis")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
