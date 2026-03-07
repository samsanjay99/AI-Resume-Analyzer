"""
Performance Optimization Layer
Implements caching, lazy loading, and performance monitoring
"""
import streamlit as st
import time
import functools
import logging
from typing import Any, Callable, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CACHING LAYER
# ============================================================================

def cache_with_ttl(ttl_seconds: int = 300):
    """
    Cache decorator with time-to-live
    Args:
        ttl_seconds: Cache expiration time in seconds (default 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Check if result is in cache and not expired
            if cache_key in st.session_state:
                cached_data, timestamp = st.session_state[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_data
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}, executing...")
            result = func(*args, **kwargs)
            st.session_state[cache_key] = (result, time.time())
            return result
        
        return wrapper
    return decorator


def clear_cache(pattern: Optional[str] = None):
    """
    Clear cached data
    Args:
        pattern: Optional pattern to match cache keys (clears all if None)
    """
    if pattern:
        keys_to_delete = [k for k in st.session_state.keys() if pattern in k]
        for key in keys_to_delete:
            del st.session_state[key]
        logger.info(f"Cleared {len(keys_to_delete)} cache entries matching '{pattern}'")
    else:
        # Clear all cache entries (preserve auth and essential state)
        essential_keys = {'authenticated', 'user_email', 'user_id', 'is_admin'}
        keys_to_delete = [k for k in st.session_state.keys() if k not in essential_keys]
        for key in keys_to_delete:
            del st.session_state[key]
        logger.info(f"Cleared {len(keys_to_delete)} cache entries")


# ============================================================================
# LAZY LOADING
# ============================================================================

class LazyLoader:
    """Lazy load heavy resources only when needed"""
    
    _instances = {}
    
    @classmethod
    def get_instance(cls, key: str, loader_func: Callable, *args, **kwargs) -> Any:
        """
        Get or create a lazy-loaded instance
        Args:
            key: Unique identifier for the instance
            loader_func: Function to create the instance
            *args, **kwargs: Arguments for loader_func
        """
        if key not in cls._instances:
            logger.info(f"Lazy loading {key}...")
            start_time = time.time()
            cls._instances[key] = loader_func(*args, **kwargs)
            logger.info(f"Loaded {key} in {time.time() - start_time:.2f}s")
        return cls._instances[key]
    
    @classmethod
    def clear_instance(cls, key: str):
        """Clear a specific lazy-loaded instance"""
        if key in cls._instances:
            del cls._instances[key]
            logger.info(f"Cleared lazy-loaded instance: {key}")


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    @staticmethod
    def measure_time(func: Callable) -> Callable:
        """Decorator to measure function execution time"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log slow operations (> 1 second)
            if execution_time > 1.0:
                logger.warning(f"Slow operation: {func.__name__} took {execution_time:.2f}s")
            else:
                logger.debug(f"{func.__name__} executed in {execution_time:.2f}s")
            
            return result
        return wrapper
    
    @staticmethod
    def log_page_load(page_name: str):
        """Log page load time"""
        if f'page_load_start_{page_name}' not in st.session_state:
            st.session_state[f'page_load_start_{page_name}'] = time.time()
        else:
            load_time = time.time() - st.session_state[f'page_load_start_{page_name}']
            logger.info(f"Page '{page_name}' loaded in {load_time:.2f}s")
            del st.session_state[f'page_load_start_{page_name}']


# ============================================================================
# STREAMLIT-SPECIFIC OPTIMIZATIONS
# ============================================================================

def optimize_streamlit():
    """Apply Streamlit-specific optimizations"""
    
    # Disable file watcher for better performance in production
    if 'STREAMLIT_SERVER_FILE_WATCHER_TYPE' not in os.environ:
        os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
    
    # Set max message size for large data transfers
    if 'STREAMLIT_SERVER_MAX_MESSAGE_SIZE' not in os.environ:
        os.environ['STREAMLIT_SERVER_MAX_MESSAGE_SIZE'] = '200'
    
    # Enable faster reruns
    if 'STREAMLIT_SERVER_RUN_ON_SAVE' not in os.environ:
        os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'false'


def batch_operations(operations: list, batch_size: int = 10):
    """
    Execute operations in batches to prevent UI blocking
    Args:
        operations: List of callable operations
        batch_size: Number of operations per batch
    """
    results = []
    for i in range(0, len(operations), batch_size):
        batch = operations[i:i + batch_size]
        batch_results = [op() for op in batch]
        results.extend(batch_results)
        
        # Allow UI to update between batches
        if i + batch_size < len(operations):
            time.sleep(0.01)
    
    return results


# ============================================================================
# DATA PRELOADING
# ============================================================================

def preload_essential_data():
    """Preload frequently accessed data at startup"""
    try:
        logger.info("Preloading essential data...")
        
        # Preload database stats (cached)
        from config.database import get_resume_stats, warm_cache
        warm_cache()
        
        logger.info("Essential data preloaded successfully")
    except Exception as e:
        logger.error(f"Error preloading data: {e}")


# ============================================================================
# RETRY MECHANISM
# ============================================================================

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry decorator for unreliable operations
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


# ============================================================================
# INITIALIZATION
# ============================================================================

import os
optimize_streamlit()
