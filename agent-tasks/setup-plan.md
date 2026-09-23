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


# Training Video Organizer - Test Suite & Ruff Formatting Plan

## Current State Analysis
- **Project**: uv-managed Python package with Typer CLI skeleton (3 commands: `search`, `categorize`, `metadata`)
- **Dependencies**: `typer[all]>=0.15.0`, `pydantic>=2.9.0` installed via `uv sync`
- **CLI verified working**: All commands respond correctly with placeholder messages

## Test Suite Strategy (Minimal & Focused)

### 1. Add Testing Dependencies to pyproject.toml
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-typer>=0.4.0",  # Typer-specific fixtures and testing utilities
    "ruff>=0.9.0",          # Linting + formatting (replaces flake8/black)
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
addopts = "-v --strict-markers"
```

**Rationale**: 
- `pytest-typer` provides automatic CLI fixtures, eliminating boilerplate test setup
- Keeps dependency count minimal (3 packages vs 5+ with separate tools)

### 2. Directory Structure for Tests
```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared fixtures (pytest-typer handles most)
├── cli_test.py              # CLI integration tests (command smoke tests)
└── commands_test.py          # Unit tests for individual command logic
```

### 3. Minimal Test Coverage Matrix

| Component | Test Type | Purpose | Lines of Code Impact |
|-----------|-----------|---------|---------------------|
| **CLI Entry Point** | Integration (pytest-typer) | Verify app loads, commands register, help text renders | ~20 lines |
| **search command** | Smoke test + argument parsing | Path validation, tag filtering flags parse correctly | ~15 lines |
| **categorize command** | Smoke test + edge cases | Empty tags rejection, output dir flag handling | ~15 lines |
| **metadata command** | Smoke test + path resolution | File existence check, duration flag parsing | ~15 lines |
| **Error Handling** | Integration tests | Invalid paths → exit code 1, missing args → proper error messages | ~20 lines |

**Total**: ~85 lines of focused tests covering all CLI entry points and argument flows.

### 4. Recommended Test Implementation Pattern
```python
# cli_test.py (pytest-typer style)
import pytest
from typer.testing import CliRunner
from training_vid_organizer.cli import app

runner = CliRunner()

def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert "v0.1.0" in result.output
    assert result.exit_code == 0

def test_search_command_basic():
    result = runner.invoke(app, ["search", "."])
    assert "Searching in:" in result.output
    assert result.exit_code == 0

def test_categorize_requires_tags():
    result = runner.invoke(app, ["categorize"])
    assert result.exit_code == 1  # Missing required Argument

def test_metadata_invalid_path():
    result = runner.invoke(app, ["metadata", "/nonexistent/video.mp4"])
    assert result.exit_code == 1
```

## Ruff Configuration Strategy

### 1. Add to pyproject.toml (Single Config File)
```toml
[tool.ruff]
target-version = "py312"
line-length = 88
extend-exclude = ["tests/"]  # Exclude tests from formatting

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings  
    "F",   # Pyflakes
    "I",   # isort (imports sorted automatically)
    "UP",  # pyupgrade (modern syntax)
]
ignore = [
    "E501",  # Line length handled by line-length config
]

[tool.ruff.lint.isort]
known-first-party = ["training_vid_organizer"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

**Rationale**: 
- `I` (isort) + `UP` (pyupgrade) handles formatting automatically during linting
- Single config file, no separate `.ruff.toml` needed
- Excludes tests to avoid reformatting test code unnecessarily

### 2. Ruff Workflow Integration

| Command | Purpose | When to Run |
|---------|---------|-------------|
| `uv run ruff check .` | Lint only (no changes) | Before committing, PR review |
| `uv run ruff format .` | Format files in place | After editing source files |
| `uv run ruff check --fix . && uv run ruff format .` | Auto-fix + format | Post-edit cleanup pipeline |

**Recommended Workflow**:
1. Edit file → 2. Run `uv run ruff format <file>` → 3. Verify with `uv run ruff check <file>`

### 3. Optional: Pre-commit Hook (Future-Proofing)
```toml
# Add to pyproject.toml if pre-commit is desired later
[tool.pytest.ini_options]
...
markers = ["slow", "integration"]
```

Later can add `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
```

## Execution Order (Minimal Path)

1. **Add dev dependencies**: `uv add --dev pytest pytest-typer ruff`
2. **Update pyproject.toml**: Insert `[tool.ruff]` and `[tool.pytest.ini_options]` sections
3. **Create tests/**: Initialize package with `__init__.py`, `conftest.py`
4. **Write cli_test.py**: Implement ~50 lines of smoke/integration tests
5. **Run verification**: 
   - `uv run pytest tests/` → should pass all 4-6 tests
   - `uv run ruff check src/training_vid_organizer/cli.py` → zero issues

## Verification Checklist

- [ ] `uv add --dev pytest pytest-typer ruff` succeeds (3 new packages)
- [ ] pyproject.toml contains `[tool.ruff]` and `[tool.pytest.ini_options]` sections
- [ ] tests/ directory created with `__init__.py`, `conftest.py`
- [ ] cli_test.py passes all 4-6 smoke/integration tests via `uv run pytest tests/cli_test.py -v`
- [ ] Running `uv run ruff check src/training_vid_organizer/cli.py` shows zero issues
- [ ] Formatting a file with `uv run ruff format <file>` produces clean output

## Tradeoffs & Decisions

| Decision | Alternative Considered | Why This Choice |
|----------|------------------------|-----------------|
| pytest-typer over plain pytest | Manual CliRunner setup everywhere | Saves ~40 lines of boilerplate per test file |
| ruff over flake8+black | Separate tools (flake8, black, isort) | Single binary, faster, auto-fixes formatting + linting |
| Line length 88 vs 120 | Standard PEP8 79/120 | 88 fits most terminal widths while allowing reasonable wrapping |
| Exclude tests from ruff format | Format everything including tests | Tests have different style; avoid unnecessary churn |

## Next Steps After Implementation

1. Add 2-3 unit tests in `commands_test.py` for edge cases (invalid paths, empty tags)
2. Run full suite: `uv run pytest tests/ -v --tb=short`
3. Commit with message: "feat: add minimal test suite + ruff formatting"

