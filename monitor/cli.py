"""Command-line interface for the network monitoring tool."""

import argparse

from .checks import check_host, check_tcp_port


def main() -> None:
    parser = argparse.ArgumentParser(description="Check host and TCP port availability.")
    parser.add_argument("host", help="Hostname or IP address to check")
    parser.add_argument("--port", type=int, help="Also check this TCP port (1-65535)")
    parser.add_argument("--timeout", type=float, default=3.0, help="Connection timeout in seconds (default: 3)")
    args = parser.parse_args()

    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    host_result = check_host(args.host, args.timeout)
    print_result(host_result)

    if args.port is not None:
        try:
            port_result = check_tcp_port(args.host, args.port, args.timeout)
        except ValueError as exc:
            parser.error(str(exc))
        print_result(port_result)


def print_result(result) -> None:
    status = "UP" if result.is_available else "DOWN"
    latency = f"{result.response_time_ms:.2f} ms" if result.response_time_ms is not None else "n/a"
    print(f"[{status}] {result.target} | response time: {latency}")
    if result.error:
        print(f"      reason: {result.error}")


if __name__ == "__main__":
    main()
