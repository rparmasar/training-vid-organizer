"""CSV parser for training log imports."""

import csv
from pathlib import Path

from training_vid_organizer.db_handling.db import LiftEntry

REQUIRED_COLUMNS = {"date", "program", "program_iteration", "lift", "weight", "reps"}
OPTIONAL_COLUMNS = {
    "bodyweight",
    "top_set",
    "warm_up_set",
    "reps_in_reserve",
    "filename",
}

# For bulk updates: ID is required, unknown columns should fail fast
UPDATE_REQUIRED_COLUMNS = {"id"} | REQUIRED_COLUMNS


def parse_csv_to_lift_entries(csv_path: Path) -> list[LiftEntry]:
    """Parse CSV file into LiftEntry objects.

    Auto-detects format from extension, validates required columns, fails fast on bad data.
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate header
        if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames or [])):
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            raise ValueError(f"CSV missing required columns: {', '.join(missing)}")

        entries: list[LiftEntry] = []
        for row_num, row in enumerate(
            reader, start=2
        ):  # start=2 because header is row 1
            try:
                entry = LiftEntry(
                    date=str(row["date"]),
                    program=str(row["program"]),
                    program_iteration=str(row["program_iteration"]),
                    lift=str(row["lift"]),
                    weight=float(row["weight"]),  # Allow float for weight
                    reps=int(row["reps"]),  # Strict int for reps
                    bodyweight=float(row["bodyweight"])
                    if row.get("bodyweight")
                    else None,
                    top_set=(row.get("top_set", "").lower() == "true")
                    if row.get("top_set")
                    and row.get("top_set", "").strip().lower() in ("true", "1", "yes")
                    else False,
                    warm_up_set=(row.get("warm_up_set", "").lower() == "true")
                    if row.get("warm_up_set")
                    and row.get("warm_up_set", "").strip().lower()
                    in ("true", "1", "yes")
                    else False,
                    reps_in_reserve=int(row["reps_in_reserve"])
                    if row.get("reps_in_reserve")
                    else None,
                    filename=str(Path(row["filename"]))
                    if row.get("filename") and str(row["filename"]).strip()
                    else None,
                )
                entries.append(entry)
            except (ValueError, KeyError) as e:
                raise ValueError(f"Row {row_num}: invalid data - {e}") from e

        return entries


def parse_csv_for_update(csv_path: Path) -> list[LiftEntry]:
    """Parse CSV file for bulk updates.

    Requires 'id' column, validates against UPDATE_REQUIRED_COLUMNS, fails fast on unknown columns.

    Args:
        csv_path: Path to CSV file

    Returns:
        List of LiftEntry objects with IDs

    Raises:
        ValueError: If missing required columns or contains unknown columns
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate header - must have id plus all standard required columns
        fieldnames = set(reader.fieldnames or [])
        if not UPDATE_REQUIRED_COLUMNS.issubset(fieldnames):
            missing = UPDATE_REQUIRED_COLUMNS - fieldnames
            raise ValueError(
                f"CSV for update missing required columns: {', '.join(missing)}"
            )

        # Fail fast on unknown columns (strict mode)
        known_columns = UPDATE_REQUIRED_COLUMNS | OPTIONAL_COLUMNS
        unknown_columns = fieldnames - known_columns
        if unknown_columns:
            raise ValueError(
                f"CSV contains unknown columns: {', '.join(sorted(unknown_columns))}"
            )

        entries: list[LiftEntry] = []
        for row_num, row in enumerate(reader, start=2):
            try:
                entry = LiftEntry(
                    id=int(row["id"]),  # ID is required and must be int
                    date=str(row["date"]),
                    program=str(row["program"]),
                    program_iteration=str(row["program_iteration"]),
                    lift=str(row["lift"]),
                    weight=float(row["weight"]),
                    reps=int(row["reps"]),
                    bodyweight=float(row["bodyweight"])
                    if row.get("bodyweight") and row["bodyweight"].strip()
                    else None,
                    top_set=(row.get("top_set", "").lower() == "true")
                    if row.get("top_set")
                    and row.get("top_set", "").strip().lower() in ("true", "1", "yes")
                    else False,
                    warm_up_set=(row.get("warm_up_set", "").lower() == "true")
                    if row.get("warm_up_set")
                    and row.get("warm_up_set", "").strip().lower()
                    in ("true", "1", "yes")
                    else False,
                    reps_in_reserve=int(row["reps_in_reserve"])
                    if row.get("reps_in_reserve") and row["reps_in_reserve"].strip()
                    else None,
                    filename=str(Path(row["filename"]))
                    if row.get("filename") and str(row["filename"]).strip()
                    else None,
                )
                entries.append(entry)
            except (ValueError, KeyError) as e:
                raise ValueError(f"Row {row_num}: invalid data - {e}") from e

        return entries
