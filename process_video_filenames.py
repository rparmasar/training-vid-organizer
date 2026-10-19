"""script to custom sort xtu go filenames in a directory, e.g. we want to sort names like 229638144_NORM0012.MP4 by the NORM0012 suffix"""

import os
import sys
from pathlib import Path


def get_norm_key(path: Path) -> tuple[int, str] | None:
    """Extract numeric NORM key and proposed normalized filename.

    Returns (numeric_value, new_filename) if valid, else None.
    Example: "229638144_NORM0012.MP4" → (12, "NORM0012_229638144.MP4")
    """
    try:
        parts = path.name.split("_", 1)
        if len(parts) < 2 or "NORM" not in parts[1]:
            return None

        norm_part = parts[1].split(".")[0]

        # Extract numeric value after "NORM" (e.g., "NORM0012" → 12)
        if not norm_part.startswith("NORM"):
            return None
        numeric_value = int(norm_part[4:])

        # New format: NORM####_original_prefix.ext
        new_name = f"NORM{numeric_value}_{parts[0]}" + (path.suffix or "")

        return numeric_value, new_name
    except (ValueError, IndexError):
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python process_video_filenames.py <directory>")
        return

    directory = Path(sys.argv[1])

    # Validate directory exists and is readable
    try:
        files = list(directory.iterdir())
    except PermissionError as e:
        print(f"Permission denied accessing '{directory}': {e}", file=sys.stderr)
        return

    # Filter for files (not directories) containing 'NORM' in name
    norm_files = [f for f in files if f.is_file() and "NORM" in f.name]

    if not norm_files:
        print("No matching files found.")
        return

    # Extract keys, filter invalid ones, then sort
    valid_files = []
    for f in norm_files:
        key = get_norm_key(f)
        if key is not None:
            valid_files.append((f, key))

    if not valid_files:
        print("No files with valid NORM format found.")
        return

    # Sort by numeric NORM value (ascending)
    sorted_files = sorted(valid_files, key=lambda x: x[1][0])

    # Dry run output
    print("Sorted order (NORM suffix):")
    for i, (f, (_, new_name)) in enumerate(sorted_files, 1):
        norm_val = (
            f"{sorted_files[i - 1][1][0]:04d}" if sorted_files[i - 1][1][0] else "???"
        )
        print(f"{i:3}. {f.name} → {new_name} (NORM{norm_val})")

    # Confirm with user before modifying
    confirm = input("\nNormalize filenames? [y/N] ").strip().lower()
    if confirm in ("y", "yes"):
        failed_files = []

        for f, (_, new_name) in sorted_files:
            target_path = directory / new_name

            # Check for naming conflicts before attempting rename
            if target_path.exists():
                print(
                    f"  ⚠️  Skipping '{f.name}': target '{new_name}' already exists",
                    file=sys.stderr,
                )
                failed_files.append((f, new_name))
                continue

            try:
                os.rename(str(f), str(target_path))
            except PermissionError as e:
                print(
                    f"  ⚠️  Skipping '{f.name}': permission denied - {e}",
                    file=sys.stderr,
                )
                failed_files.append((f, new_name))
            except OSError as e:
                print(f"  ⚠️  Skipping '{f.name}': {e}", file=sys.stderr)
                failed_files.append((f, new_name))

        if failed_files:
            print(
                f"\n{len(failed_files)} file(s) were skipped due to errors.",
                file=sys.stderr,
            )
        else:
            print("\nNormalization complete.")


if __name__ == "__main__":
    main()
