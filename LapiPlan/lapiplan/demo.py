"""Synthetic sample timetable. No real children's data."""
from . import db

DEMO_EVENTS = [
    (0, "08:00", "13:30", "School / Szkoła", "school"),
    (1, "08:00", "14:15", "School / Szkoła", "school"),
    (2, "08:00", "13:30", "School / Szkoła", "school"),
    (3, "08:00", "14:15", "School / Szkoła", "school"),
    (4, "08:00", "12:40", "School / Szkoła", "school"),
    (0, "16:30", "17:15", "Swimming / Basen", "extracurricular"),
    (2, "16:00", "16:45", "Art club / Plastyka", "extracurricular"),
    (1, "17:30", "18:00", "Math revision / Matematyka", "study"),
    (3, "17:00", "17:30", "Reading / Czytanie", "study"),
    (5, "11:00", "13:00", "Family walk / Spacer", "family"),
    (6, "15:00", "17:00", "Free time / Czas wolny", "free"),
]


def seed_schedule(child_id: int, db_path=None) -> bool:
    if db.list_events(child_id, db_path):
        return False
    for weekday, start, end, title, kind in DEMO_EVENTS:
        db.add_event(child_id, weekday, start, end, title, kind, db_path=db_path)
    return True
