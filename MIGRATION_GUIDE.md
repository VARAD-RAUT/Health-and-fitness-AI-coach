# 🔄 Data Lake to Blob Storage Migration Guide

## Overview

The project has been refactored to **remove Azure Data Lake architecture** and use **single Blob Storage container** for all data.

### What Changed?

| Aspect | Before | After |
|--------|--------|-------|
| **Containers** | 2 (`health-fitness-data`, `health-fitness-lake`) | 1 (`health-fitness-data`) |
| **Zones** | Bronze/Silver/Gold zones | Direct folder structure |
| **Env Var** | `AZURE_STORAGE_CONNECTION_STRING` | `AZURE_STORAGE_CONNECTION_STRING` + `BLOB_CONTAINER_NAME` |
| **Helper Module** | `datalake_helper.py` (complex) | `datalake_helper.py` (thin wrappers) |
| **Blob Paths** | `bronze/silver/gold/...` | Direct paths like `diet-plans/`, `users/`, etc. |

---

## ✅ What's Different?

### 1. **Environment Variables**

**Before:**
```env
AZURE_STORAGE_CONNECTION_STRING=...
# (no container name variable)
```

**After:**
```env
AZURE_STORAGE_CONNECTION_STRING=...
BLOB_CONTAINER_NAME=health-fitness-data
```

---

### 2. **Container Names**

**Before:**
- `health-fitness-data` (for profiles, photos)
- `health-fitness-lake` (for bronze/silver/gold zones)

**After:**
- `health-fitness-data` (for everything)

**Action:** You can **delete** the `health-fitness-lake` container from Azure Portal.

---

### 3. **Blob Storage Paths**

**Before (with zones):**
```
health-fitness-data/profiles/john_doe.json
health-fitness-data/food-photos/john_doe/20260317_120000.jpg

health-fitness-lake/bronze/user-profiles/john_doe.json
health-fitness-lake/bronze/daily-logs/john_doe/2026-03-17.json
health-fitness-lake/silver/food-analysis/john_doe/20260317_120000.json
health-fitness-lake/silver/daily-logs/john_doe/2026-03-17.json
health-fitness-lake/gold/diet-plans/john_doe_2026-03-17.json
health-fitness-lake/gold/workout-plans/john_doe_2026-03-17.json
health-fitness-lake/gold/weekly-reports/john_doe_2026-03-17.json
```

**After (flat structure):**
```
health-fitness-data/
├── users/john_doe.json
├── diet-plans/john_doe.json
├── workout-plans/john_doe.json
├── daily-logs/john_doe/2026-03-17.json
├── food-images/john_doe/20260317_120000.jpg
├── food-analysis/john_doe/20260317_120000.json
└── reports/john_doe.json
```

---

### 4. **Module Function Changes**

#### `blob_helper.py`

**Old functions (removed):**
- `save_profile_blob()` → now `save_profile()`
- `load_profile_blob()` → now `load_profile()`
- `save_food_photo_blob()` → now `save_food_image()`
- `save_generic_blob()`, `load_generic_blob()` → (removed)

**New functions:**
- `save_profile(username, data)` - Save profile
- `load_profile(username)` - Load profile
- `save_food_image(username, datetime, bytes)` - Upload food photo
- `save_diet_plan(username, plan)` - Save diet plan
- `save_workout_plan(username, plan)` - Save workout plan
- `save_daily_log(username, date, log)` - Save daily log
- `load_daily_log(username, date)` - Load single daily log
- `load_daily_logs(username, dates)` - Load multiple daily logs
- `save_food_analysis(username, datetime, analysis)` - Save nutrition analysis
- `save_weekly_report(username, report)` - Save weekly report

#### `datalake_helper.py`

**Old interface (still available for backward compatibility):**
```python
write_bronze_profile(username, data)          # Still works via save_profile()
write_bronze_daily_log(username, date, data)  # Still works via save_daily_log()
write_silver_daily_log(username, date, data)  # Still works via save_daily_log()
read_silver_daily_logs(username, dates)       # Still works via load_daily_logs()
write_silver_food_analysis(username, dt, data) # Still works via save_food_analysis()
write_gold_diet_plan(username, date, plan)    # Still works via save_diet_plan()
write_gold_workout_plan(username, date, plan) # Still works via save_workout_plan()
write_gold_weekly_report(username, date, report) # Still works via save_weekly_report()
```

**How it works:**
- `datalake_helper.py` now contains thin wrappers
- Functions map directly to `blob_helper.py` functions
- No more bronze/silver/gold zones
- **Backward compatible** - existing imports still work

---

## 🔧 Migration Checklist

### For Developers

- [x] Update `blob_helper.py` with new function signatures
- [x] Update `datalake_helper.py` with wrappers
- [x] Update `profile.py` to use `save_profile()` instead of `save_profile_blob()`
- [x] Update `food_analyzer.py` to use `save_food_image()` instead of `save_food_photo_blob()`
- [x] Update `app.py` to use `load_profile()` instead of `load_profile_blob()`
- [x] Update `.env.example` with `BLOB_CONTAINER_NAME`
- [x] Update `README.md` to remove Data Lake references
- [x] Update all documentation

### For Operations

**If you have existing data in the old structure:**

1. **Backup old data** from `health-fitness-lake` container
2. **Migrate manually** (if needed):
   - Download from old paths
   - Re-upload to new paths
   - Delete `health-fitness-lake` container
3. **Or start fresh:**
   - Delete `health-fitness-lake` container
   - Only use `health-fitness-data` going forward

---

## 📝 Code Examples

### Before (Old Code)

```python
from utils.blob_helper import save_profile_blob, load_profile_blob
from utils.datalake_helper import write_bronze_profile

# Save profile
save_profile_blob(username, profile_data)
write_bronze_profile(username, profile_data)  # Redundant

# Load profile
profile = load_profile_blob(username)
```

### After (New Code)

```python
from utils.blob_helper import save_profile, load_profile

# Save profile (single call)
save_profile(username, profile_data)

# Load profile
profile = load_profile(username)
```

---

## 🔌 API Compatibility

The `datalake_helper.py` functions **still exist** for backward compatibility, but they're now wrappers:

```python
# These old calls still work:
from utils.datalake_helper import write_bronze_profile, write_silver_daily_log

write_bronze_profile(username, data)        # → calls save_profile()
write_silver_daily_log(username, date, data) # → calls save_daily_log()
```

**This means:** Existing code continues to work without changes, but the underlying storage is now unified.

---

## 🗑️ What Can Be Deleted

### Azure Portal
- ✅ Delete container `health-fitness-lake` (no longer needed)

### Python Files
- ✅ Could delete old function calls like `save_profile_blob()` (now `save_profile()`)
- ✅ Could optimize imports in modules to use new names
- ⚠️ Do NOT delete `datalake_helper.py` (still used by modules for backward compatibility)

---

## 📊 Blob Storage Usage

### Before
- Container 1: `health-fitness-data` (small)
- Container 2: `health-fitness-lake` (large with bronze/silver/gold)
- **Total:** 2 containers

### After
- Container 1: `health-fitness-data` (consolidated)
- **Total:** 1 container
- **Benefit:** Simpler management, no zone confusion

---

## 🎯 Benefits of This Change

1. **Simpler Architecture** - No more bronze/silver/gold zones
2. **Easier to Understand** - Flat folder structure is intuitive
3. **Fewer Azure Resources** - 1 container instead of 2
4. **Clearer Code** - Direct function names instead of zone-based names
5. **Lower Cost** - One container = lower management overhead
6. **Backward Compatible** - Old code still works via wrapper functions

---

## ⚠️ Important Notes

### Session State Loading
The sidebar feature "Load Saved Profile" still works:
- Loads from `users/{username}.json`
- Same functionality, different path
- User experience unchanged

### Environment Variables
You **MUST** add `BLOB_CONTAINER_NAME` to `.env`:
```env
BLOB_CONTAINER_NAME=health-fitness-data
```

Without this, the app will try to use the default: `health-fitness-data`

### Existing Users
- Profiles saved with old code in `profiles/{username}.json` won't be found
- New profiles saved in `users/{username}.json`
- **You may need to:**
  - Re-save user profiles, OR
  - Manually migrate old paths to new paths in Azure Portal

---

## 🔍 Testing After Migration

1. **Test Profile Save:**
   ```
   Create new profile → Check Blob Storage for users/{username}.json
   ```

2. **Test Profile Load:**
   ```
   Save profile → Load it back via sidebar → Verify it loads correctly
   ```

3. **Test Diet Plan:**
   ```
   Generate plan → Check Blob Storage for diet-plans/{username}.json
   ```

4. **Test Food Analysis:**
   ```
   Upload photo → Check food-images/ and food-analysis/ folders
   ```

5. **Test Daily Log:**
   ```
   Log daily activity → Check daily-logs/{username}/{date}.json
   ```

---

## 📚 Related Documentation

- [README.md](README.md) - Updated with new paths
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Still valid, only 1 container needed
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Updated checklist

---

## ❓ FAQ

**Q: Do I need to delete the old `health-fitness-lake` container?**  
A: Not immediately, but you can. It won't be used anymore. Back it up first if you need the historical data.

**Q: Will old code still work?**  
A: Yes! `datalake_helper.py` functions act as wrappers and maintain the same interface.

**Q: Can I migrate existing data?**  
A: Yes, manually via Azure Portal or using migration scripts (not provided). For development, just start fresh.

**Q: Where did the zone concept go?**  
A: Removed completely. Files are stored in direct folders like `diet-plans/`, `users/`, etc.

**Q: Is this a breaking change?**  
A: No, due to backward-compatible wrappers in `datalake_helper.py`.

---

**Questions?** Check [README.md](README.md) or [SETUP_GUIDE.md](SETUP_GUIDE.md) for more details.
