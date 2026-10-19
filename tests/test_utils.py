"""Tests for training_vid_organizer.utils module."""

from pathlib import Path

from src.training_vid_organizer.utils import (
    get_norm_key,
)


def test_get_norm_key_valid_file():
    """Test that get_norm_key correctly extracts NORM value from valid filename."""
    # Test basic format: prefix_NORM####.ext
    path = Path("195035136_NORM0162.MP4")
    result = get_norm_key(path)
    assert result == (162, "NORM162_195035136.MP4")

    # Test different NORM values
    path = Path("273678336_NORM0165.mp4")
    result = get_norm_key(path)
    assert result == (165, "NORM165_273678336.mp4")

    # Test with uppercase extension
    path = Path("file_NORM9999.MP4")
    result = get_norm_key(path)
    assert result == (9999, "NORM9999_file.MP4")


def test_get_norm_key_invalid_format():
    """Test that get_norm_key returns None for invalid filenames."""
    # No NORM in name
    path = Path("123456789_video.mp4")
    assert get_norm_key(path) is None

    # NORM not at expected position (in first part instead of second)
    path = Path("NORM0012_123456789.mp4")
    assert get_norm_key(path) is None

    # Missing underscore separator
    path = Path("123456789NORM0012.mp4")
    assert get_norm_key(path) is None

    # Empty filename
    path = Path("")
    assert get_norm_key(path) is None


def test_get_norm_key_edge_cases():
    """Test edge cases and error handling."""
    # NORM without numeric suffix (should fail on int conversion)
    path = Path("123456789_NORMabc.mp4")
    assert get_norm_key(path) is None

    # Multiple underscores - NORM must be immediately after first underscore
    path = Path("prefix_extra_NORM0012.mp4")
    assert get_norm_key(path) is None

    # No extension
    path = Path("123456789_NORM0012")
    result = get_norm_key(path)
    assert result == (12, "NORM12_123456789")


def test_get_norm_key_zero_value():
    """Test that NORM0 is handled correctly."""
    path = Path("123456789_NORM0.mp4")
    result = get_norm_key(path)
    assert result == (0, "NORM0_123456789.mp4")
