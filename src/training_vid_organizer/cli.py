"""CLI entry point using Typer."""

from typing import Annotated

from typer import Argument, Exit, Option, Typer, echo

from training_vid_organizer.__init__ import __version__
from training_vid_organizer.db_handling.db import init_database

app = Typer(
    name="training-vid-organizer",
    help="A CLI tool for organizing training videos.",
    add_completion=False,
)
add_group = Typer(name="add", help="Add training data")


@app.callback(invoke_without_command=True)
def callback(
    version: Annotated[bool, Option("--version", "-v")] = False,
):
    """Main callback for the CLI."""
    if version:
        echo(f"training-vid-organizer v{__version__}")


@app.command("init")
def init_db(
    db_path: Annotated[str, Option("--db-path", "-d")] = "db/training.db",
):
    """initializes the database to store lift information"""
    echo(f"creating training log database in {db_path=}")

    init_database(db_path=db_path)

    echo("database created successfully!")


@add_group.command("lift")
def add_lift(
    date: Annotated[str, Option("--date")] = "",
    program: Annotated[str, Option("--program")] = "",
    program_iteration: Annotated[int, Option("--iteration", "-i")] = 1,
    lift_name: Annotated[str, Option("--lift", "-l")] = "Bench Press",
    weight: Annotated[int, Option("--weight", "-w")] = 0,
    reps: Annotated[int, Option("--reps", "-r")] = 0,
    bodyweight: Annotated[float | None, Option("--bodyweight", "-b")] = None,
):
    """Add a single lift entry."""
    echo(f"Adding lift: {lift_name} - {weight} x {reps}")


@add_group.command("session")
def add_session(
    config_path: Annotated[str, Argument(help="Path to JSON configuration file")] = "",
):
    """Add multiple lifts from a JSON configuration file."""
    echo(f"Loading session data from {config_path=}")


app.add_typer(add_group)


if __name__ == "__main__":
    app()
