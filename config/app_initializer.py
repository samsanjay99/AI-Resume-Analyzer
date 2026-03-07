"""
Application Initialization and Optimization
Handles startup, caching, and performance optimization
"""
import streamlit as st
import logging
import time
from typing import Optional
from config.performance_optimizer import (
    LazyLoader, PerformanceMonitor, preload_essential_data, clear_cache
)
from config.security_validator import SecureEnvManager, InputValidator

logger = logging.getLogger(__name__)

# ============================================================================
# SINGLETON INSTANCES (Lazy Loaded)
# ============================================================================

def get_ai_analyzer():
    """Get or create AI analyzer instance (lazy loaded)"""
    from utils.ai_resume_analyzer import AIResumeAnalyzer
    return LazyLoader.get_instance('ai_analyzer', AIResumeAnalyzer)


def get_resume_builder():
    """Get or create resume builder instance (lazy loaded)"""
    from utils.resume_builder import ResumeBuilder
    return LazyLoader.get_instance('resume_builder', ResumeBuilder)


def get_resume_analyzer():
    """Get or create resume analyzer instance (lazy loaded)"""
    from utils.resume_analyzer import ResumeAnalyzer
    return LazyLoader.get_instance('resume_analyzer', ResumeAnalyzer)


def get_portfolio_generator():
    """Get or create portfolio generator instance (lazy loaded)"""
    from utils.portfolio_generator import PortfolioGenerator
    return LazyLoader.get_instance('portfolio_generator', PortfolioGenerator)


def get_dashboard_manager():
    """Get or create dashboard manager instance (lazy loaded)"""
    from dashboard.dashboard import DashboardManager
    return LazyLoader.get_instance('dashboard_manager', DashboardManager)


def get_feedback_manager():
    """Get or create feedback manager instance (lazy loaded)"""
    from feedback.feedback import FeedbackManager
    return LazyLoader.get_instance('feedback_manager', FeedbackManager)


# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

@PerformanceMonitor.measure_time
def initialize_app():
    """Initialize application with optimizations"""
    
    # Check if already initialized
    if st.session_state.get('app_initialized', False):
        return
    
    logger.info("🚀 Initializing Smart Resume AI...")
    start_time = time.time()
    
    try:
        # Step 1: Validate environment variables
        logger.info("🔐 Validating environment variables...")
        all_present, missing = SecureEnvManager.validate_env_vars()
        if not all_present:
            logger.warning(f"⚠️  Missing environment variables: {', '.join(missing)}")
            st.session_state['missing_env_vars'] = missing
        
        # Step 2: Initialize database
        logger.info("💾 Initializing database...")
        from config.database import init_database
        init_database()
        
        # Step 3: Preload essential data
        logger.info("📦 Preloading essential data...")
        preload_essential_data()
        
        # Step 4: Initialize authentication
        logger.info("🔑 Initializing authentication...")
        from auth.auth_manager import AuthManager
        AuthManager.initialize()
        
        # Mark as initialized
        st.session_state['app_initialized'] = True
        
        init_time = time.time() - start_time
        logger.info(f"✅ Application initialized in {init_time:.2f}s")
        
    except Exception as e:
        logger.error(f"❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        st.session_state['init_error'] = str(e)


# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def init_session_state():
    """Initialize session state variables"""
    
    # Authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
    # Page state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Performance tracking
    if 'page_loads' not in st.session_state:
        st.session_state.page_loads = 0
    
    st.session_state.page_loads += 1


# ============================================================================
# ERROR HANDLING
# ============================================================================

def handle_initialization_error():
    """Display initialization error to user"""
    if 'init_error' in st.session_state:
        st.error(f"⚠️ Application initialization error: {st.session_state.init_error}")
        st.info("Please check your configuration and try refreshing the page.")
        return True
    return False


def display_missing_env_vars():
    """Display warning for missing environment variables"""
    if 'missing_env_vars' in st.session_state:
        missing = st.session_state.missing_env_vars
        
        with st.expander("⚠️ Configuration Warning", expanded=False):
            st.warning(f"Missing environment variables: {', '.join(missing)}")
            st.info("""
            Some features may not work without proper configuration:
            
            - **DATABASE_URL**: Required for data persistence
            - **GOOGLE_API_KEY**: Required for AI analysis features
            - **NETLIFY_TOKEN**: Required for portfolio hosting
            
            Add these to your `.env` file or Streamlit Cloud secrets.
            """)


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

def display_performance_metrics():
    """Display performance metrics (admin only)"""
    from auth.auth_manager import AuthManager
    
    if not AuthManager.is_admin():
        return
    
    with st.sidebar.expander("⚡ Performance Metrics", expanded=False):
        st.metric("Page Loads", st.session_state.get('page_loads', 0))
        
        # Cache statistics
        cache_size = len([k for k in st.session_state.keys() if not k.startswith('_')])
        st.metric("Cache Entries", cache_size)
        
        # Clear cache button
        if st.button("🗑️ Clear Cache", key="clear_cache_btn"):
            clear_cache()
            st.success("Cache cleared!")
            st.rerun()


# ============================================================================
# HEALTH CHECK
# ============================================================================

def check_system_health() -> dict:
    """Check system health and return status"""
    health = {
        'database': False,
        'ai_service': False,
        'file_system': False,
        'overall': False
    }
    
    try:
        # Check database
        from config.database import get_database_connection
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            health['database'] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    try:
        # Check AI service
        import os
        health['ai_service'] = bool(os.getenv('GOOGLE_API_KEY') or os.getenv('OPENROUTER_API_KEY'))
    except Exception as e:
        logger.error(f"AI service health check failed: {e}")
    
    try:
        # Check file system
        import tempfile
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            tmp.write(b'test')
            health['file_system'] = True
    except Exception as e:
        logger.error(f"File system health check failed: {e}")
    
    # Overall health
    health['overall'] = all([health['database'], health['ai_service'], health['file_system']])
    
    return health


# ============================================================================
# STARTUP OPTIMIZATION
# ============================================================================

def optimize_startup():
    """Apply startup optimizations"""
    
    # Set Streamlit configuration for better performance
    import os
    
    # Disable file watcher in production
    if not os.getenv('STREAMLIT_DEV_MODE'):
        os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
    
    # Increase max message size for large data
    os.environ['STREAMLIT_SERVER_MAX_MESSAGE_SIZE'] = '200'
    
    # Enable faster reruns
    os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'false'
    
    # Set browser gather usage stats to false
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'


# ============================================================================
# MAIN INITIALIZATION FUNCTION
# ============================================================================

def run_initialization():
    """Main initialization function to be called at app startup"""
    
    # Apply startup optimizations
    optimize_startup()
    
    # Initialize session state
    init_session_state()
    
    # Initialize application
    initialize_app()
    
    # Handle errors
    if handle_initialization_error():
        return False
    
    # Display warnings
    display_missing_env_vars()
    
    # Display performance metrics (admin only)
    display_performance_metrics()
    
    return True
