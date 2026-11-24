from datetime import datetime, timedelta, timezone
from lapiplan.subscription import trial_status

def test_trial_first_launch(tmp_path):
    when = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)
    path = tmp_path / "trial.db"
    result = trial_status(path, when)
    assert result["active"]
    assert result["days_left"] == 30
    assert result["price_pln"] == 14.99
    assert trial_status(path, when + timedelta(days=29))["active"]
    assert not trial_status(path, when + timedelta(days=30))["active"]
    assert not trial_status(path, when + timedelta(days=50))["active"]

def test_trial_uses_aware_datetime(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        trial_status(tmp_path / "trial.db", datetime(2026, 11, 17))
