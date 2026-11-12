"""A dependency-free local dashboard for network check history."""

import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer

from .history import get_recent_checks, get_summaries


def render_dashboard(database, target_filter="", status_filter="all"):
    """Build a refreshable HTML dashboard, optionally filtering recent checks."""
    summaries = get_summaries(database)
    recent = get_recent_checks(database, 50)
    target_filter = target_filter.strip()
    if target_filter:
        recent = [item for item in recent if item["target"] == target_filter]
    if status_filter == "up":
        recent = [item for item in recent if item["is_available"]]
    elif status_filter == "down":
        recent = [item for item in recent if not item["is_available"]]
    else:
        status_filter = "all"
    total_checks = sum(item["checks"] for item in summaries)
    total_available = sum(item["available"] for item in summaries)
    overall_uptime = (total_available / total_checks * 100) if total_checks else 0

    summary_rows = []
    for item in summaries:
        average = item["average_response_time_ms"]
        latency = f"{average:.2f} ms" if average is not None else "n/a"
        summary_rows.append(
            "<tr>"
            f"<td>{escape(item['target'])}</td>"
            f"<td>{item['uptime_percentage']:.2f}%</td>"
            f"<td>{item['available']} / {item['checks']}</td>"
            f"<td>{latency}</td>"
            "</tr>"
        )

    recent_rows = []
    for item in recent:
        status = "UP" if item["is_available"] else "DOWN"
        latency = (
            f"{item['response_time_ms']:.2f} ms"
            if item["response_time_ms"] is not None else "n/a"
        )
        recent_rows.append(
            "<tr>"
            f"<td>{escape(item['checked_at'])}</td>"
            f"<td>{escape(item['target'])}</td>"
            f"<td><span class='status {'up' if item['is_available'] else 'down'}'>{status}</span></td>"
            f"<td>{latency}</td>"
            f"<td>{escape(item['error'] or '-')}</td>"
            "</tr>"
        )

    summary_body = "".join(summary_rows) or "<tr><td colspan='4'>No checks recorded yet.</td></tr>"
    recent_body = "".join(recent_rows) or "<tr><td colspan='5'>No checks match these filters.</td></tr>"
    target_options = ["<option value=''>All targets</option>"]
    for item in summaries:
        selected = " selected" if item["target"] == target_filter else ""
        target_options.append(
            f"<option value='{escape(item['target'], quote=True)}'{selected}>"
            f"{escape(item['target'])}</option>"
        )
    status_options = []
    for value, label in (("all", "All statuses"), ("up", "UP only"), ("down", "DOWN only")):
        selected = " selected" if status_filter == value else ""
        status_options.append(f"<option value='{value}'{selected}>{label}</option>")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="30">
<title>Network Monitor Dashboard</title>
<style>
:root {{ color-scheme: light; font-family: Arial, sans-serif; background: #f4f6f8; color: #17202a; }}
body {{ max-width: 1100px; margin: 36px auto; padding: 0 18px; }}
header {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }}
h1 {{ margin-bottom: 6px; }} .muted {{ color: #65717d; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(190px,1fr)); gap: 14px; margin: 24px 0; }}
.card, section {{ background: white; border: 1px solid #e1e6eb; border-radius: 10px; padding: 18px; }}
.value {{ font-size: 27px; font-weight: 700; margin-top: 8px; }}
section {{ margin: 16px 0; overflow-x: auto; }} table {{ width: 100%; border-collapse: collapse; text-align: left; }}
th,td {{ padding: 11px 10px; border-bottom: 1px solid #edf0f2; vertical-align: top; }}
th {{ color: #536170; font-size: 13px; }} .status {{ font-weight: 700; }}
.up {{ color: #16834a; }} .down {{ color: #c0392b; }}
footer {{ margin: 20px 0; font-size: 13px; color: #65717d; }}
.filters {{ display: flex; align-items: end; flex-wrap: wrap; gap: 12px; margin: 12px 0 18px; }}
.filters label {{ display: grid; gap: 5px; color: #536170; font-size: 13px; }}
.filters select, .filters button {{ padding: 8px 10px; border: 1px solid #ccd4dc; border-radius: 6px; background: white; }}
.filters a {{ padding: 8px 0; color: #245b91; }}
</style>
</head>
<body>
<header><div><h1>Network Monitor</h1><div class="muted">Local availability and performance history</div></div>
<div class="muted">Refreshes every 30 seconds</div></header>
<div class="cards">
<div class="card"><div class="muted">Targets monitored</div><div class="value">{len(summaries)}</div></div>
<div class="card"><div class="muted">Total checks</div><div class="value">{total_checks}</div></div>
<div class="card"><div class="muted">Overall uptime</div><div class="value">{overall_uptime:.2f}%</div></div>
</div>
<section><h2>Target summary</h2><table><thead><tr><th>Target</th><th>Uptime</th><th>Successful checks</th><th>Avg. latency</th></tr></thead>
<tbody>{summary_body}</tbody></table></section>
<section><h2>Recent checks</h2>
<form method="get" action="/" class="filters">
<label>Target <select name="target">{''.join(target_options)}</select></label>
<label>Status <select name="status">{''.join(status_options)}</select></label>
<button type="submit">Apply filters</button>
<a href="/">Clear</a>
</form>
<table><thead><tr><th>Checked at (UTC)</th><th>Target</th><th>Status</th><th>Latency</th><th>Error</th></tr></thead>
<tbody>{recent_body}</tbody></table></section>
<footer>Dashboard reads the local SQLite history only. It does not start checks by itself. Keep this server bound to localhost unless you intentionally configure network access.</footer>
</body></html>"""


def main():
    parser = argparse.ArgumentParser(description="Start the local network monitoring dashboard.")
    parser.add_argument("--database", default="network_history.db", help="SQLite history database path")
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind (default: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Dashboard port (default: 8000)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            from urllib.parse import parse_qs, urlparse

            parsed = urlparse(self.path)
            if parsed.path not in ("/", "/index.html"):
                self.send_error(404, "Page not found")
                return
            query = parse_qs(parsed.query)
            target_filter = query.get("target", [""])[0]
            status_filter = query.get("status", ["all"])[0]
            if status_filter not in ("all", "up", "down"):
                status_filter = "all"
            page = render_dashboard(args.database, target_filter, status_filter).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)

        def log_message(self, format_string, *values):
            print(f"[dashboard] {values[0]}")

    server = HTTPServer((args.host, args.port), DashboardHandler)
    print(f"Dashboard running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
