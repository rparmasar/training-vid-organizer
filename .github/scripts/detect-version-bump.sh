#!/usr/bin/env bash
# Detect semantic version bump from conventional commits (last 10 commits)
# Outputs: major|minor|micro|none

set -euo pipefail

python3 << 'PYTHON_SCRIPT'
import subprocess
import re

def get_commits():
    """Get last N commit messages."""
    result = subprocess.run(
        ["git", "log", "--oneline", "-10"],
        capture_output=True, text=True, check=True
    )
    # git log --oneline format: <hash> <message>
    return [line.split(" ", 1)[1] if len(line.split(" ")) > 1 else "" for line in result.stdout.strip().split("\n")]

def parse_commit_type(commit_msg):
    """Extract commit type and breaking flag from conventional commit."""
    match = re.match(r"^([a-z]+)(!)?\s*:", commit_msg, re.IGNORECASE)
    if not match:
        return None, False
    return match.group(1).lower(), match.group(2) == "!"

def determine_bump_type(commits):
    """Apply version bump rules based on commit history."""
    # Priority order: MAJOR > MINOR > MICRO
    
    for commit in commits:
        commit_type, is_breaking = parse_commit_type(commit)
        
        if not commit_type:
            continue
        
        # MAJOR bump conditions (highest priority)
        if is_breaking or commit_type == "refactor!":
            return "major"
        
        # MINOR bump for features
        elif commit_type == "feat":
            return "minor"
        
        # MICRO bump for bug fixes
        elif commit_type == "fix":
            return "micro"
    
    return "none"

if __name__ == "__main__":
    commits = get_commits()
    bump_type = determine_bump_type(commits)
    # Output only the bump type, no label (workflow will handle echo)
    print(bump_type)
PYTHON_SCRIPT
