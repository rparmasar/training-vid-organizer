from src.training_vid_organizer.db_handling.query import fetch_lifts, _build_query
from src.training_vid_organizer.db_handling.db import init_database, LiftEntry, add_lift_entry

def test_build_query_works_exact_date(all_lift_cols):
    """Test that _build_query returns the correct SQL query for exact date matching."""
    # sample input
    filter_input = {
        'date': '2025-03-15'
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE date = ?"
    expected_parameter = ["2025-03-15"]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_partial_date(all_lift_cols):
    """Test that _build_query returns the correct SQL query for partial date matching."""
    # sample input
    filter_input = {
        'date': '2025-03'
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE date LIKE ?"
    expected_parameter = ["2025-03%"]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_lift(all_lift_cols):
    """Test that _build_query returns the correct SQL query for lift matching."""
    # sample input
    filter_input = {
        'lift': 'front_squat'
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE lift = ?"
    expected_parameter = ["front_squat"]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_program(all_lift_cols):
    """Test that _build_query returns the correct SQL query for program matching."""
    # sample input
    filter_input = {
        'program': '531-5+'
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE program = ?"
    expected_parameter = ["531-5+"]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_program_iteration(all_lift_cols):
    """Test that _build_query returns the correct SQL query for program_iteration matching."""
    # sample input
    filter_input = {
        'program_iteration': '1'
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE program_iteration = ?"
    expected_parameter = [1]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_weight(all_lift_cols):
    """Test that _build_query returns the correct SQL query for weight matching."""
    # sample input
    filter_input = {
        'weight': '275'
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE weight = ?"
    expected_parameter = [275.0]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_bodyweight(all_lift_cols):
    """Test that _build_query returns the correct SQL query for bodyweight matching."""
    # sample input
    filter_input = {
        'bodyweight': '275'
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE bodyweight = ?"
    expected_parameter = [275.0]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_top_set(all_lift_cols):
    """Test that _build_query returns the correct SQL query for top_set matching."""
    # sample input
    filter_input = {
        'top_set': True
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE top_set = ?"
    expected_parameter = [1]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_warm_up_set(all_lift_cols):
    """Test that _build_query returns the correct SQL query for warm_up_set matching."""
    # sample input
    filter_input = {
        'warm_up_set': True
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE warm_up_set = ?"
    expected_parameter = [1]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_reps_in_reserve(all_lift_cols):
    """Test that _build_query returns the correct SQL query for reps_in_reserve matching."""
    # sample input
    filter_input = {
        'reps_in_reserve': 2
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE reps_in_reserve = ?"
    expected_parameter = [2]

    # check success
    observed_query, observed_parameter = _build_query(filter_input)
    assert observed_query == expected_query
    assert observed_parameter == expected_parameter


def test_build_query_works_combination(all_lift_cols):
    """Test that _build_query returns the correct SQL query for a combination of filters."""
    # sample input
    filter_input = {
        'lift': 'front_squat',
        'reps_in_reserve': 2,
        'date': '2025-02'
    }

    # expected return vals
    expected_query = f"SELECT {all_lift_cols} FROM lifts WHERE date LIKE ? AND lift = ? AND reps_in_reserve = ?"
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
    expected_query = "SELECT date, program, program_iteration, lift, weight, reps, bodyweight, top_set, warm_up_set, reps_in_reserve, filepath FROM lifts"
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
    )
    add_lift_entry(
        test_db_path,
        sample_lift_entry
    )

    # call fn
    sample_filters = {}
    observed_rows = fetch_lifts(test_db_path, sample_filters)

    # check success
    assert observed_rows == [sample_lift_entry]
    

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
    )
    add_lift_entry(
        test_db_path,
        sample_lift_entry
    )

    # call fn
    sample_filters = {
        "lift": "Bicep Curl",
    }
    observed_rows = fetch_lifts(test_db_path, sample_filters)

    # check success
    assert observed_rows == [sample_lift_entry]


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
    )
    add_lift_entry(
        test_db_path,
        sample_lift_entry
    )

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
        )
        add_lift_entry(
            test_db_path,
            sample_lift_entry
        )

    # call fn
    sample_filters = {
        "lift": "Bicep Curl",
    }
    observed_rows = fetch_lifts(test_db_path, sample_filters, limit=2)

    # check success
    assert len(observed_rows) == 2