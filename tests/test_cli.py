import json

from src.training_vid_organizer.cli import app


def test_cli_works(runner):
    """test that the CLI can be run without errors."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0


def test_cli_init_db_works(runner, tmpdir):
    """test that we can initialize the database using some path"""
    result = runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])
    assert result.exit_code == 0


def test_cli_init_db_reset_no_existing(runner, tmpdir):
    """test --reset flag with non-existent DB (no-op)"""
    result = runner.invoke(
        app, ["init", "--db-path", tmpdir / "nonexistent.db", "--reset"]
    )
    assert result.exit_code == 0


def test_cli_init_db_reset_with_confirmation(runner, tmpdir):
    """test --reset flag deletes and recreates existing DB after confirmation"""
    # Initialize first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # Verify data exists
    result = runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Bicep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )
    assert result.exit_code == 0

    # Reset with confirmation (simulate typing 'yes')
    result = runner.invoke(
        app, ["init", "--db-path", tmpdir / "test.db", "--reset"], input="y\n"
    )
    assert result.exit_code == 0

    # Verify data is gone but DB exists
    result = runner.invoke(
        app,
        [
            "list",
            "lifts",
            "--db-path",
            tmpdir / "test.db",
        ],
    )
    assert result.exit_code == 0
    assert "no lifts found" in result.output.lower()


def test_cli_init_db_reset_aborted(runner, tmpdir):
    """test --reset flag aborts when user declines confirmation"""
    # Initialize first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # Add some data
    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Bicep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )

    # Reset with 'no' confirmation (simulate typing 'n')
    result = runner.invoke(
        app, ["init", "--db-path", tmpdir / "test.db", "--reset"], input="n\n"
    )
    assert result.exit_code == 1
    assert "aborted" in result.output.lower()

    # Verify data still exists
    result = runner.invoke(
        app,
        [
            "list",
            "lifts",
            "--db-path",
            tmpdir / "test.db",
        ],
    )
    assert result.exit_code == 0
    output_lower = result.output.lower()
    assert "bicep" in output_lower and "curl" in output_lower


def test_cli_add_lift_works(runner, tmpdir):
    """test that we can add an entry to the db using the cli"""
    # init db first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # call cli with required arguments
    result = runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Bicep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )

    # assert success
    assert result.exit_code == 0
    assert "added" in result.output


def test_cli_add_session_works(runner, tmpdir):
    """test that we can add a session to the db using the cli and a json file"""
    # init db first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])
    # create test json
    INPUT_SESSION = [
        {
            "date": "2023-04-01",
            "program": "P9",
            "program_iteration": 1,
            "lift": "Bicep Curl",
            "weight": 85,
            "reps": 4,
        },
        {
            "date": "2024-04-01",
            "program": "P9",
            "program_iteration": 1,
            "lift": "Tricep Curl",
            "weight": 85,
            "reps": 4,
        },
    ]

    json_path = tmpdir / "session.json"
    with open(json_path, "w") as f:
        json.dump(INPUT_SESSION, f)

    # call cli with required arguments
    result = runner.invoke(
        app,
        [
            "add",
            "session",
            "--db-path",
            tmpdir / "test.db",
            str(json_path),
        ],
    )

    # assert success
    assert result.exit_code == 0
    assert "added" in result.output.lower()


def test_cli_list_lifts_works(runner, tmpdir):
    """test that we can list lifts from the db using the cli"""
    # init db first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add some test entries
    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Bicep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )

    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Tricep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )

    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Bicep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )

    # call cli to list lifts with --top-set filter
    result = runner.invoke(
        app,
        [
            "list",
            "lifts",
            "--db-path",
            tmpdir / "test.db",
        ],
    )

    # assert success and output contains expected data
    assert result.exit_code == 0
    output_lower = result.output.lower()
    assert "bicep" in output_lower and "curl" in output_lower
    assert "tric" in output_lower  # lift name truncated to 'tric' in test data


def test_cli_list_lifts_with_filter(runner, tmpdir):
    """test that we can filter lifts using the cli"""
    # init db first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add some test entries with different programs
    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Bicep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )

    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "Push/Pull/Legs",
            "--iteration",
            "1",
            "--lift",
            "Bench Press",
            "--weight",
            "100",
            "--reps",
            "5",
        ],
    )

    # call cli to list lifts filtered by program
    result = runner.invoke(
        app,
        [
            "list",
            "lifts",
            "--db-path",
            tmpdir / "test.db",
            "--program",
            "P9",
        ],
    )

    # assert success and output contains only P9 lifts
    assert result.exit_code == 0
    output_lower = result.output.lower()
    assert "bicep" in output_lower and "curl" in output_lower
    assert "bench press" not in output_lower


def test_cli_list_lifts_no_results(runner, tmpdir):
    """test that we get a proper message when no lifts match the filter"""
    # init db first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add some entries with program P9
    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Bicep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )

    # call cli with a filter that won't match anything
    result = runner.invoke(
        app,
        [
            "list",
            "lifts",
            "--db-path",
            tmpdir / "test.db",
            "--program",
            "NonExistentProgram",
        ],
    )

    # assert success and proper message
    assert result.exit_code == 0
    assert "no lifts found" in result.output.lower()


def test_cli_list_lifts_with_date_filter(runner, tmpdir):
    """test that we can filter lifts by date using the cli"""
    # init db first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add entries on different dates
    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Bicep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )

    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-05-15",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Tricep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )

    # call cli to list lifts filtered by exact date (April 2023)
    result = runner.invoke(
        app,
        [
            "list",
            "lifts",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
        ],
    )

    # assert success and output contains only April lifts
    assert result.exit_code == 0
    output_lower = result.output.lower()
    assert "bicep" in output_lower and "curl" in output_lower
    assert "tricep" not in output_lower or "curl" not in output_lower


def test_cli_list_lifts_with_top_set_filter(runner, tmpdir):
    """test that we can filter lifts by top_set flag using the cli"""
    # init db first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add entries with different flags
    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Bicep Curl",
            "--weight",
            "85",
            "--reps",
            "4",
        ],
    )

    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Bench Press",
            "--weight",
            "100",
            "--reps",
            "5",
            "--top-set",  # top_set flag
        ],
    )

    # call cli to list lifts filtered by top_set flag
    result = runner.invoke(
        app,
        [
            "list",
            "lifts",
            "--db-path",
            tmpdir / "test.db",
            "--top-set",  # top_set filter
        ],
    )

    # assert success and output contains only top set lifts
    assert result.exit_code == 0
    output_lower = result.output.lower()
    assert "bench" in output_lower and "press" in output_lower
    assert "bicep" not in output_lower or "curl" not in output_lower


def test_cli_list_lifts_with_limit(runner, tmpdir):
    """test that we can limit the number of results using the cli"""
    # init db first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add 5 entries
    for i in range(1, 6):
        runner.invoke(
            app,
            [
                "add",
                "lift",
                "--db-path",
                tmpdir / "test.db",
                "--date",
                f"2023-04-{i:02d}",
                "--program",
                "P9",
                "--iteration",
                "1",
                "--lift",
                f"Lift {i}",
                "--weight",
                str(85 + i),
                "--reps",
                "4",
            ],
        )

    # call cli with limit of 2
    result = runner.invoke(
        app,
        [
            "list",
            "lifts",
            "--db-path",
            tmpdir / "test.db",
            "--limit",
            "2",
        ],
    )

    # assert success and output contains only 2 entries
    assert result.exit_code == 0
    lines = [line.strip() for line in result.output.split("\n") if line.strip()]
    # First two lines are header + empty, so data rows start from index 2
    data_lines = [line for line in lines[2:] if "lift" in line.lower()]
    assert len(data_lines) == 2


def test_cli_add_lift_with_virtual_columns(runner, tmpdir):
    """test that virtual columns are computed when adding a lift via CLI."""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # Add entry with known values: weight=200, reps=5 -> 1RM = 228.57
    result = runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Squat",
            "--weight",
            "200",
            "--reps",
            "5",
        ],
    )

    assert result.exit_code == 0
    assert "added" in result.output


def test_cli_list_lifts_shows_virtual_columns(runner, tmpdir):
    """test that virtual columns appear in list output."""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # Add entry with known values: weight=200, reps=5 -> 1RM = 228.57
    runner.invoke(
        app,
        [
            "add",
            "lift",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-01",
            "--program",
            "P9",
            "--iteration",
            "1",
            "--lift",
            "Squat",
            "--weight",
            "200",
            "--reps",
            "5",
        ],
    )

    # List lifts and verify virtual columns appear in output
    result = runner.invoke(
        app, ["list", "lifts", "--db-path", tmpdir / "test.db"]
    )

    assert result.exit_code == 0
    # Virtual columns should be present with computed values
    # estimated_1rm = 200 * (36 / (37 - 5)) = 225.0, volume = 200 * 5 = 1000.0
    assert "225." in result.output and "1000." in result.output


def test_cli_list_lifts_with_virtual_columns_aggregation(runner, tmpdir):
    """test that virtual columns work correctly with aggregation queries."""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # Add multiple entries for same program_iteration/lift combination
    weights_reps = [(200, 5), (210, 4), (190, 6)]
    for weight, reps in weights_reps:
        runner.invoke(
            app,
            [
                "add",
                "lift",
                "--db-path",
                tmpdir / "test.db",
                "--date",
                f"2023-04-{(weights_reps.index((weight, reps)) + 1):02d}",
                "--program",
                "P9",
                "--iteration",
                "1",
                "--lift",
                "Squat",
                "--weight",
                str(weight),
                "--reps",
                str(reps),
            ],
        )

    # List lifts and verify multiple entries exist
    result = runner.invoke(
        app, ["list", "lifts", "--db-path", tmpdir / "test.db"]
    )

    assert result.exit_code == 0
    assert result.output.count("Squat") >= 3
