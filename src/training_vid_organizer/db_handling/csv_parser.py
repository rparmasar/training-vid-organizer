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
                    program_iteration=int(row["program_iteration"]),
                    lift=str(row["lift"]),
                    weight=int(row["weight"]),
                    reps=int(row["reps"]),
                    bodyweight=float(row["bodyweight"])
                    if row.get("bodyweight")
                    else None,
                    top_set=(row.get("top_set", "").lower() == "true")
                    if row.get("top_set")
                    else False,
                    warm_up_set=(row.get("warm_up_set", "").lower() == "true")
                    if row.get("warm_up_set")
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
