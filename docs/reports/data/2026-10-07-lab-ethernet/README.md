# Ethernet between the three lab machines, 7 October 2026

On Wed 7 Oct 2026 the owner asked whether aifoundry1, aifoundry2 and aifoundry3, newly cabled together, are really
connected over Ethernet, and how fast. They are: every port is up at 1 Gb/s full duplex and each machine reaches the
other two. Between any two machines one TCP stream moves **928.5 Mb/s** (the most a gigabit link carries),
against a median **31.0 Mb/s** over WiFi and 29.9 Mb/s over Tailscale (which between these
machines runs directly over the WiFi network). A round trip takes **0.26 ms** on the cable, 5.9 ms
over WiFi. The published page is [2026-10-07-lab-ethernet.html](../../2026-10-07-lab-ethernet.html).

**Nothing uses the cable yet.** The wired ports have no IPv4 address: nothing on that network runs DHCP, so each
machine's NetworkManager tries for 45 s four times, waits 5 minutes and repeats (`nm-restarts.txt`). The tests used the
ports' IPv6 link-local addresses, which exist only during those tries, and waited for both ends to have one.

| File | What it is |
|---|---|
| `netbench.py` | the tool: a Python TCP sender/receiver (`serve`, `up`, `down`, `rtt`); 8 s per test after a 1 s warm-up that is discarded, counted by the receiver; one JSON line per test |
| `drive.py` | round 1, run from aifoundry1: every pair over Ethernet, WiFi and Tailscale (round trip, each direction, and 4 streams on Ethernet). Reads the machines' addresses from `hosts.json`, which is kept out of this public repository |
| `phase2.py` | round 2: both directions of one link at once, and all three links at once |
| `phase3.py` | round 3: the two directions whose first run was slow, run again |
| `phase4.py` | round 4: all three links at once, watching each port's address (`ip monitor`) so a run hit by a NetworkManager restart is flagged |
| `results.jsonl` | every result, in time order (`client`, `server`, `path` eth/wifi/ts, `test`, `Mbps`, round trip in µs, `tries`, `t`); addresses removed |
| `nm-restarts.txt` | the three machines' NetworkManager log lines for the wired port, 15:00 onwards: each `failed for connection` is a moment the port's address dropped |
| `build_report.py`, `report.css` | build the published page from `results.jsonl` and `nm-restarts.txt`: `python3 build_report.py results.jsonl report.css out.html nm-restarts.txt` |

## Findings

- **Ethernet, one stream:** 928.5 Mb/s in every direction (best run per direction); 4 streams give the same
  total, so the link is the limit.
- **Both directions at once:** 925.0, 925.3 Mb/s: full duplex.
- **All three links at once:** 925.0, 925.0, 925.0 Mb/s, with no address change on any port during the run.
- **Slow runs:** every Ethernet run below 900 Mb/s overlapped a NetworkManager restart (by `nm-restarts.txt`, or
  seen by `phase4.py`'s address watch), and every run that no restart touched ran at full speed. A restart on one
  machine sometimes slowed the link between the other two as well, and it does not bounce the cable (carrier counters
  unchanged). No port counted an error or a drop; MTU 1500.
- **Why 1 Gb/s:** each port is an Aquantia AQC107 (10 GbE, also 2.5 and 5) and offers every speed; all three links
  settled at 1 Gb/s, so the switch or the cabling is gigabit.
- **ssh over the wired address** was refused (no key in `~/.ssh/authorized_keys`): between the machines, ssh works only
  through Tailscale SSH, on the tailnet.

## To rerun

Copy `netbench.py` to `~/claude/work/netbench/` on all three machines, start `python3 netbench.py serve` on each,
write `hosts.json` on aifoundry1 and run `python3 drive.py` there. Once the wired ports have fixed addresses, the
Ethernet tests no longer need to wait for NetworkManager.

