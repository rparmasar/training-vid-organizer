"""Pure database operations for training video organizer."""

from typing import Any, Iterable

from src.models import LiftEntry


def db_add_lift(db: "DB", entry: LiftEntry) -> int:
    """Pure function to add a single lift entry.

    Args:
        db: Database instance
        entry: LiftEntry dataclass instance with typed fields

    Returns:
        ID of inserted row (or 0 on error)
    """
    try:
        with db.connection() as conn:
            c = conn.cursor()
            placeholders = ",".join(["?" for _ in range(5)])
            cols = ", ".join(
                ["date", "bodyweight", "lift", "weight", "reps"]
            )
            values = (
                entry.date,
                entry.bodyweight,
                entry.lift,
                entry.weight,
                entry.reps,
            )
            c.execute(f"INSERT INTO lifts ({cols}) VALUES ({placeholders})", values)
            conn.commit()
            return c.lastrowid or 0
    except Exception:
        return 0


def add_session(db: "DB", entries: Iterable[LiftEntry]) -> int:
    """Pure function to add multiple lift entries from a session.

    Args:
        db: Database instance
        entries: List of LiftEntry dataclass instances (or dicts with same fields)

    Returns:
        Number of rows inserted (0 on error)
    """
    try:
        if not entries:
            return 0

        with db.connection() as conn:
            c = conn.cursor()
            cols = ", ".join(
                ["date", "bodyweight", "lift", "weight", "reps"]
            )
            placeholders = ",".join(["?" for _ in range(len(entries[0]))])

            # Handle both LiftEntry instances and dicts
            data_list: list[tuple[Any, ...]] = []
            for entry in entries:
                if hasattr(entry, "__dataclass_fields__"):  # LiftEntry instance
                    data_list.append(
                        (entry.date, entry.bodyweight, entry.lift, entry.weight, entry.reps)
                    )
                else:  # dict
                    data_list.append(
                        (
                            entry.get("date"),
                            entry.get("bodyweight"),
                            entry.get("lift"),
                            entry.get("weight"),
                            entry.get("reps"),
                        )
                    )

            c.executemany(f"INSERT INTO lifts ({cols}) VALUES ({placeholders})", data_list)
            conn.commit()
            return len(data_list)
    except Exception:
        return 0


def list_videos(db: "DB", filters: dict[str, Any] | None = None) -> Iterable[tuple]:
    """Pure function to query training videos.

    Args:
        db: Database instance
        filters: Optional dictionary of column-value pairs to filter by

    Returns:
        Iterable of rows (tuples) from the database
    """
    try:
        with db.connection() as conn:
            c = conn.cursor()
            
            if filters is None or not filters:
                query = "SELECT * FROM lifts"
            else:
                conditions = []
                values = []
                for col, val in filters.items():
                    conditions.append(f"{col}=?")
                    values.append(val)
                
                if conditions:
                    query = f"SELECT * FROM lifts WHERE {' AND '.join(conditions)}"
                    c.execute(query, values)
                else:
                    query = "SELECT * FROM lifts"
            
            return c.fetchall()
    except Exception:
        return []


def update_entry(db: "DB", entry_id: int, updates: dict[str, Any]) -> bool:
    """Pure function to update a lift entry by ID.

    Args:
        db: Database instance
        entry_id: Primary key of the entry to update
        updates: Dictionary of column-value pairs to update

    Returns:
        True if row was updated, False otherwise
    """
    try:
        with db.connection() as conn:
            c = conn.cursor()
            
            if not updates:
                return False
            
            conditions = []
            values = []
            
            for col, val in updates.items():
                conditions.append(f"{col}=?")
                values.append(val)
            
            query = f"UPDATE lifts SET {', '.join(conditions)} WHERE id=?"
            values.append(entry_id)
            
            c.execute(query, values)
            conn.commit()
            return c.rowcount > 0
    except Exception:
        return False
