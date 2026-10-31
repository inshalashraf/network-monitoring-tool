import unittest
from unittest.mock import patch

from monitor.checks import CheckResult, check_host, check_tcp_port


class NetworkCheckTests(unittest.TestCase):
    @patch("monitor.checks.socket.create_connection")
    def test_tcp_port_available(self, connect):
        connect.return_value.__enter__.return_value = None
        result = check_tcp_port("localhost", 8080)
        self.assertTrue(result.is_available)
        self.assertEqual(result.target, "localhost:8080")
        self.assertIsNotNone(result.response_time_ms)

    @patch("monitor.checks.socket.create_connection", side_effect=OSError("connection refused"))
    def test_tcp_port_unavailable(self, connect):
        result = check_tcp_port("localhost", 8080)
        self.assertFalse(result.is_available)
        self.assertEqual(result.error, "connection refused")
        self.assertIsNone(result.response_time_ms)

    @patch("monitor.checks.socket.create_connection")
    def test_host_tries_https_first(self, connect):
        connect.return_value.__enter__.return_value = None
        result = check_host("example.com")
        self.assertTrue(result.is_available)
        self.assertEqual(connect.call_args.args[0], ("example.com", 443))

    def test_invalid_port_is_rejected(self):
        with self.assertRaises(ValueError):
            check_tcp_port("localhost", 70000)

    def test_empty_host_is_rejected(self):
        with self.assertRaises(ValueError):
            check_host("  ")

    def test_non_positive_timeout_is_rejected(self):
        with self.assertRaises(ValueError):
            check_tcp_port("localhost", 80, 0)


if __name__ == "__main__":
    unittest.main()
