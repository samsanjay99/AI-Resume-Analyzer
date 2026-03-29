"""
Authentication Manager for Multi-User System
Handles user registration, login, and session management
"""
import bcrypt
import streamlit as st
from config.database import get_database_connection
from config.profile_manager import ProfileManager
from datetime import datetime

class AuthManager:
    """Manages user authentication and sessions"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def create_user(email: str, password: str, full_name: str = None) -> dict:
        """Create a new user account"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                # Check if user already exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return {"success": False, "message": "Email already registered"}
                
                # Hash password
                password_hash = AuthManager.hash_password(password)
                
                # Create user
                cursor.execute("""
                    INSERT INTO users (email, password_hash, full_name)
                    VALUES (%s, %s, %s)
                    RETURNING id, email, full_name, created_at
                """, (email, password_hash, full_name))
                
                user = cursor.fetchone()
                conn.commit()
                
                # Auto-create profile for new user
                ProfileManager.create_profile(user[0], full_name)
                
                return {
                    "success": True,
                    "message": "Account created successfully",
                    "user": {
                        "id": user[0],
                        "email": user[1],
                        "full_name": user[2],
                        "created_at": user[3]
                    }
                }
        except Exception as e:
            return {"success": False, "message": f"Error creating account: {str(e)}"}
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> dict:
        """Authenticate a user with email and password"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                # Get user by email
                cursor.execute("""
                    SELECT id, email, password_hash, full_name, is_active
                    FROM users
                    WHERE email = %s
                """, (email,))
                
                user = cursor.fetchone()
                
                if not user:
                    return {"success": False, "message": "Invalid email or password"}
                
                user_id, user_email, password_hash, full_name, is_active = user
                
                # Check if account is active
                if not is_active:
                    return {"success": False, "message": "Account is deactivated"}
                
                # Verify password
                if not AuthManager.verify_password(password, password_hash):
                    return {"success": False, "message": "Invalid email or password"}
                
                # Update last login
                cursor.execute("""
                    UPDATE users SET last_login = %s WHERE id = %s
                """, (datetime.now(), user_id))
                conn.commit()
                
                return {
                    "success": True,
                    "message": "Login successful",
                    "user": {
                        "id": user_id,
                        "email": user_email,
                        "full_name": full_name
                    }
                }
        except Exception as e:
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    @staticmethod
    def login_user(user_data: dict):
        """Store user data in session"""
        st.session_state['authenticated'] = True
        st.session_state['user_id'] = user_data['id']
        st.session_state['user_email'] = user_data['email']
        st.session_state['user_name'] = user_data.get('full_name', user_data['email'])
    
    @staticmethod
    def logout_user():
        """Clear user session"""
        st.session_state['authenticated'] = False
        st.session_state['user_id'] = None
        st.session_state['user_email'] = None
        st.session_state['user_name'] = None
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def get_current_user_id() -> int:
        """Get current user ID"""
        return st.session_state.get('user_id')
    
    @staticmethod
    def get_current_user_email() -> str:
        """Get current user email"""
        return st.session_state.get('user_email')
    
    @staticmethod
    def get_current_user_name() -> str:
        """Get current user name"""
        return st.session_state.get('user_name', 'User')
    
    @staticmethod
    def require_authentication():
        """Decorator/middleware to require authentication"""
        if not AuthManager.is_authenticated():
            st.warning("⚠️ Please log in to access this feature")
            st.stop()
    
    @staticmethod
    def get_user_profile(user_id: int) -> dict:
        """Get user profile information"""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, email, full_name, created_at, last_login
                    FROM users
                    WHERE id = %s
                """, (user_id,))
                
                user = cursor.fetchone()
                
                if user:
                    return {
                        "success": True,
                        "user": {
                            "id": user[0],
                            "email": user[1],
                            "full_name": user[2],
                            "created_at": user[3],
                            "last_login": user[4]
                        }
                    }
                else:
                    return {"success": False, "message": "User not found"}
        except Exception as e:
            return {"success": False, "message": f"Error fetching profile: {str(e)}"}
