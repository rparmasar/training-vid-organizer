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
# def test_fetch_lifts_empty_db(tmpdir):
#     """Test that fetch_lifts returns empty list when no data exists."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     result = fetch_lifts(str(db_path))

#     assert result == []


# def test_fetch_lifts_all_data(tmpdir):
#     """Test fetching all lifts without filters."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     # Add sample data
#     entries = [
#         LiftEntry(
#             date="2025-03-15",
#             program="StrongLifts",
#             program_iteration=1,
#             lift="squat",
#             weight=100,
#             reps=5,
#             bodyweight=85.5,
#             top_set=True,
#         ),
#         LiftEntry(
#             date="2025-03-16",
#             program="StrongLifts",
#             program_iteration=1,
#             lift="deadlift",
#             weight=140,
#             reps=3,
#             bodyweight=85.5,
#             top_set=True,
#         ),
#     ]

#     for entry in entries:
#         add_lift_entry(str(db_path), entry)

#     result = fetch_lifts(str(db_path))

#     assert len(result) == 2
#     assert all(isinstance(e, LiftEntry) for e in result)


# def test_fetch_lifts_by_weight(tmpdir):
#     """Test filtering by weight."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     # Add sample data with different weights
#     for i in range(5):
#         add_lift_entry(str(db_path), LiftEntry(
#             date=f"2025-03-{i+1:02d}",
#             program="Test",
#             program_iteration=1,
#             lift="squat",
#             weight=100 + i * 10,  # 100, 110, 120, 130, 140
#             reps=5,
#         ))

#     result = fetch_lifts(str(db_path), filters={"weight": 120})

#     assert len(result) == 1
#     assert result[0].weight == 120


# def test_fetch_lifts_by_program(tmpdir):
#     """Test filtering by program name."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     for prog in ["StrongLifts", "P90X", "CrossFit"]:
#         add_lift_entry(str(db_path), LiftEntry(
#             date="2025-03-15",
#             program=prog,
#             program_iteration=1,
#             lift="pushup",
#             weight=80,
#             reps=10,
#         ))

#     result = fetch_lifts(str(db_path), filters={"program": "StrongLifts"})

#     assert len(result) == 1
#     assert result[0].program == "StrongLifts"


# def test_fetch_lifts_by_date(tmpdir):
#     """Test exact date filtering."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     for day in ["2025-03-14", "2025-03-15", "2025-03-16"]:
#         add_lift_entry(str(db_path), LiftEntry(
#             date=day,
#             program="Test",
#             program_iteration=1,
#             lift="squat",
#             weight=100,
#             reps=5,
#         ))

#     result = fetch_lifts(str(db_path), filters={"date": "2025-03-15"})

#     assert len(result) == 1
#     assert result[0].date == "2025-03-15"


# def test_fetch_lifts_by_top_set(tmpdir):
#     """Test filtering by top_set flag."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     for is_top in [True, False]:
#         add_lift_entry(str(db_path), LiftEntry(
#             date="2025-03-15",
#             program="Test",
#             program_iteration=1,
#             lift="squat",
#             weight=100,
#             reps=5,
#             top_set=is_top,
#         ))

#     result = fetch_lifts(str(db_path), filters={"top_set": True})

#     assert len(result) == 1
#     assert result[0].top_set is True


# def test_fetch_lifts_combined_filters(tmpdir):
#     """Test combining multiple filter criteria."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     # Add data that matches various combinations
#     for i in range(6):
#         add_lift_entry(str(db_path), LiftEntry(
#             date="2025-03-15",
#             program="StrongLifts" if i % 2 == 0 else "P90X",
#             program_iteration=1,
#             lift="squat",
#             weight=100 + (i * 10),  # 100, 110, 120, 130, 140, 150
#             reps=5,
#             top_set=i % 2 == 0,
#         ))

#     # Filter: StrongLifts + weight = 120 + top set
#     result = fetch_lifts(str(db_path), filters={
#         "program": "StrongLifts",
#         "weight": 120,
#         "top_set": True,
#     })

#     assert len(result) == 1
#     assert result[0].program == "StrongLifts"
#     assert result[0].weight == 120.0
#     assert result[0].top_set is True


# def test_fetch_lifts_limit(tmpdir):
#     """Test that limit parameter restricts results."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     for i in range(10):
#         add_lift_entry(str(db_path), LiftEntry(
#             date=f"2025-03-{i+1:02d}",
#             program="Test",
#             program_iteration=1,
#             lift="squat",
#             weight=100,
#             reps=5,
#         ))

#     result = fetch_lifts(str(db_path), limit=5)

#     assert len(result) == 5


# def test_fetch_lifts_no_matches(tmpdir):
#     """Test that empty list is returned when no matches found."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     add_lift_entry(str(db_path), LiftEntry(
#         date="2025-03-15",
#         program="StrongLifts",
#         program_iteration=1,
#         lift="squat",
#         weight=100,
#         reps=5,
#     ))

#     result = fetch_lifts(str(db_path), filters={"weight": 999})

#     assert result == []


# def test_fetch_lifts_date_prefix_match(tmpdir):
#     """Test date prefix matching via min_date/max_date (e.g., '2025-03' matches all of March)."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     for day in ["2025-02-14", "2025-03-01", "2025-03-15", "2025-04-01"]:
#         add_lift_entry(str(db_path), LiftEntry(
#             date=day,
#             program="Test",
#             program_iteration=1,
#             lift="squat",
#             weight=100,
#             reps=5,
#         ))

#     # Use min_date for prefix matching (matches all dates starting with '2025-03')
#     result = fetch_lifts(str(db_path), filters={"min_date": "2025-03"})

#     assert len(result) == 2
#     # Should match both March dates
#     dates = [r.date for r in result]
#     assert "2025-03-01" in dates
#     assert "2025-03-15" in dates


# def test_fetch_lifts_date_range(tmpdir):
#     """Test date range filtering with min_date and max_date."""
#     db_path = tmpdir / "test.db"
#     init_database(db_path)

#     for day in ["2025-03-14", "2025-03-15", "2025-03-16"]:
#         add_lift_entry(str(db_path), LiftEntry(
#             date=day,
#             program="Test",
#             program_iteration=1,
#             lift="squat",
#             weight=100,
#             reps=5,
#         ))

#     result = fetch_lifts(str(db_path), filters={
#         "min_date": "2025-03-14",
#         "max_date": "2025-03-16",
#     })

#     assert len(result) == 3
