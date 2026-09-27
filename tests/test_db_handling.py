from src.training_vid_organizer.db_handling.db import init_database

def test_init_database_works(tmpdir):
    # if this passes, then we can be confident that the db is initialized correctly. 
    init_database(tmpdir / "test.db")
    