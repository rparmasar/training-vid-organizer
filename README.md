# Training Video Organizer

A CLI tool for organizing training videos and logging lift data with SQLite storage.

## Features

- Add individual lifts or bulk import sessions from JSON
- List, update, and delete logged entries
- Filter by date, program, exercise, weight, RIR, etc.
- Open video files directly from the database
- Rich terminal output with tables and colors

## Tech Stack

- Python 3.10+
- Typer (CLI framework)
- SQLite (via dynamic schema generation)
- Rich (terminal UI)

## Quick Start

```bash
# Install dependencies
uv sync

# Initialize the database
tvo init -d db/training.db

# Add a single lift
tvo add lift --date 2026-09-30 --program "Push/Pull/Legs" \
             --iteration 1 --lift squat --weight 225 --reps 8 \
             --top-set -f /videos/squat_20260930.mp4

# List all lifts
tvo list lifts

# Filter by program and iteration
tvo list lifts --program "Push/Pull/Legs" --iteration 1

# Open videos for top sets
tvo open --top-set -l 50

# Update a lift entry (by ID)
tvo update 42 --weight 230

# Delete an entry
tvo delete 42 --force
```

## Project Structure

- `src/training_vid_organizer/` — core package
  - `cli.py` — Typer app with all commands
  - `db_handling/db.py` — dynamic SQLite schema from dataclass
  - `logging_config.py` — structured logging setup
  - `utils.py` — video path helpers

## Environment Variables

- `TVO_DB_PATH` — override default database location
- `TVO_VIDEO_DIR` — base directory for video files
- `TVO_LOG_LEVEL` — set to DEBUG or INFO for verbose output

## CI/CD Workflows

Automated pipelines run on GitHub:

- **CI (`ci.yml`)**: Runs on every commit/PR against main. Executes lint checks and fast tests for developer feedback.
- **Build & Release (`build-and-release.yml`)**: Triggers on push to `main`. Uses Hatch to auto-detect semantic version bumps from conventional commits, builds distributions, creates annotated tags, and generates release notes.
- **Publish (`publish.yml`)**: Manual trigger via workflow_dispatch. Publishes to TestPyPI or PyPI using GitHub Actions trusted publishing (id-token).

### Local Development Hooks

A pre-commit hook validates commit messages against Conventional Commits format before allowing commits to be staged. Run `git commit` and it will automatically check your message.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) to enable automated versioning and release notes generation.

**Format:**
```bash
<type>[optional scope]!: <description>
[optional body explaining the change]
[optional BREAKING CHANGE footer]
```

**Version Bump Rules (auto-detected by Hatch in CI):**
- `feat!` → MINOR bump (new feature)
- `fix!` → PATCH bump (bug fix)
- `BREAKING CHANGE:` or `type!: ` → MAJOR bump
- All other types → no version change

**Supported Types:**
| Type | Example | Effect |
|------|---------|--------|
| `feat` | `feat: add export command` | MINOR (new functionality) |
| `fix` | `fix: correct query filter NULL` | PATCH (bug fixes) |
| `docs` | `docs: update README examples` | No bump |
| `style` | `style: format code with ruff` | No bump |
| `refactor` | `refactor: simplify db init` | No bump |
| `perf` | `perf: optimize query execution` | No bump |
| `test` | `test: add edge case coverage` | No bump |
| `chore` | `chore: update dependencies` | No bump |

**Examples:**
```bash
feat!: add export command          # MINOR (breaking feature)
fix: correct query filter NULL     # PATCH
refactor: simplify db init         # No bump
BREAKING CHANGE: schema change     # MAJOR (when used with type!)
```

Local commits are validated by pre-commit hooks before being pushed. CI uses Hatch to auto-detect and apply version bumps based on commit types.
