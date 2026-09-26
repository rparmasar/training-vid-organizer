"""Pure CRUD command functions for database operations."""

from typing import Optional, Iterable

from src.db import DB
from src.models import LiftEntry


def add_lift(db: "DB", entry: LiftEntry) -> int:
    """Add a single lift entry.

    Args:
        db: Database instance
        entry: LiftEntry dataclass instance

    Returns:
        Number of rows inserted (0 on error)
    """
    from src.training_vid_organizer.db_operations import db_add_lift
    return db_add_lift(db, entry)


def add_session(db: "DB", entries: Iterable[LiftEntry]) -> int:
    """Add multiple lift entries from a session.

    Args:
        db: Database instance
        entries: List of LiftEntry dataclass instances (or dicts with same fields)

    Returns:
        Number of rows inserted (0 on error)
    """
    from src.training_vid_organizer.db_operations import add_session as _add_session
    return _add_session(db, entries)


def list_videos(db: "DB", filters: Optional[dict] = None) -> Iterable[tuple]:
    """List training videos with optional filters.

    Args:
        db: Database instance
        filters: Dict of filter criteria (e.g., {"lift": "front_squat"})

    Returns:
        Iterable of tuples containing row data
    """
    from src.training_vid_organizer.db_operations import list_videos as _list_videos
    if filters is not None:
        return _list_videos(db, filters)  # type: ignore[union-attr]
    return _list_videos(db)


def update_entry(
    db: "DB", entry_id: int, updates: dict[str, object]
) -> int:
    """Update a lift entry by ID.

    Args:
        db: Database instance
        entry_id: Primary key of the entry to update
        updates: Dict of field names and new values to set

    Returns:
        Number of rows updated (0 on error or no match)
    """
    from src.training_vid_organizer.db_operations import update_entry as _update_entry
    return _update_entry(db, entry_id, updates)  # type: ignore[union-attr]
