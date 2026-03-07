# 💾 Storage Management Guide

Complete guide to managing storage in Smart Resume AI, especially for cloud deployments.

---

## 📊 Storage Overview

### What Gets Stored

| Folder | Purpose | Lifecycle | Cloud Impact |
|--------|---------|-----------|--------------|
| `temp_portfolios/` | Temporary portfolio copies during generation | Auto-deleted after 1 hour | ⚠️ Can accumulate |
| `generated_portfolios/` | ZIP files of generated portfolios | Kept for 7 days | ⚠️ Can accumulate |
| `uploads/` | User-uploaded resume files | Kept for 30 days | ⚠️ Can accumulate |
| `analysis_reports/` | Generated analysis PDFs | Kept for 30 days | ⚠️ Can accumulate |

---

## ⚠️ Cloud Storage Concerns

### The Problem

On cloud platforms like **Streamlit Cloud**, **Render**, or **Railway**:

1. **Ephemeral Storage**: Files are temporary but still consume resources
2. **Limited Space**: Free tiers have storage limits (usually 512MB-1GB)
3. **Accumulation**: Without cleanup, files pile up quickly
4. **Performance**: Full storage slows down the app

### The Solution

We've implemented **automatic cleanup** at multiple levels:

---

## ✅ Automatic Cleanup (Implemented)

### 1. Immediate Cleanup After Generation

**When**: After portfolio ZIP is created
**What**: Deletes `temp_portfolios/` folder immediately
**Impact**: Prevents 90% of storage accumulation

```python
# In portfolio_generator.py
# Step 7: Clean up temp files immediately after ZIP creation
self.cleanup_temp_portfolio(user_id)
```

### 2. Auto-Cleanup on Startup

**When**: Every time the app starts
**What**: Removes temp files older than 1 hour
**Impact**: Cleans up any orphaned files

```python
# In PortfolioGenerator.__init__()
self._cleanup_old_temp_files()
```

### 3. Manual Cleanup Script

**When**: Run manually or via cron job
**What**: Cleans all old files
**Impact**: Complete storage cleanup

```bash
python scripts/cleanup_temp_files.py
```

---

## 🔧 Manual Cleanup

### Run Cleanup Script

```bash
# Clean all old files
python scripts/cleanup_temp_files.py
```

**What it does:**
- Removes temp portfolios older than 1 hour
- Removes generated ZIPs older than 7 days
- Removes uploads older than 30 days
- Shows storage statistics before/after

### Check Storage Usage

```bash
# View current storage stats
python scripts/cleanup_temp_files.py
```

**Output:**
```
📊 Current Storage Statistics:
==================================================
  temp_portfolios           0.00MB (0 items)
  generated_portfolios      5.23MB (12 items)
  uploads                   8.45MB (25 items)
  analysis_reports          3.12MB (8 items)
==================================================
  TOTAL                    16.80MB
```

---

## 🚀 Cloud Deployment Best Practices

### Streamlit Cloud

**Storage Limit**: ~1GB
**Recommendation**: 
- Enable automatic cleanup (already implemented)
- Run cleanup script weekly via GitHub Actions

```yaml
# .github/workflows/cleanup.yml
name: Weekly Cleanup
on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight
jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: python scripts/cleanup_temp_files.py
```

### Render/Railway

**Storage Limit**: Ephemeral (resets on restart)
**Recommendation**:
- Files are automatically deleted on restart
- No additional cleanup needed
- But still good to clean up for performance

### Docker

**Storage Limit**: Depends on host
**Recommendation**:
- Use volumes for persistent data
- Add cleanup to cron job inside container

```dockerfile
# Add to Dockerfile
RUN echo "0 * * * * python /app/scripts/cleanup_temp_files.py" | crontab -
```

---

## 📁 Folder Details

### temp_portfolios/

**Purpose**: Temporary copies of portfolio templates during generation

**Lifecycle**:
1. Created when user generates portfolio
2. Used to replace placeholders
3. Deleted immediately after ZIP creation
4. Auto-cleanup removes files older than 1 hour

**Size**: ~2-5MB per portfolio
**Cleanup**: Automatic + on startup

**Why it exists**:
- Keeps original templates untouched
- Allows parallel portfolio generation
- Enables preview before download

### generated_portfolios/

**Purpose**: ZIP files of generated portfolios for download

**Lifecycle**:
1. Created after portfolio generation
2. Available for user download
3. Kept for 7 days
4. Auto-cleanup removes old files

**Size**: ~1-3MB per ZIP
**Cleanup**: Manual script (7 days)

**Why it exists**:
- Users can download multiple times
- Allows re-download if needed
- Provides backup of generated portfolios

### uploads/

**Purpose**: User-uploaded resume files

**Lifecycle**:
1. Created when user uploads resume
2. Used for analysis/generation
3. Kept for 30 days
4. Auto-cleanup removes old files

**Size**: ~100KB-5MB per file
**Cleanup**: Manual script (30 days)

**Why it exists**:
- Allows re-analysis without re-upload
- Provides history of uploads
- Enables admin review if needed

### analysis_reports/

**Purpose**: Generated analysis PDF reports

**Lifecycle**:
1. Created after resume analysis
2. Available for download
3. Kept for 30 days
4. Auto-cleanup removes old files

**Size**: ~500KB-2MB per report
**Cleanup**: Manual script (30 days)

**Why it exists**:
- Users can download reports later
- Provides history of analyses
- Enables comparison over time

---

## 🔍 Monitoring Storage

### Check Current Usage

```python
from scripts.cleanup_temp_files import get_storage_stats

get_storage_stats()
```

### Monitor in Production

**Streamlit Cloud**:
- Check app logs for cleanup messages
- Monitor app performance

**Render/Railway**:
- Check deployment logs
- Monitor disk usage in dashboard

**Docker**:
- Use `df -h` to check disk usage
- Monitor container logs

---

## ⚙️ Configuration

### Adjust Cleanup Intervals

Edit `scripts/cleanup_temp_files.py`:

```python
# Clean temp portfolios (default: 1 hour)
cleanup_temp_portfolios(max_age_hours=2)  # Change to 2 hours

# Clean generated portfolios (default: 7 days)
cleanup_generated_portfolios(max_age_days=14)  # Change to 14 days

# Clean uploads (default: 30 days)
cleanup_uploads(max_age_days=60)  # Change to 60 days
```

### Disable Auto-Cleanup

Edit `utils/portfolio_generator.py`:

```python
# Comment out auto-cleanup in __init__
# self._cleanup_old_temp_files()

# Comment out immediate cleanup in generate_portfolio_with_ai
# self.cleanup_temp_portfolio(user_id)
```

**⚠️ Not recommended for cloud deployments!**

---

## 🎯 Best Practices

### For Development

1. **Run cleanup weekly**: `python scripts/cleanup_temp_files.py`
2. **Monitor storage**: Check stats regularly
3. **Test cleanup**: Verify files are deleted correctly

### For Production

1. **Enable auto-cleanup**: Already implemented ✅
2. **Schedule cleanup**: Use cron or GitHub Actions
3. **Monitor logs**: Check for cleanup messages
4. **Set alerts**: Alert if storage > 80%

### For Cloud Deployments

1. **Use ephemeral storage**: Don't rely on persistent files
2. **Store important data in database**: Not in files
3. **Use external storage**: S3, Cloudinary for long-term files
4. **Monitor usage**: Check platform dashboard

---

## 🚨 Troubleshooting

### Storage Full Error

**Symptoms**:
- App crashes
- "No space left on device" error
- Slow performance

**Solution**:
```bash
# Run cleanup immediately
python scripts/cleanup_temp_files.py

# Check what's using space
du -sh temp_portfolios/ generated_portfolios/ uploads/

# Manual cleanup if needed
rm -rf temp_portfolios/*
rm -rf generated_portfolios/*.zip
```

### Files Not Cleaning Up

**Check**:
1. Verify auto-cleanup is enabled
2. Check file permissions
3. Review error logs
4. Test cleanup script manually

**Debug**:
```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

**Symptoms**:
- Slow portfolio generation
- High memory usage
- Timeouts

**Solution**:
1. Run cleanup script
2. Restart application
3. Check storage usage
4. Optimize cleanup intervals

---

## 📊 Storage Optimization Tips

### 1. Reduce File Sizes

- Compress images in portfolios
- Optimize PDF generation
- Use smaller templates

### 2. Faster Cleanup

- Reduce cleanup intervals
- Clean up immediately after use
- Don't store unnecessary files

### 3. External Storage

For production, consider:
- **AWS S3**: For long-term file storage
- **Cloudinary**: For images and media
- **Database**: For metadata only

---

## 🔄 Migration to External Storage

If you need to scale beyond local storage:

### Option 1: AWS S3

```python
import boto3

s3 = boto3.client('s3')

# Upload to S3
s3.upload_file('portfolio.zip', 'my-bucket', 'portfolios/user123.zip')

# Generate presigned URL for download
url = s3.generate_presigned_url('get_object', 
    Params={'Bucket': 'my-bucket', 'Key': 'portfolios/user123.zip'},
    ExpiresIn=3600)
```

### Option 2: Cloudinary

```python
import cloudinary
import cloudinary.uploader

# Upload file
result = cloudinary.uploader.upload('portfolio.zip', 
    resource_type='raw',
    folder='portfolios')

# Get URL
url = result['secure_url']
```

---

## 📝 Summary

### Current Implementation

✅ **Automatic cleanup after generation**
✅ **Auto-cleanup on startup (1 hour)**
✅ **Manual cleanup script**
✅ **Storage monitoring**
✅ **.gitignore configured**

### Storage Lifecycle

- **temp_portfolios**: Deleted immediately (< 1 minute)
- **generated_portfolios**: Kept for 7 days
- **uploads**: Kept for 30 days
- **analysis_reports**: Kept for 30 days

### Cloud Deployment

- **Streamlit Cloud**: Auto-cleanup prevents accumulation ✅
- **Render/Railway**: Ephemeral storage, resets on restart ✅
- **Docker**: Add cron job for cleanup ✅

---

**Your storage is now optimized for cloud deployment!** 💾✨
