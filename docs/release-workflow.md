# Release Workflow & Publishing

## Overview

This project uses semantic versioning with automatic bumping based on conventional commits. Releases are published to PyPI via GitHub Actions when a version bump is detected.

## Version Bumping Strategy

The workflow automatically detects version changes from your commit messages:

- `feat:` → minor version bump (e.g., 1.0.0 → 1.1.0)
- `fix:` → patch version bump (e.g., 1.0.0 → 1.0.1)
- `BREAKING CHANGE` or `!` in commit message → major version bump (e.g., 1.0.0 → 2.0.0)

See [Hatch Versioning](https://hatch.pypa.io/1.9/version/) for details on how the version is managed.

## Publishing to PyPI

### Why `uv publish` Directly?

Instead of using Docker-based publishing actions, this project uses `uv publish` directly in GitHub Actions. This approach was chosen because:

1. **Metadata-Version Compatibility**: Hatch generates wheels with `Metadata-Version: 2.5`, which exceeds the PyPI action's supported range (up to 2.3). Using `uv publish` natively handles newer metadata versions without compatibility issues.

2. **Simpler Workflow**: Direct execution avoids Docker layer overhead and configuration complexity.

3. **Trusted Publishing**: Uses GitHub Actions' id-token authentication for secure PyPI uploads.

### Required Secrets

To enable publishing, add the following secret to your repository:

1. Go to: Settings → Secrets and variables → Actions → Repository secrets
2. Click "New repository secret"
3. Add a secret named `PYPI_API_TOKEN` with your PyPI API token

**How to get your PyPI API token:**
- Visit https://pypi.org/account/#api
- Generate an API token (select "Limited access" or "Full access")
- Copy the generated token and paste it into GitHub Secrets

### Publishing Flow

When a commit with a version bump is pushed:

1. Workflow detects the bump from conventional commits
2. Creates a git tag matching the new version (e.g., `v1.1.0`)
3. Builds wheel and source distributions using Hatch
4. Publishes to PyPI via `uv publish --token ${{ secrets.PYPI_API_TOKEN }}`

### Manual Publishing

For local development or testing, you can manually publish:

```bash
# Build distributions first
uvx hatch build

# Then publish (requires PYPI_API_TOKEN in GitHub Secrets)
uv publish --token $PYPI_API_TOKEN
```

## Local Development Setup

To initialize the SQLite database for CLI operations:

```bash
tvo init -d db/training.db
```

This creates the required database schema at runtime from the `LiftEntry` dataclass fields.
