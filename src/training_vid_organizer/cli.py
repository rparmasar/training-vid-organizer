"""CLI entry point using Typer."""

import sys
from pathlib import Path

from typer import Typer, echo, Argument, Option

from training_vid_organizer.__init__ import __version__

app = Typer(
    name="training-vid-organizer",
    help="A CLI tool for organizing training videos.",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def callback(
    version: bool = Option(False, "--version", "-v", help="Show version and exit."),
    verbose: bool = Option(False, "--verbose", "-V", help="Enable verbose output."),
):
    """Main callback for the CLI."""
    if version:
        echo(f"training-vid-organizer v{__version__}")


@app.command()
def search(
    path: str = Argument("...", help="Path to search in (default: current directory)."),
    tags: list[str] | None = Option(None, "--tags", "-t", help="Filter by tags."),
    min_duration: float | None = Option(None, "--min-duration", "-d", help="Minimum duration in seconds."),
):
    """Search videos by path and optional criteria."""
    search_path = Path(path).expanduser().resolve()

    if not search_path.exists():
        raise typer.Exit(1)

    echo(f"Searching in: {search_path}")
    # TODO: Implement actual search logic
    echo("Search functionality coming soon...")


@app.command()
def categorize(
    tags: list[str] = Argument(..., help="Tags to assign."),
    output_dir: str = Option("videos", "--output-dir", "-o", help="Output directory for organized videos."),
):
    """Categorize videos with given tags."""
    if not tags:
        raise typer.Exit(1)

    output_path = Path(output_dir).expanduser().resolve()
    echo(f"Categorizing videos with tags: {', '.join(tags)}")
    # TODO: Implement actual categorization logic
    echo("Categorization functionality coming soon...")


@app.command()
def metadata(
    path: str = Argument(..., help="Path to video file."),
    extract_duration: bool = Option(False, "--duration", "-D", help="Extract and display duration."),
):
    """Extract video metadata."""
    video_path = Path(path).expanduser().resolve()

    if not video_path.exists():
        raise typer.Exit(1)

    # TODO: Implement actual metadata extraction logic
    echo(f"Metadata for: {video_path}")
    if extract_duration:
        echo("Duration functionality coming soon...")


if __name__ == "__main__":
    app()
