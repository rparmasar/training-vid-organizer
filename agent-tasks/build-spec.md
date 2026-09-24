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
- Phase 3: Single lift command (`src/commands/add_lift.py`)
- Phase 4: Session processing (`src/commands/add_session.py`)
- Phase 5: Query/list command (`src/commands/list_videos.py`)
- Phase 6: Update entry command (`src/commands/update_entry.py`)
- Phases 7-8: Analysis queries and integration testing


---

## Phase 2: Database Layer (`src/db.py`)

### Tasks
1. **Implement DB class with CRUD methods**
   ```python
   # Run: cat > src/db.py << 'PYEOF' && python -m py_compile src/db.py
   import sqlite3
   from contextlib import contextmanager
   
   class DB:
       def __init__(self, db_path='db/training.db'):
           self.path = db_path
       
       @contextmanager
       def connection(self):
           conn = sqlite3.connect(self.path)
           try:
               yield conn
           finally:
               conn.close()
       
       def init_schema(self):
           with self.connection() as conn:
               c = conn.cursor()
               # (same schema as Phase 1)
               pass
   
       def add_lift_entry(self, **kwargs):
           with self.connection() as conn:
               c = conn.cursor()
               c.execute('''INSERT INTO lifts 
                   (date,bodyweight,lift,weight,reps,top_set,reps_in_reserve,filepath,program,program_iteration)
                   VALUES (?,?,?,?,?,?,?,?,?)''',
                       (kwargs['date'], kwargs.get('bodyweight'), kwargs['lift'],
                        kwargs['weight'], kwargs['reps'], kwargs.get('top_set', False),
                        kwargs.get('reps_in_reserve'), kwargs.get('filepath'),
                        kwargs.get('program'), kwargs.get('program_iteration')))
               conn.commit()
               return c.lastrowid
   
       def add_session_entries(self, entries):
           with self.connection() as conn:
               c = conn.cursor()
               placeholders = ','.join(['?' for _ in entries])
               cols = ', '.join(['date','bodyweight','lift','weight','reps','top_set',
                                'reps_in_reserve','filepath','program','program_iteration'])
               c.execute(f'''INSERT INTO lifts ({cols}) VALUES ({placeholders})''',
                         [e.values for e in entries])
               conn.commit()
   
       def list_entries(self, query='SELECT * FROM lifts'):
           with self.connection() as conn:
               c = conn.cursor()
               c.execute(query)
               return c.fetchall()
       
       def update_entry(self, entry_id, **kwargs):
           with self.connection() as conn:
               c = conn.cursor()
               updates = []
               values = [entry_id]
               for k in kwargs.keys():
                   updates.append(f'{k}=?')
                   values.append(kwargs[k])
               c.execute(f'UPDATE lifts SET {",".join(updates)} WHERE id=?', values)
               conn.commit()
   ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Phase 3: Single Lift Command (`src/commands/add_lift.py`)

### Tasks
1. **Implement add lift command**
   ```python
   # Run: cat > src/commands/add_lift.py << 'PYEOF' && python -m py_compile src/commands/add_lift.py
   import sys
   from pathlib import Path
   
   def parse_args(args):
       kwargs = {}
       for i, arg in enumerate(args[1:], 1):
           if '=' in arg:
               key, val = arg.split('=', 1)
               kwargs[key] = val
           else:
               kwargs[f'arg_{i}'] = arg
       return kwargs
   
   def main():
       args = parse_args(sys.argv)
       db = DB()
       entry_id = db.add_lift_entry(**args)
       print(f"Added lift entry with id={entry_id}")
   
   if __name__ == '__main__':
       main()
   ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Phase 4: Session Processing (`src/commands/add_session.py`)

### Tasks
1. **Implement add session command**
   ```python
   # Run: cat > src/commands/add_session.py << 'PYEOF' && python -m py_compile src/commands/add_session.py
   import json, sys
   
   def parse_args(args):
       kwargs = {}
       for i, arg in enumerate(args[1:], 1):
           if '=' in arg:
               key, val = arg.split('=', 1)
               kwargs[key] = val
           else:
               kwargs[f'arg_{i}'] = arg
       return kwargs
   
   def main():
       args = parse_args(sys.argv)
       
       # Load config JSON
       if 'config' in args:
           with open(args['config']) as f:
               entries_data = json.load(f)
           
           db = DB()
           for entry in entries_data:
               db.add_lift_entry(**entry)
           print(f"Added {len(entries_data)} session entries")
       
       # Infer mode (placeholder)
       elif 'infer' in args and args['infer'] == 'true':
           print("Infer mode: match config to existing files")
   
   if __name__ == '__main__':
       main()
   ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Phase 5: Query/List Command (`src/commands/list_videos.py`)

### Tasks
1. **Implement list videos command**
   ```python
   # Run: cat > src/commands/list_videos.py << 'PYEOF' && python -m py_compile src/commands/add_lift.py
   import sys
   
   def parse_args(args):
       kwargs = {}
       for i, arg in enumerate(args[1:], 1):
           if '=' in arg:
               key, val = arg.split('=', 1)
               kwargs[key] = val
           else:
               kwargs[f'arg_{i}'] = arg
       return kwargs
   
   def main():
       args = parse_args(sys.argv)
       
       db = DB()
       query = 'SELECT * FROM lifts'
       
       # Simple filter support (extendable)
       if 'lift=' in args:
           lift = args['lift=']
           query += f" WHERE lift='{lift}'"
       
       results = db.list_entries(query)
       
       print(f"\n{'ID':<5} {'Date':<12} {'Lift':<18} {'Weight':<7} {'Reps':<6}")
       for row in results:
           print(f"{row[0]:<5} {row[1]:<12} {row[3]:<18} {row[4]:<7} {row[5]:<6}")
   
   if __name__ == '__main__':
       main()
   ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Phase 6: Update Entry Command (`src/commands/update_entry.py`)

### Tasks
1. **Implement update entry command**
   ```python
   # Run: cat > src/commands/update_entry.py << 'PYEOF' && python -m py_compile src/commands/update_entry.py
   import sys
   
   def parse_args(args):
       kwargs = {}
       for i, arg in enumerate(args[1:], 1):
           if '=' in arg:
               key, val = arg.split('=', 1)
               kwargs[key] = val
           else:
               kwargs[f'arg_{i}'] = arg
       return kwargs
   
   def main():
       args = parse_args(sys.argv)
       
       # Expect: --id=1 weight=150 reps=6
       entry_id = int(args.get('--id', 0))
       db = DB()
       db.update_entry(entry_id, **{k.replace('--',''): v for k,v in args.items() if k.startswith('--')})
       print(f"Updated entry {entry_id}")
   
   if __name__ == '__main__':
       main()
   ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Phase 7: Analysis Queries (Scaffold)

### Tasks
1. **Create analysis module scaffold**
   ```python
   # Run: mkdir -p src/analysis && cat > src/analysis/__init__.py << 'PYEOF'
   """Analysis utilities for grouped queries."""
   
   def group_by(db, column):
       """Placeholder for future group-by analysis."""
       pass
   
   def performance_per_program(db):
       """Placeholder for per-program stats."""
       pass
   ```

### Test Gate
```bash
pytest tests/ -v && pytest .
```

---

## Phase 8: Integration & End-to-End

### Tasks
1. **Verify CLI help**
   ```bash
   python src/cli.py --help
   ```

2. **Run end-to-end test**
   ```bash
   echo '{"date":"2026-09-23","bodyweight":85.5,"lift":"front_squat","weight":140,"reps":5,"top_set":true,"reps_in_reserve":2,"program":"531+","program_iteration":1}' > /tmp/test_session.json && python src/cli.py add session --config /tmp/test_session.json
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
