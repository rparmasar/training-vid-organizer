from src.training_vid_organizer.cli import app

def test_cli_works(runner):
    """Test that the CLI can be run without errors."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0

def test_cli_init_db_works(runner, tmpdir):
    """test that we can initialize the database using some path"""
    result = runner.invoke(app, ["init", "--db-path", tmpdir / "test.db"])
    assert result.exit_code == 0

def test_cli_add_lift_works(runner):
    pass
