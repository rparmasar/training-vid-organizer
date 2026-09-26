"""CLI entry point using Typer."""

from pathlib import Path
from typing import Optional, Union

from typer import Argument, Exit, Option, Typer, echo

"""CLI entry point using Typer."""


from src.db import DB
from src.models import LiftEntry
from src.training_vid_organizer.crud_commands import (
    add_lift as _add_lift,
)
from src.training_vid_organizer.crud_commands import (
    add_session as _add_session,
)
from src.training_vid_organizer.crud_commands import (
    list_videos as _list_videos,
)
from src.training_vid_organizer.crud_commands import (
    update_entry as _update_entry,
)
from training_vid_organizer.__init__ import __version__

app = Typer(
    name="training-vid-organizer",
    help="A CLI tool for organizing training videos.",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def callback(
    version: bool = Option(False, "--version", "-v"),
    verbose: bool = Option(False, "--verbose", "-V"),
):
    """Main callback for the CLI."""
    if version:
        echo(f"training-vid-organizer v{__version__}")


@app.command()
def search(
    path: str = Argument("...", help="Path to search in (default: current directory)."),
    tags: list[str] | None = Option(None, "--tags", "-t", help="Filter by tags."),
    min_duration: float | None = Option(
        None, "--min-duration", "-d", help="Minimum duration in seconds."
    ),
):
    """Search videos by path and optional criteria."""
    search_path = Path(path).expanduser().resolve()

    if not search_path.exists():
        raise Exit(1)

    echo(f"Searching in: {search_path}")
    # TODO: Implement actual search logic
    echo("Search functionality coming soon...")


@app.command()
def categorize(
    tags: list[str] = Argument(..., help="Tags to assign."),
    output_dir: str = Option(
        "videos", "--output-dir", "-o", help="Output directory for organized videos."
    ),
):
    """Categorize videos with given tags."""
    if not tags:
        raise Exit(1)

    echo(f"Categorizing videos with tags: {', '.join(tags)}")
    # TODO: Implement actual categorization logic
    echo("Categorization functionality coming soon...")


@app.command()
def metadata(
    path: str = Argument(..., help="Path to video file."),
    extract_duration: bool = Option(
        False, "--duration", "-D", help="Extract and display duration."
    ),
):
    """Extract video metadata."""
    video_path = Path(path).expanduser().resolve()

    if not video_path.exists():
        raise Exit(1)

    # TODO: Implement actual metadata extraction logic
    echo(f"Metadata for: {video_path}")
    if extract_duration:
        echo("Duration functionality coming soon...")


@app.command()
def add_lift(
    db_path: str = Option("db/training.db", "--db-path", "-d"),
    date: str = Argument(..., show_default=False),
    bodyweight: float | None = Option(None, "--bodyweight", "-w"),
    lift: str = Argument(..., show_default=False),
    weight: float = Argument(..., show_default=False),
    reps: int = Argument(..., show_default=False),
):
    """Add a single lift entry."""
    db = DB(db_path)
    db.init_schema()

    entry = LiftEntry(
        date=date,
        bodyweight=bodyweight,
        lift=lift,
        weight=weight,
        reps=reps,
    )
    result = _add_lift(db, entry)  # pure function with typed dataclass
    echo(f"Added {result} entry/entries")


@app.command()
def add_session(
    db_path: str = Option("db/training.db", "--db-path", "-d"),
    config: str = Argument(..., show_default=False),
):
    """Add multiple lift entries from a JSON session config."""
    import json

    db = DB(db_path)
    db.init_schema()

    with open(config) as f:
        data = json.load(f)  # list[LiftEntry] dicts

    entries = [LiftEntry(**d) for d in data]

    result = _add_session(db, entries)  # pure function with typed list[LiftEntry]
    echo(f"Added {result} entry/entries")


@app.command()
def list_videos(
    db_path: str = Option("db/training.db", "--db-path", "-d"),
    lift: str | None = Option(None, "--lift", "-l"),
):
    """List training videos."""
    db = DB(db_path)
    db.init_schema()

    if lift is not None:
        results = _list_videos(db, {"lift": lift})  # type: ignore[union-attr]
    else:
        results = _list_videos(db)

    print(f"\n{'ID':<5} {'Date':<12} {'Lift':<18} {'Weight':<7} {'Reps':<6}")
    for row in results:
        print(f"{row[0]:<5} {row[1]:<12} {row[3]:<18} {row[4]:<7} {row[5]:<6}")


@app.command()
def update_entry(
    db_path: str = Option("db/training.db", "--db-path", "-d"),
    entry_id: int = Argument(..., show_default=False),
    date: str | None = Option(None, "--date", "-D"),
    bodyweight: float | None = Option(None, "--bodyweight", "-w"),
    lift: str | None = Option(None, "--lift", "-l"),
    weight: float | None = Option(None, "--weight", "-W"),
    reps: int | None = Option(None, "--reps", "-R"),
):
    """Update a lift entry by ID."""
    db = DB(db_path)
    db.init_schema()

    updates = {}
    if date is not None:
        updates["date"] = date
    if bodyweight is not None:
        updates["bodyweight"] = bodyweight
    if lift is not None:
        updates["lift"] = lift
    if weight is not None:
        updates["weight"] = weight
    if reps is not None:
        updates["reps"] = reps

    result = _update_entry(db, entry_id, updates)  # pure function with patch dict
    echo(f"Updated entry {entry_id}")


if __name__ == "__main__":
    app()
