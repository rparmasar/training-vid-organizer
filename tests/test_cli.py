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
