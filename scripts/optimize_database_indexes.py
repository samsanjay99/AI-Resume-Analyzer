"""
Database Index Optimization Script
Creates indexes for better query performance
"""
from config.database import get_database_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_performance_indexes():
    """Create indexes for all tables to improve query performance"""
    
    indexes = [
        # Resume data indexes
        ("idx_resume_data_email", "resume_data", "email"),
        ("idx_resume_data_user_id", "resume_data", "user_id"),
        ("idx_resume_data_created_at", "resume_data", "created_at DESC"),
        ("idx_resume_data_target_role", "resume_data", "target_role"),
        
        # Resume analysis indexes
        ("idx_resume_analysis_resume_id", "resume_analysis", "resume_id"),
        ("idx_resume_analysis_user_id", "resume_analysis", "user_id"),
        ("idx_resume_analysis_created_at", "resume_analysis", "created_at DESC"),
        ("idx_resume_analysis_ats_score", "resume_analysis", "ats_score DESC"),
        
        # AI analysis indexes
        ("idx_ai_analysis_resume_id", "ai_analysis", "resume_id"),
        ("idx_ai_analysis_user_id", "ai_analysis", "user_id"),
        ("idx_ai_analysis_created_at", "ai_analysis", "created_at DESC"),
        ("idx_ai_analysis_resume_score", "ai_analysis", "resume_score DESC"),
        ("idx_ai_analysis_job_role", "ai_analysis", "job_role"),
        
        # User indexes
        ("idx_users_email", "users", "email"),
        ("idx_users_created_at", "users", "created_at DESC"),
        
        # Uploaded files indexes
        ("idx_uploaded_files_user_id", "uploaded_files", "user_id"),
        ("idx_uploaded_files_created_at", "uploaded_files", "created_at DESC"),
        ("idx_uploaded_files_upload_source", "uploaded_files", "upload_source"),
        
        # Portfolio deployments indexes
        ("idx_portfolio_deployments_user_id", "portfolio_deployments", "user_id"),
        ("idx_portfolio_deployments_created_at", "portfolio_deployments", "created_at DESC"),
        
        # Course recommendations indexes
        ("idx_course_recommendations_user_id", "course_recommendations", "user_id"),
        ("idx_course_recommendations_created_at", "course_recommendations", "created_at DESC"),
        
        # Admin logs indexes
        ("idx_admin_logs_admin_email", "admin_logs", "admin_email"),
        ("idx_admin_logs_timestamp", "admin_logs", "timestamp DESC"),
        
        # Feedback indexes
        ("idx_feedback_user_email", "feedback", "user_email"),
        ("idx_feedback_created_at", "feedback", "created_at DESC"),
        ("idx_feedback_rating", "feedback", "rating DESC"),
    ]
    
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        created_count = 0
        skipped_count = 0
        
        for index_name, table_name, column in indexes:
            try:
                # Check if index already exists
                cursor.execute("""
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = %s
                """, (index_name,))
                
                if cursor.fetchone():
                    logger.info(f"⏭️  Index {index_name} already exists, skipping")
                    skipped_count += 1
                    continue
                
                # Create index
                sql = f"CREATE INDEX {index_name} ON {table_name}({column})"
                cursor.execute(sql)
                conn.commit()
                logger.info(f"✅ Created index: {index_name} on {table_name}({column})")
                created_count += 1
                
            except Exception as e:
                logger.warning(f"⚠️  Could not create index {index_name}: {e}")
                conn.rollback()
        
        logger.info(f"\n📊 Index creation summary:")
        logger.info(f"   Created: {created_count}")
        logger.info(f"   Skipped: {skipped_count}")
        logger.info(f"   Total: {len(indexes)}")


def analyze_tables():
    """Run ANALYZE on all tables to update statistics for query planner"""
    
    tables = [
        'resume_data', 'resume_analysis', 'ai_analysis', 'users',
        'uploaded_files', 'portfolio_deployments', 'course_recommendations',
        'admin_logs', 'feedback', 'admin'
    ]
    
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        for table in tables:
            try:
                cursor.execute(f"ANALYZE {table}")
                conn.commit()
                logger.info(f"✅ Analyzed table: {table}")
            except Exception as e:
                logger.warning(f"⚠️  Could not analyze table {table}: {e}")
                conn.rollback()


def vacuum_tables():
    """Run VACUUM on tables to reclaim storage and update statistics"""
    
    tables = [
        'resume_data', 'resume_analysis', 'ai_analysis', 'users',
        'uploaded_files', 'portfolio_deployments'
    ]
    
    with get_database_connection() as conn:
        # VACUUM requires autocommit mode
        old_isolation_level = conn.isolation_level
        conn.set_isolation_level(0)
        cursor = conn.cursor()
        
        for table in tables:
            try:
                cursor.execute(f"VACUUM ANALYZE {table}")
                logger.info(f"✅ Vacuumed table: {table}")
            except Exception as e:
                logger.warning(f"⚠️  Could not vacuum table {table}: {e}")
        
        conn.set_isolation_level(old_isolation_level)


def get_database_stats():
    """Get database statistics and performance metrics"""
    
    with get_database_connection() as conn:
        cursor = conn.cursor()
        
        logger.info("\n📊 Database Statistics:")
        
        # Table sizes
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY size_bytes DESC
        """)
        
        logger.info("\n📦 Table Sizes:")
        for row in cursor.fetchall():
            logger.info(f"   {row[1]}: {row[2]}")
        
        # Index usage
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC
            LIMIT 10
        """)
        
        logger.info("\n🔍 Top 10 Most Used Indexes:")
        for row in cursor.fetchall():
            logger.info(f"   {row[2]} on {row[1]}: {row[3]} scans")
        
        # Unused indexes
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public' AND idx_scan = 0
        """)
        
        unused = cursor.fetchall()
        if unused:
            logger.info("\n⚠️  Unused Indexes (consider removing):")
            for row in unused:
                logger.info(f"   {row[2]} on {row[1]}")


if __name__ == "__main__":
    logger.info("🚀 Starting database optimization...")
    
    try:
        # Create indexes
        logger.info("\n📝 Creating performance indexes...")
        create_performance_indexes()
        
        # Analyze tables
        logger.info("\n📊 Analyzing tables...")
        analyze_tables()
        
        # Get statistics
        get_database_stats()
        
        logger.info("\n✅ Database optimization complete!")
        
    except Exception as e:
        logger.error(f"❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()
