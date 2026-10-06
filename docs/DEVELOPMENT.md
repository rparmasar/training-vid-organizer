# Development Guide

This document covers the development workflow, architecture, and tooling for Training Video Organizer.

## Project Structure

```
src/training_vid_organizer/
├── __init__.py          # Package initialization
├── __about__.py         # Version metadata (__version__)
├── cli.py               # Typer CLI app (main entrypoint)
├── logging_config.py     # Structured logging setup
├── utils.py             # Video path helpers and utilities
└── db_handling/
    ├── __init__.py      # Module exports
    ├── db.py            # Dynamic SQLite schema from dataclass
    ├── query.py         # Database queries and filters
    └── update.py         # Entry modification operations
```

## Architecture Overview

### CLI Layer (`cli.py`)
- Built with **Typer** for type-safe command-line interface
- Single `app` object that registers all subcommands
- Uses Rich for formatted terminal output (tables, colors, progress)

### Database Layer (`db_handling/`)
- Schema generated at runtime from the `LiftEntry` dataclass fields
- No static SQL files; queries built dynamically via SQLAlchemy-style expressions
- Supports filtering by date range, program, exercise, weight thresholds, RIR values, etc.

### Logging (`logging_config.py`)
- Configured with structured JSON logging for production readiness
- Levels: DEBUG (verbose), INFO (default), WARNING, ERROR

## Database Schema

The schema is derived from the `LiftEntry` dataclass in `cli.py`. Core fields include:

- `id` — Primary key
- `date` — Training date (YYYY-MM-DD)
- `program` — Program name (e.g., "Push/Pull/Legs")
- `iteration` — Iteration number within a program cycle
- `lift_name` — Exercise name (e.g., "squat", "bench press")
- `weight`, `reps` — Set metrics
- `top_set`, `back_off` — Flags for set type
- `rir` — Rating of perceived exertion
- `video_path` — Path to associated video file

## Environment Variables

See [README.md](../README.md) for environment variables used to configure CLI behavior.

## Development Workflow

### Local Setup

```bash
# Install dependencies and create venv
uv sync

# Initialize database for testing
tvo init -d db/training.db

# Run CLI commands
uv run tvo list lifts
```

### Running Tests

```bash
# All tests (fast path)
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=src/training_vid_organizer
```

Automated pipelines run on GitHub:

- **CI (`ci.yml`)**: Triggers on push to non-main branches and pull requests against main. Executes lint checks and fast tests for developer feedback.
- **Build & Release (`build-and-release.yml`)**: Triggers on push to `main`. Builds distributions and publishes via `uv publish --token ${{ secrets.PYPI_API_TOKEN }}`.

## Pre-commit Hooks

All linting and validation runs via pre-commit framework before commits are finalized:

```bash
# Install hooks once (run in repo root)
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Auto-update hook versions
pre-commit autoupdate
```

**Hooks:**
- **Ruff**: Lints & formats code in `src/` and `tests/`
- **Commitlint**: Validates commit message format (Conventional Commits)

### Config Files

- `.pre-commit-config.yaml`: Single source of truth for all hooks
- `.commitlintrc.json`: Shared config for commitlint validation

## Conventional Commits & Version Bumping

Local commits are validated by pre-commit hooks before being pushed. CI uses Hatch to auto-detect and apply version bumps based on commit types.

### Format

```bash
<type>[optional scope]!: <description>
[optional body explaining the change]
[optional BREAKING CHANGE footer]
```

### Version Bump Rules (auto-detected by Hatch in CI)

| Commit Type | Effect | Example |
|-------------|--------|---------|
| `feat!` | MINOR bump (new feature) | 1.0.0 → 1.1.0 |
| `fix!` | PATCH bump (bug fix) | 1.0.0 → 1.0.1 |
| `BREAKING CHANGE:` or `type!: ` | MAJOR bump | 1.0.0 → 2.0.0 |
| All other types (`docs`, `style`, `refactor`, etc.) | No version change | — |

### Supported Types

- `feat` — New functionality (MINOR)
- `fix` — Bug fixes (PATCH)
- `docs` — Documentation updates
- `style` — Formatting changes
- `refactor` — Code restructuring
- `perf` — Performance improvements
- `test` — Test additions/modifications
- `chore` — Maintenance tasks

### Examples

```bash
feat!: add export command          # MINOR (breaking feature)
fix: correct query filter NULL     # PATCH
refactor: simplify db init         # No bump
BREAKING CHANGE: schema change     # MAJOR (when used with type!)
```

## Releases & Versioning

See [RELEASE.md](./RELEASE.md) for the complete guide on version bumping, publishing workflows, and PyPI deployment.

## Logging Configuration

The application uses structured logging configured in `logging_config.py`:

- **Format**: JSON for production compatibility
- **Levels**: DEBUG (verbose), INFO (default), WARNING, ERROR
- **Output**: Console and file rotation enabled

To enable verbose output during development:

```bash
export TVO_LOG_LEVEL=DEBUG
uv run tvo list lifts --debug
```

See [README.md](../README.md) for logging level environment variable configuration.

## Extending the CLI

### Adding a New Command

1. Import `app` from `cli.py`
2. Register using Typer's decorator syntax:

```python
from typer import echo, confirm

@app.command()
def export(format: str = "json"):
    """Export all entries to file."""
    # implementation...
```

### Adding Database Fields

1. Add fields to the `LiftEntry` dataclass in `cli.py`
2. The schema auto-generates at runtime via `db_handling/db.py`
3. Update queries in `query.py` as needed

## Troubleshooting

See [README.md](../README.md) for common troubleshooting steps.

## API Reference

### LiftEntry Dataclass Fields

The core data model is defined in `cli.py` as a Python dataclass. All database operations derive from this schema:

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Primary key, auto-generated |
| `date` | str | Training date (YYYY-MM-DD) |
| `program` | str | Program name (e.g., "Push/Pull/Legs") |
| `iteration` | int | Iteration number within a program cycle |
| `lift_name` | str | Exercise name (e.g., "squat", "bench press") |
| `weight` | float | Weight lifted in kg or lbs |
| `reps` | int | Number of repetitions |
| `top_set` | bool | Flag indicating this is a top set |
| `back_off` | bool | Flag indicating this is a back-off set |
| `rir` | float | Rating of perceived exertion (0-10) |
| `video_path` | str | Path to associated video file |

### Database Operations Module Structure

#### db_handling/db.py
- Generates SQLite schema dynamically from LiftEntry fields at runtime
- Provides connection management and initialization

#### db_handling/query.py
- Implements filtering logic for list operations
- Supports compound filters: date ranges, program/exercise matching, weight thresholds, RIR values
- Returns paginated results with count metadata

#### db_handling/update.py
- Handles single-entry modifications (update/delete)
- Validates required fields before mutation
- Uses optimistic locking to prevent concurrent update conflicts
