"""Pure functions for schedule validation, progress summaries and age hints."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta

DAYS = (0, 1, 2, 3, 4, 5, 6)
EVENT_KINDS = ("school", "extracurricular", "study", "family", "free", "other")


def age_on(birthday: str, on: date | None = None) -> int:
    """Calculate age on the selected date, with no dependency on locale."""
    born = date.fromisoformat(birthday)
    today = on or date.today()
    if born > today:
        raise ValueError("Date of birth cannot be in the future")
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def suggested_focus_minutes(age: int) -> int:
    """Editable product defaults; NOT health or education standards."""
    if age < 6:
        return 10
    if age <= 9:
        return 20
    if age <= 12:
        return 30
    if age <= 15:
        return 40
    return 50


def hhmm_to_minutes(value: str) -> int:
    parsed = time.fromisoformat(value)
    return parsed.hour * 60 + parsed.minute


def validate_event(day: int, start: str, end: str) -> None:
    if day not in DAYS:
        raise ValueError("Day must be an integer from 0 to 6")
    if hhmm_to_minutes(start) >= hhmm_to_minutes(end):
        raise ValueError("End time must be after start time")


def overlaps(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
    return max(hhmm_to_minutes(start_a), hhmm_to_minutes(start_b)) < min(
        hhmm_to_minutes(end_a), hhmm_to_minutes(end_b)
    )


def conflicts(events: list[dict], day: int, start: str, end: str, exclude_id: int | None = None) -> list[dict]:
    validate_event(day, start, end)
    return [
        event for event in events
        if int(event["weekday"]) == day
        and (exclude_id is None or int(event["id"]) != exclude_id)
        and overlaps(start, end, str(event["start_time"]), str(event["end_time"]))
    ]


def week_bounds(target: date) -> tuple[date, date]:
    monday = target - timedelta(days=target.weekday())
    return monday, monday + timedelta(days=6)


def completion_rate(done: int, total: int) -> float:
    return round(100.0 * done / total, 1) if total else 0.0


def duration_minutes(start: str, end: str) -> int:
    validate_event(0, start, end)
    return hhmm_to_minutes(end) - hhmm_to_minutes(start)


def parse_hhmm(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()
