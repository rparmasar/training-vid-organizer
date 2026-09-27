"""CLI entry point using Typer."""

import json
import os
from pathlib import Path
from typing import Annotated

import typer
from typer import Argument, Option, Typer, echo

from training_vid_organizer.__init__ import __version__
from training_vid_organizer.db_handling.db import (
    LiftEntry,
    add_lift_entry,
    add_session_entry,
    init_database,
)
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
    top_set: Annotated[float | None, Option("--top_set", "-t")] = False,
    warm_up_set: Annotated[float | None, Option("--warm_up_set", "-w")] = False,
    reps_in_reserve: Annotated[
        float | None, Option("--reps_in_reserve", "-rir")
    ] = False,
    filepath: Annotated[float | None, Option("--filepath", "-f")] = False,
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
        echo(f"failed to add all {len(entries)} entries ({rows_updated}/{len(entries)})")


@list_group.command("config")
def show_config():
    """Display current DB and video directory paths."""
    db_path, video_dir = get_config_paths(default_db_path=DB_DEFAULT)

    # Check which env vars are active
    has_db_env = bool(os.getenv("TVO_DB_PATH"))
    has_video_env = bool(os.getenv("TVO_VIDEO_DIR"))

    echo(f"Typer App Directory: {CONFIG_DIR}")
    echo(f"DB Path: {db_path} {'(from TVO_DB_PATH)' if has_db_env else '(default)'}")
    if video_dir:
        echo(
            f"Video Dir: {video_dir} {'(from TVO_VIDEO_DIR)' if has_video_env else '(empty)'}"
        )


if __name__ == "__main__":
    app()
