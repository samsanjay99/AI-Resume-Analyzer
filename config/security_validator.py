"""
Security Validation Layer
Implements input validation, SQL injection protection, and secure practices
"""
import re
import html
import logging
from typing import Any, Optional, Dict
from email.utils import parseaddr

logger = logging.getLogger(__name__)

# ============================================================================
# INPUT VALIDATION
# ============================================================================

class InputValidator:
    """Validate and sanitize user inputs"""
    
    # Regex patterns for validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?1?\d{9,15}$')
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    # Dangerous SQL keywords
    SQL_KEYWORDS = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC', 'EXECUTE',
        'SCRIPT', 'UNION', 'SELECT', '--', ';--', '/*', '*/',
        'xp_', 'sp_', 'DECLARE', 'CAST', 'CONVERT'
    ]
    
    @classmethod
    def validate_email(cls, email: str) -> tuple[bool, Optional[str]]:
        """
        Validate email address
        Returns: (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        email = email.strip().lower()
        
        if len(email) > 254:
            return False, "Email is too long"
        
        if not cls.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        # Additional check using email.utils
        name, addr = parseaddr(email)
        if addr != email:
            return False, "Invalid email format"
        
        return True, None
    
    @classmethod
    def validate_phone(cls, phone: str) -> tuple[bool, Optional[str]]:
        """
        Validate phone number
        Returns: (is_valid, error_message)
        """
        if not phone:
            return True, None  # Phone is optional
        
        # Remove common separators
        phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
        
        if not cls.PHONE_PATTERN.match(phone_clean):
            return False, "Invalid phone number format"
        
        return True, None
    
    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, Optional[str]]:
        """
        Validate URL
        Returns: (is_valid, error_message)
        """
        if not url:
            return True, None  # URL is optional
        
        url = url.strip()
        
        if len(url) > 2048:
            return False, "URL is too long"
        
        if not cls.URL_PATTERN.match(url):
            return False, "Invalid URL format"
        
        return True, None
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = 10000) -> str:
        """
        Sanitize text input to prevent XSS and injection attacks
        """
        if not text:
            return ""
        
        # Truncate to max length
        text = text[:max_length]
        
        # HTML escape to prevent XSS
        text = html.escape(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        return text.strip()
    
    @classmethod
    def check_sql_injection(cls, text: str) -> tuple[bool, Optional[str]]:
        """
        Check for potential SQL injection attempts
        Returns: (is_safe, warning_message)
        """
        if not text:
            return True, None
        
        text_upper = text.upper()
        
        for keyword in cls.SQL_KEYWORDS:
            if keyword in text_upper:
                logger.warning(f"Potential SQL injection detected: {keyword}")
                return False, f"Input contains potentially dangerous content: {keyword}"
        
        return True, None
    
    @classmethod
    def validate_file_upload(cls, filename: str, allowed_extensions: list) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        Returns: (is_valid, error_message)
        """
        if not filename:
            return False, "Filename is required"
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            logger.warning(f"Path traversal attempt detected: {filename}")
            return False, "Invalid filename"
        
        # Check file extension
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in allowed_extensions:
            return False, f"File type .{ext} not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        # Check filename length
        if len(filename) > 255:
            return False, "Filename is too long"
        
        return True, None
    
    @classmethod
    def validate_password(cls, password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password is too long"
        
        # Check for at least one letter and one number
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        
        if not (has_letter and has_number):
            return False, "Password must contain both letters and numbers"
        
        return True, None


# ============================================================================
# SECURE DATABASE OPERATIONS
# ============================================================================

class SecureDBOperations:
    """Secure database operation helpers"""
    
    @staticmethod
    def sanitize_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize query parameters before database operations
        """
        sanitized = {}
        
        for key, value in params.items():
            if isinstance(value, str):
                # Check for SQL injection
                is_safe, warning = InputValidator.check_sql_injection(value)
                if not is_safe:
                    logger.error(f"SQL injection attempt in parameter '{key}': {value}")
                    raise ValueError(f"Invalid input in {key}")
                
                # Sanitize the value
                sanitized[key] = InputValidator.sanitize_text(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def validate_user_input(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate user input data before processing
        Returns: (is_valid, error_message)
        """
        # Validate email if present
        if 'email' in data:
            is_valid, error = InputValidator.validate_email(data['email'])
            if not is_valid:
                return False, error
        
        # Validate phone if present
        if 'phone' in data:
            is_valid, error = InputValidator.validate_phone(data['phone'])
            if not is_valid:
                return False, error
        
        # Validate URLs if present
        for url_field in ['linkedin', 'github', 'portfolio']:
            if url_field in data and data[url_field]:
                is_valid, error = InputValidator.validate_url(data[url_field])
                if not is_valid:
                    return False, f"{url_field.capitalize()}: {error}"
        
        return True, None


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    _call_history: Dict[str, list] = {}
    
    @classmethod
    def check_rate_limit(cls, key: str, max_calls: int = 10, window_seconds: int = 60) -> tuple[bool, Optional[str]]:
        """
        Check if rate limit is exceeded
        Args:
            key: Identifier for the rate limit (e.g., user_id, ip_address)
            max_calls: Maximum number of calls allowed
            window_seconds: Time window in seconds
        Returns: (is_allowed, error_message)
        """
        import time
        
        current_time = time.time()
        
        # Initialize history for this key
        if key not in cls._call_history:
            cls._call_history[key] = []
        
        # Remove old entries outside the time window
        cls._call_history[key] = [
            timestamp for timestamp in cls._call_history[key]
            if current_time - timestamp < window_seconds
        ]
        
        # Check if limit exceeded
        if len(cls._call_history[key]) >= max_calls:
            return False, f"Rate limit exceeded. Maximum {max_calls} calls per {window_seconds} seconds."
        
        # Add current call
        cls._call_history[key].append(current_time)
        
        return True, None


# ============================================================================
# ENVIRONMENT VARIABLE SECURITY
# ============================================================================

class SecureEnvManager:
    """Manage environment variables securely"""
    
    REQUIRED_VARS = [
        'DATABASE_URL',
        'GOOGLE_API_KEY',
        'NETLIFY_TOKEN'
    ]
    
    @classmethod
    def validate_env_vars(cls) -> tuple[bool, list]:
        """
        Validate that required environment variables are set
        Returns: (all_present, missing_vars)
        """
        import os
        
        missing = []
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                missing.append(var)
                logger.warning(f"Missing environment variable: {var}")
        
        return len(missing) == 0, missing
    
    @classmethod
    def mask_sensitive_data(cls, text: str) -> str:
        """
        Mask sensitive data in logs
        """
        # Mask API keys
        text = re.sub(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_-]+)', r'\1***MASKED***', text, flags=re.IGNORECASE)
        
        # Mask tokens
        text = re.sub(r'(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_-]+)', r'\1***MASKED***', text, flags=re.IGNORECASE)
        
        # Mask passwords
        text = re.sub(r'(password["\']?\s*[:=]\s*["\']?)([^\s"\']+)', r'\1***MASKED***', text, flags=re.IGNORECASE)
        
        return text
