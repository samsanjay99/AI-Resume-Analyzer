# Cleanup System Workflow

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SMART RESUME AI                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Resume     │  │  Portfolio   │  │    Upload    │     │
│  │  Analyzer    │  │  Generator   │  │   Handler    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌──────────────────────────────────────────────────┐      │
│  │         TEMPORARY FILE STORAGE                   │      │
│  │                                                  │      │
│  │  • temp_portfolios/  (35.2 MB, 15 folders)     │      │
│  │  • uploads/          (5.9 MB, 57 files)        │      │
│  │  • generated_portfolios/ (33.1 MB, 15 files)   │      │
│  │                                                  │      │
│  │  Total: 87 items, 74.2 MB                      │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ (Files accumulate over time)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              CLEANUP SYSTEM (Independent)                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         cleanup_temp_files.py                       │   │
│  │                                                     │   │
│  │  1. Scan directories                               │   │
│  │  2. Sort by age (newest first)                     │   │
│  │  3. Keep N most recent (default: 5)               │   │
│  │  4. Check age threshold (default: 24h)            │   │
│  │  5. Delete old files                               │   │
│  │  6. Log results                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      auto_cleanup_service.py                        │   │
│  │                                                     │   │
│  │  • Runs every 6 hours                              │   │
│  │  • Calls cleanup_temp_files.py                     │   │
│  │  • Logs to cleanup_service.log                     │   │
│  │  • Runs in background                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLEAN STORAGE                            │
│                                                             │
│  • ~15 items (5 per directory)                             │
│  • ~15-20 MB storage                                        │
│  • Production ready                                         │
│  • No bloat                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Cleanup Decision Flow

```
                    START CLEANUP
                         │
                         ▼
              ┌──────────────────────┐
              │  Scan Directory      │
              │  (temp_portfolios,   │
              │   uploads, etc.)     │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Get All Items       │
              │  with Creation Time  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Sort by Age         │
              │  (Newest First)      │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Keep N Most Recent  │
              │  (Default: 5)        │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  For Each Remaining  │
              │  Item...             │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Age > Threshold?    │
              │  (Default: 24h)      │
              └──────────┬───────────┘
                         │
                ┌────────┴────────┐
                │                 │
               YES               NO
                │                 │
                ▼                 ▼
    ┌──────────────────┐  ┌──────────────────┐
    │  DELETE FILE     │  │  KEEP FILE       │
    │  Log deletion    │  │  Log keeping     │
    └──────────────────┘  └──────────────────┘
                │                 │
                └────────┬────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Show Statistics     │
              │  - Deleted count     │
              │  - Kept count        │
              │  - Space freed       │
              └──────────┬───────────┘
                         │
                         ▼
                    END CLEANUP
```

---

## File Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    FILE LIFECYCLE                           │
└─────────────────────────────────────────────────────────────┘

Time: 0h (Created)
│
│  ┌─────────────────────────────────────────┐
│  │  FILE CREATED                           │
│  │  Status: NEW                            │
│  │  Action: KEEP (always safe)             │
│  └─────────────────────────────────────────┘
│
▼

Time: 1-23h (Recent)
│
│  ┌─────────────────────────────────────────┐
│  │  FILE AGING                             │
│  │  Status: RECENT                         │
│  │  Action: KEEP (within threshold)        │
│  └─────────────────────────────────────────┘
│
▼

Time: 24h (Threshold)
│
│  ┌─────────────────────────────────────────┐
│  │  THRESHOLD REACHED                      │
│  │  Status: OLD                            │
│  │  Check: Is it in top N recent?          │
│  └─────────────────────────────────────────┘
│
├─────────────┬─────────────┐
│             │             │
▼             ▼             ▼
In Top N    Not in Top N   
│             │             
│             ▼             
│  ┌─────────────────────────────────────────┐
│  │  ELIGIBLE FOR DELETION                  │
│  │  Status: OLD + NOT RECENT               │
│  │  Action: DELETE                         │
│  └─────────────────────────────────────────┘
│             │
│             ▼
│  ┌─────────────────────────────────────────┐
│  │  FILE DELETED                           │
│  │  - Logged                               │
│  │  - Space freed                          │
│  │  - Statistics updated                   │
│  └─────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────┐
│  FILE KEPT                              │
│  Status: OLD BUT RECENT                 │
│  Action: KEEP (protected by top N)      │
└─────────────────────────────────────────┘
```

---

## Usage Modes

### Mode 1: Manual Cleanup

```
USER
  │
  │ Runs: cleanup_temp_files.bat
  ▼
┌─────────────────────────────┐
│  cleanup_temp_files.py      │
│                             │
│  1. Scan directories        │
│  2. Show statistics         │
│  3. Delete old files        │
│  4. Show results            │
└─────────────────────────────┘
  │
  │ Output: Console + Log
  ▼
USER sees results immediately
```

### Mode 2: Stats Only

```
USER
  │
  │ Runs: check_storage.bat
  ▼
┌─────────────────────────────┐
│  cleanup_temp_files.py      │
│  --stats-only               │
│                             │
│  1. Scan directories        │
│  2. Show statistics         │
│  3. NO DELETION             │
└─────────────────────────────┘
  │
  │ Output: Statistics only
  ▼
USER sees current state
(Safe preview mode)
```

### Mode 3: Auto Service

```
USER
  │
  │ Runs: start_auto_cleanup.bat
  ▼
┌─────────────────────────────┐
│  auto_cleanup_service.py    │
│                             │
│  Runs in background         │
│  Every 6 hours              │
└─────────────────────────────┘
  │
  │ Every 6 hours
  ▼
┌─────────────────────────────┐
│  cleanup_temp_files.py      │
│                             │
│  1. Scan directories        │
│  2. Delete old files        │
│  3. Log results             │
└─────────────────────────────┘
  │
  │ Output: cleanup_service.log
  ▼
Automatic maintenance
(No user interaction needed)
```

---

## Safety Mechanisms

```
┌─────────────────────────────────────────────────────────────┐
│                    SAFETY LAYERS                            │
└─────────────────────────────────────────────────────────────┘

Layer 1: Recent File Protection
┌─────────────────────────────────────────┐
│  Top N files NEVER deleted              │
│  (Default: 5 most recent)               │
│  Even if they're old                    │
└─────────────────────────────────────────┘
              │
              ▼
Layer 2: Age Threshold
┌─────────────────────────────────────────┐
│  Only files older than threshold        │
│  (Default: 24 hours)                    │
│  Recent files always safe               │
└─────────────────────────────────────────┘
              │
              ▼
Layer 3: Detailed Logging
┌─────────────────────────────────────────┐
│  Every action logged                    │
│  - What was deleted                     │
│  - What was kept                        │
│  - Why (age, size, etc.)                │
└─────────────────────────────────────────┘
              │
              ▼
Layer 4: Error Handling
┌─────────────────────────────────────────┐
│  Graceful error handling                │
│  - Continues on errors                  │
│  - Logs errors                          │
│  - Doesn't crash                        │
└─────────────────────────────────────────┘
              │
              ▼
Layer 5: Stats-Only Mode
┌─────────────────────────────────────────┐
│  Preview before deletion                │
│  - See what would be deleted            │
│  - No actual deletion                   │
│  - Safe testing                         │
└─────────────────────────────────────────┘
```

---

## Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│              SMART RESUME AI APPLICATION                    │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  app.py  │  │ utils/   │  │ config/  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│                                                             │
│  NO CHANGES REQUIRED ✅                                     │
│  Works independently                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ (No integration needed)
                            │
┌─────────────────────────────────────────────────────────────┐
│              CLEANUP SYSTEM (Standalone)                    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  cleanup_temp_files.py                               │  │
│  │  - Scans temp directories                            │  │
│  │  - Deletes old files                                 │  │
│  │  - Independent operation                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  auto_cleanup_service.py                             │  │
│  │  - Runs in background                                │  │
│  │  - Scheduled execution                               │  │
│  │  - No app dependency                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

✅ **Independent System**: No code changes to your application  
✅ **Safe Operation**: Multiple safety layers protect recent files  
✅ **Flexible**: Manual, automatic, or scheduled modes  
✅ **Well Documented**: Complete guides and examples  
✅ **Production Ready**: Can run as background service  

---

**Version**: 1.0  
**Status**: Production Ready ✅
