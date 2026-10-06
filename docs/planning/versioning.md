# versioning

previous attempts at auto bumping were problematic so this is a new approach.

## current state

* static version lives in `pyproject.toml`
* currently bumping it manually by altering strings in the file and committing to git.

## future state

* currently trying to practice using conventional commits
* would like to have these be used to bump the version number in the `pyproject.toml` file.
* release pipeline should also create a git tag

### current conventional commits

| Commit Type | Effect | Example |
|-------------|--------|---------|
| `feat:` | MINOR bump (new feature) | 1.0.0 → 1.1.0 |
| `fix:` | PATCH bump (bug fix) | 1.0.0 → 1.0.1 |
| `BREAKING CHANGE:` or `type!: ` | MAJOR bump | 1.0.0 → 2.0.0 |
| All other types (`docs`, `style`, `refactor`, etc.) | No version change | — |

## things needed to reach future state

### creating a tag for each version

this one is simpler,

1. call `uv version`
2. pipe the result into `git tag`
3. push to remote repo

### figuring out how to bump the version

ok so this should happen on pushes to `main`, and should look like:

1. get all commit messages between the last tag and the current commit (inclusive)
2. strip the conventional commits out (these should be separated by `:`)
3. find the max of `feat`, `fix`, `BREAKING CHANGE:`, etc. (where `BREAKING CHANGE` > `feat` > `fix`)
4. use the conventional commits table above to make the relevant bump e.g. if `feat` is the max, then bump the minor version using `uv version --bump minor`