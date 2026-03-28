#!/usr/bin/env python3
"""
Automatic Cleanup Service
Runs in the background and periodically cleans up old temporary files
"""

import time
import schedule
import logging
from cleanup_temp_files import TempFileCleanup
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoCleanupService:
    """Background service for automatic cleanup"""
    
    def __init__(self, interval_hours=6, max_age_hours=24, keep_recent=5):
        """
        Initialize auto cleanup service
        
        Args:
            interval_hours: Run cleanup every X hours (default: 6)
            max_age_hours: Delete files older than X hours (default: 24)
            keep_recent: Keep X most recent files (default: 5)
        """
        self.interval_hours = interval_hours
        self.max_age_hours = max_age_hours
        self.keep_recent = keep_recent
        self.cleanup_manager = TempFileCleanup(max_age_hours, keep_recent)
        self.run_count = 0
    
    def run_cleanup_job(self):
        """Run a single cleanup job"""
        self.run_count += 1
        logger.info(f"\n{'='*70}")
        logger.info(f"🤖 AUTO CLEANUP JOB #{self.run_count}")
        logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*70}")
        
        try:
            # Show stats before
            logger.info("\n📊 Storage before cleanup:")
            self.cleanup_manager.print_storage_stats()
            
            # Run cleanup
            self.cleanup_manager.run_cleanup()
            
            # Show stats after
            logger.info("\n📊 Storage after cleanup:")
            self.cleanup_manager.print_storage_stats()
            
            logger.info(f"\n✅ Cleanup job #{self.run_count} completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error in cleanup job #{self.run_count}: {str(e)}")
    
    def start(self):
        """Start the auto cleanup service"""
        logger.info("\n" + "="*70)
        logger.info("🚀 STARTING AUTO CLEANUP SERVICE")
        logger.info("="*70)
        logger.info(f"Configuration:")
        logger.info(f"  - Cleanup interval: Every {self.interval_hours} hours")
        logger.info(f"  - Max file age: {self.max_age_hours} hours")
        logger.info(f"  - Keep recent: {self.keep_recent} items")
        logger.info(f"  - Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        # Run immediately on start
        logger.info("\n🔄 Running initial cleanup...")
        self.run_cleanup_job()
        
        # Schedule periodic cleanup
        schedule.every(self.interval_hours).hours.do(self.run_cleanup_job)
        
        logger.info(f"\n⏰ Next cleanup scheduled in {self.interval_hours} hours")
        logger.info("Press Ctrl+C to stop the service\n")
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Auto cleanup service stopped by user")
            logger.info(f"Total cleanup jobs run: {self.run_count}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto cleanup service')
    parser.add_argument('--interval', type=int, default=6,
                       help='Run cleanup every X hours (default: 6)')
    parser.add_argument('--max-age', type=int, default=24,
                       help='Delete files older than X hours (default: 24)')
    parser.add_argument('--keep-recent', type=int, default=5,
                       help='Keep X most recent files (default: 5)')
    
    args = parser.parse_args()
    
    # Create and start service
    service = AutoCleanupService(
        interval_hours=args.interval,
        max_age_hours=args.max_age,
        keep_recent=args.keep_recent
    )
    
    service.start()


if __name__ == '__main__':
    main()
