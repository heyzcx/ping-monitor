# ping-monitor

Ping a host and log latency and packet loss to CSV. Zero-dependency Python CLI — just the standard library plus the system `ping` command.

## Install

Requires Python 3.8+ and a system `ping` binary (present on Linux and macOS).

```bash
git clone https://github.com/mrzhoucx/ping-monitor.git
cd ping-monitor
```

## Usage

```bash
# Ping a host 4 times (default) and append results to ping-log.csv
python3 ping_monitor.py example.com

# 10 pings, 2 seconds apart, custom log file
python3 ping_monitor.py 8.8.8.8 -c 10 -i 2 -o my-log.csv

# Print the summary only, without writing a CSV file
python3 ping_monitor.py 127.0.0.1 --summary-only
```

## Example output

```
[1/4] 8.8.8.8: 12.34 ms
[2/4] 8.8.8.8: 11.87 ms
[3/4] 8.8.8.8: 12.01 ms
[4/4] 8.8.8.8: 12.45 ms

--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 received, 0.0% packet loss
rtt min/avg/max = 11.87/12.17/12.45 ms
results appended to ping-log.csv
```

## CSV format

`ping-log.csv` gets one row per ping:

| timestamp | host | seq | latency_ms |
| --- | --- | --- | --- |
| 2026-11-06T15:00:00+00:00 | 8.8.8.8 | 1 | 12.34 |
| 2026-11-06T15:00:01+00:00 | 8.8.8.8 | 2 | 11.87 |

A lost packet is recorded with an empty `latency_ms`. The exit code is `0` when at least one reply was received, `1` when all packets were lost — handy for cron jobs and uptime scripts.

## Options

| Flag | Default | Description |
| --- | --- | --- |
| `-c, --count` | 4 | Number of pings to send |
| `-i, --interval` | 1 | Seconds between pings |
| `-o, --output` | ping-log.csv | CSV file to append results to |
| `--summary-only` | — | Print the summary without writing the CSV |
