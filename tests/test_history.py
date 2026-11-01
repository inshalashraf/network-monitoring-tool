import tempfile
import unittest
from pathlib import Path

from monitor.checks import CheckResult
from monitor.history import get_summaries, record_result


class HistoryTests(unittest.TestCase):
    def test_records_checks_and_calculates_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "history.sqlite3"
            record_result(CheckResult("server-a", True, 10.0), database)
            record_result(CheckResult("server-a", False, None, "refused"), database)
            record_result(CheckResult("server-a", True, 20.0), database)
            summary = get_summaries(database)
            self.assertEqual(len(summary), 1)
            self.assertEqual(summary[0]["checks"], 3)
            self.assertEqual(summary[0]["available"], 2)
            self.assertEqual(summary[0]["uptime_percentage"], 66.67)
            self.assertEqual(summary[0]["average_response_time_ms"], 15.0)

    def test_missing_database_has_empty_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(get_summaries(Path(directory) / "missing.db"), [])


if __name__ == "__main__":
    unittest.main()
