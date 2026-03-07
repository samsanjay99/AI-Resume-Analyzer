"""
Cleanup Script for Temporary Files
Run this periodically to clean up old temporary files
"""
import os
import shutil
import time
from datetime import datetime

def cleanup_temp_portfolios(max_age_hours=1):
    """Clean up old temporary portfolio files"""
    temp_path = "temp_portfolios"
    
    if not os.path.exists(temp_path):
        print(f"✅ No temp_portfolios folder found")
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    cleaned_count = 0
    total_size = 0
    
    print(f"🧹 Cleaning up temp files older than {max_age_hours} hour(s)...")
    
    for item in os.listdir(temp_path):
        item_path = os.path.join(temp_path, item)
        
        if os.path.isdir(item_path):
            item_age = current_time - os.path.getmtime(item_path)
            item_size = get_folder_size(item_path)
            
            if item_age > max_age_seconds:
                print(f"  Removing: {item} (age: {item_age/3600:.1f}h, size: {item_size/1024/1024:.2f}MB)")
                shutil.rmtree(item_path)
                cleaned_count += 1
                total_size += item_size
    
    if cleaned_count > 0:
        print(f"\n✅ Cleaned up {cleaned_count} folder(s)")
        print(f"💾 Freed {total_size/1024/1024:.2f}MB of storage")
    else:
        print(f"✅ No old temp files to clean up")

def cleanup_generated_portfolios(max_age_days=7):
    """Clean up old generated portfolio ZIP files"""
    gen_path = "generated_portfolios"
    
    if not os.path.exists(gen_path):
        print(f"✅ No generated_portfolios folder found")
        return
    
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 3600
    cleaned_count = 0
    total_size = 0
    
    print(f"\n🧹 Cleaning up generated portfolios older than {max_age_days} day(s)...")
    
    for item in os.listdir(gen_path):
        item_path = os.path.join(gen_path, item)
        
        if os.path.isfile(item_path) and item.endswith('.zip'):
            item_age = current_time - os.path.getmtime(item_path)
            item_size = os.path.getsize(item_path)
            
            if item_age > max_age_seconds:
                print(f"  Removing: {item} (age: {item_age/86400:.1f}d, size: {item_size/1024/1024:.2f}MB)")
                os.remove(item_path)
                cleaned_count += 1
                total_size += item_size
    
    if cleaned_count > 0:
        print(f"\n✅ Cleaned up {cleaned_count} ZIP file(s)")
        print(f"💾 Freed {total_size/1024/1024:.2f}MB of storage")
    else:
        print(f"✅ No old ZIP files to clean up")

def cleanup_uploads(max_age_days=30):
    """Clean up old uploaded files"""
    uploads_path = "uploads"
    
    if not os.path.exists(uploads_path):
        print(f"✅ No uploads folder found")
        return
    
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 3600
    cleaned_count = 0
    total_size = 0
    
    print(f"\n🧹 Cleaning up uploads older than {max_age_days} day(s)...")
    
    for item in os.listdir(uploads_path):
        item_path = os.path.join(uploads_path, item)
        
        if os.path.isfile(item_path):
            item_age = current_time - os.path.getmtime(item_path)
            item_size = os.path.getsize(item_path)
            
            if item_age > max_age_seconds:
                print(f"  Removing: {item} (age: {item_age/86400:.1f}d, size: {item_size/1024/1024:.2f}MB)")
                os.remove(item_path)
                cleaned_count += 1
                total_size += item_size
    
    if cleaned_count > 0:
        print(f"\n✅ Cleaned up {cleaned_count} upload(s)")
        print(f"💾 Freed {total_size/1024/1024:.2f}MB of storage")
    else:
        print(f"✅ No old uploads to clean up")

def get_folder_size(folder_path):
    """Calculate total size of a folder"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

def get_storage_stats():
    """Get current storage statistics"""
    print("\n📊 Current Storage Statistics:")
    print("=" * 50)
    
    folders = {
        'temp_portfolios': 'temp_portfolios',
        'generated_portfolios': 'generated_portfolios',
        'uploads': 'uploads',
        'analysis_reports': 'analysis_reports'
    }
    
    total_size = 0
    
    for name, path in folders.items():
        if os.path.exists(path):
            size = get_folder_size(path)
            count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) or os.path.isdir(os.path.join(path, f))])
            total_size += size
            print(f"  {name:25} {size/1024/1024:8.2f}MB ({count} items)")
        else:
            print(f"  {name:25} {'N/A':>8} (not found)")
    
    print("=" * 50)
    print(f"  {'TOTAL':25} {total_size/1024/1024:8.2f}MB")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("🧹 Smart Resume AI - Storage Cleanup")
    print("=" * 50)
    print()
    
    # Show current stats
    get_storage_stats()
    
    # Clean up temp portfolios (older than 1 hour)
    cleanup_temp_portfolios(max_age_hours=1)
    
    # Clean up generated portfolios (older than 7 days)
    cleanup_generated_portfolios(max_age_days=7)
    
    # Clean up uploads (older than 30 days)
    cleanup_uploads(max_age_days=30)
    
    # Show final stats
    print("\n" + "=" * 50)
    print("After Cleanup:")
    get_storage_stats()
    
    print("=" * 50)
    print("✅ Cleanup complete!")
    print("=" * 50)
