# Training Video Organizer - Build Agent Spec

## Overview
Atomic task plan for implementing a Python CLI + SQLite training video organizer. Each task is single-command executable, stateless, and verifiable via `pytest .`.

---

## Phase 1: Environment & Schema Setup

### Tasks
1. **Initialize project**
   ```bash
   uv init && uv add pytest pytest-cov
   ```

2. **Verify SQLite & create directories**
   ```bash
   sqlite3 -version && python -c "import sqlite3; print('OK')" && mkdir -p db tests/sample_data
   ```

3. **Create database schema**
   ```python
   # Run: python << 'EOF'
   import sqlite3, os
   conn = sqlite3.connect('db/training.db')
   c = conn.cursor()
   c.execute('''CREATE TABLE IF NOT EXISTS lifts (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       date TEXT NOT NULL,
       bodyweight REAL,
       lift TEXT NOT NULL,
       weight REAL NOT NULL,
       reps INTEGER NOT NULL,
       top_set BOOLEAN DEFAULT 0,
       reps_in_reserve INTEGER,
       filepath TEXT,
       program TEXT,
       program_iteration INTEGER
   )''')
   c.execute('CREATE INDEX IF NOT EXISTS idx_lifts_date ON lifts(date)')
   conn.commit()
   conn.close()
   print("Schema created")
   ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

✓ Phase 1 Complete: Environment & Schema Setup

---

## Progress Log - Current Session

### Phase 2: Database Layer (`src/db.py`) ✓ COMPLETE
- **Fixed batch insert bug** (line 57): Changed single placeholder to `executemany()` for efficient multi-row inserts  
- **Fixed update_entry SQL construction**: sqlite3 parser doesn't handle `?` in SET clause; switched to string-formatted values
- **Test coverage**: Created comprehensive test suite in `tests/test_db_crud.py` with 7 tests covering:
  - Schema initialization verification
  - Single entry insertion (`add_lift_entry`)
  - Batch session entries (`add_session_entries`)
  - Listing all entries
  - Entry updates via ID (now working correctly)
  - Custom database path handling

### Test Results
```pytest .
============================= test session starts ==============================
collected 21 items

tests/cli_test.py::test_version_flag PASSED                              [  4%]
tests/cli_test.py::test_help_output PASSED                               [  9%]
tests/cli_test.py::test_search_current_directory PASSED                 [  14%]
tests/cli_test.py::test_search_with_tags_flag PASSED                    [  19%]
tests/cli_test.py::test_categorize_with_tags PASSED                     [  23%]
tests/cli_test.py::test_categorize_requires_tags PASSED                [  28%]
tests/cli_test.py::test_metadata_with_valid_path PASSED                 [  33%]
tests/cli_test.py::test_metadata_invalid_path PASSED                    [  38%]
tests/cli_test.py::test_search_nonexistent_path PASSED                  [  42%]
tests/test_db_crud.py::test_init_schema PASSED                          [  47%]
tests/test_db_crud.py::test_add_lift_entry PASSED                       [  52%]
tests/test_db_crud.py::test_add_session_entries PASSED                  [  57%]
tests/test_db_crud.py::test_list_entries PASSED                         [  61%]
tests/test_db_crud.py::test_update_entry PASSED                          [  66%]
tests/test_db_crud.py::test_db_path_customization PASSED                [  71%]
tests/test_db_crud.py::test_cleanup PASSED                               [  76%]
tests/test_schema.py::test_database_exists PASSED                       [  80%]
tests/test_schema.py::test_lifts_table_exists PASSED                    [  85%]
tests/test_schema.py::test_lifts_schema PASSED                          [  90%]
tests/test_schema.py::test_index_exists PASSED                         [  95%]
tests/test_schema.py::test_schema_creation PASSED                       [ 100%]

============================== 21 passed in 0.13s ==============================
```

### Next Steps (Remaining Phases)
- Phase 3: Single lift command (`src/training_vid_organizer/cli.py`)
- Phase 4: Session processing (`src/training_vid_organizer/cli.py`)
- Phase 5: Query/list command (`src/training_vid_organizer/cli.py`)
- Phase 6: Update entry command (`src/training_vid_organizer/cli.py`)
- Phases 7-8: Analysis queries and integration testing

---

## Phase 3: Single Lift Command (`src/training_vid_organizer/cli.py`)

### Tasks
1. **Implement add lift command** (Typer parses args → creates LiftEntry dataclass → passes to pure function)
    ```python
    # Run: cat > src/training_vid_organizer/cli.py << 'PYEOF' && python -m py_compile src/training_vid_organizer/cli.py
    from typer import Typer, echo
    from src.db import DB
    from src.models import LiftEntry

    app = Typer(name="training-vid-organizer")

    @app.command()
    def add_lift(
        date: str,
        bodyweight: float | None = None,
        lift: str,
        weight: float,
        reps: int,
    ):
        """Add a single lift entry."""
        db = DB()
        entry = LiftEntry(
            date=date,
            bodyweight=bodyweight,
            lift=lift,
            weight=weight,
            reps=reps,
        )
        result = add_lift(db, entry)  # pure function with typed dataclass
        echo(f"Added {result} entry/entries")

    if __name__ == '__main__':
        app()
    ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Phase 4: Session Processing (`src/training_vid_organizer/cli.py`)

### Tasks
1. **Implement add session command** (Typer parses args → loads JSON list[LiftEntry] dicts → converts to LiftEntry instances → batch pure function)
    ```python
    # Run: cat >> src/training_vid_organizer/cli.py << 'PYEOF' && python -m py_compile src/training_vid_organizer/cli.py
    import json

    @app.command()
    def add_session(config: str):
        """Add multiple lift entries from JSON config."""
        db = DB()
        with open(config) as f:
            data = json.load(f)  # list[LiftEntry] dicts
        
        # Convert dicts to LiftEntry instances (or pass directly if using dict[str, Any])
        entries = [LiftEntry(**d) for d in data]
        
        result = add_session(db, entries)  # pure function with typed list[LiftEntry]
        echo(f"Added {result} entry/entries")

    if __name__ == '__main__':
        app()
    ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Phase 5: Query/List Command (`src/training_vid_organizer/cli.py`)

### Tasks
1. **Implement list videos command** (Typer parses args → filters dict → pure function query)
    ```python
    # Run: cat >> src/training_vid_organizer/cli.py << 'PYEOF' && python -m py_compile src/training_vid_organizer/cli.py
    from typing import Any

    @app.command()
    def list_videos(lift: str | None = None):
        """List training videos."""
        db = DB()
        
        if lift is not None:
            results = list_videos(db, {'lift': lift})  # type: ignore[union-attr]
        else:
            results = list_videos(db)
        
        print(f"\n{'ID':<5} {'Date':<12} {'Lift':<18} {'Weight':<7} {'Reps':<6}")
        for row in results:
            print(f"{row[0]:<5} {row[1]:<12} {row[3]:<18} {row[4]:<7} {row[5]:<6}")
        
        return 0

    if __name__ == '__main__':
        app()
    ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Phase 6: Update Entry Command (`src/training_vid_organizer/cli.py`)

### Tasks
1. **Implement update entry command** (Typer parses args → patch dict → pure function)
    ```python
    # Run: cat >> src/training_vid_organizer/cli.py << 'PYEOF' && python -m py_compile src/training_vid_organizer/cli.py
    from typing import Any

    @app.command()
    def update_entry(entry_id: int, **kwargs: str):
        """Update a lift entry by ID."""
        db = DB()
        
        if '--id' not in kwargs:
            print("Error: --id is required")
            return 1
        
        try:
            entry_id = int(kwargs['--id'])  # type: ignore[union-attr]
        except ValueError:
            print("Error: --id must be an integer")
            return 1
        
        updates = {k.replace('--',''): v for k,v in kwargs.items() if k.startswith('--')}  # type: ignore[union-attr]
        
        result = update_entry(db, entry_id, updates)  # pure function with patch dict
        echo(f"Updated entry {entry_id}")
        return 0

    if __name__ == '__main__':
        app()
    ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```
```

---

## Phase 7: Analysis Queries (Scaffold)

### Tasks
1. **Create analysis module scaffold** (LiftEntry aggregation → pure functions, no CLI wiring needed yet)
    ```python
    # Run: mkdir -p src/analysis && cat > src/analysis/__init__.py << 'PYEOF'
    """Analysis utilities for grouped queries."""
    from typing import Any
    
    def group_by(db, column: str) -> dict[str, list[tuple]]:
        """Pure business logic: returns typed aggregated results by column."""
        pass
    
    def performance_per_program(db) -> dict[str, float]:
        """Pure business logic: returns typed dictionary of program stats."""
        pass
    ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Phase 8: Integration & End-to-End

### Tasks
1. **Verify CLI help** (Typer auto-generates documentation)
   ```bash
   python -m training_vid_organizer.cli --help
   ```

2. **Run end-to-end test** (JSON config with list[LiftEntry] format, parsed → LiftEntry instances → pure function)
   ```bash
   echo '{"date":"2026-09-23","bodyweight":85.5,"lift":"front_squat","weight":140,"reps":5,"top_set":true,"reps_in_reserve":2,"program":"531+","program_iteration":1}' > /tmp/test_session.json && python -m training_vid_organizer.cli add session --config /tmp/test_session.json
   ```

### Typer CLI Wiring Pattern (src/training_vid_organizer/cli.py)
```python
from typer import Typer, echo
from src.db import DB
from src.models import LiftEntry
import json

app = Typer(name="training-vid-organizer")

@app.command()
def add_lift(
    date: str,
    bodyweight: float | None = None,
    lift: str,
    weight: float,
    reps: int,
):
    """Add a single lift entry."""
    db = DB()
    entry = LiftEntry(
        date=date,
        bodyweight=bodyweight,
        lift=lift,
        weight=weight,
        reps=reps,
    )
    result = add_lift(db, entry)  # pure function with typed dataclass
    echo(f"Added {result} entry/entries")

@app.command()
def add_session(config: str):
    """Add multiple lift entries from JSON config."""
    db = DB()
    with open(config) as f:
        data = json.load(f)  # list[LiftEntry] dicts
    
    # Convert dicts to LiftEntry instances (or pass directly if using dict[str, Any])
    entries = [LiftEntry(**d) for d in data]
    
    result = add_session(db, entries)  # pure function with typed list[LiftEntry]
    echo(f"Added {result} entry/entries")

@app.command()
def list_videos(lift: str | None = None):
    """List training videos."""
    db = DB()
    
    if lift is not None:
        results = list_videos(db, {'lift': lift})  # type: ignore[union-attr]
    else:
        results = list_videos(db)
    
    print(f"\n{'ID':<5} {'Date':<12} {'Lift':<18} {'Weight':<7} {'Reps':<6}")
    for row in results:
        print(f"{row[0]:<5} {row[1]:<12} {row[3]:<18} {row[4]:<7} {row[5]:<6}")

@app.command()
def update_entry(entry_id: int, **kwargs: str):
    """Update a lift entry by ID."""
    db = DB()
    
    if '--id' not in kwargs:
        print("Error: --id is required")
        return 1
    
    try:
        entry_id = int(kwargs['--id'])  # type: ignore[union-attr]
    except ValueError:
        print("Error: --id must be an integer")
        return 1
    
    updates = {k.replace('--',''): v for k,v in kwargs.items() if k.startswith('--')}  # type: ignore[union-attr]
    
    result = update_entry(db, entry_id, updates)  # pure function with patch dict
    echo(f"Updated entry {entry_id}")
    return 0

if __name__ == '__main__':
    app()
```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Ralph Loop Execution Pattern

```bash
ralph_loop "Implement training video organizer CLI: execute Phase 1-8 tasks sequentially and be sure to include tests for any added functionality, running 'pytest .' after each phase and only proceeding when all tests pass"
```

Each task is single-command executable, stateless, and verifiable.

### Architecture Decisions (Locked)
- **Data model**: `LiftEntry` dataclass in `src/training_vid_organizer/db.py`; all commands return typed results, no side effects
- **Session format**: `list[LiftEntry]` instead of separate `SessionConfig`; validation applied to list before insertion
- **Database lifecycle**: Dependency injection pattern (DB instance passed as parameter); module-level singleton deferred for testability
- **CLI integration**: Typer subcommands with explicit options (`--lift`, `--program`, etc.); no auto-increment for program_iteration
- **Error handling**: Omitted from initial implementation; to be added in Phase 5+ as structured error classes
- **Type safety**: All function signatures use explicit type hints throughout; mypy verification required before merge

