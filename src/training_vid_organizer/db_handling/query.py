"""Query module for fetching lift data from SQLite."""

import csv
import sqlite3
from dataclasses import fields
from pathlib import Path
from typing import Any

from training_vid_organizer.logging_config import logger as tv_logger

from .db import LiftEntry, LiftResult


def fetch_lifts(
    db_path: Path,
    filters: dict[str, Any],
    limit: int | None = 100,
) -> list[LiftResult]:
    """Execute a parameterized query and return LiftEntry objects.

    Args:
        db_path: Path to SQLite database
        filters: Dict of filter keys → values (see _build_query for supported keys)
        limit: Maximum number of rows to fetch (default 100, None = no limit)

    Returns:
        List of LiftEntry objects. Empty list if no matches found.
    """
    query_sql, params = _build_query(filters)

    # Apply LIMIT if specified
    if limit is not None:
        query_sql += f" LIMIT {int(limit)}"

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query_sql, params)

        rows = cursor.fetchall()

        # Handle edge case where description is None (no columns returned)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        if not rows:
            return []

        tv_logger.debug(f"fetched {len(rows)} lift(s) with filters={filters}")

        # Map raw tuples to LiftResult instances
        entries = []
        for row in rows:
            entry_dict = dict(zip(columns, row))

            # Keep both 'id' and 'entry_id' fields for compatibility
            if "id" in entry_dict:
                entry_dict["entry_id"] = int(entry_dict.get("id"))  # Preserve original id value

            # Convert boolean flags - SQLite returns integers (1/0) or booleans
            for key in ["top_set", "warm_up_set"]:
                if isinstance(entry_dict[key], int):
                    entry_dict[key] = bool(entry_dict[key])

            # Convert numeric strings back to numbers where needed
            if isinstance(entry_dict.get("bodyweight"), str):
                try:
                    entry_dict["bodyweight"] = float(entry_dict["bodyweight"])
                except (ValueError, TypeError):
                    pass  # Keep as string if conversion fails

            # Ensure integer fields are ints (SQLite returns floats for REAL type)
            int_fields = ["weight", "reps"]
            for field in int_fields:
                if (
                    isinstance(entry_dict.get(field), float)
                    and entry_dict[field].is_integer()
                ):
                    entry_dict[field] = int(entry_dict[field])

            # Handle filename field - ensure it's a Path or None
            if "filename" in entry_dict and isinstance(entry_dict["filename"], str):
                entry_dict["filename"] = Path(entry_dict["filename"])

            # Convert stored virtual columns from DB values
            if "estimated_1rm" in entry_dict and "total_set_volume" in entry_dict:
                entry_dict["estimated_1rm"] = (
                    float(entry_dict["estimated_1rm"])
                    if entry_dict["estimated_1rm"]
                    else None
                )
                entry_dict["total_set_volume"] = float(entry_dict["total_set_volume"])

            # Compute type_label from flags (not stored in DB)
            labels = []
            if entry_dict.get("top_set"):
                labels.append("top")
            if entry_dict.get("warm_up_set"):
                labels.append("warm-up")

            # Create LiftResult without 'id' and type_label ('id' is not a field, use entry_id)
            filtered_dict = {k: v for k, v in entry_dict.items() if k not in ("id", "type_label")}
            try:
                result = LiftResult(**filtered_dict)
                entries.append(result)
                tv_logger.debug(f"Created LiftResult: {result}")
            except Exception as e:
                tv_logger.error(f"Failed to create LiftResult from entry_dict={entry_dict}: {e}")

        return entries

    finally:
        conn.close()


def _build_query(filters: dict[str, Any]) -> tuple[str, list[Any]]:
    """Construct parameterized SQL query with WHERE clauses.

    Supported filter keys:
      - date: exact + partial match match (e.g., '2025-03-15')
      - lift: exact match
      - program: exact match
      - program_iteration: integer match
      - weight: numeric match
      - bodyweight: numeric match
      - top_set, warm_up_set: boolean flags (1/0 in SQLite)
      - reps_in_reserve: numeric match

    Returns:
        Tuple of (SQL string with placeholders, list of parameters)
    """
    # fetch cols from `LiftEntry`
    all_cols = [field.name for field in fields(LiftEntry)]

    base = f"SELECT id, {', '.join(all_cols)} FROM lifts"

    where_clauses: list[str] = []
    params: list[Any] = []

    if "date" in filters:
        date_val = filters["date"]

        # check if full date (YYYY-MM-DD)
        if date_val.count("-") == 2:
            # exact match for full dates
            where_clauses.append("date = ?")
            params.append(date_val)
        # or partial (YYYY-MM or YYYY)
        else:
            where_clauses.append("date LIKE ?")
            # sqlite3-specific syntax
            params.append(f"{date_val}%")

    if "lift" in filters:
        where_clauses.append("lift = ?")
        params.append(filters["lift"])

    if "program" in filters:
        where_clauses.append("program = ?")
        params.append(filters["program"])

    if "program_iteration" in filters:
        where_clauses.append("program_iteration = ?")
        params.append(int(filters["program_iteration"]))

    if "weight" in filters:
        where_clauses.append("weight = ?")
        params.append(float(filters["weight"]))

    if "bodyweight" in filters:
        where_clauses.append("bodyweight = ?")
        params.append(float(filters["bodyweight"]))

    # Boolean flags - SQLite returns integers, handle both True/False and 1/0
    for key in ["top_set", "warm_up_set"]:
        if key in filters:
            val = 1 if bool(filters[key]) else 0
            where_clauses.append(f"{key} = ?")
            params.append(val)

    if "reps_in_reserve" in filters:
        where_clauses.append("reps_in_reserve = ?")
        params.append(int(filters["reps_in_reserve"]))

    # Assemble final query
    if where_clauses:
        sql = f"{base} WHERE {' AND '.join(where_clauses)}"
    else:
        sql = base

    # always order by date desc
    final_sql = f"{sql} ORDER BY date DESC"

    tv_logger.debug(f"_build_query generated: {sql}, params={params}")
    return final_sql, params


def analyze_lifts(
    db_path: Path,
    metric: str | None = None,
    lift: str | None = None,
    iteration: str | None = None,
) -> list[tuple[int, str, float | None, float | None]]:
    """Run program iteration comparison analysis.

    Returns list of (program_iteration, lift_name, avg_metric_value, avg_bodyweight).

    If no metric is specified, returns both estimated_1rm and total_set_volume.

    Uses case-insensitive LIKE prefix matching for `iteration` filter (e.g. `"iteration%"`) and exact matching for `lift`.
    """

    # Build WHERE clause dynamically based on provided filters
    where_parts: list[str] = []
    params: list[Any] = []

    # Add lift and iteration filters if provided (exact match for both)
    if lift is not None:
        where_parts.append("lift = ?")
        params.append(lift)
    if iteration is not None:
        iteration_val = f"{iteration}%"
        where_parts.append("program_iteration LIKE ?")
        params.append(iteration_val)

    # Build base query with NOT NULL filter for both metrics when no metric specified
    if metric is None and not where_parts:
        query = """
            SELECT
                program_iteration,
                lift,
                AVG(CASE WHEN top_set = TRUE THEN estimated_1rm END) as avg_estimated_1rm,
                AVG(total_set_volume) as avg_total_set_volume,
                AVG(bodyweight) as avg_bodyweight
            FROM lifts
        """

    elif metric is None:
        # Has filters but no metric specified - combine lift/iteration with metric filter
        query = f"""
            SELECT
                program_iteration,
                lift,
                AVG(CASE WHEN top_set = TRUE THEN estimated_1rm ELSE NULL END) as avg_estimated_1rm,
                AVG(total_set_volume) as avg_total_set_volume,
                AVG(bodyweight) as avg_bodyweight
            FROM lifts
            WHERE ({" AND ".join(where_parts)})
              AND (estimated_1rm IS NOT NULL OR total_set_volume IS NOT NULL)
        """
    else:
        if metric == "estimated_1rm":
            col = "estimated_1rm"
            alias = "avg_estimated_1rm"
            # check 1rms for topsets only
            computation_col = f"AVG(CASE WHEN top_set = TRUE THEN {col} END) as {alias}"
        elif metric == "total_set_volume":
            col = "total_set_volume"
            alias = "avg_total_set_volume"
            computation_col = f"AVG({col}) as {alias}"
        else:
            raise ValueError(f"Unknown metric: {metric}")

        # Build base query with NOT NULL filter for selected metric
        if where_parts:
            query = f"""
                SELECT
                    program_iteration,
                    lift,
                    {computation_col},
                    AVG(bodyweight) as avg_bodyweight
                FROM lifts
                WHERE ({" AND ".join(where_parts)})
                  AND ({col} IS NOT NULL)
            """
        else:
            query = f"""
                SELECT
                    program_iteration,
                    lift,
                    {computation_col},
                    AVG(bodyweight) as avg_bodyweight
                FROM lifts
                WHERE {col} IS NOT NULL
            """

    # Add metric NOT NULL filter if not already included in base query (for when we have filters but no metric)
    if metric is None and where_parts:
        query += " AND (estimated_1rm IS NOT NULL OR total_set_volume IS NOT NULL)"

    query += " GROUP BY program_iteration, lift ORDER BY date DESC"

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)

        rows = cursor.fetchall()

        if not rows or not cursor.description:
            return []

        columns = [desc[0] for desc in cursor.description]

        results = []
        for row in rows:
            entry_dict = dict(zip(columns, row))

            # Handle both-metrics case (metric is None)
            if metric is None:
                # Both metrics mode - return both estimated_1rm and total_set_volume
                est_1rm = (
                    float(entry_dict["avg_estimated_1rm"])
                    if entry_dict["avg_estimated_1rm"]
                    else None
                )
                vol = (
                    float(entry_dict["avg_total_set_volume"])
                    if entry_dict["avg_total_set_volume"]
                    else None
                )
                results.append(
                    (
                        str(entry_dict["program_iteration"]),
                        str(entry_dict["lift"]),
                        est_1rm,
                        vol,
                        float(entry_dict["avg_bodyweight"])
                        if entry_dict["avg_bodyweight"]
                        else None,
                    )
                )
            else:
                # Single metric case - return avg_bodyweight as 4th column for consistency
                results.append(
                    (
                        str(entry_dict["program_iteration"]),
                        str(entry_dict["lift"]),
                        float(entry_dict[alias]) if entry_dict[alias] else None,
                        float(entry_dict["avg_bodyweight"])
                        if entry_dict["avg_bodyweight"]
                        else None,
                    )
                )

        return results

    finally:
        conn.close()


def export_lifts_to_csv(
    entries: list[LiftResult], output_path: Path, csv_columns: list[str] | None = None
) -> bool:
    """Write lift entries to CSV file.

    Args:
        entries: List of LiftResult objects to export.
        output_path: Destination path for the CSV file.
        csv_columns: Optional custom column order (default: standard columns including id).

    Returns:
        True on success, raises typer.Exit(code=2) on failure.
    """
    try:
        # Use provided columns or default to standard set with ID included
        if csv_columns is None:
            fieldnames = [
                "id",
                "date",
                "program",
                "program_iteration",
                "lift",
                "weight",
                "reps",
                "bodyweight",
                "type",
                "filename",
                "estimated_1rm",
                "total_set_volume",
            ]
        else:
            fieldnames = csv_columns

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for entry in entries:
                row = {
                    "id": str(entry.entry_id)
                    if entry.entry_id
                    else "",  # Use .entry_id from LiftEntry (mapped from DB 'id' column)
                    "date": str(entry.date),
                    "program": str(entry.program),
                    "program_iteration": str(entry.program_iteration),
                    "lift": str(entry.lift),
                    "weight": f"{entry.weight:.1f}",
                    "reps": int(entry.reps),
                    "bodyweight": (
                        f"{entry.bodyweight:.1f}" if entry.bodyweight else ""
                    ),
                    "type": getattr(entry, "type_label", "-"),
                    "filename": str(entry.filename) if entry.filename else "",
                    "estimated_1rm": (
                        f"{entry.estimated_1rm:.2f}" if entry.estimated_1rm else ""
                    ),
                    "total_set_volume": (
                        f"{entry.total_set_volume:.2f}"
                        if entry.total_set_volume
                        else ""
                    ),
                }
                writer.writerow(row)

        tv_logger.debug(f"exported {len(entries)} lift(s) to '{output_path}'")
        return True
    except Exception as e:
        tv_logger.error(f"CSV export failed: {e}")
