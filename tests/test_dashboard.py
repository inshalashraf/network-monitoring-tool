import tempfile
import unittest
from pathlib import Path

from monitor.checks import CheckResult
from monitor.dashboard import render_dashboard
from monitor.history import get_recent_checks, record_result


class DashboardTests(unittest.TestCase):
    def test_dashboard_shows_summary_and_recent_results(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "history.db"
            record_result(CheckResult("server-a", True, 12.5), database)
            record_result(CheckResult("server-b", False, None, "connection refused"), database)

            page = render_dashboard(database)

            self.assertIn("Network Monitor", page)
            self.assertIn("server-a", page)
            self.assertIn("server-b", page)
            self.assertIn("100.00%", page)
            self.assertIn("connection refused", page)
            self.assertIn("DOWN", page)

    def test_dashboard_handles_empty_database(self):
        with tempfile.TemporaryDirectory() as directory:
            page = render_dashboard(Path(directory) / "missing.db")
            self.assertIn("No checks recorded yet.", page)
            self.assertIn("0.00%", page)

    def test_recent_checks_are_newest_first_and_limited(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "history.db"
            record_result(CheckResult("first", True, 1.0), database)
            record_result(CheckResult("second", True, 2.0), database)
            recent = get_recent_checks(database, 1)
            self.assertEqual(len(recent), 1)
            self.assertEqual(recent[0]["target"], "second")

    def test_recent_check_limit_must_be_positive_integer(self):
        with self.assertRaises(ValueError):
            get_recent_checks("unused.db", 0)


if __name__ == "__main__":
    unittest.main()
