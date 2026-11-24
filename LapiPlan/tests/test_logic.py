from datetime import date
import pytest
from lapiplan.logic import age_on, suggested_focus_minutes, overlaps, conflicts, week_bounds, completion_rate


def test_age_before_and_after_birthday():
    assert age_on("2012-12-10", date(2026, 11, 17)) == 13
    assert age_on("2012-12-10", date(2026, 12, 10)) == 14


def test_focus_defaults():
    assert suggested_focus_minutes(8) == 20
    assert suggested_focus_minutes(14) == 40


def test_overlap_and_touching_boundaries():
    assert overlaps("09:00", "10:00", "09:30", "11:00")
    assert not overlaps("09:00", "10:00", "10:00", "11:00")


def test_schedule_conflicts():
    events = [{"id": 1, "weekday": 0, "start_time": "08:00", "end_time": "14:00", "title": "School"}]
    assert len(conflicts(events, 0, "13:30", "14:30")) == 1
    assert conflicts(events, 1, "13:30", "14:30") == []
    with pytest.raises(ValueError):
        conflicts(events, 0, "17:00", "16:00")


def test_week_bounds():
    assert week_bounds(date(2026, 11, 17)) == (date(2026, 11, 16), date(2026, 11, 22))


def test_completion():
    assert completion_rate(1, 4) == 25.0
    assert completion_rate(0, 0) == 0.0
