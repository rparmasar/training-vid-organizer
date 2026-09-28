"""CLI entry point using Typer."""

import json
import os
import sqlite3
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer, echo

from training_vid_organizer.__init__ import __version__
from training_vid_organizer.db_handling.db import (
    LiftEntry,
    add_lift_entry,
    add_session_entry,
    init_database,
)
from training_vid_organizer.db_handling.query import fetch_lifts
from training_vid_organizer.utils import get_config_paths

APP_NAME = "training-vid-organizer"
CONFIG_DIR = Path(typer.get_app_dir(APP_NAME))
DB_DEFAULT = CONFIG_DIR / "training.db"


app = Typer(
    name="training-vid-organizer",
    help="A CLI tool for organizing training videos.",
    add_completion=False,
)
# wire up subcommands
add_group = Typer(name="add", help="Add training data")
list_group = Typer(name="list", help="List training data")
app.add_typer(add_group)
app.add_typer(list_group)


@app.callback(invoke_without_command=True)
def callback(
    version: Annotated[bool, Option("--version", "-v")] = False,
):
    """Main callback for the CLI."""
    if version:
        echo(f"training-vid-organizer v{__version__}")


@app.command("init")
def init_db(
    db_path: Annotated[str, Option("--db-path", "-d")] = None,
):
    """initializes the database to store lift information"""
    # Use CONFIG_DIR/training.db if not overridden
    effective_db_path = db_path or str(DB_DEFAULT)

    # Create config directory if needed (for future use)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    echo(f"creating training log database in {effective_db_path=}")
    init_database(db_path=effective_db_path)

    # Persist the choice to env vars for future commands
    os.environ["TVO_DB_PATH"] = effective_db_path
    os.environ["TVO_VIDEO_DIR"] = ""  # empty string, user sets later

    echo("database created successfully!")


@add_group.command("lift")
def add_lift(
    date: Annotated[str, Option("--date")],
    program: Annotated[str, Option("--program")],
    program_iteration: Annotated[int, Option("--iteration", "-i")],
    lift: Annotated[str, Option("--lift", "-l")],
    weight: Annotated[int, Option("--weight", "-w")],
    reps: Annotated[int, Option("--reps", "-r")],
    bodyweight: Annotated[float | None, Option("--bodyweight", "-b")] = None,
    top_set: Annotated[bool, Option("--top-set", "-t")] = False,
    warm_up_set: Annotated[bool, Option("--warm-up-set", "-w")] = False,
    reps_in_reserve: Annotated[
        float | None, Option("--reps_in_reserve", "-rir")
    ] = None,
    filepath: Annotated[str | None, Option("--filepath", "-f")] = None,
    db_path: Annotated[str, Option("--db-path", "-d")] = None,
):
    """Add a single lift entry."""
    # allow per-command override
    effective_db_path = db_path or get_config_paths(default_db_path=DB_DEFAULT)[0]

    # convert args to LiftEntry
    try:
        current_lift_entry = LiftEntry(
            date,
            program,
            program_iteration,
            lift,
            weight,
            reps,
            bodyweight,
            top_set,
            warm_up_set,
            reps_in_reserve,
            filepath,
        )
    except (TypeError, ValueError) as e:
        echo(f"Error creating lift entry: {e}")
        raise typer.Exit(code=1)

    # add via function
    rows_updated = add_lift_entry(db_path=effective_db_path, entry=current_lift_entry)

    if rows_updated:
        echo(f"added {current_lift_entry} to the database!")
    else:
        echo(f"failed to add {current_lift_entry} to the database!")


@add_group.command("session")
def add_session(
    config_path: Annotated[str, Argument(help="Path to JSON configuration file")] = "",
    db_path: Annotated[str, Option("--db-path", "-d")] = None,
):
    """Add multiple lifts from a JSON configuration file."""
    # allow per-command override
    effective_db_path = db_path or get_config_paths(default_db_path=DB_DEFAULT)[0]

    # load and parse JSON
    with open(config_path) as f:
        session_data = json.load(f)

    if not isinstance(session_data, list):
        echo("Error: JSON root must be a list of lift entries")
        raise typer.Exit(code=1)

    # convert dicts to LiftEntry objects
    try:
        entries = [LiftEntry(**entry_dict) for entry_dict in session_data]
    except (TypeError, ValueError) as e:
        echo(f"Error parsing lift entries: {e}")
        raise typer.Exit(code=1)

    # add via function
    rows_updated = add_session_entry(db_path=effective_db_path, entries=entries)

    if rows_updated == len(entries):
        echo(f"added {rows_updated} entries from {config_path=} to the database!")
    else:
        echo(
            f"failed to add all {len(entries)} entries ({rows_updated}/{len(entries)})"
        )


@list_group.command("lifts")
def list_lifts(
    date: Annotated[str | None, Option("--date")] = None,
    program: Annotated[str | None, Option("--program")] = None,
    iteration: Annotated[int | None, Option("--iteration", "-i")] = None,
    lift: Annotated[str | None, Option("--lift", "-L")] = None,
    weight: Annotated[float | None, Option("--weight", "-w")] = None,
    bodyweight: Annotated[float | None, Option("--bodyweight", "-b")] = None,
    top_set: Annotated[bool | None, Option("--top-set", "-t")] = None,
    warm_up_set: Annotated[bool | None, Option("--warm-up-set", "-w")] = None,
    reps_in_reserve: Annotated[
        float | None, Option("--reps_in_reserve", "-rir")
    ] = None,
    db_path: Annotated[str | None, Option("--db-path", "-d")] = None,
    limit: Annotated[int | None, Option("--limit", "-l")] = 100,
):
    """List lifts from the database with optional filters."""
    # Build filters dict from CLI arguments
    filters: dict[str, Any] = {}

    if date is not None:
        filters["date"] = str(date)
    if program is not None:
        filters["program"] = str(program)
    if iteration is not None:
        filters["program_iteration"] = int(iteration)
    if lift is not None:
        filters["lift"] = str(lift)
    if weight is not None:
        filters["weight"] = float(weight)
    if bodyweight is not None:
        filters["bodyweight"] = float(bodyweight)
    if top_set is not None:
        filters["top_set"] = bool(top_set)
    if warm_up_set is not None:
        filters["warm_up_set"] = bool(warm_up_set)
    if reps_in_reserve is not None:
        filters["reps_in_reserve"] = float(reps_in_reserve)

    # Use provided db_path or fall back to default config path
    effective_db_path = db_path or get_config_paths(default_db_path=DB_DEFAULT)[0]

    try:
        entries = fetch_lifts(
            db_path=effective_db_path, filters=filters or {}, limit=limit
        )
    except sqlite3.Error as e:
        echo(f"Database error: {e}")
        raise typer.Exit(code=2)

    if not entries:
        echo("No lifts found matching the specified criteria.")
        return

    console = Console()
    table = Table(
        box=None,
        show_header=True,
        header_style="dim",
        expand=False,
    )

    # Column definitions with auto-width
    table.add_column("date", style="dim", width=12)
    table.add_column("program", style="dim", width=15)
    table.add_column("iteration", justify="right", width=8)
    table.add_column("lift", style="dim", width=15)
    table.add_column("weight (kg)", justify="right", width=9)
    table.add_column("reps", justify="right", width=6)
    table.add_column("bw (kg)", justify="right", width=10)
    table.add_column("type", style="dim", width=7)

    for entry in entries:
        type_label = (
            "top" if entry.top_set else ("warm-up" if entry.warm_up_set else "-")
        )
        table.add_row(
            str(entry.date),
            str(entry.program),
            f"{int(entry.program_iteration)}",
            str(entry.lift),
            f"{entry.weight:.1f}",
            f"{int(entry.reps)}",
            f"{entry.bodyweight:.1f}" if entry.bodyweight else "-",
            type_label,
        )

    console.print(table)


if __name__ == "__main__":
    app()
