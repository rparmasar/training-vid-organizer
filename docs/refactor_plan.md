# refactor plan

do these to simplify the agent design (as it is too complicated)

## tasks

1. get rid of db class and turn its methods into pure functions that take a connection object, and some form of `LiftEntry`

2. write tests for these and include a fixture that can generate/initialize a test db using `LiftEntry` schema.

3. prune files that are not needed