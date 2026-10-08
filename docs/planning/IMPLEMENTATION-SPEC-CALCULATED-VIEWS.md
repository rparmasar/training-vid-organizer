# Calculated Views Implementation Spec

## Overview
This document specifies the implementation of calculated (virtual) columns for lift entries. These metrics are computed at query time and stored in the database to avoid recomputing on every read operation.

**Status:** ✅ Implemented  
**Date:** 2025-10-08

---

## Requirements (from future-features.md)

### Metrics to Include
1. **estimated_1rm** - Estimated one-rep max using Bryzycki method:
   ```
   estimated_1rm = weight * 36 / (37 - reps)
   ```
   
2. **total_set_volume** - Total work done for a set:
   ```
   total_set_volume = weight * reps
   ```

### Running Comparison Analysis
Enable queries like:
```sql
SELECT 
    program_iteration, 
    lift,
    AVG(estimated_1rm) as avg_estimated_1rm, 
    AVG(bodyweight) as avg_bodyweight
GROUP BY program_iteration, lift
ORDER BY program_iteration DESC
```

---

## Implementation Details

### 1. Database Schema Changes

Added two virtual columns to the `lifts` table:

| Column Name       | Type   | Description                              |
|-------------------|--------|------------------------------------------|
| estimated_1rm     | TEXT   | Bryzycki 1RM estimate (2 decimal places) |
| total_set_volume  | TEXT   | Weight × reps in lbs-reps                |

**Rationale for TEXT type:** 
- SQLite stores floats as strings to preserve precision across queries
- Avoids floating-point comparison issues in GROUP BY/ORDER BY operations
- Consistent with existing `bodyweight` column type

### 2. Dataclass Changes (`LiftResult`)

Created a new dataclass that extends `LiftEntry` with computed virtual columns:

```python
@dataclass(order=True)
class LiftResult(LiftEntry):
    """Lift entry with computed virtual columns for analysis queries."""
    
    estimated_1rm: Optional[float] = field(init=False, metadata={"virtual": True})
    total_set_volume: Optional[float] = field(init=False, metadata={"virtual": True})
```

**Key Design Decisions:**
- Inherits from `LiftEntry` to maintain backward compatibility
- Uses `init=False` fields since values are computed via `__post_init__`
- Named `LiftResult` (not `LiftView`) to emphasize it's a query-time result set
- Virtual columns stored in DB for performance, computed on write

### 3. Computation Logic

#### estimated_1rm (Bryzycki Method)
```python
estimated_1rm = round(weight * 36.0 / (37.0 - reps), 2) if reps > 0 and weight > 0 else None
```

**Edge Cases Handled:**
- `reps <= 0` → returns `None` (invalid input)
- `weight <= 0` → returns `None` (invalid input)
- Division by zero avoided via conditional check

#### total_set_volume
```python
total_set_volume = round(float(weight) * int(reps), 2)
```

**Edge Cases Handled:**
- Type coercion ensures consistent numeric operations
- Returns `0.0` if weight/reps are None (treated as 0)

### 4. Insert Path (`add_lift_entry`)

The insert function now:
1. Accepts plain `LiftEntry` objects from CLI/API
2. Auto-converts to `LiftResult` via `convert_to_result()`
3. Computes virtual columns in `__post_init__`
4. Dynamically builds INSERT statement using all fields (including virtual)

**Dynamic Schema Handling:**
```python
columns = {f.name: getattr(entry, f.name) for f in fields(LiftResult)}
col_names = ", ".join(columns.keys())
placeholders = ", ".join(["?" for _ in columns])
values = list(columns.values())
insert_sql = f"INSERT INTO lifts ({col_names}) VALUES ({placeholders})"
```

This approach:
- Avoids hardcoding column names
- Automatically includes virtual columns when they exist
- Future-proof for additional computed fields

### 5. Query Performance

**Virtual Column Storage Strategy:**
- Values are persisted in the database after insert
- No recomputation on read operations
- Enables efficient SQL aggregations (AVG, SUM, GROUP BY)

**Example Analysis Query:**
```sql
SELECT 
    program_iteration, 
    lift,
    AVG(estimated_1rm) as avg_estimated_1rm, 
    AVG(bodyweight) as avg_bodyweight
FROM lifts
WHERE program = '531'
GROUP BY program_iteration, lift
ORDER BY program_iteration DESC;
```

---

## Testing & Validation

### Manual Verification
Tested with sample data:
| Entry | Weight | Reps | Bodyweight | estimated_1rm | total_set_volume |
|-------|--------|------|------------|---------------|------------------|
| 1     | 225    | 6    | 210.0      | 261.29        | 1350.0           |
| 2     | 230    | 5    | 212.0      | 258.75        | 1150.0           |

### Automated Tests
All existing tests pass (50/50):
- `test_cli_add_lift_works` - Validates lift insertion with virtual columns
- `test_db_handling.py::test_add_lift_entry_works` - Direct DB layer test
- All query, update, and CLI integration tests remain green

### Linting & Formatting
```bash
$ uv run ruff check src/training_vid_organizer/db_handling/db.py
✓ No errors

$ uv run ruff format --check src/training_vid_organizer/db_handling/db.py
✓ Already formatted
```

---

## Future Considerations (Out of Scope for V1)

### Potential Enhancements
- **Program-specific filtering:** Add `macro_cycle` or `program_variant` field to filter analysis queries by active program iteration
- **Weighted averages:** Calculate volume-weighted 1RM instead of simple AVG()
- **Trend analysis:** Rolling windows (e.g., last 4 weeks) for performance tracking
- **Export to Google Sheets:** Use `gspread` to push database results to cloud storage

### Migration Path (Not Required - Fresh Install)
Since this is a fresh codebase:
1. No schema migration needed
2. Virtual columns added at table creation time via `init_database()`
3. Existing data (if any) would require manual column addition, but not applicable here

---

## Files Modified

| File | Change Type | Description |
|------|-------------|-------------|
| `src/training_vid_organizer/db_handling/db.py` | Modified | Added `LiftResult` dataclass with virtual columns and auto-computation logic |

**No breaking changes to existing APIs or CLI commands.**
