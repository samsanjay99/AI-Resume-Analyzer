#!/usr/bin/env python3
"""
Automated Cleanup Script for Temporary Files
Removes old temporary portfolios and uploads to prevent storage bloat
"""

import os
import shutil
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TempFileCleanup:
    """Manages cleanup of temporary files and folders"""
    
    def __init__(self, max_age_hours=24, keep_recent=5):
        """
        Initialize cleanup manager
        
        Args:
            max_age_hours: Delete files older than this many hours (default: 24)
            keep_recent: Always keep this many most recent files (default: 5)
        """
        self.max_age_hours = max_age_hours
        self.keep_recent = keep_recent
        self.cutoff_time = time.time() - (max_age_hours * 3600)
        
        # Directories to clean
        self.temp_dirs = [
            'temp_portfolios',
            'uploads',
            'generated_portfolios'
        ]
    
    def get_folder_age(self, folder_path):
        """Get the age of a folder in seconds"""
        try:
            return time.time() - os.path.getctime(folder_path)
        except:
            return 0
    
    def get_file_age(self, file_path):
        """Get the age of a file in seconds"""
        try:
            return time.time() - os.path.getctime(file_path)
        except:
            return 0
    
    def should_delete(self, path, age_seconds):
        """Determine if a file/folder should be deleted"""
        return age_seconds > (self.max_age_hours * 3600)
    
    def cleanup_directory(self, directory):
        """Clean up old files in a directory"""
        if not os.path.exists(directory):
            logger.info(f"Directory does not exist: {directory}")
            return
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Cleaning directory: {directory}")
        logger.info(f"{'='*60}")
        
        # Get all items with their ages
        items = []
        for item_name in os.listdir(directory):
            item_path = os.path.join(directory, item_name)
            
            if os.path.isdir(item_path):
                age = self.get_folder_age(item_path)
            else:
                age = self.get_file_age(item_path)
            
            items.append({
                'name': item_name,
                'path': item_path,
                'age_seconds': age,
                'age_hours': age / 3600,
                'is_dir': os.path.isdir(item_path),
                'size': self.get_size(item_path)
            })
        
        # Sort by age (newest first)
        items.sort(key=lambda x: x['age_seconds'])
        
        # Keep the most recent items
        items_to_keep = items[:self.keep_recent]
        items_to_check = items[self.keep_recent:]
        
        deleted_count = 0
        deleted_size = 0
        kept_count = 0
        
        # Always keep recent items
        for item in items_to_keep:
            logger.info(f"✅ KEEPING (recent): {item['name']} "
                       f"(age: {item['age_hours']:.1f}h, size: {self.format_size(item['size'])})")
            kept_count += 1
        
        # Check older items
        for item in items_to_check:
            if self.should_delete(item['path'], item['age_seconds']):
                try:
                    if item['is_dir']:
                        shutil.rmtree(item['path'])
                        logger.info(f"🗑️  DELETED: {item['name']} "
                                   f"(age: {item['age_hours']:.1f}h, size: {self.format_size(item['size'])})")
                    else:
                        os.remove(item['path'])
                        logger.info(f"🗑️  DELETED: {item['name']} "
                                   f"(age: {item['age_hours']:.1f}h, size: {self.format_size(item['size'])})")
                    
                    deleted_count += 1
                    deleted_size += item['size']
                except Exception as e:
                    logger.error(f"❌ ERROR deleting {item['name']}: {str(e)}")
            else:
                logger.info(f"✅ KEEPING: {item['name']} "
                           f"(age: {item['age_hours']:.1f}h, size: {self.format_size(item['size'])})")
                kept_count += 1
        
        logger.info(f"\n📊 Summary for {directory}:")
        logger.info(f"   - Deleted: {deleted_count} items ({self.format_size(deleted_size)})")
        logger.info(f"   - Kept: {kept_count} items")
    
    def get_size(self, path):
        """Get size of file or directory in bytes"""
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            total = 0
            try:
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total += os.path.getsize(filepath)
                        except:
                            pass
            except:
                pass
            return total
        return 0
    
    def format_size(self, size_bytes):
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def run_cleanup(self):
        """Run cleanup on all configured directories"""
        logger.info("\n" + "="*60)
        logger.info("🧹 STARTING AUTOMATED CLEANUP")
        logger.info("="*60)
        logger.info(f"Configuration:")
        logger.info(f"  - Max age: {self.max_age_hours} hours")
        logger.info(f"  - Keep recent: {self.keep_recent} items")
        logger.info(f"  - Cutoff time: {datetime.fromtimestamp(self.cutoff_time).strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_deleted = 0
        total_kept = 0
        
        for directory in self.temp_dirs:
            self.cleanup_directory(directory)
        
        logger.info("\n" + "="*60)
        logger.info("✅ CLEANUP COMPLETED")
        logger.info("="*60)
    
    def get_storage_stats(self):
        """Get storage statistics for all temp directories"""
        stats = {}
        
        for directory in self.temp_dirs:
            if not os.path.exists(directory):
                stats[directory] = {
                    'exists': False,
                    'total_size': 0,
                    'item_count': 0
                }
                continue
            
            total_size = 0
            item_count = 0
            
            for item_name in os.listdir(directory):
                item_path = os.path.join(directory, item_name)
                total_size += self.get_size(item_path)
                item_count += 1
            
            stats[directory] = {
                'exists': True,
                'total_size': total_size,
                'total_size_formatted': self.format_size(total_size),
                'item_count': item_count
            }
        
        return stats
    
    def print_storage_stats(self):
        """Print storage statistics"""
        logger.info("\n" + "="*60)
        logger.info("📊 STORAGE STATISTICS")
        logger.info("="*60)
        
        stats = self.get_storage_stats()
        total_size = 0
        total_items = 0
        
        for directory, info in stats.items():
            if info['exists']:
                logger.info(f"\n📁 {directory}/")
                logger.info(f"   - Items: {info['item_count']}")
                logger.info(f"   - Size: {info['total_size_formatted']}")
                total_size += info['total_size']
                total_items += info['item_count']
            else:
                logger.info(f"\n📁 {directory}/ (does not exist)")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"TOTAL: {total_items} items, {self.format_size(total_size)}")
        logger.info(f"{'='*60}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up temporary files')
    parser.add_argument('--max-age', type=int, default=24,
                       help='Delete files older than this many hours (default: 24)')
    parser.add_argument('--keep-recent', type=int, default=5,
                       help='Always keep this many most recent files (default: 5)')
    parser.add_argument('--stats-only', action='store_true',
                       help='Only show statistics, do not delete anything')
    parser.add_argument('--aggressive', action='store_true',
                       help='Aggressive mode: max-age=1 hour, keep-recent=2')
    
    args = parser.parse_args()
    
    # Aggressive mode
    if args.aggressive:
        max_age = 1
        keep_recent = 2
        logger.info("⚠️  AGGRESSIVE MODE ENABLED")
    else:
        max_age = args.max_age
        keep_recent = args.keep_recent
    
    # Create cleanup manager
    cleanup = TempFileCleanup(max_age_hours=max_age, keep_recent=keep_recent)
    
    # Show stats before
    logger.info("\n📊 BEFORE CLEANUP:")
    cleanup.print_storage_stats()
    
    if args.stats_only:
        logger.info("\n✅ Stats-only mode. No files deleted.")
        return
    
    # Run cleanup
    cleanup.run_cleanup()
    
    # Show stats after
    logger.info("\n📊 AFTER CLEANUP:")
    cleanup.print_storage_stats()


if __name__ == '__main__':
    main()
