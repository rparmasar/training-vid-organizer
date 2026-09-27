# Agent Quick Reference

## Commands (use uv, not pip)
```bash
uv sync                    # install deps / create venv
uv run pytest tests/       # run all tests
uv run ruff check .        # lint source only (excludes tests/)
uv run ruff format .       # format source only
tvo init -d db/training.db # initialize SQLite DB for CLI
```

## Structure
- `src/training_vid_organizer/` — core package
  - `cli.py` — Typer app entrypoint (also defines `app` object)
  - `db_handling/db.py` — dynamic SQLite schema from dataclass
- `tests/` — pytest suite with `conftest.py` providing `runner` fixture

## Testing quirks
- CLI tests use `typer.testing.CliRunner`; no external services required.
- `--strict-markers` is enabled in pytest; markers must be defined or ignored.

## DB notes
- Default path: `db/training.db`.
- Schema generated at runtime from `LiftEntry` dataclass fields.
