from src.training_vid_organizer.db_handling.db import (
    LiftEntry,
    add_lift_entry,
    init_database,
)
from src.training_vid_organizer.db_handling.query import _build_query, fetch_lifts


def test_build_query_works_exact_date(all_lift_cols):
    """Test that _build_query returns the correct SQL query for exact date matching."""
    # sample input
    filter_input = {"date": "2025-03-15"}

    # expected return vals
    expected_query = (
        f"SELECT id, {all_lift_cols} FROM lifts WHERE date = ? ORDER BY date DESC"
    )
    expected_parameter = ["2025-03-15"]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_partial_date(all_lift_cols):
    """Test that _build_query returns the correct SQL query for partial date matching."""
    # sample input
    filter_input = {"date": "2025-03"}

    # expected return vals
    expected_query = (
        f"SELECT id, {all_lift_cols} FROM lifts WHERE date LIKE ? ORDER BY date DESC"
    )
    expected_parameter = ["2025-03%"]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_lift(all_lift_cols):
    """Test that _build_query returns the correct SQL query for lift matching."""
    # sample input
    filter_input = {"lift": "front_squat"}

    # expected return vals
    expected_query = (
        f"SELECT id, {all_lift_cols} FROM lifts WHERE lift = ? ORDER BY date DESC"
    )
    expected_parameter = ["front_squat"]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_program(all_lift_cols):
    """Test that _build_query returns the correct SQL query for program matching."""
    # sample input
    filter_input = {"program": "531-5+"}

    # expected return vals
    expected_query = (
        f"SELECT id, {all_lift_cols} FROM lifts WHERE program = ? ORDER BY date DESC"
    )
    expected_parameter = ["531-5+"]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_program_iteration(all_lift_cols):
    """Test that _build_query returns the correct SQL query for program_iteration matching."""
    # sample input
    filter_input = {"program_iteration": "1"}

    # expected return vals
    expected_query = f"SELECT id, {all_lift_cols} FROM lifts WHERE program_iteration = ? ORDER BY date DESC"
    expected_parameter = [1]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_weight(all_lift_cols):
    """Test that _build_query returns the correct SQL query for weight matching."""
    # sample input
    filter_input = {"weight": "275"}

    # expected return vals
    expected_query = (
        f"SELECT id, {all_lift_cols} FROM lifts WHERE weight = ? ORDER BY date DESC"
    )
    expected_parameter = [275.0]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_bodyweight(all_lift_cols):
    """Test that _build_query returns the correct SQL query for bodyweight matching."""
    # sample input
    filter_input = {"bodyweight": "275"}

    # expected return vals
    expected_query = (
        f"SELECT id, {all_lift_cols} FROM lifts WHERE bodyweight = ? ORDER BY date DESC"
    )
    expected_parameter = [275.0]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_top_set(all_lift_cols):
    """Test that _build_query returns the correct SQL query for top_set matching."""
    # sample input
    filter_input = {"top_set": True}

    # expected return vals
    expected_query = (
        f"SELECT id, {all_lift_cols} FROM lifts WHERE top_set = ? ORDER BY date DESC"
    )
    expected_parameter = [1]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_warm_up_set(all_lift_cols):
    """Test that _build_query returns the correct SQL query for warm_up_set matching."""
    # sample input
    filter_input = {"warm_up_set": True}

    # expected return vals
    expected_query = (
        f"SELECT id, {all_lift_cols} FROM lifts WHERE warm_up_set = ? ORDER BY date DESC"
    )
    expected_parameter = [1]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_reps_in_reserve(all_lift_cols):
    """Test that _build_query returns the correct SQL query for reps_in_reserve matching."""
    # sample input
    filter_input = {"reps_in_reserve": 2}

    # expected return vals
    expected_query = f"SELECT id, {all_lift_cols} FROM lifts WHERE reps_in_reserve = ? ORDER BY date DESC"
    expected_parameter = [2]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_combination(all_lift_cols):
    """Test that _build_query returns the correct SQL query for a combination of filters."""
    # sample input
    filter_input = {"lift": "front_squat", "reps_in_reserve": 2, "date": "2025-02"}

    # expected return vals
    expected_query = f"SELECT id, {all_lift_cols} FROM lifts WHERE date LIKE ? AND lift = ? AND reps_in_reserve = ? ORDER BY date DESC"
    expected_parameter = ["2025-02%", "front_squat", 2]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_empty():
    """Test that _build_query returns the correct SQL query for an empty filter."""
    # sample input
    filter_input = {}

    # expected return vals
    expected_query = "SELECT id, date, program, program_iteration, lift, weight, reps, bodyweight, top_set, warm_up_set, reps_in_reserve, filename, entry_id FROM lifts ORDER BY date DESC"
    expected_parameter = []

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_fetch_lifts_works_no_filters(tmpdir):
    # initialize temp db
    test_db_path = tmpdir / "test.db"
    init_database(test_db_path)

    # add some data to the db
    sample_lift_entry = LiftEntry(
        date="2025-01-01",
        program="Test Program",
        program_iteration=1,
        lift="Bicep Curl",
        weight=100,
        reps=2,
        entry_id=None,  # ID is assigned by DB after insertion
    )
    add_lift_entry(test_db_path, sample_lift_entry)

    # call fn
    sample_filters = {}
    observed_rows = fetch_lifts(test_db_path, sample_filters)

    # check success (compare all fields except entry_id which is DB-assigned)
    assert len(observed_rows) == 1
    fetched = observed_rows[0]
    assert fetched.date == sample_lift_entry.date
    assert fetched.program == sample_lift_entry.program
    assert fetched.program_iteration == sample_lift_entry.program_iteration
    assert fetched.lift == sample_lift_entry.lift
    assert fetched.weight == sample_lift_entry.weight
    assert fetched.reps == sample_lift_entry.reps
    assert fetched.bodyweight == sample_lift_entry.bodyweight
    assert fetched.top_set == sample_lift_entry.top_set
    assert fetched.warm_up_set == sample_lift_entry.warm_up_set
    assert fetched.reps_in_reserve == sample_lift_entry.reps_in_reserve
    assert fetched.filename == sample_lift_entry.filename


def test_fetch_lifts_works_with_filter(tmpdir):
    # initialize temp db
    test_db_path = tmpdir / "test.db"
    init_database(test_db_path)

    # add some data to the db
    sample_lift_entry = LiftEntry(
        date="2025-01-01",
        program="Test Program",
        program_iteration=1,
        lift="Bicep Curl",
        weight=100,
        reps=2,
        entry_id=None,  # ID is assigned by DB after insertion
    )
    add_lift_entry(test_db_path, sample_lift_entry)

    # call fn
    sample_filters = {
        "lift": "Bicep Curl",
    }
    observed_rows = fetch_lifts(test_db_path, sample_filters)

    # check success (compare all fields except entry_id which is DB-assigned)
    assert len(observed_rows) == 1
    fetched = observed_rows[0]
    assert fetched.date == sample_lift_entry.date
    assert fetched.program == sample_lift_entry.program
    assert fetched.program_iteration == sample_lift_entry.program_iteration
    assert fetched.lift == sample_lift_entry.lift
    assert fetched.weight == sample_lift_entry.weight
    assert fetched.reps == sample_lift_entry.reps
    assert fetched.bodyweight == sample_lift_entry.bodyweight
    assert fetched.top_set == sample_lift_entry.top_set
    assert fetched.warm_up_set == sample_lift_entry.warm_up_set
    assert fetched.reps_in_reserve == sample_lift_entry.reps_in_reserve
    assert fetched.filename == sample_lift_entry.filename


def test_fetch_lifts_works_with_filter_no_matches(tmpdir):
    # initialize temp db
    test_db_path = tmpdir / "test.db"
    init_database(test_db_path)

    # add some data to the db
    sample_lift_entry = LiftEntry(
        date="2025-01-01",
        program="Test Program",
        program_iteration=1,
        lift="Bicep Curl",
        weight=100,
        reps=2,
        entry_id=None,  # ID is assigned by DB after insertion
    )
    add_lift_entry(test_db_path, sample_lift_entry)

    # call fn
    sample_filters = {
        "lift": "Bench Press",
    }
    observed_rows = fetch_lifts(test_db_path, sample_filters)

    # check success
    assert observed_rows == []


def test_fetch_lifts_works_with_limit(tmpdir):
    # initialize temp db
    test_db_path = tmpdir / "test.db"
    init_database(test_db_path)

    # add some data to the db
    for i in range(10):
        sample_lift_entry = LiftEntry(
            date=f"2025-01-{i}",
            program="Test Program",
            program_iteration=1,
            lift="Bicep Curl",
            weight=100,
            reps=2,
            entry_id=None,  # ID is assigned by DB after insertion
        )
        add_lift_entry(test_db_path, sample_lift_entry)

    # call fn
    sample_filters = {
        "lift": "Bicep Curl",
    }
    observed_rows = fetch_lifts(test_db_path, sample_filters, limit=2)

    # check success
    assert len(observed_rows) == 2


def test_fetch_lifts_includes_virtual_columns(tmpdir):
    """Test that virtual columns are included in fetch results."""
    init_database(tmpdir / "test.db")

    sample_lift_entry = LiftEntry(
        date="2025-01-01",
        program="Test Program",
        program_iteration=1,
        lift="Squat",
        weight=200,
        reps=5,  # 1RM = 200*36/(37-5) = 228.57
        entry_id=None,
    )
    add_lift_entry(tmpdir / "test.db", sample_lift_entry)

    observed_rows = fetch_lifts(tmpdir / "test.db", {})
    assert len(observed_rows) == 1
    fetched = observed_rows[0]

    # Virtual columns should be present in the result object (LiftResult dataclass)
    assert hasattr(fetched, "estimated_1rm"), "estimated_1rm attribute missing"
    assert hasattr(fetched, "total_set_volume"), "total_set_volume attribute missing"

    # Values should match expected calculations (Bryzycki: 200*36/(37-5)=225)
    assert fetched.estimated_1rm == 225.0, f"Expected 225.0, got {fetched.estimated_1rm}"
    assert fetched.total_set_volume == 1000.0, f"Expected 1000.0, got {fetched.total_set_volume}"


def test_fetch_lifts_virtual_columns_with_filter(tmpdir):
    """Test that virtual columns work correctly with filtered queries."""
    init_database(tmpdir / "test.db")

    # Add multiple entries for same program_iteration/lift combination
    weights_reps = [(200, 5), (210, 4), (190, 6)]
    for weight, reps in weights_reps:
        sample_lift_entry = LiftEntry(
            date=f"2025-01-{(weights_reps.index((weight, reps)) + 1):02d}",
            program="Test Program",
            program_iteration=1,
            lift="Squat",
            weight=weight,
            reps=reps,
            entry_id=None,
        )
        add_lift_entry(tmpdir / "test.db", sample_lift_entry)

    # Fetch with filter for this program_iteration and lift
    observed_rows = fetch_lifts(
        tmpdir / "test.db", {"program_iteration": 1, "lift": "Squat"}
    )
    assert len(observed_rows) == 3

    # Verify virtual columns are present in all results (LiftResult dataclass)
    for row in observed_rows:
        assert hasattr(row, "estimated_1rm"), f"Row missing estimated_1rm: {row}"
        assert hasattr(row, "total_set_volume"), f"Row missing total_set_volume: {row}"


def test_fetch_lifts_virtual_columns_aggregation(tmpdir):
    """Test that virtual columns work correctly with aggregation queries."""
    init_database(tmpdir / "test.db")

    # Add multiple entries for same program_iteration/lift combination
    weights_reps = [(200, 5), (210, 4), (190, 6)]
    for weight, reps in weights_reps:
        sample_lift_entry = LiftEntry(
            date=f"2025-01-{(weights_reps.index((weight, reps)) + 1):02d}",
            program="Test Program",
            program_iteration=1,
            lift="Squat",
            weight=weight,
            reps=reps,
            entry_id=None,
        )
        add_lift_entry(tmpdir / "test.db", sample_lift_entry)

    # Fetch all entries and verify virtual columns are present
    observed_rows = fetch_lifts(tmpdir / "test.db", {})
    assert len(observed_rows) == 3

    # Verify each row has the expected virtual column values (LiftResult dataclass)
    for row in observed_rows:
        assert row.estimated_1rm is not None or row.reps == 0, f"Row missing estimated_1rm: {row}"
        assert row.total_set_volume is not None, f"Row missing total_set_volume: {row}"


def test_fetch_lifts_virtual_columns_edge_case(tmpdir):
    """Test that virtual columns handle edge cases correctly."""
    init_database(tmpdir / "test.db")

    # Edge case: reps=0 should return None for estimated_1rm
    sample_lift_entry = LiftEntry(
        date="2025-01-01",
        program="Test Program",
        program_iteration=1,
        lift="Squat",
        weight=200,
        reps=0,  # Invalid reps
        entry_id=None,
    )
    add_lift_entry(tmpdir / "test.db", sample_lift_entry)

    observed_rows = fetch_lifts(tmpdir / "test.db", {})
    assert len(observed_rows) == 1
    fetched = observed_rows[0]

    # estimated_1rm should be None for reps=0
    assert fetched.estimated_1rm is None, f"Expected None for reps=0, got {fetched.estimated_1rm}"
