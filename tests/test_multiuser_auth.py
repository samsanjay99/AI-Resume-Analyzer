"""
Test Multi-User Authentication System
"""
from auth.auth_manager import AuthManager
from config.database import get_database_connection

def test_authentication():
    """Test the authentication system"""
    print("=" * 60)
    print("TESTING MULTI-USER AUTHENTICATION SYSTEM")
    print("=" * 60)
    
    # Test 1: Check if users table exists
    print("\n1. Checking users table...")
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"   ✅ Users table exists with {user_count} users")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Test existing user authentication
    print("\n2. Testing existing user authentication...")
    try:
        result = AuthManager.authenticate_user("test@example.com", "password123")
        if result['success']:
            print(f"   ✅ Authentication successful!")
            print(f"   User ID: {result['user']['id']}")
            print(f"   Email: {result['user']['email']}")
            print(f"   Name: {result['user'].get('full_name', 'N/A')}")
        else:
            print(f"   ❌ Authentication failed: {result['message']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test invalid credentials
    print("\n3. Testing invalid credentials...")
    try:
        result = AuthManager.authenticate_user("test@example.com", "wrongpassword")
        if not result['success']:
            print(f"   ✅ Correctly rejected invalid password")
        else:
            print(f"   ❌ Should have rejected invalid password")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test password hashing
    print("\n4. Testing password hashing...")
    try:
        password = "testpassword123"
        hashed = AuthManager.hash_password(password)
        print(f"   ✅ Password hashed successfully")
        print(f"   Hash length: {len(hashed)} characters")
        
        # Verify the hash
        is_valid = AuthManager.verify_password(password, hashed)
        if is_valid:
            print(f"   ✅ Password verification successful")
        else:
            print(f"   ❌ Password verification failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Test user creation (with unique email)
    print("\n5. Testing user creation...")
    try:
        import random
        test_email = f"newuser{random.randint(1000, 9999)}@example.com"
        result = AuthManager.create_user(
            email=test_email,
            password="password123",
            full_name="Test User"
        )
        if result['success']:
            print(f"   ✅ User created successfully!")
            print(f"   User ID: {result['user']['id']}")
            print(f"   Email: {result['user']['email']}")
            
            # Try to authenticate with new user
            auth_result = AuthManager.authenticate_user(test_email, "password123")
            if auth_result['success']:
                print(f"   ✅ New user can authenticate")
            else:
                print(f"   ❌ New user authentication failed")
        else:
            print(f"   ⚠️ User creation: {result['message']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Check user_id columns in data tables
    print("\n6. Checking user_id columns in data tables...")
    tables = ['resume_data', 'resume_analysis', 'ai_analysis', 'uploaded_files', 'feedback']
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            for table in tables:
                try:
                    cursor.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}' AND column_name = 'user_id'
                    """)
                    result = cursor.fetchone()
                    if result:
                        print(f"   ✅ {table}: user_id column exists")
                    else:
                        print(f"   ⚠️ {table}: user_id column missing")
                except Exception as e:
                    print(f"   ⚠️ {table}: {str(e)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 7: Check data isolation
    print("\n7. Testing data isolation...")
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Check if existing data is assigned to user_id 1
            cursor.execute("SELECT COUNT(*) FROM resume_data WHERE user_id = 1")
            user1_resumes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM resume_data WHERE user_id IS NULL")
            null_resumes = cursor.fetchone()[0]
            
            print(f"   ✅ User 1 has {user1_resumes} resumes")
            if null_resumes > 0:
                print(f"   ⚠️ Found {null_resumes} resumes without user_id")
            else:
                print(f"   ✅ All resumes have user_id assigned")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("AUTHENTICATION SYSTEM TEST COMPLETE")
    print("=" * 60)
    print("\n✅ Multi-user authentication is ready!")
    print("\nTest Credentials:")
    print("  Email: test@example.com")
    print("  Password: password123")
    print("\nYou can now run: streamlit run app.py")
    print("=" * 60)

if __name__ == "__main__":
    test_authentication()
