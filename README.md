# Network Monitoring Tool

A small Python utility for checking whether hosts and network services are reachable, measuring connection latency, and keeping a local record of monitoring results.

The project is being built in stages, starting with a command-line monitor before adding persistent history and a lightweight dashboard.

## Planned features

- Check whether a host or website responds.
- Measure connection time and report failures clearly.
- Check selected TCP ports (for example, 22, 80, 443, and 3306).
- Save check results with timestamps in SQLite.
- Summarise availability and response-time history.
- Provide a simple local dashboard once the monitoring core is stable.

## Project status

**In development.** Features will be added and documented as they are implemented. The initial version focuses on reliable host and port checks.

## Planned structure

```text
network-monitoring-tool/
├── monitor/
│   ├── __init__.py
│   ├── checks.py
│   └── ...
├── tests/
├── README.md
└── requirements.txt
```

## Getting started

Setup and usage instructions will be added with the first working release.

## Scope and safety

This tool is intended for monitoring systems and networks you own or are authorised to test. It performs basic availability checks; it is not a vulnerability scanner or a substitute for a production monitoring platform.

## License

A license will be selected before the project is published as a reusable release.
