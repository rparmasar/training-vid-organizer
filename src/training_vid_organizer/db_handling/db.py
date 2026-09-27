import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any


@dataclass
class LiftEntry:
    """Represents a single lift entry in the lifts table in the database."""

    date: str
    program: str
    program_iteration: int
    bodyweight: float | None = None
    lift: str = ""
    weight: int = 0
    reps: int = 0
    top_set: bool = False
    warm_up_set: bool = False
    reps_in_reserve: int | None = None
    filepath: str | None = None


def init_database(db_path: str | Path) -> None:
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
        print("converting dataclass schema to SQL-friendly schema ...")
        for field in fields(LiftEntry):
            name = field.name.lower()
            dtype = _get_sql_type(field.type, field.default)
            default = _format_default(field.default)
            col_def = f"{name} {dtype}"
            if default is not None:
                col_def += f" DEFAULT {default}"
            columns.append(col_def)

        print("preparing to execute creation query ...")
        create_table_sql = (
            "CREATE TABLE IF NOT EXISTS lifts (" + ", ".join(columns) + ") "
        )
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"successfully created lifts table in database at {db_path=}")
    finally:
        conn.close()


def _get_sql_type(annotation: Any, default: Any) -> str:
    """Determine the SQLite column type from a Python annotation."""
    if annotation is None or annotation == type(None):
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
    if annotation == bool:
        return "INTEGER"
    if annotation == str:
        return "TEXT"
    if annotation == bytes:
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
