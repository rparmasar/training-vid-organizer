"""Shared test fixtures for CLI testing."""

import pytest
from typer.testing import CliRunner

@pytest.fixture
def runner():
    """Provide a CliRunner instance for all tests."""
    return CliRunner()
