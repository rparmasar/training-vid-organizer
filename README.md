# Training Video Organizer

A CLI tool for organizing training videos and logging lift data with SQLite storage.

## Features

- Add individual lifts or bulk import sessions from JSON
- List, update, and delete logged entries
- Filter by date, program, exercise, weight, RIR, etc.
- Open video files to compare lift performance across various factors
- Rich terminal output with tables and colors

## Prerequisites

- Python 3.10+
- `uv` (recommended for dependency management)

## Installation

```bash
# Install dependencies
uv sync
```

## Quick Start

```bash
# Initialize the database
tvo init -d db/training.db

# Add a single lift with video
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

## Command Reference

| Command | Description |
|---------|-------------|
| `tvo init -d <path>` | Initialize SQLite database at given path |
| `tvo add lift` | Add a single lift entry |
| `tvo list lifts` | List all logged lifts with filters |
| `tvo update <id>` | Update an existing lift entry |
| `tvo delete <id>` | Remove a lift entry from the database |
| `tvo open` | Open video files associated with entries |

## Environment Variables

- `TVO_DB_PATH` — Override default database location
- `TVO_VIDEO_DIR` — Base directory for video files
- `TVO_LOG_LEVEL` — Set to DEBUG or INFO for verbose output
