from src.training_vid_organizer.cli import app

def test_cli_works(runner):
    """Test that the CLI can be run without errors."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0