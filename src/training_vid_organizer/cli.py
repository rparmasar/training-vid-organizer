"""CLI entry point using Typer."""

import json
import logging
import os
import sqlite3
from dataclasses import fields
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer, confirm, echo

from training_vid_organizer.__init__ import __version__
from training_vid_organizer.db_handling.db import (
    LiftEntry,
    add_lift_entry,
    add_session_entry,
    init_database,
)
from training_vid_organizer.db_handling.query import fetch_lifts
from training_vid_organizer.db_handling.update import (
    delete_lift_entry,
    update_lift_entry,
)
from training_vid_organizer.logging_config import logger as tv_logger
from training_vid_organizer.utils import (
    get_config_paths,
    get_video_base_dir,
    open_video_file,
)

# Set log level from environment variable if set
log_level = os.getenv("TVO_LOG_LEVEL", "INFO").upper()
if log_level in ("DEBUG", "INFO"):
    tv_logger.setLevel(getattr(logging, log_level))


APP_NAME = "training-vid-organizer"
CONFIG_DIR = Path(typer.get_app_dir(APP_NAME))
DB_DEFAULT = CONFIG_DIR / "training.db"

console = Console()


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
    version: Annotated[
        bool, Option("--version", "-v", help="show version number")
    ] = False,
):
    """main callback for the cli"""
    if version:
        echo(f"training-vid-organizer v{__version__}")


@app.command("init")
def init_db(
    db_path: Annotated[
        str, Option("--db-path", "-d", help="path to sqlite database file")
    ] = None,
    reset: Annotated[
        bool, Option("--reset", help="delete existing db and recreate")
    ] = False,
):
    """initializes the database to store lift information"""
    # Use CONFIG_DIR/training.db if not overridden
    effective_db_path = db_path or str(DB_DEFAULT)

    # Reset mode: delete existing DB if present and confirmed
    if reset and Path(effective_db_path).exists():
        if not confirm(f"Delete '{effective_db_path}' and recreate?"):
            echo("[yellow]Aborted.[/yellow]")
            raise typer.Exit(code=1)
        Path(effective_db_path).unlink()

    # Create config directory if needed (for future use)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    tv_logger.info(f"creating training log database in {effective_db_path=}")
    init_database(db_path=effective_db_path)

    # Persist the choice to env vars for future commands
    os.environ["TVO_DB_PATH"] = effective_db_path
    os.environ["TVO_VIDEO_DIR"] = ""  # empty string, user sets later

    tv_logger.info("database created successfully!")


@add_group.command("lift")
def add_lift(
    date: Annotated[str, Option("--date", help="training date (YYYY-MM-DD)")],
    program: Annotated[
        str, Option("--program", help="name of the training program")
    ] = None,
    program_iteration: Annotated[
        int, Option("--iteration", "-i", help="current iteration number")
    ] = 1,
    lift: Annotated[
        str, Option("--lift", "-l", help="exercise name (e.g. squat)")
    ] = None,
    weight: Annotated[int, Option("--weight", "-w", help="weight lifted in lbs")] = 0,
    reps: Annotated[int, Option("--reps", "-r", help="number of repetitions")] = 10,
    bodyweight: Annotated[
        float | None, Option("--bodyweight", "-b", help="total body weight in lbs")
    ] = None,
    top_set: Annotated[
        bool, Option("--top-set", "-t", help="mark as a top set")
    ] = False,
    warm_up_set: Annotated[
        bool, Option("--warm-up-set", "-w", help="mark as a warmup set")
    ] = False,
    reps_in_reserve: Annotated[
        float | None, Option("--reps_in_reserve", "-rir", help="RIR value (e.g. 1.5)")
    ] = None,
    filepath: Annotated[
        str | None, Option("--filepath", "-f", help="path to video file")
    ] = None,
    db_path: Annotated[
        str, Option("--db-path", "-d", help="override database path")
    ] = None,
):
    """add a single lift entry"""
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
        tv_logger.error(f"Error creating lift entry: {e}")
        raise typer.Exit(code=1)

    # add via function
    rows_updated = add_lift_entry(db_path=effective_db_path, entry=current_lift_entry)

    if rows_updated:
        console.print(f"[green]✓[/green] added {current_lift_entry} to the database!")
    else:
        console.print("[red]✗[/red] failed to add lift to the database!")


@add_group.command("session")
def add_session(
    config_path: Annotated[str, Argument(help="path to json configuration file")] = "",
    db_path: Annotated[
        str, Option("--db-path", "-d", help="override database path")
    ] = None,
):
    """add multiple lifts from a json configuration file"""
    # allow per-command override
    effective_db_path = db_path or get_config_paths(default_db_path=DB_DEFAULT)[0]

    # load and parse JSON
    tv_logger.debug(f"loading session data from {config_path}")
    with open(config_path) as f:
        session_data = json.load(f)

    if not isinstance(session_data, list):
        tv_logger.error("Error: JSON root must be a list of lift entries")
        raise typer.Exit(code=1)

    # convert dicts to LiftEntry objects
    try:
        entries = [LiftEntry(**entry_dict) for entry_dict in session_data]
    except (TypeError, ValueError) as e:
        tv_logger.error(f"Error parsing lift entries: {e}")
        raise typer.Exit(code=1)

    # add via function
    rows_updated = add_session_entry(db_path=effective_db_path, entries=entries)

    if rows_updated == len(entries):
        console.print(
            f"[green]✓[/green] added {rows_updated} entries from {config_path}"
        )
    else:
        console.print(
            f"[red]✗[/red] failed to add all {len(entries)} entries ({rows_updated}/{len(entries)})"
        )


@list_group.command("lifts")
def list_lifts(
    date: Annotated[
        str | None, Option("--date", help="filter by training date")
    ] = None,
    program: Annotated[
        str | None, Option("--program", help="filter by program name")
    ] = None,
    iteration: Annotated[
        int | None, Option("--iteration", "-i", help="filter by iteration number")
    ] = None,
    lift: Annotated[
        str | None, Option("--lift", "-L", help="filter by exercise name")
    ] = None,
    weight: Annotated[
        float | None, Option("--weight", "-w", help="filter by weight in lbs")
    ] = None,
    bodyweight: Annotated[
        float | None, Option("--bodyweight", "-b", help="filter by bodyweight in lbs")
    ] = None,
    top_set: Annotated[
        bool | None, Option("--top-set", "-t", help="filter for top sets only")
    ] = None,
    warm_up_set: Annotated[
        bool | None, Option("--warm-up-set", "-w", help="filter for warmup sets only")
    ] = None,
    reps_in_reserve: Annotated[
        float | None, Option("--reps_in_reserve", "-rir", help="filter by RIR value")
    ] = None,
    db_path: Annotated[
        str | None, Option("--db-path", "-d", help="override database path")
    ] = None,
    limit: Annotated[
        int | None, Option("--limit", "-l", help="maximum number of results to show")
    ] = 100,
):
    """list lifts from the database with optional filters"""
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

    tv_logger.debug(f"fetch_lifts called with filters={filters}, limit={limit}")

    try:
        entries = fetch_lifts(
            db_path=effective_db_path, filters=filters or {}, limit=limit
        )
    except sqlite3.Error as e:
        tv_logger.error(f"Database error: {e}")
        raise typer.Exit(code=2)

    if not entries:
        console.print("[dim]No lifts found matching the specified criteria.[/dim]")
        return

    table = Table(
        box=None,
        show_header=True,
        header_style="dim",
        expand=False,
    )

    # Define table columns explicitly (matching row data order)
    col_defs = [
        ("date", "dim", None, None),
        ("program", "dim", None, None),
        ("program_iteration", "dim", None, None),
        ("lift", "dim", None, None),
        ("weight", None, "right", None),
        ("reps", None, "right", None),
        ("bodyweight", None, "right", None),
        ("type_label", "dim", None, None),
        ("filename", None, None, None),
    ]

    for name, style, justify, width in col_defs:
        label = {
            "date": "date",
            "program": "program",
            "program_iteration": "iteration",
            "lift": "lift",
            "weight": "weight (lbs)",
            "reps": "reps",
            "bodyweight": "bw (lbs)",
            "type_label": "type",
            "filename": "file",
        }[name]
        table.add_column(label, style=style, justify=justify, width=width)

    for entry in entries:
        type_labels = []
        if entry.top_set:
            type_labels.append("top")
        if entry.warm_up_set:
            type_labels.append("warm-up")
        type_label = ", ".join(type_labels) if type_labels else "-"

        filepath_str = str(entry.filename) if entry.filename else "-"

        table.add_row(
            str(entry.date),
            str(entry.program),
            f"{int(entry.program_iteration)}",
            str(entry.lift),
            f"{entry.weight:.1f}",
            f"{int(entry.reps)}",
            f"{entry.bodyweight:.1f}" if entry.bodyweight else "-",
            type_label,
            filepath_str,
        )

    # Add ID column header after the table is built
    table.add_column("id", style="dim", justify="right")

    # Rebuild rows with ID column included
    table.rows.clear()

    for entry in entries:
        type_labels = []
        if entry.top_set:
            type_labels.append("top")
        if entry.warm_up_set:
            type_labels.append("warm-up")
        type_label = ", ".join(type_labels) if type_labels else "-"

        filepath_str = str(entry.filename) if entry.filename else "-"

        table.add_row(
            str(entry.date),
            str(entry.program),
            f"{int(entry.program_iteration)}",
            str(entry.lift),
            f"{entry.weight:.1f}",
            f"{int(entry.reps)}",
            f"{entry.bodyweight:.1f}" if entry.bodyweight else "-",
            type_label,
            filepath_str,
            str(entry.entry_id) if entry.entry_id else "-",
        )

    console.print(table)
    tv_logger.info(f"listed {len(entries)} lift(s)")


@app.command("update")
def update(
    entry_id: Annotated[int, Argument(help="row id to update")] = 0,
    date: Annotated[str | None, Option("--date", help="new training date")] = None,
    program: Annotated[str | None, Option("--program", help="new program name")] = None,
    program_iteration: Annotated[
        int | None, Option("--iteration", "-i", help="new iteration number")
    ] = None,
    lift: Annotated[
        str | None, Option("--lift", "-l", help="new exercise name")
    ] = None,
    weight: Annotated[
        float | None, Option("--weight", "-w", help="new weight in lbs")
    ] = None,
    reps: Annotated[
        int | None, Option("--reps", "-r", help="new repetition count")
    ] = None,
    bodyweight: Annotated[
        float | None, Option("--bodyweight", "-b", help="new bodyweight in lbs")
    ] = None,
    top_set: Annotated[
        bool | None, Option("--top-set", "-t", help="mark as top set")
    ] = None,
    warm_up_set: Annotated[
        bool | None, Option("--warm-up-set", "-w", help="mark as warmup set")
    ] = None,
    reps_in_reserve: Annotated[
        float | None, Option("--reps_in_reserve", "-rir", help="new RIR value")
    ] = None,
    filepath: Annotated[
        str | None, Option("--filepath", "-f", help="new video file path")
    ] = None,
    db_path: Annotated[
        str | None, Option("--db-path", "-d", help="override database path")
    ] = None,
):
    """update a lift entry by id with the provided fields"""
    # allow per-command override
    effective_db_path = db_path or get_config_paths(default_db_path=DB_DEFAULT)[0]

    # Collect update kwargs (exclude None values to avoid unintended NULLs)
    update_kwargs: dict[str, Any] = {}
    if date is not None:
        update_kwargs["date"] = str(date)
    if program is not None:
        update_kwargs["program"] = str(program)
    if program_iteration is not None:
        update_kwargs["program_iteration"] = int(program_iteration)
    if lift is not None:
        update_kwargs["lift"] = str(lift)
    if weight is not None:
        update_kwargs["weight"] = float(weight)
    if reps is not None:
        update_kwargs["reps"] = int(reps)
    if bodyweight is not None:
        update_kwargs["bodyweight"] = float(bodyweight)
    if top_set is not None:
        update_kwargs["top_set"] = bool(top_set)
    if warm_up_set is not None:
        update_kwargs["warm_up_set"] = bool(warm_up_set)
    if reps_in_reserve is not None:
        update_kwargs["reps_in_reserve"] = float(reps_in_reserve)
    if filepath is not None:
        update_kwargs["filename"] = str(filepath)

    tv_logger.debug(
        f"update_lift_entry called with entry_id={entry_id}, kwargs={update_kwargs}"
    )

    try:
        rows_updated = update_lift_entry(
            db_path=effective_db_path, entry_id=entry_id, **update_kwargs
        )
    except ValueError as e:
        tv_logger.error(f"Database error: {e}")
        raise typer.Exit(code=2)

    if rows_updated:
        fields_str = ", ".join(f"{k}={v}" for k, v in update_kwargs.items())
        console.print(f"[green]✓[/green] updated lift #{entry_id}: {fields_str}")
    else:
        console.print(
            f"[red]✗[/red] no row found with ID {entry_id} or no valid fields provided"
        )


@app.command("delete")
def delete(
    entry_id: Annotated[int, Argument(help="row id to delete")] = 0,
    force: Annotated[bool, Option("--force", help="skip confirmation prompt")] = False,
    db_path: Annotated[
        str | None, Option("--db-path", "-d", help="override database path")
    ] = None,
):
    """delete a lift entry by id"""
    # allow per-command override
    effective_db_path = db_path or get_config_paths(default_db_path=DB_DEFAULT)[0]

    if not force and not confirm(
        f"Delete lift entry #{entry_id} from '{effective_db_path}'?"
    ):
        echo("[yellow]Aborted.[/yellow]")
        raise typer.Exit(code=1)

    tv_logger.debug(f"delete_lift_entry called with entry_id={entry_id}")

    try:
        deleted = delete_lift_entry(db_path=effective_db_path, entry_id=entry_id)
    except ValueError as e:
        tv_logger.error(f"Database error: {e}")
        raise typer.Exit(code=2)

    if deleted:
        console.print(f"[green]✓[/green] deleted lift #{entry_id} from the database")
    else:
        console.print(
            f"[red]✗[/red] no row found with ID {entry_id} or deletion failed"
        )


@app.command("open")
def open_files(
    date: Annotated[
        str | None, Option("--date", help="filter by training date")
    ] = None,
    program: Annotated[
        str | None, Option("--program", help="filter by program name")
    ] = None,
    iteration: Annotated[
        int | None, Option("--iteration", "-i", help="filter by iteration number")
    ] = None,
    lift: Annotated[
        str | None, Option("--lift", "-L", help="filter by exercise name")
    ] = None,
    weight: Annotated[
        float | None, Option("--weight", "-w", help="filter by weight in lbs")
    ] = None,
    top_set: Annotated[
        bool | None, Option("--top-set", "-t", help="filter for top sets only")
    ] = None,
    warm_up_set: Annotated[
        bool | None, Option("--warm-up-set", "-w", help="filter for warmup sets only")
    ] = None,
    limit: Annotated[
        int, Option("--limit", "-l", help="maximum number of results to show")
    ] = 50,
    db_path: Annotated[
        str | None, Option("--db-path", "-d", help="override database path")
    ] = None,
):
    """open video files for filtered lifts"""

    # Build filters (same pattern as list_lifts)
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
    if top_set is not None:
        filters["top_set"] = bool(top_set)
    if warm_up_set is not None:
        filters["warm_up_set"] = bool(warm_up_set)

    # Fetch data
    effective_db_path = db_path or get_config_paths(default_db_path=DB_DEFAULT)[0]
    entries = fetch_lifts(db_path=effective_db_path, filters=filters, limit=limit)

    if not entries:
        console.print("[dim]No lifts found matching the specified criteria.[/dim]")
        return

    # Show results table (same style as list_lifts)
    table = Table(box=None, show_header=True, header_style="dim", expand=False)
    col_defs = [
        ("date", "dim"),
        ("program", "dim"),
        ("program_iteration", "dim"),
        ("lift", "dim"),
        ("weight", None, "right"),
        ("reps", None, "right"),
        ("type_label", "dim"),
        ("filename", None),
    ]

    for name, style, justify in col_defs:
        label = {
            "date": "date",
            "program": "program",
            "program_iteration": "iteration",
            "lift": "lift",
            "weight": "weight (lbs)",
            "reps": "reps",
            "type_label": "type",
            "filename": "file",
        }[name]
        table.add_column(label, style=style, justify=justify)

    for entry in entries:
        type_labels = (
            ["top"]
            if entry.top_set
            else [] + (["warm-up"] if entry.warm_up_set else [])
        )
        type_label = ", ".join(type_labels) if type_labels else "-"

        table.add_row(
            str(entry.date),
            str(entry.program),
            f"{int(entry.program_iteration)}",
            str(entry.lift),
            f"{entry.weight:.1f}",
            f"{int(entry.reps)}",
            type_label,
            str(entry.filename) if entry.filename else "-",
        )

    console.print(table)

    # Open files (deduplicate with set)
    base_dir = get_video_base_dir()
    unique_files = sorted(set(str(e.filename) for e in entries if e.filename))

    for filepath in unique_files:
        open_video_file(filepath, base_dir)


if __name__ == "__main__":
    app()
