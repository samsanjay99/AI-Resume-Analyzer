# Temporary Files Cleanup Guide

## Problem

Your Smart Resume AI project generates temporary files in these directories:
- `temp_portfolios/` - Temporary portfolio generation folders
- `uploads/` - Uploaded resume files
- `generated_portfolios/` - Generated portfolio ZIP files

Over time, these accumulate and cause:
- ❌ Storage bloat
- ❌ Deployment issues
- ❌ Messy repository
- ❌ Not production-ready

## Solution

Automated cleanup system that removes old files while keeping recent ones safe.

---

## Quick Start

### Option 1: Manual Cleanup (Recommended for First Time)

**Windows:**
```bash
cleanup_temp_files.bat
```

**Linux/Mac:**
```bash
python cleanup_temp_files.py
```

This will:
- Delete files older than 24 hours
- Keep 5 most recent items in each directory
- Show before/after statistics

### Option 2: Check Storage Only (No Deletion)

**Windows:**
```bash
check_storage.bat
```

**Linux/Mac:**
```bash
python cleanup_temp_files.py --stats-only
```

### Option 3: Aggressive Cleanup

**Windows:**
```bash
cleanup_aggressive.bat
```

**Linux/Mac:**
```bash
python cleanup_temp_files.py --aggressive
```

This will:
- Delete files older than 1 hour
- Keep only 2 most recent items

---

## Automated Background Cleanup

### Start Auto Cleanup Service

**Windows:**
```bash
start_auto_cleanup.bat
```

**Linux/Mac:**
```bash
python auto_cleanup_service.py
```

This service:
- ✅ Runs every 6 hours automatically
- ✅ Deletes files older than 24 hours
- ✅ Keeps 5 most recent items
- ✅ Logs all operations to `cleanup_service.log`
- ✅ Runs in background (press Ctrl+C to stop)

### Custom Configuration

```bash
# Run cleanup every 3 hours
python auto_cleanup_service.py --interval 3

# Delete files older than 12 hours
python auto_cleanup_service.py --max-age 12

# Keep only 3 most recent items
python auto_cleanup_service.py --keep-recent 3

# Combine options
python auto_cleanup_service.py --interval 3 --max-age 12 --keep-recent 3
```

---

## Command Line Options

### cleanup_temp_files.py

```bash
# Default: Delete files older than 24 hours, keep 5 recent
python cleanup_temp_files.py

# Custom max age
python cleanup_temp_files.py --max-age 48

# Custom keep recent
python cleanup_temp_files.py --keep-recent 10

# Stats only (no deletion)
python cleanup_temp_files.py --stats-only

# Aggressive mode (1 hour, keep 2)
python cleanup_temp_files.py --aggressive
```

### auto_cleanup_service.py

```bash
# Default: Every 6 hours, max age 24 hours, keep 5
python auto_cleanup_service.py

# Custom interval
python auto_cleanup_service.py --interval 12

# Custom max age
python auto_cleanup_service.py --max-age 48

# Custom keep recent
python auto_cleanup_service.py --keep-recent 10

# Combine all
python auto_cleanup_service.py --interval 12 --max-age 48 --keep-recent 10
```

---

## How It Works

### Cleanup Logic

1. **Scan Directories**: Scans `temp_portfolios/`, `uploads/`, `generated_portfolios/`
2. **Sort by Age**: Sorts all items by creation time (newest first)
3. **Keep Recent**: Always keeps the N most recent items (default: 5)
4. **Check Age**: For older items, checks if they exceed max age (default: 24 hours)
5. **Delete Old**: Deletes items that are both old AND not in the "keep recent" list
6. **Log Results**: Shows what was deleted and what was kept

### Safety Features

✅ **Always keeps recent items** - Even if they're old, the N most recent are never deleted
✅ **Age-based deletion** - Only deletes files older than threshold
✅ **Detailed logging** - Shows exactly what's being deleted
✅ **Size reporting** - Shows how much space is freed
✅ **Error handling** - Continues even if some files can't be deleted

---

## Example Output

```
============================================================
🧹 STARTING AUTOMATED CLEANUP
============================================================
Configuration:
  - Max age: 24 hours
  - Keep recent: 5 items
  - Cutoff time: 2026-02-23 10:00:00

============================================================
Cleaning directory: temp_portfolios
============================================================
✅ KEEPING (recent): user_20260224_120000 (age: 2.5h, size: 1.2 MB)
✅ KEEPING (recent): user_20260224_110000 (age: 3.5h, size: 1.1 MB)
✅ KEEPING (recent): user_20260224_100000 (age: 4.5h, size: 1.3 MB)
✅ KEEPING (recent): user_20260224_090000 (age: 5.5h, size: 1.0 MB)
✅ KEEPING (recent): user_20260224_080000 (age: 6.5h, size: 1.2 MB)
🗑️  DELETED: user_20260223_200000 (age: 26.5h, size: 1.1 MB)
🗑️  DELETED: user_20260223_190000 (age: 27.5h, size: 1.0 MB)
🗑️  DELETED: user_20260223_180000 (age: 28.5h, size: 1.2 MB)

📊 Summary for temp_portfolios:
   - Deleted: 3 items (3.3 MB)
   - Kept: 5 items

============================================================
✅ CLEANUP COMPLETED
============================================================

📊 STORAGE STATISTICS
============================================================

📁 temp_portfolios/
   - Items: 5
   - Size: 5.8 MB

📁 uploads/
   - Items: 8
   - Size: 12.4 MB

📁 generated_portfolios/
   - Items: 5
   - Size: 15.2 MB

============================================================
TOTAL: 18 items, 33.4 MB
============================================================
```

---

## Integration with Application

### Option 1: Manual Cleanup (Current)

Run cleanup scripts manually when needed.

### Option 2: Scheduled Task (Recommended)

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Smart Resume AI Cleanup"
4. Trigger: Daily at 3:00 AM
5. Action: Start a program
6. Program: `C:\path\to\python.exe`
7. Arguments: `C:\path\to\cleanup_temp_files.py`

**Linux Cron:**
```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 3 AM)
0 3 * * * /usr/bin/python3 /path/to/cleanup_temp_files.py >> /path/to/cleanup.log 2>&1
```

### Option 3: Background Service (Advanced)

Run `auto_cleanup_service.py` as a system service that starts with your application.

---

## Production Deployment

### Recommended Settings

**Development:**
- Interval: 6 hours
- Max age: 24 hours
- Keep recent: 5 items

**Production:**
- Interval: 3 hours
- Max age: 12 hours
- Keep recent: 3 items

**High Traffic:**
- Interval: 1 hour
- Max age: 6 hours
- Keep recent: 2 items

### Docker Integration

Add to your `Dockerfile`:

```dockerfile
# Copy cleanup scripts
COPY cleanup_temp_files.py /app/
COPY auto_cleanup_service.py /app/

# Install schedule package
RUN pip install schedule

# Start cleanup service in background
CMD python auto_cleanup_service.py & streamlit run app.py
```

### Environment Variables

Add to `.env`:

```env
# Cleanup configuration
CLEANUP_INTERVAL_HOURS=6
CLEANUP_MAX_AGE_HOURS=24
CLEANUP_KEEP_RECENT=5
```

---

## Troubleshooting

### Issue: Files not being deleted

**Solution:**
- Check file permissions
- Run with administrator/sudo privileges
- Check if files are in use

### Issue: Too many files being deleted

**Solution:**
- Increase `--keep-recent` value
- Increase `--max-age` value
- Use `--stats-only` first to preview

### Issue: Service stops unexpectedly

**Solution:**
- Check `cleanup_service.log` for errors
- Ensure Python and schedule package are installed
- Run manually first to test

### Issue: Storage still growing

**Solution:**
- Reduce cleanup interval (run more frequently)
- Reduce max age (delete files sooner)
- Reduce keep recent (keep fewer files)

---

## Best Practices

1. ✅ **Run stats first**: Always use `--stats-only` before first cleanup
2. ✅ **Start conservative**: Use default settings initially
3. ✅ **Monitor logs**: Check `cleanup_service.log` regularly
4. ✅ **Adjust gradually**: Fine-tune settings based on usage
5. ✅ **Backup important files**: Keep backups of any critical data
6. ✅ **Test in development**: Test cleanup thoroughly before production
7. ✅ **Schedule wisely**: Run during low-traffic hours

---

## Files Created

### Scripts
- `cleanup_temp_files.py` - Main cleanup script
- `auto_cleanup_service.py` - Background service
- `cleanup_temp_files.bat` - Windows batch file
- `cleanup_aggressive.bat` - Aggressive cleanup
- `check_storage.bat` - Storage statistics
- `start_auto_cleanup.bat` - Start background service

### Logs
- `cleanup_service.log` - Auto cleanup service logs

### Documentation
- `CLEANUP_GUIDE.md` - This file

---

## Summary

✅ **Problem Solved**: Automatic cleanup of temporary files
✅ **No Code Changes**: Works without modifying existing application code
✅ **Safe**: Always keeps recent files
✅ **Flexible**: Configurable intervals and thresholds
✅ **Production Ready**: Can run as background service
✅ **Well Documented**: Complete guide and examples

---

## Quick Reference

```bash
# Check storage
python cleanup_temp_files.py --stats-only

# Manual cleanup (default)
python cleanup_temp_files.py

# Aggressive cleanup
python cleanup_temp_files.py --aggressive

# Start auto service
python auto_cleanup_service.py

# Custom settings
python cleanup_temp_files.py --max-age 48 --keep-recent 10
python auto_cleanup_service.py --interval 3 --max-age 12
```

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Status**: Production Ready ✅
