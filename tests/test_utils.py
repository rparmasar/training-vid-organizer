import os
import typer
from pathlib import Path
from src.training_vid_organizer.utils import get_config_paths, open_video_file


def test_get_config_paths_defaults():
    # if this doesn't throw an error, we should be okay
    db_path, video_dir = get_config_paths(Path("default/db/training.db"))

    assert db_path == "default/db/training.db"
    assert video_dir == ""


def test_get_config_paths_db_env_var(tmpdir):
    # set env var
    os.environ["TVO_DB_PATH"] = str(tmpdir / "custom.db")

    # call fn
    db_path, video_dir = get_config_paths(Path("default/db/training.db"))

    # exactly one row should be affected
    assert db_path == str(tmpdir / "custom.db")
    assert video_dir == ""


def test_get_config_paths_video_env_var():
    # set env var
    os.environ["TVO_VIDEO_DIR"] = "/videos/storage"

    # call fn
    db_path, video_dir = get_config_paths(Path("default/db/training.db"))

    assert db_path == "default/db/training.db"
    assert video_dir == "/videos/storage"


def test_get_config_paths_both_env_vars():
    # set both env vars
    os.environ["TVO_DB_PATH"] = "/custom/db.sqlite"
    os.environ["TVO_VIDEO_DIR"] = "/custom/videos"

    # call fn
    db_path, video_dir = get_config_paths(Path("default/db/training.db"))

    assert db_path == "/custom/db.sqlite"
    assert video_dir == "/custom/videos"


def test_get_config_paths_empty_string_video():
    # set empty string for video dir
    os.environ["TVO_VIDEO_DIR"] = ""

    # call fn
    db_path, video_dir = get_config_paths(Path("default/db/training.db"))

    assert db_path == "default/db/training.db"
    assert video_dir == ""


def test_get_config_paths_custom_default():
    # use custom default path
    custom_default = Path("/app/data/training.db")

    # call fn
    db_path, video_dir = get_config_paths(custom_default)

    assert db_path == "/app/data/training.db"
    assert video_dir == ""


def test_open_video_file_works(tmpdir, monkeypatch):
    # setup inputs
    input_filename = "test.txt"
    input_base_dir = Path(tmpdir)

    # write file to tmp dir
    (input_base_dir / input_filename).write_text("Hello, world!")

    # mock typer launch
    called_urls = []
    mock_launch = monkeypatch.setattr(typer, "launch", lambda url: called_urls.append(url))

    # call fn
    observed_result = open_video_file(input_filename, input_base_dir)

    assert observed_result == True


def test_open_video_file_handles_not_found(tmpdir, monkeypatch):
    # setup inputs
    input_filename = "test.txt"
    input_base_dir = Path(tmpdir)

    # call fn
    observed_result = open_video_file(input_filename, input_base_dir)

    assert observed_result == False