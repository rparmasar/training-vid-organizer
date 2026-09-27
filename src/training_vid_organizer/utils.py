import os
from pathlib import Path


def get_config_paths(default_db_path: Path) -> tuple[str, str]:
    """Return DB and video paths from environment variables or defaults."""
    db_path = os.getenv("TVO_DB_PATH")
    if not db_path:
        db_path = str(default_db_path)

    video_dir = os.getenv("TVO_VIDEO_DIR", "")  # empty string by default

    return db_path, video_dir
