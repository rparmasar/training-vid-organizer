import os
import pytest
import sqlite3
from src.db import DB


@pytest.fixture(scope='function')
def test_db():
    """Provide a fresh database for each test."""
    path = 'db/training_test.db'
    if os.path.exists(path):
        os.remove(path)
    
    db = DB(path)
    db.init_schema()
    
    yield db
    
    # Teardown: clear all data and remove file
    conn = sqlite3.connect(path)
    conn.execute('DELETE FROM lifts')
    conn.close()
    if os.path.exists(path):
        os.remove(path)


def test_init_schema(test_db):
    """Test that schema initialization works"""
    conn = sqlite3.connect('db/training_test.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lifts'")
    assert c.fetchone() is not None, "lifts table should exist"
    
    # Verify schema columns
    c.execute("PRAGMA table_info(lifts)")
    cols = {row[1] for row in c.fetchall()}
    expected = {'id', 'date', 'bodyweight', 'lift', 'weight', 'reps', 
                'top_set', 'reps_in_reserve', 'filepath', 'program', 'program_iteration'}
    assert expected.issubset(cols), f"Missing columns: {expected - cols}"
    
    conn.close()


def test_add_lift_entry(test_db):
    """Test adding a single lift entry"""
    entry_id = test_db.add_lift_entry(
        date='2026-09-23',
        bodyweight=85.5,
        lift='front_squat',
        weight=140,
        reps=5,
        top_set=True,
        reps_in_reserve=2,
        filepath='/videos/front_squat_2026.mp4',
        program='531+',
        program_iteration=1
    )
    
    assert entry_id == 1, "First entry should have id=1"


def test_add_session_entries(test_db):
    """Test adding multiple session entries at once"""
    entries = [
        {'date': '2026-09-23', 'bodyweight': 85.5, 'lift': 'front_squat', 
         'weight': 140, 'reps': 5, 'top_set': True, 'reps_in_reserve': 2},
        {'date': '2026-09-23', 'bodyweight': 85.5, 'lift': 'back_squat', 
         'weight': 160, 'reps': 4, 'top_set': False, 'reps_in_reserve': 1},
        {'date': '2026-09-23', 'bodyweight': 85.5, 'lift': 'deadlift', 
         'weight': 220, 'reps': 3, 'top_set': False, 'reps_in_reserve': 0},
    ]
    
    # Convert dicts to tuples of values for the batch insert
    test_db.add_session_entries([tuple(e.values()) for e in entries])
    
    results = test_db.list_entries('SELECT * FROM lifts')
    assert len(results) == 3, f"Should have 3 entries, got {len(results)}"


def test_list_entries(test_db):
    """Test listing all entries"""
    test_db.add_lift_entry(date='2026-09-23', bodyweight=85.5, lift='front_squat', 
                          weight=140, reps=5, top_set=True, filepath='/v.mp4')
    
    results = test_db.list_entries()
    assert len(results) == 1, f"Should have 1 entry, got {len(results)}"


def test_update_entry(test_db):
    """Test updating an existing entry"""
    # Add initial entry (commit is handled by add_lift_entry)
    test_db.add_lift_entry(
        date='2026-09-23', 
        bodyweight=85.5, 
        lift='front_squat', 
        weight=140, 
        reps=5, 
        top_set=True, 
        filepath='/v.mp4'
    )
    
    # Verify it exists before update
    results = test_db.list_entries("SELECT id FROM lifts WHERE date='2026-09-23'")
    assert len(results) == 1
    
    # Update the entry
    print(f"TEST DEBUG: Calling update_entry with id=1, weight=145, reps=6")
    test_db.update_entry(1, weight=145, reps=6)
    
    # Verify update (schema: id,date,bodyweight,lift,weight,reps,top_set,...)
    print(f"TEST DEBUG: Querying for row id=1 after update")
    results = test_db.list_entries('SELECT * FROM lifts WHERE id=1')
    assert len(results) == 1
    row = results[0]
    assert row[4] == 145, f"Weight should be updated to 145, got {row[4]}"
    assert row[5] == 6, f"Reps should be updated to 6, got {row[5]}"


def test_db_path_customization(test_db):
    """Test that custom db path is respected"""
    custom_path = 'db/custom_training.db'
    
    # Remove existing database if present
    if os.path.exists(custom_path):
        os.remove(custom_path)
    
    db = DB(custom_path)
    db.init_schema()
    
    assert os.path.exists(custom_path), "Custom database path should be used"


def test_cleanup():
    """Clean up any leftover test databases"""
    for path in ['db/training_test.db', 'db/custom_training.db']:
        if os.path.exists(path):
            os.remove(path)
