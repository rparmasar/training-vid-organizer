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

## Pre-commit Hooks (Consolidated)
All linting and validation runs via pre-commit framework before commits are finalized:

```bash
# Install hooks once
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Auto-update hook versions
pre-commit autoupdate
```

**Hooks:**
- **Ruff**: Lints & formats code in `src/` and `tests/`
- **Commitlint**: Validates commit message format (Conventional Commits)

**Config files:**
- `.pre-commit-config.yaml`: Single source of truth for all hooks
- `.commitlintrc.json`: Shared config for commitlint validation

## Publishing to PyPI
Releases are published via GitHub Actions using `uv publish` directly. This approach handles Hatch's Metadata-Version 2.5+ wheels natively, avoiding compatibility issues with Docker-based publishing tools.

**Required secret:** Add `PYPI_API_TOKEN` repository secret (from https://pypi.org/account/#api).
