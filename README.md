# Network Monitoring Tool

A Python utility for checking host availability, testing TCP ports, measuring connection response time, and reviewing local monitoring history in a browser dashboard.

## Features

- Check host reachability by attempting HTTPS (port 443), then HTTP (port 80).
- Check a specific TCP port.
- Measure successful TCP connection time in milliseconds.
- Save every check to a local SQLite history database.
- Calculate per-target uptime percentages and average successful latency.
- View overall uptime, target summaries, and the 50 most recent checks in a local web dashboard.
- Configure connection timeouts and the dashboard host/port.
- Run automated unit tests using Python's standard library.

> Host checks use TCP connectivity, not ICMP ping or a full HTTP request. A host may be online while both tested ports are blocked.

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

Set a custom timeout and history database:

```bash
python -m monitor.cli example.com --timeout 5 --history data/network_history.db
```

Each run records its results in SQLite and prints a per-target historical summary.

## Local dashboard

Start the dashboard:

```bash
python -m monitor.dashboard
```

Open **http://127.0.0.1:8000** in your browser. The dashboard displays:

- Number of monitored targets and total checks
- Overall uptime percentage
- Per-target uptime, successful check count, and average latency
- The 50 most recent results, including failures and error messages

Use the same database file as the CLI:

```bash
python -m monitor.dashboard --database network_history.db --port 8000
```

The dashboard refreshes every 30 seconds. It reads history only; run the CLI to perform new checks. By default, the server binds to localhost so the dashboard is not exposed to your network.

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
│   ├── cli.py
│   ├── dashboard.py
│   └── history.py
├── tests/
│   ├── test_checks.py
│   ├── test_dashboard.py
│   └── test_history.py
└── .github/workflows/tests.yml
```

## Roadmap

- [x] Host and TCP port checks
- [x] Connection response-time measurement
- [x] Command-line interface
- [x] Unit tests for core checks
- [x] SQLite monitoring history
- [x] Uptime and latency summaries
- [x] Local browser dashboard
- [ ] Continuous scheduled monitoring
- [ ] Dashboard charts and filtering

## Scope and safety

Use this tool only to monitor systems and networks you own or are authorised to test. It performs basic availability checks; it is not a vulnerability scanner or a substitute for a production monitoring platform.
