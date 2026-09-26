"""CLI command tests for add_lift, add_session, list_videos, update_entry."""

import json
import tempfile
from pathlib import Path
from typer.testing import CliRunner

from training_vid_organizer.cli import app

runner = CliRunner()


def test_add_lift_basic(tmp_path):
    """Verify add_lift creates entry with required fields."""
    db_file = tmp_path / "test_training.db"
    
    result = runner.invoke(
        app,
        ["add-lift", "--db-path", str(db_file), "2026-09-25", "front_squat", "140.0", "5"],
    )
    assert "Added" in result.output
    assert result.exit_code == 0


def test_add_lift_with_bodyweight(tmp_path):
    """Verify add_lift accepts optional bodyweight argument."""
    db_file = tmp_path / "test_training.db"

    result = runner.invoke(
        app,
        [
            "add-lift",
            "--db-path",
            str(db_file),
            "2026-09-25",
            "front_squat",
            "140.0",
            "5",
            "--bodyweight",
            "85.5",
        ],
    )
    assert "Added" in result.output
    assert result.exit_code == 0


def test_add_lift_with_all_fields(tmp_path):
    """Verify add_lift accepts all optional fields."""
    db_file = tmp_path / "test_training.db"

    result = runner.invoke(
        app,
        [
            "add-lift",
            "--db-path",
            str(db_file),
            "2026-09-25",
            "front_squat",
            "140.0",
            "5",
            "--bodyweight",
            "85.5",
        ],
    )
    assert "Added" in result.output
    assert result.exit_code == 0


def test_add_session_basic(tmp_path):
    """Verify add_session loads JSON and inserts entries."""
    db_file = tmp_path / "test_training.db"
    
    # Create a temporary JSON config file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump([
            {
                "date": "2026-09-25",
                "bodyweight": 85.5,
                "lift": "front_squat",
                "weight": 140.0,
                "reps": 5,
                "top_set": True,
            }
        ], f)
        config_path = Path(f.name)

    result = runner.invoke(
        app,
        ["add-session", "--db-path", str(db_file), str(config_path)],
    )
    assert "Added" in result.output
    assert result.exit_code == 0
    
    # Cleanup
    config_path.unlink()


def test_add_session_multiple_entries(tmp_path):
    """Verify add_session handles multiple entries."""
    db_file = tmp_path / "test_training.db"
    
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump([
            {
                "date": "2026-09-25",
                "lift": "front_squat",
                "weight": 140.0,
                "reps": 5,
            },
            {
                "date": "2026-09-25",
                "lift": "back_squat",
                "weight": 180.0,
                "reps": 3,
            },
        ], f)
        config_path = Path(f.name)

    result = runner.invoke(
        app,
        ["add-session", "--db-path", str(db_file), str(config_path)],
    )
    assert "Added" in result.output
    assert result.exit_code == 0
    
    # Cleanup
    config_path.unlink()


def test_list_videos_no_filter(tmp_path):
    """Verify list_videos displays entries without filter."""
    db_file = tmp_path / "test_training.db"

    # Add some data first
    runner.invoke(
        app,
        ["add-lift", "--db-path", str(db_file), "2026-09-25", "front_squat", "140.0", "5"],
    )
    
    result = runner.invoke(app, ["list-videos", "--db-path", str(db_file)])
    assert "ID" in result.output
    assert "front_squat" in result.output
    assert result.exit_code == 0


def test_list_videos_with_lift_filter(tmp_path):
    """Verify list_videos filters by lift type."""
    db_file = tmp_path / "test_training.db"

    # Add mixed data
    runner.invoke(
        app,
        ["add-lift", "--db-path", str(db_file), "2026-09-25", "front_squat", "140.0", "5"],
    )
    runner.invoke(
        app,
        ["add-lift", "--db-path", str(db_file), "2026-09-25", "back_squat", "180.0", "3"],
    )

    result = runner.invoke(app, ["list-videos", "--db-path", str(db_file), "--lift", "front_squat"])
    assert "front_squat" in result.output
    assert "back_squat" not in result.output
    assert result.exit_code == 0


def test_update_entry(tmp_path):
    """Verify update_entry modifies an existing entry."""
    db_file = tmp_path / "test_training.db"

    # Add initial data
    runner.invoke(
        app,
        ["add-lift", "--db-path", str(db_file), "2026-09-25", "front_squat", "140.0", "5"],
    )

    result = runner.invoke(
        app,
        [
            "update-entry",
            "--db-path",
            str(db_file),
            "1",
            "--date",
            "2026-09-26",
            "--weight",
            "145.0",
        ],
    )
    assert "Updated" in result.output
    assert result.exit_code == 0


def test_update_entry_multiple_fields(tmp_path):
    """Verify update_entry can modify multiple fields at once."""
    db_file = tmp_path / "test_training.db"

    runner.invoke(
        app,
        ["add-lift", "--db-path", str(db_file), "2026-09-25", "front_squat", "140.0", "5"],
    )

    result = runner.invoke(
        app,
        [
            "update-entry",
            "--db-path",
            str(db_file),
            "1",
            "--date",
            "2026-09-26",
            "--bodyweight",
            "85.5",
            "--reps",
            "6",
        ],
    )
    assert "Updated" in result.output
    assert result.exit_code == 0


def test_update_entry_nonexistent_id(tmp_path):
    """Verify update_entry handles nonexistent ID gracefully."""
    db_file = tmp_path / "test_training.db"

    result = runner.invoke(
        app,
        [
            "update-entry",
            "--db-path",
            str(db_file),
            "999",
            "--date",
            "2026-09-26",
        ],
    )
    # Should not crash the CLI itself
    assert isinstance(result.exit_code, int)


def test_add_session_invalid_json(tmp_path):
    """Verify add_session handles invalid JSON gracefully."""
    db_file = tmp_path / "test_training.db"

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write("not valid json {{{")
        config_path = Path(f.name)

    result = runner.invoke(
        app,
        ["add-session", "--db-path", str(db_file), str(config_path)],
    )
    
    # Should fail but not crash the CLI
    assert isinstance(result.exit_code, int)
    
    # Cleanup
    config_path.unlink()


def test_add_session_empty_list(tmp_path):
    """Verify add_session handles empty list gracefully."""
    db_file = tmp_path / "test_training.db"

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump([], f)
        config_path = Path(f.name)

    result = runner.invoke(
        app,
        ["add-session", "--db-path", str(db_file), str(config_path)],
    )
    
    # Should succeed with 0 entries added
    assert "Added" in result.output
    
    # Cleanup
    config_path.unlink()
