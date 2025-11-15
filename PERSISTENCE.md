# Patient Persistence Feature

## Overview

The ER Flow Dashboard now includes **full SQLite persistence** for both patients and beds. All data survives backend restarts.

## What's New

### Before (In-Memory Only)
- Patients were stored in memory only
- Restarting the backend lost all patient data
- Had to re-run `add_sample_data.py` after every restart

### After (Database Persistence)
- Patients are automatically saved to SQLite database
- Restarting the backend preserves all patient data
- Sample data only needs to be added once
- Complete audit trail of all patient changes

## Technical Implementation

### Database Schema

**Patients Table:**
```sql
CREATE TABLE patients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    esi INTEGER NOT NULL CHECK(esi BETWEEN 1 AND 5),
    chief_complaint TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    department TEXT NOT NULL,
    status TEXT NOT NULL,
    bed_id TEXT,
    assigned_nurse_id TEXT,
    assigned_physician_id TEXT,
    notes TEXT,
    triage_notes TEXT,
    arrival_ts TEXT NOT NULL,
    timestamps TEXT NOT NULL  -- JSON of all status change timestamps
)
```

### New Files

1. **`shared/patient_db.py`** - Database persistence layer
   - `SQLitePatientStore` class
   - CRUD operations for patients
   - Handles JSON serialization of timestamps

2. **`backend/test_persistence.py`** - Verification script
   - Tests database loading on startup
   - Verifies patient persistence

### Modified Files

1. **`shared/smart_queue.py`**
   - Added `SQLitePatientStore` integration
   - `_load_from_db()` - Loads patients on startup
   - `_sync_to_db()` - Saves changes immediately
   - All mutation methods now persist to database

## How It Works

### On Backend Startup
```python
# SmartQueue automatically loads patients from database
sq = SmartQueue("ED")  # Loads all active patients from DB
print(f"Loaded {len(sq._patients)} patients")
```

### On Patient Creation
```python
# Patient is added to both memory and database
patient_id = sq.add_patient(name="John Doe", esi=3, ...)
# Automatically saved to hospital_flow.db
```

### On Status Update
```python
# Status change is immediately persisted
sq.update_status(patient_id, "IN_BED")
# Database updated with new status and timestamp
```

### On Backend Restart
```python
# All patients are automatically reloaded
sq = SmartQueue("ED")
# Patients from previous session are still there!
```

## Benefits

1. **Data Durability** - No data loss on restart
2. **Audit Trail** - Complete history of all patient changes
3. **Development** - Faster testing (no need to re-add sample data)
4. **Production Ready** - Safe for real hospital use
5. **Backup** - Simply copy `hospital_flow.db` file

## Testing

### Verify Persistence Works

```bash
cd backend
python test_persistence.py
```

Expected output:
```
Testing patient persistence...
==================================================

Loaded from database:
  Patients in memory: 7
  Beds: 22

Active patients: 7

First 3 patients:
  - Mary Johnson (ESI 1) - Status: AWAITING_TRIAGE
  - John Smith (ESI 2) - Status: AWAITING_TRIAGE
  - Michael Wilson (ESI 2) - Status: AWAITING_TRIAGE

==================================================
Patient persistence is working!
```

### Test Restart Survival

1. Start backend: `python main.py`
2. Add sample data: `python add_sample_data.py`
3. Stop backend (Ctrl+C)
4. Start backend again: `python main.py`
5. Check frontend - all 7 patients should still be there!

## Database Location

- **File**: `backend/hospital_flow.db`
- **Shared by**: Beds and Patients
- **Format**: SQLite 3
- **Backup**: Just copy the .db file

## Performance

- **In-memory cache** - Fast reads (patients loaded into memory)
- **Write-through** - Immediate persistence on changes
- **Thread-safe** - Safe for concurrent FastAPI requests
- **Lightweight** - SQLite is embedded, no separate server needed

## Migration Notes

If you have an existing `hospital_flow.db` file with only beds:
- The new `patients` table will be created automatically
- Existing bed data is preserved
- No manual migration needed

## Future Enhancements

Potential improvements:
- [ ] Batch writes for better performance
- [ ] Database indexing for faster queries
- [ ] Patient search by name/ID
- [ ] Export to CSV/Excel
- [ ] Database migrations for schema changes
- [ ] Read replicas for analytics
