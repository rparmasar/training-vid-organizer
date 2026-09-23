# Training Video Organizer - Repository Setup Plan

## Overview
A Python CLI for organizing training videos with metadata extraction, categorization/tagging, and search capabilities. Built with Typer for the CLI interface and uv for package management.

## Directory Structure

```
training-vid-organizer/
├── pyproject.toml              # Package metadata + dependencies (uv-native)
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
├── src/
│   └── training_vid_organizer/  # Main package
│       ├── __init__.py         # Package init with version/__all__
│       ├── cli.py              # Typer CLI entry point
│       ├── commands/           # Command modules
│       │   ├── __init__.py
│       │   ├── metadata.py     # Video metadata extraction
│       │   ├── categorize.py   # Categorization & tagging
│       │   └── search.py       # Search & filtering
│       ├── models.py           # Data models (Pydantic)
│       ├── storage.py          # File system operations
│       └── config.py           # Configuration handling
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures
│   ├── cli_test.py             # CLI integration tests
│   ├── commands_test.py        # Command unit tests
│   └── models_test.py          # Model validation tests
├── scripts/                    # Development utilities (optional)
│   └── seed_data.py            # Sample data for testing
```

## Key Design Decisions

1. **Typer CLI**: Clean, type-safe command definitions with automatic help generation
2. **uv-native**: Uses `pyproject.toml` as single source of truth; no separate requirements.txt
3. **src-layout**: Prevents namespace pollution, cleaner imports
4. **Pydantic models**: For data validation and serialization (recommended)

## Typer CLI Structure Example

```python
# src/training_vid_organizer/cli.py
from typer import Typer, echo

app = Typer(name="training-vid-organizer")

@app.command()
def search(path: str = "...", tags: list[str] | None = None):
    """Search videos by path and optional tags."""
    ...

@app.command()
def categorize(tags: list[str], output_dir: str = "videos"):
    """Categorize videos with given tags."""
    ...

@app.command()
def metadata(path: str, extract_duration: bool = False):
    """Extract video metadata."""
    ...
```

## Dependencies (pyproject.toml)

- **typer[all]** - CLI framework
- **pydantic** - Data validation/models  
- **pathlib** - Path operations (stdlib in 3.10+)
- **rich** - Optional: pretty terminal output
- **click** - Typer dependency for advanced features

## Implementation Phases

### Phase 1: Foundation ✅ COMPLETE
- [x] Create pyproject.toml with uv configuration
- [x] Set up src-layout package structure (`src/training_vid_organizer/`)
- [x] Implement basic CLI entry point (Typer-based)
- [x] Add .gitignore and README.md

**Completed files:**
- `pyproject.toml` - uv-native config with typer, pydantic dependencies
- `src/training_vid_organizer/__init__.py` - Package init with version export
- `src/training_vid_organizer/cli.py` - Typer CLI with search, categorize, metadata commands
- `.gitignore` - Python/uv-specific ignore rules
- `README.md` - Project documentation

**Verified working:**
- uv installed globally (v0.12.18)
- Dependencies synced via `uv sync`
- CLI tested: `training-vid-organizer --version`, `--help`, all commands respond correctly

### Phase 2: Core Modules
- [ ] Build models.py with Pydantic schemas
- [ ] Implement storage.py for file operations
- [ ] Create metadata.py for video info extraction
- [ ] Develop search.py functionality

### Phase 3: Commands & Testing
- [ ] Wire up Typer commands to modules
- [ ] Write unit tests for each module
- [ ] Add CLI integration tests
- [ ] Include seed_data.py script for testing

## Development Workflow

1. Install uv globally or use as subcommand
2. Run `uv sync` to create virtual environment and install dependencies
3. Use `uv run python -m training_vid_organizer.cli --help` to test CLI
4. Tests via: `uv run pytest tests/`
