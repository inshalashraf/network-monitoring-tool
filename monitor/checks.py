"""Basic host and TCP port availability checks."""

from dataclasses import dataclass
import socket
import time
from typing import Optional


@dataclass
class CheckResult:
    target: str
    is_available: bool
    response_time_ms: Optional[float]
    error: Optional[str] = None


def check_host(host: str, timeout: float = 3.0) -> CheckResult:
    """Check whether a hostname resolves and accepts a TCP connection on port 443 or 80.

    HTTPS (443) is tried first, then HTTP (80). This is a TCP reachability
    check, not a full HTTP request or an ICMP ping.
    """
    if not host or not host.strip():
        raise ValueError("host must not be empty")
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")

    clean_host = host.strip()
    last_error = None
    for port in (443, 80):
        started = time.perf_counter()
        try:
            with socket.create_connection((clean_host, port), timeout=timeout):
                elapsed = (time.perf_counter() - started) * 1000
                return CheckResult(clean_host, True, round(elapsed, 2))
        except OSError as exc:
            last_error = str(exc)

    return CheckResult(clean_host, False, None, last_error or "Connection failed")


def check_tcp_port(host: str, port: int, timeout: float = 3.0) -> CheckResult:
    """Check whether a TCP port is accepting connections on a host."""
    if not host or not host.strip():
        raise ValueError("host must not be empty")
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")

    clean_host = host.strip()
    started = time.perf_counter()
    try:
        with socket.create_connection((clean_host, port), timeout=timeout):
            elapsed = (time.perf_counter() - started) * 1000
            return CheckResult(f"{clean_host}:{port}", True, round(elapsed, 2))
    except OSError as exc:
        return CheckResult(f"{clean_host}:{port}", False, None, str(exc))
