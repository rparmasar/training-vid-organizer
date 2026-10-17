# Training Video Organizer

A CLI tool for organizing training videos, logging lift data, and sorting video files by NORM suffix.

## Features

### Lift & Session Management
- Add individual lifts or bulk import sessions from JSON or CSV files
- List, update, and delete logged entries
- Filter by date, program, exercise, weight, RIR, etc.
- Open video files to compare lift performance across various factors
- Rich terminal output with tables and colors
- Automatic calculation of estimated 1RM (Bryzycki method) and total set volume for each entry
- Analyze progress across program iterations with built-in metrics comparison

### Video File Organization & Playback
- Process directories containing NORM-labeled video files
- Automatically sort files by their NORM suffix in ascending order
- Open filtered videos sequentially using VLC for side-by-side comparison
- Dry-run mode to preview changes before applying them

## Prerequisites

- Python 3.10+
- `uv` (recommended for dependency management)
- VLC media player (for video playback feature; optional but recommended)

### Installing VLC

**Linux:**
```bash
sudo apt install vlc        # Debian/Ubuntu
sudo dnf install vlc        # Fedora/RHEL
sudo pacman -S vlc          # Arch Linux
```

**macOS:**
Download from [VLC official site](https://www.videolan.org/vlc/) or use Homebrew:
```bash
brew install vlc
```

**Windows:**
Download installer from [VLC official site](https://www.videolan.org/vlc/).

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

# Open videos for top sets (sequentially with VLC)
tvo open --top-set -l 50

# Process NORM video files in a directory
tvo process /videos/NORM --dry-run          # Preview sorting without changes
tvo process /videos/NORM                    # Apply sorting after confirmation

# Update a lift entry (by ID)
tvo update 42 --weight 230

# Delete an entry
tvo delete 42 --force
```

## CSV Import Format

Bulk import training sessions from a CSV file:

```bash
tvo add session -c data/sessions.csv
```

### Required Columns

| Column | Type | Description |
|--------|------|-------------|
| `date` | string | Date in YYYY-MM-DD format |
| `program` | string | Program name (e.g., "Push/Pull/Legs") |
| `program_iteration` | integer | Iteration number of the program |
| `lift` | string | Exercise name (e.g., "squat", "bench press") |
| `weight` | integer | Weight lifted in lbs or kg |
| `reps` | integer | Number of repetitions |

### Optional Columns

| Column | Type | Description |
|--------|------|-------------|
| `bodyweight` | float | Body weight at time of lift |
| `top_set` | boolean | Mark as top set (true/false) |
| `warm_up_set` | boolean | Mark as warm-up set (true/false) |
| `reps_in_reserve` | integer | RIR value (e.g., 1, 2, 3) |
| `filename` | string | Path to video file for this lift |

### Example CSV

```csv
date,program,program_iteration,lift,weight,reps,bodyweight,top_set,reps_in_reserve,filename
2026-09-30,Push/Pull/Legs,1,squat,225,8,185,true,1,/videos/squat_20260930.mp4
2026-09-30,Push/Pull/Legs,1,bench press,135,10,185,false,2,/videos/bench_20260930.mp4
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

## Video File Processing

The `process` command organizes NORM-labeled video files in a directory by sorting them based on their NORM suffix. This is useful when you have multiple videos from different sessions that need to be ordered chronologically or numerically.

### How It Works

1. Scans the target directory for files containing "NORM"
2. Extracts the numeric value from each file's NORM suffix (e.g., `NORM0042` → 42)
3. Sorts files in ascending order by this numeric value
4. Displays a preview of the sorted order

### Usage

```bash
# Preview changes without modifying files
tvo process /videos/NORM --dry-run

# Apply changes after confirming with prompt
tvo process /videos/NORM
```

### Example Output

```
Sorted order (NORM suffix):
   1. 229638144_NORM0012.MP4 → 229638144_NORM0012.MP4 (NORM0012)
   2. 273678336_NORM0165.mp4 → 273678336_NORM0165.mp4 (NORM0165)
   3. file_NORM9999.MP4 → file_NORM9999.MP4 (NORM9999)

Normalize 3 file(s) in '/videos/NORM'? [y/N]: y
```

### Notes

- Only files directly in the target directory are processed (no subdirectories)
- Files must contain "NORM" and follow the expected naming convention
- Invalid filenames are skipped with a warning message
