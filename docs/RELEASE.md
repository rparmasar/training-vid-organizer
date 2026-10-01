# Release & Publishing Guide

This project uses semantic versioning with automatic bumping based on conventional commits and annotated git tags. Releases are published to PyPI via GitHub Actions when a new tag is created.

## How Version Bumping Works

Hatch-VCS automatically determines the next version from your commit history:

1. **Annotated Git Tags**: Create an annotated tag (e.g., `git tag -a v1.0.0 -m "Release 1.0.0"`)
2. **Commit Analysis**: Hatch scans commits since the previous tag to detect conventional commits
3. **Auto-Bump**: The version in `src/training_vid_organizer/__about__.py` is updated automatically during build

### Version Bumping Rules (from commit types)

- Commits with `feat:` → minor version bump (e.g., 1.0.0 → 1.1.0)
- Commits with `fix:` → patch version bump (e.g., 1.0.0 → 1.0.1)
- Commits with `BREAKING CHANGE` or `!` in type → major version bump (e.g., 1.0.0 → 2.0.0)

See [Hatch-VCS Versioning](https://hatch.pypa.io/1.12/version/#version-schemes) for details on how the algorithm works.

## Conventional Commits Format

### Structure

```bash
<type>[optional scope]!: <description>
[optional body explaining the change]
[optional BREAKING CHANGE footer]
```

### Supported Types

| Type | Effect | Example |
|------|--------|---------|
| `feat` | New functionality (MINOR) | 1.0.0 → 1.1.0 |
| `fix` | Bug fixes (PATCH) | 1.0.0 → 1.0.1 |
| `BREAKING CHANGE:` or `type!: ` | MAJOR bump | 1.0.0 → 2.0.0 |
| All other types (`docs`, `style`, `refactor`, etc.) | No version change | — |

### Examples

```bash
feat!: add export command          # MINOR (breaking feature)
fix: correct query filter NULL     # PATCH
refactor: simplify db init         # No bump
BREAKING CHANGE: schema change     # MAJOR (when used with type!)
docs: update README examples       # No bump
```

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

### Publishing Flow (Fully Automated)

When you push commits with conventional commit messages:

1. **Push Commits**: Push your changes to `main` branch (no tags needed!)
2. **Workflow Triggers**: GitHub Actions detects the push and analyzes commit history
3. **Auto-Calculate Version**: Uses Hatch-VCS to determine next version from conventional commits
4. **Update __about__.py**: Automatically updates `src/training_vid_organizer/__about__.py` with new version
5. **Build & Tag**: Builds distributions and creates annotated git tag automatically
6. **Publish to PyPI**: Publishes via `uv publish --token ${{ secrets.PYPI_API_TOKEN }}`

**Note:** You do NOT need to manually create tags or update the version file. The workflow handles everything automatically based on your commit messages.

### Manual Publishing

For local development or testing, you can manually trigger the workflow:

```bash
# Build distributions first
uvx hatch build

# Then publish (requires PYPI_API_TOKEN in GitHub Secrets)
uv publish --token $PYPI_API_TOKEN
```

## Example Release Workflow (Fully Automated)

Here's a typical release flow using conventional commits:

```bash
# 1. Make changes with conventional commit messages
git add .
git commit -m "feat!: add export command"           # Will bump minor version
# or
git commit -m "fix: correct query filter NULL"      # Will bump patch version

# 2. Push to GitHub (no tags needed!)
git push origin main

# 3. GitHub Actions workflow automatically:
#    - Analyzes commits since last release
#    - Calculates next semantic version (e.g., 1.0.0 → 1.1.0)
#    - Updates __about__.py with new version
#    - Builds distributions and creates tag v1.1.0
#    - Publishes to PyPI via uv publish
```

The key insight: **Hatch-VCS determines the version automatically** based on what it finds in your commit history since the last release. You don't need to know or specify the exact version number—it's calculated from conventional commits (`feat:`, `fix:`, etc.).

## GitHub Actions Workflows

Two workflows run automatically on the repository:

### CI (`ci.yml`)
- **Trigger**: Every commit/PR against main branch
- **Purpose**: Fast feedback for developers during development
- **Steps**: Lint checks (ruff) and fast test suite execution

### Build & Release (`build-and-release.yml`)
- **Trigger**: Push to `main` branch with version bump commits
- **Purpose**: Full release pipeline including PyPI publishing
- **Steps**:
  - Detect semantic version from conventional commits
  - Create annotated git tag (e.g., `v1.1.0`)
  - Build wheel and source distributions via Hatch
  - Generate release notes automatically
  - Publish to PyPI using configured API token

See [README.md](../README.md) for local development setup and environment variable configuration.
