"""Command-line interface for the network monitoring tool."""

import argparse

from .checks import check_host, check_tcp_port
from .history import get_summaries, record_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Check host and TCP port availability.")
    parser.add_argument("host", help="Hostname or IP address to check")
    parser.add_argument("--port", type=int, help="Also check this TCP port (1-65535)")
    parser.add_argument("--timeout", type=float, default=3.0, help="Connection timeout in seconds (default: 3)")
    parser.add_argument("--history", default="network_history.db", help="SQLite history database path")
    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    host_result = check_host(args.host, args.timeout)
    print_result(host_result)
    record_result(host_result, args.history)

    if args.port is not None:
        try:
            port_result = check_tcp_port(args.host, args.port, args.timeout)
        except ValueError as exc:
            parser.error(str(exc))
        print_result(port_result)
        record_result(port_result, args.history)

    print("\nHistorical summary:")
    for item in get_summaries(args.history):
        average = item["average_response_time_ms"]
        latency = f"{average:.2f} ms" if average is not None else "n/a"
        print(f"  {item['target']}: {item['uptime_percentage']:.2f}% uptime "
              f"({item['available']}/{item['checks']} checks), average latency {latency}")


def print_result(result) -> None:
    status = "UP" if result.is_available else "DOWN"
    latency = f"{result.response_time_ms:.2f} ms" if result.response_time_ms is not None else "n/a"
    print(f"[{status}] {result.target} | response time: {latency}")
    if result.error:
        print(f"      reason: {result.error}")


if __name__ == "__main__":
    main()
