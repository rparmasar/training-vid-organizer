import sqlite3
from dataclasses import dataclass, field, fields
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
    filename: Path | None = None
    entry_id: int | None = None


@dataclass
class LiftResult(LiftEntry):
    """Computed view of lift entry with virtual columns.

    Inherits all LiftEntry fields plus computed metrics for database insertion.
    __post_init__ automatically calculates estimated_1rm and total_set_volume.
    """

    # Virtual columns (computed at insert time, stored for fast reads)
    estimated_1rm: float | None = field(init=False, default=None)
    total_set_volume: float | None = field(init=False, default=0.0)

    def __post_init__(self):
        # Bryzycki method: w * (36 / (37 - r))
        if self.weight and self.reps:
            weight = float(self.weight)
            reps = int(self.reps)
            self.estimated_1rm = (
                round(weight * 36.0 / (37.0 - reps), 2)
                if reps > 0 and weight > 0
                else None
            )
            self.total_set_volume = round(float(self.weight) * int(self.reps), 2)


def convert_to_result(entry: LiftEntry | LiftResult) -> LiftResult:
    """Convert a plain LiftEntry to LiftResult with computed virtual columns."""
    if isinstance(entry, LiftResult):
        return entry

    # Create LiftResult without passing init=False fields (they'll be set by __post_init__)
    result = LiftResult(
        date=entry.date,
        program=entry.program,
        program_iteration=entry.program_iteration,
        lift=entry.lift,
        weight=int(entry.weight),
        reps=int(entry.reps),
        bodyweight=entry.bodyweight,
        top_set=entry.top_set,
        warm_up_set=entry.warm_up_set,
        reps_in_reserve=entry.reps_in_reserve,
        filename=entry.filename,
        entry_id=entry.entry_id,  # pass through for backward compat
    )

    # __post_init__ will compute estimated_1rm and total_set_volume automatically
    return result


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

    Creates a 'lifts' table using LiftResult dataclass as schema (includes virtual columns).
    Uses CREATE TABLE IF NOT EXISTS for idempotency.
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # Build CREATE TABLE statement from dataclass fields
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]  # Add ID column first
        tv_logger.debug("converting dataclass schema to SQL-friendly schema ...")

        # Include all init=True fields from LiftResult
        for field in fields(LiftResult):
            if field.init:  # Only include fields that can be initialized
                name = field.name.lower()
                dtype = _get_sql_type(field.type, field.default)
                default = _format_default(field.default)
                col_def = f"{name} {dtype}"
                if default is not None:
                    col_def += f" DEFAULT {default}"
                columns.append(col_def)

        # Manually add virtual columns (init=False fields) to schema
        for field in fields(LiftResult):
            if not field.init:  # Add init=False fields explicitly
                name = field.name.lower()
                dtype = _get_sql_type(field.type, None)  # No default for computed cols
                col_def = f"{name} {dtype}"
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


def add_lift_entry(db_path: Path, entry: LiftEntry | LiftResult) -> int:
    """Insert a lift entry into the database.

    Args:
        db_path: Path to the SQLite database file.
        entry: LiftEntry or LiftResult containing lift entry data.

    Returns:
        Number of rows affected (should be 1).
    """
    # Auto-convert plain LiftEntry to LiftResult with computed virtual columns
    entry = convert_to_result(entry)

    # Convert LiftResult to dict for dynamic column handling (includes virtual cols)
    columns = {f.name: getattr(entry, f.name) for f in fields(LiftResult)}

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # Build INSERT statement dynamically from LiftResult fields
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


def add_session_entry(db_path: Path, data: list[LiftEntry | LiftResult] | Path) -> int:
    """Insert multiple lift entries into the database.

    Args:
        db_path: Path to the SQLite database file.
        data: Either a list of LiftEntry/LiftResult objects OR a CSV file path.

    Returns:
        Total number of rows affected.

    Raises:
        TypeError: If data is not a list or Path, or contains non-LiftEntry items.
        ValueError: If database write fails or CSV parsing fails.
    """
    # Handle CSV input path → parse and convert to LiftEntry list
    if isinstance(data, Path):
        from training_vid_organizer.db_handling.csv_parser import (
            parse_csv_to_lift_entries,
        )

        entries = parse_csv_to_lift_entries(data)
        return add_session_entry(db_path, entries)  # recursive call for existing logic

    # Validate input type immediately (existing JSON/list behavior)
    if not isinstance(entries := data, list):
        raise TypeError("data must be a list of LiftEntry objects or a CSV Path")

    # Empty list is valid - return 0 without DB access
    if not entries:
        tv_logger.debug("add_session_entry called with empty list")
        return 0

    # Auto-convert plain LiftEntry to LiftResult with computed virtual columns
    converted_entries = [
        convert_to_result(e)
        if isinstance(e, LiftEntry) and not isinstance(e, LiftResult)
        else e
        for e in entries
    ]

    # Batch insert with executemany (single connection)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        col_names = ", ".join(f.name.lower() for f in fields(LiftResult))
        placeholders = ", ".join(["?" for _ in fields(LiftResult)])
        values_list = [
            tuple(getattr(e, f.name) for f in fields(LiftResult))
            for e in converted_entries
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
