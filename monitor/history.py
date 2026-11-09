"""SQLite-backed history and uptime/latency summaries."""
import sqlite3
from pathlib import Path


def _connect(database):
    target = Path(database)
    if target.parent != Path("."):
        target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.execute(
        """CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            is_available INTEGER NOT NULL,
            response_time_ms REAL,
            error TEXT,
            checked_at TEXT NOT NULL
        )"""
    )
    return connection


def record_result(result, database="network_history.db"):
    """Persist one network check result and return its inserted row ID."""
    with _connect(database) as connection:
        cursor = connection.execute(
            """INSERT INTO checks (target, is_available, response_time_ms, error, checked_at)
               VALUES (?, ?, ?, ?, datetime('now'))""",
            (result.target, int(result.is_available), result.response_time_ms, result.error),
        )
        return cursor.lastrowid


def get_summaries(database="network_history.db"):
    """Return per-target check count, uptime percentage, and average successful latency."""
    target = Path(database)
    if not target.exists():
        return []
    with _connect(target) as connection:
        rows = connection.execute(
            """SELECT target, COUNT(*), SUM(is_available),
                      AVG(CASE WHEN is_available = 1 THEN response_time_ms END)
               FROM checks GROUP BY target ORDER BY target"""
        ).fetchall()
    return [
        {
            "target": row[0],
            "checks": row[1],
            "available": row[2],
            "uptime_percentage": round((row[2] / row[1]) * 100, 2),
            "average_response_time_ms": round(row[3], 2) if row[3] is not None else None,
        }
        for row in rows
    ]


def get_recent_checks(database="network_history.db", limit=50):
    """Return the newest check records, with a safe upper bound on the result size."""
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("limit must be a positive integer")
    target = Path(database)
    if not target.exists():
        return []
    with _connect(target) as connection:
        rows = connection.execute(
            """SELECT target, is_available, response_time_ms, error, checked_at
               FROM checks ORDER BY id DESC LIMIT ?""",
            (min(limit, 500),),
        ).fetchall()
    return [
        {
            "target": row[0],
            "is_available": bool(row[1]),
            "response_time_ms": row[2],
            "error": row[3],
            "checked_at": row[4],
        }
        for row in rows
    ]
