from datetime import date

from backend.app.workers.due_date_worker import run_due_date_worker


def test_due_date_worker_accepts_explicit_date(session):
    assert run_due_date_worker(session, date(2026, 10, 2)) >= 0
