# Calculated Views Implementation Spec

## Overview
Add computed metrics (`estimated_1rm` and `total_set_volume`) as virtual columns to the training database. Values are calculated at insert time, stored for fast reads, and recomputed only when new data is added.

---

## 1. Dataclass Structure

### LiftEntry (unchanged)
Base model for input/insertion. Keep `entry_id` here for backward compatibility with existing code.

```python
@dataclass
class LiftEntry:
    date: str
    program: str
    program_iteration: int
    lift: str
    weight: int
    reps: int
    bodyweight: float | None = None
    top_set: bool = False
    warm_up_set: bool = False
    reps_in_reserve: int | None = None
    filename: Path | None = None
    entry_id: int | None = None  # kept for backward compat
```

### LiftResult (new)
Computed view with virtual columns. Inherits all `LiftEntry` fields plus computed metrics.

```python
@dataclass
class LiftResult(LiftEntry):
    """Computed view of lift entry with virtual columns."""
    
    estimated_1rm: float | None = field(init=False, default=None)
    total_set_volume: float | None = field(init=False, default=0.0)
```

---

## 2. Insert-Time Computation (db.py)

### compute_virtual_columns()
Takes a `LiftEntry`, computes metrics, returns a new `LiftResult` instance.

**Formula:**
- `estimated_1rm = weight * 36 / (37 - reps)` (Bryzycki method)
- `total_set_volume = weight * reps`

```python
def compute_virtual_columns(entry: LiftEntry) -> LiftResult:
    """Calculate estimated_1rm and total_set_volume for a lift entry."""
    
    weight = float(entry.weight) if entry.weight else 0.0
    reps = int(entry.reps) if entry.reps else 0
    
    # Bryzycki method: w * (36 / (37 - r))
    estimated_1rm = round(weight * 36.0 / (37.0 - reps), 2) if reps > 0 and weight > 0 else None
    total_set_volume = round(float(weight) * int(reps), 2)
    
    return LiftResult(
        date=entry.date,
        program=entry.program,
        program_iteration=entry.program_iteration,
        lift=entry.lift,
        weight=int(entry.weight),
        reps=int(entry.reps),
        bodyweight=entry.bodyweight,
        top_set=entry.top_set,
        warm_up_set=entry.warm_up_set,
        reps_in_reserve=entry.reps_in_reserve,
        filename=entry.filename,
        entry_id=entry.entry_id,  # pass through for backward compat
        estimated_1rm=estimated_1rm,
        total_set_volume=total_set_volume,
    )
```

---

## 3. Insert Flow (db.py)

### add_lift_entry() & add_session_entry()
Accept both `LiftEntry` and `LiftResult`. Auto-convert plain entries before insert:

```python
def _ensure_result(entry: LiftEntry | LiftResult) -> LiftResult:
    """Convert LiftEntry to LiftResult if needed."""
    if isinstance(entry, LiftEntry) and not isinstance(entry, LiftResult):
        return compute_virtual_columns(entry)
    return entry  # already a LiftResult or compatible dict

# Inside add_lift_entry():
entry = _ensure_result(entry)
columns = {f.name: getattr(entry, f.name) for f in fields(LiftEntry)}
# ... rest of insert logic uses columns.values()
```

---

## 4. Query Module (query.py)

### fetch_lifts() Update
Return `LiftResult` objects with stored virtual column values mapped from DB rows:

```python
def fetch_lifts(db_path: Path, filters: dict[str, Any], limit: int | None = 100) -> list[LiftResult]:
    # ... existing SQL query logic ...
    
    for row in rows:
        entry_dict = dict(zip(columns, row))
        
        # Map 'id' column to 'entry_id' field (backward compat)
        if "id" in entry_dict:
            entry_dict["entry_id"] = int(entry_dict.pop("id"))
        
        # Convert stored virtual columns from DB values
        if "estimated_1rm" in entry_dict and "total_set_volume" in entry_dict:
            entry_dict["estimated_1rm"] = float(entry_dict["estimated_1rm"]) if entry_dict["estimated_1rm"] else None
            entry_dict["total_set_volume"] = float(entry_dict["total_set_volume"])
        
        entries.append(LiftResult(**entry_dict))
    
    return entries
```

---

## 5. Analysis Helper (query.py)

### analyze_lifts() - Pure Function
Handles its own DB connection, returns structured results for CLI rendering:

```python
def analyze_lifts(
    db_path: Path,
    metric: str = "estimated_1rm"
) -> list[tuple[int, str, float | None, float | None]]:
    """Run program iteration comparison analysis.
    
    Returns list of (program_iteration, lift, avg_metric_value, avg_bodyweight).
    """
    
    if metric == "estimated_1rm":
        col = "estimated_1rm"
        alias = "avg_estimated_1rm"
    elif metric == "total_set_volume":
        col = "total_set_volume"
        alias = "avg_total_set_volume"
    else:
        raise ValueError(f"Unknown metric: {metric}")
    
    query = f"""
        SELECT 
            program_iteration, 
            lift,
            AVG({col}) as {alias}, 
            AVG(bodyweight) as avg_bodyweight
        FROM lifts
        WHERE {col} IS NOT NULL
        GROUP BY program_iteration, lift
        ORDER BY program_iteration DESC
    """
    
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        
        rows = cursor.fetchall()
        
        if not rows or not cursor.description:
            return []
        
        columns = [desc[0] for desc in cursor.description]
        result_columns = ["program_iteration", "lift", alias, "avg_bodyweight"]
        
        results = []
        for row in rows:
            entry_dict = dict(zip(columns, row))
            results.append((
                int(entry_dict["program_iteration"]),
                str(entry_dict["lift"]),
                float(entry_dict[alias]) if entry_dict[alias] else None,
                float(entry_dict["avg_bodyweight"]) if entry_dict["avg_bodyweight"] else None
            ))
        
        return results
        
    finally:
        conn.close()
```

---

## 6. CLI Wrapper (cli.py)

### analyze Command
Follows existing pattern: pure helper first, then decorator wrapper.

```python
@app.command("analyze")
def analyze(
    metric: Annotated[str, Argument(help="metric to analyze (estimated_1rm | total_set_volume)")] = "",
    db_path: Annotated[
        str | None, Option("--db-path", "-d", help="override database path")
    ] = None,
):
    """Run comparison analysis across program iterations."""
    
    effective_db_path = db_path or get_config_paths(default_db_path=DB_DEFAULT)[0]
    
    # Call pure helper function (handles connection internally)
    results = analyze_lifts(effective_db_path, metric)
    
    if not results:
        console.print("[dim]No data found for analysis.[/dim]")
        return
    
    # Render as Rich table (same pattern as list_lifts)
    table = Table(box=None, show_header=True, header_style="bold")
    table.add_column("Iteration", style="cyan")
    table.add_column("Lift", style="magenta")
    table.add_column(f"Avg {metric.replace('_', ' ').title()}", justify="right")
    table.add_column("Avg Bodyweight (lbs)", justify="right")
    
    for iteration, lift, metric_val, bw in results:
        table.add_row(
            str(iteration),
            lift,
            f"{metric_val:.2f}" if metric_val is not None else "-",
            f"{bw:.1f}" if bw is not None else "-"
        )
    
    console.print(table)
```

---

## 7. Migration Notes

- **No ALTER TABLE needed**: Virtual columns are computed at insert time and stored as REAL fields.
- **Backward compatible**: Existing queries continue to work; new fields are optional.
- **Storage overhead**: Minimal (2 extra REAL columns per row).
- **Read performance**: Stored values avoid recomputation on every query.

---

## 8. Usage Examples

```bash
# Initialize database (auto-includes virtual column support)
tvo init

# View lifts with computed metrics
tvo list lifts --limit 20

# Analyze estimated 1RM progression across iterations
tvo analyze estimated_1rm

# Analyze total set volume progression across iterations  
tvo analyze total_set_volume
```

---

## 9. Future Enhancements (Optional)

- Add `--macro-cycle` flag to filter by program name + iteration range
- Export analysis results as CSV/JSON via `tvo export analyze --metric=...`
- Add more computed metrics (e.g., RPE-adjusted volume, trend indicators)
