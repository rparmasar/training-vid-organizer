"""Tests for update and delete CLI commands."""

from src.training_vid_organizer.cli import app


def test_cli_update_lift_success(runner, tmpdir):
    """test that we can update a lift entry using the cli"""
    # init db first
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add an entry to get its ID (first row = id 1)
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

    # update the entry by ID
    result = runner.invoke(
        app,
        [
            "update",
            "1",
            "--db-path",
            tmpdir / "test.db",
            "--date",
            "2023-04-02",
            "--weight",
            "90",
        ],
    )

    # assert success and output contains update confirmation
    assert result.exit_code == 0
    assert "updated" in result.output.lower()


def test_cli_update_lift_nonexistent_id(runner, tmpdir):
    """test that updating a non-existent ID returns friendly error"""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # try to update an ID that doesn't exist
    result = runner.invoke(
        app,
        [
            "update",
            "999",
            "--db-path",
            tmpdir / "test.db",
            "--weight",
            "100",
        ],
    )

    # assert error message but no crash
    assert result.exit_code == 0
    assert "no row found" in result.output.lower()


def test_cli_update_lift_partial_fields(runner, tmpdir):
    """test that we can update only specific fields"""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add entry with filepath (will be stored as string)
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
            "--filepath",
            "/path/to/vid.mp4",
        ],
    )

    # update only the filepath, leaving other fields unchanged
    result = runner.invoke(
        app,
        [
            "update",
            "1",
            "--db-path",
            tmpdir / "test.db",
            "--filepath",
            "/new/path/to/vid.mp4",
        ],
    )

    assert result.exit_code == 0
    assert "updated" in result.output.lower()


def test_cli_update_lift_invalid_field(runner, tmpdir):
    """test that Typer rejects unrecognized CLI options (expected behavior)"""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add entry first
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

    # update with an invalid field name - Typer treats this as a CLI error
    result = runner.invoke(
        app,
        [
            "update",
            "1",
            "--db-path",
            tmpdir / "test.db",
            "--invalid-field-name",
            "some_value",
            "--date",
            "2023-04-02",  # valid field, but Typer fails before reaching it
        ],
    )

    # Typer exits with code 2 for unrecognized options (expected)
    assert result.exit_code == 2
    assert (
        "no such option" in result.output.lower()
        or "invalid value" in result.output.lower()
    )


def test_cli_delete_lift_success(runner, tmpdir):
    """test that we can delete a lift entry using the cli"""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add an entry to get its ID (first row = id 1)
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

    # delete the entry by ID with --force to skip prompt
    result = runner.invoke(
        app,
        [
            "delete",
            "1",
            "--db-path",
            tmpdir / "test.db",
            "--force",
        ],
    )

    # assert success and output contains delete confirmation
    assert result.exit_code == 0
    assert "deleted" in result.output.lower()


def test_cli_delete_lift_nonexistent_id(runner, tmpdir):
    """test that deleting a non-existent ID returns friendly error"""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # try to delete an ID that doesn't exist
    result = runner.invoke(
        app,
        [
            "delete",
            "999",
            "--db-path",
            tmpdir / "test.db",
            "--force",
        ],
    )

    # assert error message but no crash
    assert result.exit_code == 0
    assert "no row found" in result.output.lower()


def test_cli_delete_lift_without_force_aborted(runner, tmpdir):
    """test that delete without --force prompts and aborts on no input"""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add an entry first
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

    # try to delete without --force and without input (should abort)
    result = runner.invoke(
        app,
        [
            "delete",
            "1",
            "--db-path",
            tmpdir / "test.db",
        ],
    )

    assert result.exit_code == 1
    assert "aborted" in result.output.lower()


def test_cli_delete_lift_with_confirmation(runner, tmpdir):
    """test that delete with --force skips prompt"""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add an entry first
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

    # delete with --force (no prompt expected)
    result = runner.invoke(
        app,
        [
            "delete",
            "1",
            "--db-path",
            tmpdir / "test.db",
            "--force",
        ],
    )

    assert result.exit_code == 0
    assert "deleted" in result.output.lower()


def test_cli_delete_lift_verifies_removal(runner, tmpdir):
    """test that deleted entry is actually removed from database"""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # add an entry
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

    # delete it with --force
    runner.invoke(
        app,
        [
            "delete",
            "1",
            "--db-path",
            tmpdir / "test.db",
            "--force",
        ],
    )

    # verify it's gone by listing all lifts
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


def test_cli_update_and_delete_combined_workflow(runner, tmpdir):
    """test a full workflow: add -> update -> delete"""
    runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])

    # 1. Add entry (id=1)
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

    # 2. Update entry (id=1)
    result = runner.invoke(
        app,
        [
            "update",
            "1",
            "--db-path",
            tmpdir / "test.db",
            "--weight",
            "90",
        ],
    )
    assert result.exit_code == 0
    assert "updated" in result.output.lower()

    # 3. Delete entry (id=1) with --force
    result = runner.invoke(
        app,
        [
            "delete",
            "1",
            "--db-path",
            tmpdir / "test.db",
            "--force",
        ],
    )
    assert result.exit_code == 0
    assert "deleted" in result.output.lower()
