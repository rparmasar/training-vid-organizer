from src.training_vid_organizer.db_handling.db import (
    init_database,
    add_lift_entry,
    LiftEntry,
)


def test_init_database_works(tmpdir):
    # if this doesn't throw an error, we should be okay
    init_database(tmpdir / "test.db")


def test_add_lift_entry_works(tmpdir):
    # initialize temp db
    init_database(tmpdir / "test.db")

    # sample entry
    INPUT_ENTRY = LiftEntry(
        date="2023-04-01",
        program="P9",
        program_iteration=1,
        lift="Bicep Curl",
        weight=85,
        reps=4,
    )

    # call fn
    OBSERVED_OUTPUT = add_lift_entry(tmpdir / "test.db", INPUT_ENTRY)

    # exactly one row should be affected
    assert OBSERVED_OUTPUT == 1
