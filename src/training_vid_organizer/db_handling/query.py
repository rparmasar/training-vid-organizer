"""Query module for fetching lift data from SQLite."""

import sqlite3
from dataclasses import fields
from typing import Any

from .db import LiftEntry


def fetch_lifts(
    db_path: str,
    filters: dict[str, Any],
    limit: int | None = 100,
) -> list[LiftEntry]:
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

        # Map raw tuples to LiftEntry instances
        entries = []
        for row in rows:
            entry_dict = dict(zip(columns, row))

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

            entries.append(LiftEntry(**entry_dict))

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
      - min_date / max_date: prefix matching for ranges ('2025-03' → March 2025)
      - top_set, warm_up_set: boolean flags (1/0 in SQLite)
      - reps_in_reserve: numeric match

    Returns:
        Tuple of (SQL string with placeholders, list of parameters)
    """
    # fetch cols from `LiftEntry`
    all_cols = [field.name for field in fields(LiftEntry)]

    base = f"SELECT {', '.join(all_cols)} FROM lifts"

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

    return sql, params
