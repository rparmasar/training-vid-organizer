#!/usr/bin/env python3
"""Calculate next semantic version based on conventional commits."""

import re
import sys


def parse_version(version_str):
    """Parse a semantic version string into components."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str)
    if not match:
        return 0, 0, 0
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(current, bump_type):
    """Apply semantic versioning rules based on bump type."""
    major, minor, patch = parse_version(current)

    if bump_type == "major":
        return (major + 1, 0, 0)
    elif bump_type == "minor":
        return (major, minor + 1, 0)
    elif bump_type in ("micro", "patch"):
        return (major, minor, patch + 1)

    else:
        return major, minor, patch


def format_version(major, minor, patch):
    """Format version components back to string."""
    return f"{major}.{minor}.{patch}"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Calculate next semantic version based on bump type")
    parser.add_argument("--bump-type", default="none", help="Type of version bump (major/minor/micro/patch)")
    parser.add_argument("--current-version", default="0.0.0", help="Current version string")
    
    args = parser.parse_args()
    
    bump_type = args.bump_type.lower()
    current_version = args.current_version

    new_major, new_minor, new_patch = bump_version(current_version, bump_type)
    next_version = format_version(new_major, new_minor, new_patch)

    print(next_version)
