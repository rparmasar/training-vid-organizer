"""CLI entry point using Typer."""

from typing import Annotated

from typer import Argument, Exit, Option, Typer, echo

# from src.models import LiftEntry
# from src.training_vid_organizer.crud_commands import (
#     add_lift as _add_lift,
# )
# from src.training_vid_organizer.crud_commands import (
#     add_session as _add_session,
# )
# from src.training_vid_organizer.crud_commands import (
#     list_videos as _list_videos,
# )
# from src.training_vid_organizer.crud_commands import (
#     update_entry as _update_entry,
# )
from training_vid_organizer.__init__ import __version__
from training_vid_organizer.db_handling.db import init_database

# from training_vid_organizer.db_handling.db import DB

app = Typer(
    name="training-vid-organizer",
    help="A CLI tool for organizing training videos.",
    add_completion=False,
)


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


if __name__ == "__main__":
    app()
