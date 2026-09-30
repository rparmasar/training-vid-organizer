"""Shared test fixtures for CLI testing."""

import os
from dataclasses import fields

import pytest
from typer.testing import CliRunner

from src.training_vid_organizer.db_handling.db import LiftEntry


@pytest.fixture()
def all_lift_cols():
    """Return all fields of LiftEntry."""
    return (", ").join([field.name for field in fields(LiftEntry)])


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
