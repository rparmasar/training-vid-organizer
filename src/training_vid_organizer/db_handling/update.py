"""Update and delete operations for SQLite database."""

import sqlite3
from pathlib import Path

from training_vid_organizer.db_handling.db import LiftEntry
from training_vid_organizer.logging_config import logger as tv_logger


def update_lift_entry(db_path: Path, entry_id: int, **kwargs) -> bool:
    """Update a lift entry by ID with only the provided fields.

    Args:
        db_path: Path to SQLite database file.
        entry_id: Primary key of row to update.
        **kwargs: Field names and values to set (e.g., date="2025-03-16", weight=225).

    Returns:
        True if a row was updated, False otherwise (e.g., ID not found).
    """
    # Validate field names against LiftEntry fields
    valid_fields = {f.name for f in LiftEntry.__dataclass_fields__.values()}
    provided_fields = set(kwargs.keys())

    unknown_fields = provided_fields - valid_fields
    if unknown_fields:
        tv_logger.warning(
            f"update_lift_entry: ignoring unknown fields: {unknown_fields}"
        )
        kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}

    # Convert string filepath to Path for validation, then back to string for SQL binding
    if "filename" in kwargs:
        original_value = kwargs["filename"]
        if isinstance(original_value, str):
            kwargs["filename"] = Path(original_value)  # For type validation
            kwargs["filename"] = str(
                kwargs["filename"]
            )  # Convert back to string for SQL

    if not kwargs:
        tv_logger.debug("update_lift_entry: no fields to update")
        return False

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # Build SET clause from provided kwargs
        set_clauses = []
        values = []
        for key, value in kwargs.items():
            if isinstance(value, bool):
                set_clauses.append(f"{key} = {'1' if value else '0'}")
            elif value is None:
                # Allow setting a field to NULL explicitly
                set_clauses.append(f"{key} = NULL")
            else:
                set_clauses.append(f"{key} = ?")
                values.append(value)

        if not set_clauses:
            return False

        sql = f"UPDATE lifts SET {', '.join(set_clauses)} WHERE id = ?"
        values.append(entry_id)

        cursor.execute(sql, values)
        conn.commit()

        tv_logger.debug(f"updated lift entry #{entry_id} with fields={kwargs}")
        return cursor.rowcount > 0

    except sqlite3.Error as e:
        raise ValueError(f"Database error while updating row #{entry_id}: {e}") from e
    finally:
        conn.close()


def delete_lift_entry(db_path: Path, entry_id: int) -> bool:
    """Delete a lift entry by ID.

    Args:
        db_path: Path to SQLite database file.
        entry_id: Primary key of row to delete.

    Returns:
        True if a row was deleted, False otherwise (e.g., ID not found).
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM lifts WHERE id = ?"
        cursor.execute(sql, (entry_id,))
        conn.commit()

        tv_logger.debug(f"deleted lift entry #{entry_id}")
        return cursor.rowcount > 0

    except sqlite3.Error as e:
        raise ValueError(f"Database error while deleting row #{entry_id}: {e}") from e
    finally:
        conn.close()
