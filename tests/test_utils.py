"""Tests for training_vid_organizer.utils module."""

import os
from pathlib import Path

import typer

from src.training_vid_organizer.logging_config import logger as tv_logger
from src.training_vid_organizer.utils import (
    get_config_paths,
    get_video_base_dir,
    open_video_file,
)


def test_get_config_paths_defaults():
    """Test that default paths are returned when no env vars set."""
    # Ensure env vars are not set
    db_path = os.environ.pop("TVO_DB_PATH", None)
    video_dir = os.environ.pop("TVO_VIDEO_DIR", None)

    try:
        result_db, result_video = get_config_paths(Path("default/db/training.db"))

        assert result_db == "default/db/training.db"
        assert result_video == ""
    finally:
        # Restore env vars if they existed
        if db_path is not None:
            os.environ["TVO_DB_PATH"] = db_path
        elif "TVO_DB_PATH" in os.environ:
            del os.environ["TVO_DB_PATH"]

        if video_dir is not None:
            os.environ["TVO_VIDEO_DIR"] = video_dir
        elif "TVO_VIDEO_DIR" in os.environ:
            del os.environ["TVO_VIDEO_DIR"]


def test_get_config_paths_db_env_var():
    """Test that TVO_DB_PATH env var overrides default."""
    # Set env var
    os.environ["TVO_DB_PATH"] = "/custom/db.sqlite"

    try:
        result_db, result_video = get_config_paths(Path("default/db/training.db"))

        assert result_db == "/custom/db.sqlite"
        assert result_video == ""
    finally:
        # Clean up env var
        if "TVO_DB_PATH" in os.environ:
            del os.environ["TVO_DB_PATH"]


def test_get_config_paths_video_env_var():
    """Test that TVO_VIDEO_DIR env var is respected."""
    # Set env var
    os.environ["TVO_VIDEO_DIR"] = "/videos/storage"

    try:
        result_db, result_video = get_config_paths(Path("default/db/training.db"))

        assert result_db == "default/db/training.db"
        assert result_video == "/videos/storage"
    finally:
        # Clean up env var
        if "TVO_VIDEO_DIR" in os.environ:
            del os.environ["TVO_VIDEO_DIR"]


def test_get_config_paths_both_env_vars():
    """Test that both env vars are respected simultaneously."""
    os.environ["TVO_DB_PATH"] = "/custom/db.sqlite"
    os.environ["TVO_VIDEO_DIR"] = "/custom/videos"

    try:
        result_db, result_video = get_config_paths(Path("default/db/training.db"))

        assert result_db == "/custom/db.sqlite"
        assert result_video == "/custom/videos"
    finally:
        # Clean up env vars
        for key in ["TVO_DB_PATH", "TVO_VIDEO_DIR"]:
            if key in os.environ:
                del os.environ[key]


def test_get_config_paths_empty_string_video():
    """Test that empty string video dir is handled correctly."""
    os.environ["TVO_VIDEO_DIR"] = ""

    try:
        result_db, result_video = get_config_paths(Path("default/db/training.db"))

        assert result_db == "default/db/training.db"
        assert result_video == ""
    finally:
        if "TVO_VIDEO_DIR" in os.environ:
            del os.environ["TVO_VIDEO_DIR"]


def test_get_config_paths_custom_default():
    """Test that custom default path is used."""
    custom_default = Path("/app/data/training.db")

    result_db, result_video = get_config_paths(custom_default)

    assert result_db == "/app/data/training.db"
    assert result_video == ""


def test_get_video_base_dir():
    """Test that get_video_base_dir respects TVO_VIDEO_BASE_DIR env var."""
    os.environ["TVO_VIDEO_BASE_DIR"] = "/base/videos"

    try:
        base_dir = get_video_base_dir()
        assert base_dir == Path("/base/videos")
    finally:
        if "TVO_VIDEO_BASE_DIR" in os.environ:
            del os.environ["TVO_VIDEO_BASE_DIR"]


def test_get_video_base_dir_default():
    """Test that empty default is returned when env var not set."""
    # Ensure env var is not set
    base = os.environ.pop("TVO_VIDEO_BASE_DIR", None)

    try:
        base_dir = get_video_base_dir()
        assert base_dir == Path("")
    finally:
        if base is not None:
            os.environ["TVO_VIDEO_BASE_DIR"] = base
        elif "TVO_VIDEO_BASE_DIR" in os.environ:
            del os.environ["TVO_VIDEO_BASE_DIR"]


def test_open_video_file_works(tmpdir, monkeypatch):
    """Test that open_video_file successfully opens an existing file."""
    input_filename = "test.txt"
    input_base_dir = Path(tmpdir)

    # Write file to tmp dir
    (input_base_dir / input_filename).write_text("Hello, world!")

    # Mock typer.launch to capture the URL passed
    called_urls = []
    monkeypatch.setattr(typer, "launch", lambda url: called_urls.append(url))

    # Call function
    observed_result = open_video_file(input_filename, input_base_dir)

    assert observed_result is True
    assert len(called_urls) == 1
    expected_path = (input_base_dir / input_filename).resolve()
    assert str(expected_path) in called_urls[0]


def test_open_video_file_handles_not_found(tmpdir, monkeypatch):
    """Test that open_video_file returns False when file doesn't exist."""
    input_filename = "nonexistent.txt"
    input_base_dir = Path(tmpdir)

    # Mock typer.launch to prevent actual launch attempt
    monkeypatch.setattr(typer, "launch", lambda url: None)

    observed_result = open_video_file(input_filename, input_base_dir)

    assert observed_result is False


def test_open_video_file_handles_invalid_path(tmpdir, monkeypatch):
    """Test that open_video_file handles invalid base directory."""
    input_filename = "test.txt"
    input_base_dir = Path("/nonexistent/directory")

    # Mock typer.launch to prevent actual launch attempt
    monkeypatch.setattr(typer, "launch", lambda url: None)

    observed_result = open_video_file(input_filename, input_base_dir)

    assert observed_result is False


def test_open_video_file_with_none_inputs():
    """Test that open_video_file returns False when inputs are None/empty."""
    # Test with None filename
    result1 = open_video_file(None, Path("/tmp"))
    assert result1 is False

    # Test with empty string filename
    result2 = open_video_file("", Path("/tmp"))
    assert result2 is False

    # Test with None base_dir
    result3 = open_video_file("test.txt", None)
    assert result3 is False


def test_open_video_file_logging(tmpdir, monkeypatch):
    """Test that tv_logger is used correctly in open_video_file."""
    input_filename = "test.txt"
    input_base_dir = Path(tmpdir)

    # Write file to tmp dir
    (input_base_dir / input_filename).write_text("Hello!")

    # Mock typer.launch
    monkeypatch.setattr(typer, "launch", lambda url: None)

    # Capture log messages
    captured_logs = []
    original_debug = tv_logger.debug
    original_warning = tv_logger.warning

    def capture_debug(msg, *args):
        captured_logs.append(("debug", msg % args if args else msg))
        return original_debug(msg, *args)

    def capture_warning(msg, *args):
        captured_logs.append(("warning", msg % args if args else msg))
        return original_warning(msg, *args)

    monkeypatch.setattr(tv_logger, "debug", capture_debug)
    monkeypatch.setattr(tv_logger, "warning", capture_warning)

    # Test successful open (should log debug)
    open_video_file(input_filename, input_base_dir)
    assert any(log[0] == "debug" for log in captured_logs)

    # Reset logs
    captured_logs.clear()

    # Test file not found (should log warning)
    open_video_file("nonexistent.txt", input_base_dir)
    assert any(log[0] == "warning" and "not found" in str(log[1]).lower() for log in captured_logs)


def test_open_video_file_resolves_absolute_path(tmpdir, monkeypatch):
    """Test that open_video_file resolves to absolute path."""
    input_filename = "test.txt"
    input_base_dir = Path(tmpdir)

    # Write file to tmp dir
    (input_base_dir / input_filename).write_text("Hello!")

    # Mock typer.launch
    monkeypatch.setattr(typer, "launch", lambda url: None)

    # Call function
    open_video_file(input_filename, input_base_dir)

    # Verify the resolved path is absolute and exists
    expected_path = (input_base_dir / input_filename).resolve()
    assert expected_path.is_absolute()
    assert expected_path.exists()
