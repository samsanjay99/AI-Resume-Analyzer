"""
Fix test user password
"""
from auth.auth_manager import AuthManager
from config.database import get_database_connection

def fix_test_user():
    """Update test user password"""
    print("Fixing test user password...")
    
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Hash the password
            password_hash = AuthManager.hash_password("password123")
            
            # Update the test user
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s 
                WHERE email = 'test@example.com'
            """, (password_hash,))
            
            conn.commit()
            
            print("✅ Test user password updated successfully!")
            
            # Test authentication
            result = AuthManager.authenticate_user("test@example.com", "password123")
            if result['success']:
                print("✅ Authentication test successful!")
                print(f"   User ID: {result['user']['id']}")
                print(f"   Email: {result['user']['email']}")
            else:
                print(f"❌ Authentication test failed: {result['message']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_test_user()
