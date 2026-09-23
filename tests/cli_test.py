"""CLI integration tests - smoke tests for all commands."""

from typer.testing import CliRunner

from training_vid_organizer.cli import app

runner = CliRunner()


def test_version_flag():
    """Verify --version displays correct version string."""
    result = runner.invoke(app, ["--version"])
    assert "v0.1.0" in result.output
    assert result.exit_code == 0


def test_help_output():
    """Verify help text renders without errors."""
    result = runner.invoke(app, ["--help"])
    assert any(x in result.output.lower() for x in ["search", "categorize", "metadata"])
    assert result.exit_code == 0


def test_search_current_directory():
    """Verify search runs on current directory without errors."""
    result = runner.invoke(app, ["search", "."])
    assert "Searching in:" in result.output
    assert result.exit_code == 0


def test_search_with_tags_flag():
    """Verify --tags flag is accepted and parsed."""
    result = runner.invoke(app, ["search", ".", "--tags", "python"])
    assert "Searching in:" in result.output
    assert result.exit_code == 0


def test_categorize_with_tags():
    """Verify categorize runs with tags provided."""
    result = runner.invoke(app, ["categorize", "python", "--output-dir", "videos"])
    assert any(x in result.output.lower() for x in ["categorizing videos"])
    assert result.exit_code == 0


def test_categorize_requires_tags():
    """Verify missing tags argument returns non-zero exit code (Typer convention: 2)."""
    result = runner.invoke(app, ["categorize"])
    assert result.exit_code == 2


def test_metadata_with_valid_path(tmp_path):
    """Verify metadata runs on existing file path."""
    # Create a dummy file to use as valid path
    (tmp_path / "dummy.txt").touch()
    result = runner.invoke(app, ["metadata", str(tmp_path)])
    assert any(x in result.output.lower() for x in ["metadata"])
    assert result.exit_code == 0


def test_metadata_invalid_path():
    """Verify metadata with non-existent path returns exit code 1."""
    result = runner.invoke(app, ["metadata", "/nonexistent/video.mp4"])
    assert result.exit_code == 1


def test_search_nonexistent_path():
    """Verify search on non-existent path returns exit code 1."""
    result = runner.invoke(app, ["search", "/nonexistent/path"])
    assert result.exit_code == 1
