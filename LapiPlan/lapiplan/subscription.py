"""Local-first 30 day trial demonstration, NOT a production billing system.

Production SaaS needs authenticated user accounts, server-side entitlement checks,
verified payment provider webhooks and privacy/security review.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .db import connection

TRIAL_DAYS = 30
PRICE_PLN = 14.99

def trial_status(db_path: str | Path | None = None, now: datetime | None = None) -> dict:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("Time must be timezone-aware")
    current = current.astimezone(timezone.utc)
    with connection(db_path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        row = db.execute("SELECT value FROM app_settings WHERE key = 'trial_started_at'").fetchone()
        if row is None:
            started = current
            db.execute("INSERT INTO app_settings(key, value) VALUES (?, ?)", ('trial_started_at', current.isoformat()))
        else:
            started = datetime.fromisoformat(row['value']).astimezone(timezone.utc)
    expires_at = started + timedelta(days=TRIAL_DAYS)
    remaining = max(0, (expires_at.date() - current.date()).days)
    return {'started_at': started, 'expires_at': expires_at, 'active': current < expires_at,
            'days_left': remaining, 'price_pln': PRICE_PLN}
