# Training Video Organizer

A Python CLI tool for organizing training videos with metadata extraction, categorization/tagging, and search capabilities.

## Features

- **Metadata Extraction**: Extract video information including tags and duration
- **Categorization & Tagging**: Organize videos into categories with custom tags
- **Search & Filtering**: Find videos by various criteria (path, tags, duration)

## Installation

### Prerequisites

- Python 3.12+
- uv (package manager and build tool)

Install uv globally:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### Setup

Clone the repository and install dependencies using uv:

```bash
git clone <repository-url>
cd training-vid-organizer
uv sync
```

This will create a virtual environment and install all required packages.

## Usage

After installation, you can run the CLI directly:

```bash
# Show help
training-vid-organizer --help

# Search videos in a directory
training-vid-organizer search /path/to/videos

# Categorize videos with tags
training-vid-organizer categorize "tag1 tag2" -o ./organized_videos

# Extract metadata from a video file
training-vid-organizer metadata /path/to/video.mp4 --duration
```

## Development

### Running Tests

```bash
uv run pytest tests/
```

### Project Structure

```
src/training_vid_organizer/
├── __init__.py      # Package initialization
├── cli.py           # Typer CLI entry point
├── commands/        # Command modules (metadata, categorize, search)
├── models.py        # Data models (Pydantic)
├── storage.py       # File system operations
└── config.py        # Configuration handling
```

## License

MIT License - see LICENSE file for details.
