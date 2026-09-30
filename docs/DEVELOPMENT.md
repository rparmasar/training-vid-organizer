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

| Variable | Description | Default |
|----------|-------------|---------|
| `TVO_DB_PATH` | Override database file location | N/A (uses CLI `-d`) |
| `TVO_VIDEO_DIR` | Base directory for resolving relative video paths | N/A |
| `TVO_LOG_LEVEL` | Logging verbosity: DEBUG, INFO, WARNING, ERROR | INFO |

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

## CI/CD Workflows

Automated pipelines run on GitHub:

- **CI (`ci.yml`)**: Triggers on every commit/PR against main. Executes lint checks and fast tests for developer feedback.
- **Build & Release (`build-and-release.yml`)**: Triggers on push to `main`. Uses Hatch to auto-detect semantic version bumps from conventional commits, builds distributions, creates annotated tags, and generates release notes. Publishes directly via `uv publish --token ${{ secrets.PYPI_API_TOKEN }}`.

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

## Publishing to PyPI

Releases are published via GitHub Actions using `uv publish` directly. This approach was chosen because:

1. **Metadata-Version Compatibility**: Hatch generates wheels with `Metadata-Version: 2.5`, which exceeds the PyPI action's supported range (up to 2.3). Using `uv publish` natively handles newer metadata versions without compatibility issues.
2. **Simpler Workflow**: Direct execution avoids Docker layer overhead and configuration complexity.
3. **Trusted Publishing**: Uses GitHub Actions' id-token authentication for secure PyPI uploads.

### Required Secret

To enable publishing, add the following secret to your repository:

1. Go to: Settings → Secrets and variables → Actions → Repository secrets
2. Click "New repository secret"
3. Add a secret named `PYPI_API_TOKEN` with your PyPI API token

**How to get your PyPI API token:**
- Visit https://pypi.org/account/#api
- Generate an API token (select "Limited access" or "Full access")
- Copy the generated token and paste it into GitHub Secrets

### Publishing Flow

When a commit with a version bump is pushed:

1. Workflow detects the bump from conventional commits
2. Creates a git tag matching the new version (e.g., `v1.1.0`)
3. Builds wheel and source distributions using Hatch
4. Publishes to PyPI via `uv publish --token ${{ secrets.PYPI_API_TOKEN }}`

### Manual Publishing

For local development or testing:

```bash
# Build distributions first
uvx hatch build

# Then publish (requires PYPI_API_TOKEN in GitHub Secrets)
uv publish --token $PYPI_API_TOKEN
```

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

### Database Not Found

```bash
# Reinitialize with explicit path
tvo init -d db/training.db
```

### Video Path Resolution Issues

Set `TVO_VIDEO_DIR` to the base directory where videos are stored:

```bash
export TVO_VIDEO_DIR=/path/to/videos
```

### Linting Errors

Run pre-commit hooks manually to catch issues before committing:

```bash
pre-commit run --all-files
```
