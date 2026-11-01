# Network Monitoring Tool

A Python command-line utility for checking host availability, testing TCP ports, and measuring connection response time.

## Features

- Check host reachability by attempting HTTPS (port 443), then HTTP (port 80).
- Check a specific TCP port.
- Measure successful connection time in milliseconds.\n- Save each check to a local SQLite history database.\n- Show per-target uptime percentages and average successful latency.
- Report connection failures and their error messages.
- Configure the connection timeout.
- Run automated unit tests with Python's standard library.

> Host checks use TCP connectivity, not ICMP ping. A host may be online while both tested ports are blocked.

## Requirements

- Python 3.9 or later
- No third-party packages required

## Getting started

Clone the repository:

```bash
git clone https://github.com/inshalashraf/network-monitoring-tool.git
cd network-monitoring-tool
```

Check a host:

```bash
python -m monitor.cli example.com
```

Check a host and a specific TCP port:

```bash
python -m monitor.cli example.com --port 22
```

Set a custom timeout (in seconds):

```bash
python -m monitor.cli example.com --timeout 5
```

## Run tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
network-monitoring-tool/
├── monitor/
│   ├── __init__.py
│   ├── checks.py
│   └── cli.py
├── tests/
│   └── test_checks.py
└── README.md
```

## Roadmap

- [x] Basic host and TCP port checks
- [x] Connection response-time measurement
- [x] Command-line interface
- [x] Unit tests for core checks
- [ ] Save monitoring history in SQLite
- [ ] Add uptime and latency summaries
- [ ] Build a lightweight local dashboard

## Scope and safety

Use this tool only to monitor systems and networks you own or are authorised to test. It performs basic availability checks; it is not a vulnerability scanner or a substitute for a production monitoring platform.
