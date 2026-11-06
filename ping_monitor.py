#!/usr/bin/env python3
"""Ping a host and log latency / packet loss to CSV.

Usage:
    python3 ping_monitor.py example.com
    python3 ping_monitor.py 8.8.8.8 -c 10 -i 1 -o ping-log.csv
    python3 ping_monitor.py 127.0.0.1 --summary-only

Options:
    -c, --count     number of pings to send (default: 4)
    -i, --interval  seconds between pings (default: 1)
    -o, --output    CSV file to append results to (default: ping-log.csv)
    --summary-only  print the summary but do not write the CSV file

The CSV has one row per ping: timestamp, host, sequence, latency_ms
(or empty when the packet was lost), plus a summary row is printed to
stdout with packets sent/received, loss %, and min/avg/max latency.
"""
import argparse
import csv
import datetime
import os
import re
import statistics
import subprocess
import sys

LATENCY_RE = re.compile(r"time[=<]([\d.]+)\s*ms")


def ping_once(host, timeout=5):
    """Send one ICMP echo and return latency in ms, or None if lost."""
    try:
        proc = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), host],
            capture_output=True, text=True, timeout=timeout + 2,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    match = LATENCY_RE.search(proc.stdout)
    return float(match.group(1)) if match else None


def main():
    parser = argparse.ArgumentParser(description="Ping a host and log results to CSV.")
    parser.add_argument("host", help="hostname or IP address to ping")
    parser.add_argument("-c", "--count", type=int, default=4, help="number of pings (default: 4)")
    parser.add_argument("-i", "--interval", type=float, default=1, help="seconds between pings (default: 1)")
    parser.add_argument("-o", "--output", default="ping-log.csv", help="CSV file to append to (default: ping-log.csv)")
    parser.add_argument("--summary-only", action="store_true", help="do not write the CSV file")
    args = parser.parse_args()

    if args.count < 1:
        parser.error("count must be at least 1")

    rows = []
    for seq in range(1, args.count + 1):
        latency = ping_once(args.host)
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        rows.append((ts, args.host, seq, latency))
        status = f"{latency:.2f} ms" if latency is not None else "timeout"
        print(f"[{seq}/{args.count}] {args.host}: {status}")
        if seq < args.count and args.interval > 0:
            import time
            time.sleep(args.interval)

    received = [r[3] for r in rows if r[3] is not None]
    sent = len(rows)
    lost = sent - len(received)
    loss_pct = lost / sent * 100
    print(f"\n--- {args.host} ping statistics ---")
    print(f"{sent} packets transmitted, {len(received)} received, {loss_pct:.1f}% packet loss")
    if received:
        print(f"rtt min/avg/max = {min(received):.2f}/{statistics.mean(received):.2f}/{max(received):.2f} ms")
    else:
        print("no replies received")

    if not args.summary_only:
        write_header = not os.path.exists(args.output)
        with open(args.output, "a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["timestamp", "host", "seq", "latency_ms"])
            for ts, host, seq, latency in rows:
                writer.writerow([ts, host, seq, "" if latency is None else f"{latency:.2f}"])
        print(f"results appended to {args.output}")
    return 0 if received else 1


if __name__ == "__main__":
    sys.exit(main())
