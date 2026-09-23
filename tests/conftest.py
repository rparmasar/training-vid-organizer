"""Shared test fixtures for CLI testing."""

import pytest
from typer.testing import CliRunner
from training_vid_organizer.cli import app

runner = CliRunner()


@pytest.fixture
def runner():
    """Provide a CliRunner instance for all tests."""
    return runner
