# Training Video Organizer

A CLI tool for organizing training videos and logging lift data with SQLite storage.

## Features

- Add individual lifts or bulk import sessions from JSON
- List, update, and delete logged entries
- Filter by date, program, exercise, weight, RIR, etc.
- Open video files to compare lift performance across various factors
- Rich terminal output with tables and colors
- Automatic calculation of estimated 1RM (Bryzycki method) and total set volume for each entry
- Analyze progress across program iterations with built-in metrics comparison

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

# List all lifts with calculated metrics
tvo list lifts

# Filter by program and iteration
tvo list lifts --program "Push/Pull/Legs" --iteration 1

# Analyze progress across iterations (est. 1RM comparison)
tvo analyze estimated_1rm

# Analyze total set volume progression
tvo analyze total_set_volume

# Open videos for top sets
tvo open --top-set -l 50

# Update a lift entry (by ID)
tvo update 42 --weight 230

# Delete an entry
tvo delete 42 --force
```

## Calculated Views

Each lift entry automatically calculates two metrics:

### Estimated 1RM (One Rep Max)
Uses the Bryzycki formula: `weight × 36 / (37 - reps)`

Example: A squat with 200 lbs for 5 reps → estimated 1RM of ~225 lbs.

View in list output as "est. 1RM" column, or analyze progression across iterations:
```bash
tvo analyze estimated_1rm
```

### Total Set Volume
Measures work done: `weight × reps`

Example: A bench press set with 135 lbs for 8 reps → volume of 1080 lbs.

Useful for comparing program iterations and tracking overall workload:
```bash
tvo analyze total_set_volume
```

## Configuration

Set environment variables to customize behavior:

- `TVO_DB_PATH` — Override default database location
- `TVO_VIDEO_DIR` — Base directory for resolving relative video paths
- `TVO_LOG_LEVEL` — Set to DEBUG or INFO for verbose output
