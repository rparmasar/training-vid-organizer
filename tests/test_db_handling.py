from src.training_vid_organizer.db_handling.db import (
    LiftEntry,
    add_lift_entry,
    add_session_entry,
    init_database,
)


def test_init_database_works(tmpdir):
    # if this doesn't throw an error, we should be okay
    init_database(tmpdir / "test.db")


def test_add_lift_entry_works(tmpdir):
    # initialize temp db
    init_database(tmpdir / "test.db")

    # sample entry
    INPUT_ENTRY = LiftEntry(
        date="2023-04-01",
        program="P9",
        program_iteration=1,
        lift="Bicep Curl",
        weight=85,
        reps=4,
        entry_id=None,  # ID is assigned by DB after insertion
    )

    # call fn
    OBSERVED_OUTPUT = add_lift_entry(tmpdir / "test.db", INPUT_ENTRY)

    # exactly one row should be affected
    assert OBSERVED_OUTPUT == 1


def test_add_session_entry_works(tmpdir):
    # initialize temp db
    init_database(tmpdir / "test.db")

    # sample session (list of entries)
    INPUT_SESSION = [
        LiftEntry(
            date="2023-04-01",
            program="P9",
            program_iteration=1,
            lift="Bicep Curl",
            weight=85,
            reps=4,
            entry_id=None,  # ID is assigned by DB after insertion
        ),
        LiftEntry(
            date="2024-04-01",
            program="P9",
            program_iteration=1,
            lift="Tricep Curl",
            weight=85,
            reps=4,
            entry_id=None,  # ID is assigned by DB after insertion
        ),
    ]

    # call fn
    OBSERVED_OUTPUT = add_session_entry(tmpdir / "test.db", INPUT_SESSION)

    # two rows should be affected
    assert OBSERVED_OUTPUT == 2


def test_virtual_columns_computed_on_insert(tmpdir):
    """Test that estimated_1rm and total_set_volume are computed correctly."""
    init_database(tmpdir / "test.db")

    # Entry with known values: weight=200, reps=5 -> 1RM = 200*36/(37-5) = 228.57
    INPUT_ENTRY = LiftEntry(
        date="2023-04-01",
        program="P9",
        program_iteration=1,
        lift="Squat",
        weight=200,
        reps=5,
        entry_id=None,
    )

    add_lift_entry(tmpdir / "test.db", INPUT_ENTRY)

    # Verify computed values in DB (stored as TEXT for precision)
    import sqlite3

    conn = sqlite3.connect(str(tmpdir / "test.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT estimated_1rm, total_set_volume FROM lifts WHERE id=1")
    row = cursor.fetchone()

    # Bryzycki: 200 * 36 / (37 - 5) = 225.0; volume: 200 * 5 = 1000.0
    assert row[0] == "225.0", f"Expected 225.0, got {row[0]}"
    assert row[1] == "1000.0", f"Expected 1000.0, got {row[1]}"

    conn.close()


def test_virtual_columns_edge_cases(tmpdir):
    """Test virtual column computation with edge cases."""
    init_database(tmpdir / "test.db")

    # Edge case: reps=0 should return None for estimated_1rm
    INPUT_ENTRY = LiftEntry(
        date="2023-04-01",
        program="P9",
        program_iteration=1,
        lift="Squat",
        weight=200,
        reps=0,  # Invalid reps
        entry_id=None,
    )

    add_lift_entry(tmpdir / "test.db", INPUT_ENTRY)

    import sqlite3

    conn = sqlite3.connect(str(tmpdir / "test.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT estimated_1rm FROM lifts WHERE id=1")
    row = cursor.fetchone()

    assert row[0] is None, f"Expected None for reps=0, got {row[0]}"

    conn.close()


def test_virtual_columns_aggregation_query(tmpdir):
    """Test that virtual columns work correctly in SQL aggregations."""
    init_database(tmpdir / "test.db")

    # Add multiple entries with same program_iteration and lift
    for i, (weight, reps) in enumerate([(200, 5), (210, 4), (190, 6)], start=1):
        INPUT_ENTRY = LiftEntry(
            date=f"2023-04-{i:02d}",
            program="P9",
            program_iteration=1,
            lift="Squat",
            weight=weight,
            reps=reps,
            entry_id=None,
        )
        add_lift_entry(tmpdir / "test.db", INPUT_ENTRY)

    # Query for average estimated_1rm across iterations (should be ~224.91)
    import sqlite3

    conn = sqlite3.connect(str(tmpdir / "test.db"))
    cursor = conn.cursor()
    cursor.execute(
        """SELECT AVG(estimated_1rm) FROM lifts WHERE program_iteration=1 AND lift='Squat'"""
    )
    avg_1rm = cursor.fetchone()[0]

    assert abs(avg_1rm - 224.91) < 0.01, f"Expected ~224.91, got {avg_1rm}"

    conn.close()
