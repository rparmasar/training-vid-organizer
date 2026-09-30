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
