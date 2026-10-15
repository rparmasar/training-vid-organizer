import os
from pathlib import Path

import typer

from training_vid_organizer.logging_config import logger as tv_logger


def get_norm_key(path: Path) -> tuple[int, str] | None:
    """Extract numeric NORM key and proposed normalized filename.

    Returns (numeric_value, new_filename) if valid, else None.
    Example: "229638144_NORM0012.MP4" → (12, "NORM0012_229638144.MP4")
    """
    try:
        parts = path.name.split("_", 1)
        if len(parts) < 2 or "NORM" not in parts[1]:
            return None

        norm_part = parts[1].split(".")[0]

        # Extract numeric value after "NORM" (e.g., "NORM0012" → 12)
        if not norm_part.startswith("NORM"):
            return None
        numeric_value = int(norm_part[4:])

        # New format: NORM####_original_prefix.ext
        new_name = f"NORM{numeric_value}_{parts[0]}" + (path.suffix or "")

        return numeric_value, new_name
    except (ValueError, IndexError):
        return None


def get_config_paths(default_db_path: Path) -> tuple[str, str]:
    """Return DB and video paths from environment variables or defaults."""
    db_path = os.getenv("TVO_DB_PATH")
    if not db_path:
        db_path = str(default_db_path)

    video_dir = os.getenv("TVO_VIDEO_DIR", "")  # empty string by default

    return db_path, video_dir


def get_video_base_dir() -> Path:
    """Get the base directory for video files from environment variable."""
    return Path(os.getenv("TVO_VIDEO_BASE_DIR", ""))


def open_video_file(filename: str | None, base_dir: Path) -> bool:
    """Resolve filename to absolute path and launch with default application.

    Args:
        filename: Relative filename from database entry.
        base_dir: Base directory where videos are stored.

    Returns:
        True if file was successfully opened, False otherwise.
    """
    if not filename or not base_dir:
        return False

    abs_path = (base_dir / filename).resolve()

    if not abs_path.exists():
        tv_logger.warning(f"Video file not found: {abs_path}")
        return False

    try:
        typer.launch(str(abs_path))
        tv_logger.debug(f"Opened video: {abs_path}")
        return True
    except Exception as e:
        tv_logger.error(f"Failed to open video '{abs_path}': {e}")
        return False
