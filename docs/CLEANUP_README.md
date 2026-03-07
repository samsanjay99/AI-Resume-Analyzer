# 🧹 Temporary Files Cleanup System

## Quick Start

### 1️⃣ Check Current Storage

```bash
# Windows
check_storage.bat

# Linux/Mac
python cleanup_temp_files.py --stats-only
```

### 2️⃣ Run Manual Cleanup

```bash
# Windows
cleanup_temp_files.bat

# Linux/Mac
python cleanup_temp_files.py
```

### 3️⃣ Start Auto Cleanup (Recommended)

```bash
# Windows
start_auto_cleanup.bat

# Linux/Mac
python auto_cleanup_service.py
```

---

## What Gets Cleaned?

- `temp_portfolios/` - Temporary portfolio folders
- `uploads/` - Uploaded resume files
- `generated_portfolios/` - Generated ZIP files

---

## Default Settings

- ⏰ **Runs**: Every 6 hours (auto mode)
- 🗑️ **Deletes**: Files older than 24 hours
- ✅ **Keeps**: 5 most recent items always safe

---

## Need More Control?

See [CLEANUP_GUIDE.md](CLEANUP_GUIDE.md) for:
- Custom configurations
- Production deployment
- Troubleshooting
- Advanced options

---

## Safety

✅ Recent files are NEVER deleted  
✅ Shows what will be deleted before doing it  
✅ Detailed logs of all operations  
✅ Can run in stats-only mode (no deletion)

---

## Quick Commands

```bash
# Just check, don't delete
python cleanup_temp_files.py --stats-only

# Delete files older than 48 hours
python cleanup_temp_files.py --max-age 48

# Keep 10 most recent files
python cleanup_temp_files.py --keep-recent 10

# Aggressive cleanup (1 hour old, keep 2)
python cleanup_temp_files.py --aggressive
```

---

**Status**: ✅ Production Ready  
**No Code Changes Required**: Works independently
