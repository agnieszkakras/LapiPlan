"""SQLite persistence. All SQL writes use parameters; foreign keys are enabled."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .logic import validate_event

DEFAULT_DB = Path(os.environ.get("LAPIPLAN_DB", "data/lapiplan.sqlite3"))


@contextmanager
def connection(db_path: str | Path | None = None):
    path = Path(db_path) if db_path is not None else DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(path))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db(db_path=None):
    with connection(db_path) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS children (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          nickname TEXT NOT NULL,
          birthdate TEXT NOT NULL,
          focus_minutes INTEGER NOT NULL CHECK(focus_minutes BETWEEN 5 AND 180),
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
          weekday INTEGER NOT NULL CHECK(weekday BETWEEN 0 AND 6),
          start_time TEXT NOT NULL, end_time TEXT NOT NULL,
          title TEXT NOT NULL, kind TEXT NOT NULL,
          notes TEXT DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_events_child_day ON events(child_id, weekday);
        CREATE TABLE IF NOT EXISTS study_sessions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
          session_date TEXT NOT NULL,
          subject TEXT NOT NULL,
          minutes INTEGER NOT NULL CHECK(minutes BETWEEN 1 AND 600),
          confidence INTEGER NOT NULL CHECK(confidence BETWEEN 1 AND 5),
          notes TEXT DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_sessions_child_date ON study_sessions(child_id, session_date);
        CREATE TABLE IF NOT EXISTS tasks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
          title TEXT NOT NULL, due_date TEXT NOT NULL,
          subject TEXT NOT NULL DEFAULT '',
          completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0, 1))
        );
        CREATE INDEX IF NOT EXISTS idx_tasks_child_due ON tasks(child_id, due_date);
        """)


def rows(sql: str, params=(), db_path=None) -> list[dict]:
    with connection(db_path) as db:
        return [dict(row) for row in db.execute(sql, params).fetchall()]


def execute(sql: str, params=(), db_path=None) -> int:
    with connection(db_path) as db:
        cur = db.execute(sql, params)
        return int(cur.lastrowid)


def list_children(db_path=None):
    return rows("SELECT * FROM children ORDER BY nickname COLLATE NOCASE, id", db_path=db_path)


def add_child(nickname: str, birthdate: str, focus_minutes: int, db_path=None):
    if not nickname.strip() or not 5 <= focus_minutes <= 180:
        raise ValueError("Invalid child profile")
    return execute("INSERT INTO children(nickname, birthdate, focus_minutes) VALUES(?,?,?)",
                   (nickname.strip(), birthdate, focus_minutes), db_path)


def delete_child(child_id: int, db_path=None):
    execute("DELETE FROM children WHERE id=?", (child_id,), db_path)


def list_events(child_id: int, db_path=None):
    return rows("SELECT * FROM events WHERE child_id=? ORDER BY weekday,start_time,end_time", (child_id,), db_path)


def add_event(child_id: int, weekday: int, start: str, end: str, title: str, kind: str, notes="", db_path=None):
    from .logic import EVENT_KINDS
    validate_event(weekday, start, end)
    if not title.strip() or kind not in EVENT_KINDS:
        raise ValueError("Invalid event")
    return execute("INSERT INTO events(child_id,weekday,start_time,end_time,title,kind,notes) VALUES(?,?,?,?,?,?,?)",
                   (child_id, weekday, start, end, title.strip(), kind, notes.strip()), db_path)


def delete_event(event_id: int, child_id: int, db_path=None):
    execute("DELETE FROM events WHERE id=? AND child_id=?", (event_id, child_id), db_path)


def add_session(child_id: int, session_date: str, subject: str, minutes: int, confidence: int, notes="", db_path=None):
    if not subject.strip() or not 1 <= minutes <= 600 or not 1 <= confidence <= 5:
        raise ValueError("Invalid study session")
    return execute("INSERT INTO study_sessions(child_id,session_date,subject,minutes,confidence,notes) VALUES(?,?,?,?,?,?)",
                   (child_id, session_date, subject.strip(), minutes, confidence, notes.strip()), db_path)


def list_sessions(child_id: int, start: str | None = None, end: str | None = None, db_path=None):
    if start is not None and end is not None:
        return rows("SELECT * FROM study_sessions WHERE child_id=? AND session_date BETWEEN ? AND ? ORDER BY session_date DESC,id DESC", (child_id, start, end), db_path)
    return rows("SELECT * FROM study_sessions WHERE child_id=? ORDER BY session_date DESC,id DESC", (child_id,), db_path)


def add_task(child_id: int, title: str, due_date: str, subject: str = "", db_path=None):
    if not title.strip():
        raise ValueError("Task title required")
    return execute("INSERT INTO tasks(child_id,title,due_date,subject) VALUES(?,?,?,?)",
                   (child_id, title.strip(), due_date, subject.strip()), db_path)


def list_tasks(child_id: int, db_path=None):
    return rows("SELECT * FROM tasks WHERE child_id=? ORDER BY completed,due_date,id", (child_id,), db_path)


def set_task_completed(task_id: int, child_id: int, completed: bool, db_path=None):
    execute("UPDATE tasks SET completed=? WHERE id=? AND child_id=?", (int(completed), task_id, child_id), db_path)


def delete_task(task_id: int, child_id: int, db_path=None):
    execute("DELETE FROM tasks WHERE id=? AND child_id=?", (task_id, child_id), db_path)


def init_assessments(db_path=None):
    """Non-destructive migration for existing LapiPlan SQLite databases."""
    with connection(db_path) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS assessments (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
          event_date TEXT NOT NULL,
          event_time TEXT NOT NULL DEFAULT '',
          category TEXT NOT NULL CHECK(category IN
            ('quiz','test','class_test','group_project','olympiad','presentation','deadline','other')),
          title TEXT NOT NULL,
          subject TEXT NOT NULL DEFAULT '',
          notes TEXT NOT NULL DEFAULT '',
          completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)),
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_assessments_child_date ON assessments(child_id,event_date);
        """)


def list_assessments(child_id: int, start: str | None = None, end: str | None = None, db_path=None):
    sql="SELECT * FROM assessments WHERE child_id=?"
    params=[child_id]
    if start is not None:
        sql += " AND event_date>=?"
        params.append(start)
    if end is not None:
        sql += " AND event_date<=?"
        params.append(end)
    return rows(sql+" ORDER BY event_date,event_time,id",tuple(params),db_path)


def add_assessment(child_id:int,event_date:str,category:str,title:str,subject:str="",event_time:str="",notes:str="",db_path=None):
    from datetime import date as _date, time as _time
    _date.fromisoformat(event_date)
    if event_time:
        _time.fromisoformat(event_time)
    categories={'quiz','test','class_test','group_project','olympiad','presentation','deadline','other'}
    if category not in categories or not title.strip():
        raise ValueError('Invalid assessment')
    return execute("INSERT INTO assessments(child_id,event_date,category,title,subject,event_time,notes) VALUES(?,?,?,?,?,?,?)",
        (child_id,event_date,category,title.strip(),subject.strip(),event_time,notes.strip()),db_path)


def set_assessment_completed(assessment_id:int,child_id:int,completed:bool,db_path=None):
    execute("UPDATE assessments SET completed=? WHERE id=? AND child_id=?",(int(completed),assessment_id,child_id),db_path)


def delete_assessment(assessment_id:int,child_id:int,db_path=None):
    execute("DELETE FROM assessments WHERE id=? AND child_id=?",(assessment_id,child_id),db_path)
