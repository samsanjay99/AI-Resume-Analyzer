"""
Test User Profile Management System
"""
from config.profile_manager import ProfileManager
from auth.auth_manager import AuthManager

def test_profile_system():
    """Test complete profile system"""
    
    print("🧪 Testing User Profile Management System\n")
    
    # Test 1: Get existing user profile
    print("1️⃣ Testing profile retrieval...")
    test_user_id = 1  # Assuming test user exists
    profile = ProfileManager.get_profile(test_user_id)
    
    if profile:
        print(f"✅ Profile found for user {test_user_id}")
        print(f"   - Full Name: {profile.get('full_name')}")
        print(f"   - Username: {profile.get('username')}")
        print(f"   - Skills: {len(profile.get('skills', []))} skills")
    else:
        print(f"⚠️  No profile found, creating one...")
        result = ProfileManager.create_profile(test_user_id, "Test User")
        if result['success']:
            print(f"✅ Profile created: {result['message']}")
            profile = ProfileManager.get_profile(test_user_id)
        else:
            print(f"❌ Failed to create profile: {result['message']}")
            return
    
    print()
    
    # Test 2: Update profile
    print("2️⃣ Testing profile update...")
    update_data = {
        'bio': 'Software engineer passionate about AI and web development',
        'location': 'San Francisco, CA',
        'experience_level': 'Mid-Level',
        'target_job_role': 'Senior Software Engineer',
        'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'PostgreSQL'],
        'linkedin_url': 'https://linkedin.com/in/testuser',
        'github_url': 'https://github.com/testuser'
    }
    
    result = ProfileManager.update_profile(test_user_id, update_data)
    if result['success']:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")
    
    print()
    
    # Test 3: Get updated profile
    print("3️⃣ Testing updated profile retrieval...")
    updated_profile = ProfileManager.get_profile(test_user_id)
    if updated_profile:
        print("✅ Updated profile retrieved:")
        print(f"   - Bio: {updated_profile.get('bio')[:50]}...")
        print(f"   - Location: {updated_profile.get('location')}")
        print(f"   - Experience: {updated_profile.get('experience_level')}")
        print(f"   - Target Role: {updated_profile.get('target_job_role')}")
        print(f"   - Skills: {', '.join(updated_profile.get('skills', []))}")
    
    print()
    
    # Test 4: Profile completion stats
    print("4️⃣ Testing profile completion stats...")
    stats = ProfileManager.get_profile_stats(test_user_id)
    print(f"✅ Profile completion: {stats['completion_percentage']}%")
    print(f"   - Completed: {stats['completed_fields']}/{stats['total_fields']} fields")
    if stats.get('missing_fields'):
        print(f"   - Missing: {', '.join(stats['missing_fields'])}")
    
    print()
    
    # Test 5: Username availability
    print("5️⃣ Testing username availability...")
    test_username = "testuser123"
    available = ProfileManager.check_username_available(test_username)
    print(f"✅ Username '{test_username}' available: {available}")
    
    print()
    
    # Test 6: Update with username
    print("6️⃣ Testing username update...")
    if available:
        result = ProfileManager.update_profile(test_user_id, {'username': test_username})
        if result['success']:
            print(f"✅ Username set to: {test_username}")
            
            # Test retrieval by username
            profile_by_username = ProfileManager.get_profile_by_username(test_username)
            if profile_by_username:
                print(f"✅ Profile retrieved by username: {profile_by_username.get('full_name')}")
        else:
            print(f"❌ {result['message']}")
    
    print()
    print("=" * 60)
    print("✅ All profile system tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_profile_system()
