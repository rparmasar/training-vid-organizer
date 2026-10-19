import os
from pathlib import Path

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
    """Resolve filename to absolute path and launch with VLC.

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
        # Use VLC explicitly for reliable GUI playback
        import subprocess

        cmd = ["vlc", str(abs_path), "--no-audio", "--video-on-top"]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        tv_logger.debug(f"Opened video with VLC: {abs_path}")
        return_code = proc.wait(timeout=5.0)
        # VLC returns 0 on success, non-zero on error (but files may still open)
        tv_logger.info(f"VLC exited with code {return_code} for {abs_path}")
        return True
    except subprocess.TimeoutExpired:
        tv_logger.warning(f"VLC timed out for {abs_path}, killing process")
        proc.kill()
        return False
    except FileNotFoundError:
        tv_logger.error("VLC not found in PATH. Please install VLC.")
        return False
    except Exception as e:
        tv_logger.error(f"Failed to open video '{abs_path}': {e}")
        return False


def open_vlc_sequential(filepaths: list[str], base_dir: Path) -> None:
    """Open multiple video files sequentially in a single VLC instance.

    Files are opened one after another as tabs, allowing comparison of lift
    performance across different sessions or angles without closing and reopening.
    The first file starts playing; subsequent files open as new tabs when the
    current one is closed or finished.

    Args:
        filepaths: List of absolute file paths to open.
        base_dir: Base directory for reference/logging.
    """
    if not filepaths:
        return

    tv_logger.info(f"Opening {len(filepaths)} files with VLC (sequential, autoplay on)")

    full_file_paths = [str(base_dir / path) for path in filepaths]
    try:
        import subprocess

        # Build VLC command with Qt interface for better Wayland/GUI compatibility
        cmd = (
            ["vlc"]
            + full_file_paths
            + [
                "-I",
                "qt",  # Use Qt interface instead of VLM for modern display servers
                "--video-on-top",
            ]
        )

        tv_logger.debug(f"VLC command: {' '.join(cmd)}")

        proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        # Wait for VLC to exit (user closes it manually)
        return_code = proc.wait()

        # Broken pipe is common when closing VLC tabs; ignore it
        if return_code != 0 and "Broken pipe" not in str(return_code):
            tv_logger.warning(f"VLC exited with code {return_code}")

    except FileNotFoundError:
        tv_logger.error("VLC not found in PATH. Please install VLC.")
    except Exception as e:
        tv_logger.error(f"Failed to open videos with VLC: {e}")


def open_video_file_from_entry(entry, db_path) -> bool:
    """Open a single video file from a LiftEntry using DB-configured paths.

    Args:
        entry: LiftEntry object containing filename.
        db_path: Database path for config lookup.

    Returns:
        True if opened successfully, False otherwise.
    """
    _, video_dir = get_config_paths(db_path)
    if not video_dir:
        tv_logger.warning("No video directory configured")
        return False

    filename = str(entry.filename) if entry.filename else None
    return open_video_file(filename, Path(video_dir))
