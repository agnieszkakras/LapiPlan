import sqlite3
import pytest
from lapiplan import db
from lapiplan.demo import seed_schedule


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "study.sqlite3"
    db.init_db(path)
    return path


def test_profiles_and_schedule(database):
    cid = db.add_child("Sample", "2014-03-10", 30, database)
    assert len(db.list_children(database)) == 1
    db.add_event(cid, 0, "08:00", "09:00", "School", "school", db_path=database)
    assert db.list_events(cid, database)[0]["title"] == "School"
    with pytest.raises(ValueError):
        db.add_event(cid, 0, "18:00", "17:00", "Invalid", "school", db_path=database)
    assert not seed_schedule(cid, database)
    db.delete_child(cid, database)
    assert not db.list_events(cid, database)


def test_study_and_tasks(database):
    cid = db.add_child("Test", "2010-09-01", 40, database)
    db.add_session(cid, "2026-11-17", "Math", 35, 4, db_path=database)
    assert db.list_sessions(cid, "2026-11-16", "2026-11-22", database)[0]["minutes"] == 35
    tid = db.add_task(cid, "Fractions", "2026-11-19", "Math", database)
    db.set_task_completed(tid, cid, True, database)
    assert db.list_tasks(cid, database)[0]["completed"] == 1
    db.delete_task(tid, cid, database)
    assert db.list_tasks(cid, database) == []


def test_demo(database):
    cid = db.add_child("Demo", "2012-01-01", 40, database)
    assert seed_schedule(cid, database)
    assert len(db.list_events(cid, database)) >= 10
