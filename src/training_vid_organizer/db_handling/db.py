import sqlite3
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

from training_vid_organizer.logging_config import logger as tv_logger


@dataclass
class LiftEntry:
    """Represents a single lift entry in the lifts table in the database."""

    date: str
    program: str
    program_iteration: int
    lift: str
    weight: int
    reps: int
    bodyweight: float | None = None
    top_set: bool = False
    warm_up_set: bool = False
    reps_in_reserve: int | None = None
    filepath: Path | None = None


def _get_sql_type(annotation: Any, default: Any) -> str:
    """Determine the SQLite column type from a Python annotation."""
    if annotation is None:
        return "TEXT"

    # Handle union types (e.g., float | None)
    origin = getattr(annotation, "__origin__", None)
    if (
        origin is not None
        and hasattr(origin, "__name__")
        and origin.__name__ in ("Union", "Optional")
    ):
        args = annotation.__args__
        if len(args) == 2 and args[1] is type(None):
            return _get_sql_type(args[0], default)

    # Handle basic types
    if annotation in (int, float):
        return "REAL"
    if annotation is bool:
        return "INTEGER"
    if annotation is str:
        return "TEXT"
    if annotation is bytes:
        return "BLOB"

    # Default to TEXT for unknown types
    return "TEXT"


def _format_default(value: Any) -> str | None:
    """Format a default value as SQL."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Escape single quotes in strings
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    return None


def init_database(db_path: Path) -> None:
    """Initialize the SQLite database with the lifts table.

    Args:
        db_path: Path to the SQLite database file.

    Creates a 'lifts' table using the LiftEntry dataclass as schema.
    Uses CREATE TABLE IF NOT EXISTS for idempotency.
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # Build CREATE TABLE statement from dataclass fields
        columns = []
        tv_logger.debug("converting dataclass schema to SQL-friendly schema ...")
        for field in fields(LiftEntry):
            name = field.name.lower()
            dtype = _get_sql_type(field.type, field.default)
            default = _format_default(field.default)
            col_def = f"{name} {dtype}"
            if default is not None:
                col_def += f" DEFAULT {default}"
            columns.append(col_def)

        tv_logger.debug("preparing to execute creation query ...")
        create_table_sql = (
            "CREATE TABLE IF NOT EXISTS lifts (" + ", ".join(columns) + ") "
        )
        cursor.execute(create_table_sql)
        conn.commit()
        tv_logger.info(f"successfully created lifts table in database at {db_path=}")
    finally:
        conn.close()


def add_lift_entry(db_path: Path, entry: LiftEntry) -> int:
    """Insert a lift entry into the database.

    Args:
        db_path: Path to the SQLite database file.
        entry: LiftEntry containing lift entry data matching LiftEntry fields.

    Returns:
        Number of rows affected (should be 1).
    """
    # Convert LiftEntry to dict for dynamic column handling
    columns = {f.name: getattr(entry, f.name) for f in fields(LiftEntry)}

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # Build INSERT statement dynamically from LiftEntry fields
        col_names = ", ".join(columns.keys())
        placeholders = ", ".join(["?" for _ in columns])
        values = list(columns.values())

        insert_sql = f"INSERT INTO lifts ({col_names}) VALUES ({placeholders})"
        cursor.execute(insert_sql, values)
        conn.commit()

        tv_logger.debug(f"inserted lift entry: {entry}")
        return cursor.rowcount
    finally:
        conn.close()


def add_session_entry(db_path: Path, entries: list[LiftEntry]) -> int:
    """Insert multiple lift entries into the database.

    Args:
        db_path: Path to the SQLite database file.
        entries: List of LiftEntry objects (already parsed from JSON at CLI layer).

    Returns:
        Total number of rows affected.

    Raises:
        TypeError: If entries is not a list or contains non-LiftEntry items.
        ValueError: If database write fails.
    """
    # Validate input type immediately
    if not isinstance(entries, list):
        raise TypeError("entries must be a list of LiftEntry objects")

    # Empty list is valid - return 0 without DB access
    if not entries:
        tv_logger.debug("add_session_entry called with empty list")
        return 0

    # Batch insert with executemany (single connection)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        col_names = ", ".join(f.name.lower() for f in fields(LiftEntry))
        placeholders = ", ".join(["?" for _ in fields(LiftEntry)])
        values_list = [
            tuple(getattr(e, f.name) for f in fields(LiftEntry)) for e in entries
        ]

        insert_sql = f"INSERT INTO lifts ({col_names}) VALUES ({placeholders})"
        cursor.executemany(insert_sql, values_list)
        conn.commit()

        tv_logger.info(f"inserted {len(entries)} lift entry(ies) into database")
        return cursor.rowcount
    except sqlite3.Error as e:
        raise ValueError(
            f"Database error while inserting {len(entries)} entries: {e}"
        ) from e
    finally:
        conn.close()
