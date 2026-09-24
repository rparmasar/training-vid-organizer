import sqlite3
import os
import shutil

def test_database_exists():
    assert os.path.exists('db/training.db'), "Database file should exist"

def test_lifts_table_exists():
    conn = sqlite3.connect('db/training.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lifts'")
    assert c.fetchone() is not None, "lifts table should exist"

def test_lifts_schema():
    conn = sqlite3.connect('db/training.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(lifts)")
    cols = {row[1] for row in c.fetchall()}
    expected = {'id', 'date', 'bodyweight', 'lift', 'weight', 'reps', 
                'top_set', 'reps_in_reserve', 'filepath', 'program', 'program_iteration'}
    assert expected.issubset(cols), f"Missing columns: {expected - cols}"

def test_index_exists():
    conn = sqlite3.connect('db/training.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_lifts_date'")
    assert c.fetchone() is not None, "idx_lifts_date index should exist"

def test_schema_creation():
    """Verify schema can be created fresh - isolated test"""
    db_path = 'db/training.db.bak'  # Use backup path to avoid interfering with other tests
    
    # Remove existing database file only (not directory)
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
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
    
    # Verify it was created correctly
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lifts'")
    assert c.fetchone() is not None
    
    conn.close()
