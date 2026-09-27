"""Shared test fixtures for CLI testing."""

import os
import pytest
from typer.testing import CliRunner


@pytest.fixture(autouse=True)
def clean_tvo_env():
    """Clean up TVO env vars before and after each test."""
    # Save existing values
    saved_db = os.environ.pop("TVO_DB_PATH", None)
    saved_video = os.environ.pop("TVO_VIDEO_DIR", None)

    yield  # run the test

    # Restore or remove as appropriate
    if saved_db is not None:
        os.environ["TVO_DB_PATH"] = saved_db
    elif "TVO_DB_PATH" in os.environ:
        del os.environ["TVO_DB_PATH"]

    if saved_video is not None:
        os.environ["TVO_VIDEO_DIR"] = saved_video
    elif "TVO_VIDEO_DIR" in os.environ:
        del os.environ["TVO_VIDEO_DIR"]


@pytest.fixture
def runner():
    """Provide a CliRunner instance for all tests."""
    return CliRunner()
