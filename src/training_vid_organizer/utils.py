import os
from pathlib import Path

import typer

from training_vid_organizer.logging_config import logger as tv_logger


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
