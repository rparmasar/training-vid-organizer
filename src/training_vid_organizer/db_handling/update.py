"""update and delete operations for sqlite database."""

import sqlite3
from pathlib import Path

from training_vid_organizer.db_handling.csv_parser import parse_csv_for_update
from training_vid_organizer.db_handling.db import LiftEntry
from training_vid_organizer.logging_config import logger as tv_logger


def update_lift_entry(db_path: Path, entry_id: int, **kwargs) -> bool:
    """update a lift entry by id with only the provided fields.

    Args:
        db_path: path to sqlite database file.
        entry_id: primary key of row to update.
        **kwargs: field names and values to set (e.g., date="2025-03-16", weight=225).

    Returns:
        True if a row was updated, False otherwise (e.g., id not found).
    """
    # validate field names against LiftEntry fields
    valid_fields = {f.name for f in LiftEntry.__dataclass_fields__.values()}
    provided_fields = set(kwargs.keys())

    unknown_fields = provided_fields - valid_fields
    if unknown_fields:
        tv_logger.warning(
            f"update_lift_entry: ignoring unknown fields: {unknown_fields}"
        )
        kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}

    # convert string filepath to Path for validation, then back to string for SQL binding
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
    """delete a lift entry by ID.

    Args:
        db_path: path to sqlite database file.
        entry_id: primary key of row to delete.

    Returns:
        True if a row was deleted, False otherwise (e.g., id not found).
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


def update_lift_entries_from_csv(
    db_path: Path, csv_path: Path, id_column: str = "id"
) -> int:
    """Parse CSV and update existing lift entries by ID.

    Args:
        db_path: SQLite database path
        csv_path: CSV file to parse (must include 'id' column)
        id_column: Name of the ID column in CSV (default: "id")

    Returns:
        Number of rows updated

    Raises:
        ValueError: If CSV missing required columns or entries lack IDs
    """
    # Parse CSV into LiftEntry objects with IDs
    entries = parse_csv_for_update(csv_path)

    if not entries:
        tv_logger.debug("No valid entries found in CSV for update")
        return 0

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # Build SET clause from each entry's fields (excluding id)
        set_clauses = []
        values_placeholders = []

        for entry in entries:
            # Collect all field values except 'id'
            row_values = {}
            for field_name, field_value in entry.__dict__.items():
                if field_name != "id":  # Skip ID, it's the WHERE clause
                    set_clauses.append(f"{field_name} = ?")
                    row_values[field_name] = field_value

            # Build placeholders and values for this row
            if row_values:
                placeholders = ",".join("?" * len(row_values))
                values_placeholders.append((placeholders, tuple(row_values.values())))

        if not values_placeholders:
            tv_logger.debug("No fields to update in CSV entries")
            return 0

        # Build WHERE clause with all IDs from the CSV
        ids = [entry.id for entry in entries]
        where_clause = f"WHERE id IN ({','.join('?' * len(ids))})"

        # Combine all values: row values + IDs for WHERE clause
        all_values = []
        for placeholders, row_vals in values_placeholders:
            all_values.extend(row_vals)
        all_values.extend(ids)

        sql = f"UPDATE lifts SET {', '.join(set_clauses)} {where_clause}"

        tv_logger.debug(
            f"Executing bulk update with {len(entries)} entries, SQL length={len(sql)}"
        )

        cursor.execute(sql, all_values)
        conn.commit()

        updated_count = cursor.rowcount
        tv_logger.debug(f"Bulk updated {updated_count} lift entries from CSV")
        return updated_count

    except sqlite3.Error as e:
        raise ValueError(f"Database error while updating lifts from CSV: {e}") from e
    finally:
        conn.close()
