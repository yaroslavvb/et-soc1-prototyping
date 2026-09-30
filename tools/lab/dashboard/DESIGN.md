# Lab dashboard: design

The owner's request (30 September 2026): "a nice interactive interface which lets me visualize the lab ... three
machines and four cards ... a high-level overview of the state of the machines and the state of the cards, and the
people using it ... automatic refresh ... the health of the cluster as well as the overall health of the people who
are using it ... make use of the scripts I've created ... I should be able to view this and use the utilities you
build up in this session to update the values."

And later that day (30 September, about 14:35 and 15:00): "it shouldn't be specific to me ... give a sense of how many
users are logged in, what they're doing, and whether the card is being used ... I want to see people using the cards
over the last 24 hours", and "aifoundry1 is dead but it's not reflected on the dashboard. The dashboard should be
modified to keep the status of the actual machine." So since 30 September the page is the same for everyone (the
collector's own account is one login among others), shows who is logged in and what they are doing in coarse
categories, reads each machine's card-use log (`et-usage`, `tools/lab/et-usage/`), and keeps each machine's own state
(up, down, unreachable, approval needed, rebooted) from Tailscale and ssh.

**What it is.** A collector on aifoundry2 reads the three hosts every 10 minutes (read-only: `/proc`, sysfs driver
counters, `et-who`, `et-usage`, `et-lab-health`, `et-lab-manifest`, nodewatch's logs, and locally `tailscale status`
for each machine's online flag), writes one JSON file under `~/.cache/lab-dashboard/`, bakes it into a single static page, and redeploys that
page to a **private** spacesheep space when something changed (or at least every 60 minutes). The spacesheep viewer
reloads open tabs on every deploy, so the page never fetches anything. `update.sh now` (or asking Claude) does the same
at once.

This design is for one build pass. Nothing here touches a card by default. The optional telemetry sample (§2.6) is
off unless it is switched on, and the main session takes the first real sample.

| File in `tools/lab/dashboard/` | Role |
|---|---|
| `DESIGN.md` | this file |
| `README.md` | usage, written in the build pass: the commands of §3 and §7, the privacy rules of §6 in short |
| `lab.json` | static lab facts: hosts, their cards, trees, telemetry binaries, card firmware and clock policy, known conditions (§1.6). No personal data |
| `remote.sh` | the read-only probe run on each host (`bash -s` over ssh, or locally on aifoundry2); prints `@@section` blocks |
| `collect.py` | runs the probes in parallel, parses them, applies the privacy filter, derives alerts, keeps state and history, writes `data.json` |
| `page/render.py` | builds `index.html` from `page/` and the shared report template and chart toolkit, with the data baked in |
| `update.sh` | collect, render, deploy only if changed, check visibility, log, lock; `now`, `status`, `ack`, cron install |
| `page/body.html`, `page/script.js`, `page/meta.json` | the page source (no personal data) |
| `page/fixture.json`, `page/make_fixture.py` | a complete data file with made-up people and card use, for `check_page` and page work, and its generator |
| `testdata/raw-aifoundry{1,2,3}.txt`, `testdata/tailscale.json`, `testdata/run2/`, `testdata/run3/` | made-up `remote.sh` and `tailscale status --json` outputs for `collect.py --from-raw` (parser tests without ssh); `run2` and `run3` are the two runs after, for the liveness cases (§2.8) |

Everything collected about people lives outside the repository: `~/.cache/lab-dashboard/` (data, history, state,
log; mode 0700) and `~/.config/lab-dashboard/` (the space uuid, overrides, acknowledgements). Nothing in the
repository needs a new `.gitignore` line, because nothing is written inside the checkout.

---

## 1. The data model: `~/.cache/lab-dashboard/data.json`

One JSON object, rewritten each run (atomically: write `data.json.tmp`, then rename). Times are ISO 8601 with the
host's offset plus epoch milliseconds (`*_ms`), so the page can format them in the viewer's time zone. Every value
that can be missing is `null` (never 0, never absent), and every block that came from an earlier run carries
`"as_of"` and `"stale": true`.

### 1.1 Top level

```json
{
  "schema": 1,
  "generated_at": "2026-09-30T13:12:04-07:00", "generated_ms": 1790799124000,
  "collector": {"host": "aifoundry2", "code": "<git short sha of tools/lab/dashboard>", "took_s": 7.9,
                "interval_min": 10, "cron_minute": 2, "heartbeat_min": 60, "stale_after_min": 80,
                "card_sample": "off", "errors": ["aifoundry3: could not parse @@disk"]},
  "status": {"level": "warn", "counts": {"bad": 0, "warn": 3, "info": 7, "known": 4},
             "headline": "3 warnings: aifoundry1 /home 99% full, aifoundry1 pool 95% full, aifoundry2 1 failed unit"},
  "fingerprint": "3fa2c1d09e4b",
  "alerts":  [ ... ],
  "hosts":   {"aifoundry1": { ... }, "aifoundry2": { ... }, "aifoundry3": { ... }},
  "cards":   {"aifoundry2": { ... }, "aifoundry3": { ... }, "aifoundry1-c1": { ... }, "aifoundry1-c0": { ... }},
  "people":  [ ... ],
  "usage":   { ... },
  "history": { ... }
}
```

Host and card keys come from `lab.json`; card ids are the chart toolkit's registry ids (`aifoundry2`, `aifoundry3`,
`aifoundry1-c1`, `aifoundry1-c0`), so `CK.card(id)` gives each card its fixed colour and mark. The page takes the
lists from the data and never hard-codes them.

### 1.2 `hosts.<name>`

| Field | Example | Source |
|---|---|---|
| `reachable`, `via`, `error` | `true`, `"ssh"` or `"local"`, `null` or `"approval needed"`, `"timeout"`, `"refused"`, `"ssh failed"` | the ssh exit and stderr (§2.2) |
| `state`, `state_since_ms`, `down_since_ms` | `"up"`, `"down"`, `"unreachable"`, `"approval needed"` (`"no data"` before a first answer); when the state began; for a machine that is not up, when it went away (the first failed run, or Tailscale's last-seen time when that is earlier, never before the last answer) | the machine's own state (§2.8), kept in `state.json` |
| `last_answer_ms`, `tailscale`, `tailscale_last_seen_ms` | the last run the probe answered; `{"online": false, "last_seen_ms": ..., "at_ms": ...}` or `null`; the newest last-seen time Tailscale reported | this collector; `tailscale status --json` on aifoundry2: only each lab host's `Online` and `LastSeen` (§6) |
| `rebooted_at_ms`, `reboot_planned` | set for 24 hours after a reboot: its time, and whether the answer before it said a reboot was pending | the boot id changed, or the uptime is shorter than the time since the last answer |
| `answered_at`, `last_ok_at`, `fails_in_row` | times; a count | collector state |
| `took_ms` | 820 | wall time of the probe |
| `uptime_h`, `boot_id8` | 285.3, `"0a1b2c3d"` | `/proc/uptime`, `/proc/sys/kernel/random/boot_id` |
| `load` | `{"1": 0.97, "5": 1.1, "15": 1.2, "threads": 12, "per_thread": 0.08}` | `/proc/loadavg`, `nproc` |
| `mem` | `{"total_gib": 63, "avail_gib": 59, "avail_pct": 93}` | `/proc/meminfo` |
| `disks` | `[{"mount": "/", "used_pct": 79, "free_gib": 190}, {"mount": "/home", ...}]` (a mount listed once even if `/home` is on `/`) | `df -P -B1 / /home` |
| `zfs` | `{"pool": "rpool", "state": "ONLINE", "used_pct": 95, "note": "42 errors at the last scrub"}` or `null` | et-lab-health lines |
| `kernel` | `{"running": "7.0.0-31-generic", "reboot_pending": true, "pending_since": "25 Sep 16:38", "pending": ["linux-image-7.0.0-34-generic", ...]}` | `uname -r`, `/var/run/reboot-required*` |
| `systemd` | `{"state": "degraded", "failed": ["apport-coredump-hook@..."]}` | `systemctl is-system-running`, `--failed` |
| `temps` | `{"cpu_c": 61, "nvme_c": 43}` | hwmon `coretemp`/`k10temp` package, `nvme` |
| `power_profile`, `chrony` | `"performance"`; `{"synced": true, "offset_ms": 0.4}` | et-lab-health lines |
| `health` | `{"rev": 3, "exit": 1, "warn": 1, "info": 4, "at": "...", "lines": [{"level": "WARN", "check": "systemd", "text": "degraded, 1 failed unit(s): ..."}]}` | `tools/lab/et-lab-health` rev 3, streamed (§2.3); run hourly per host, so `at` is when these lines were read |
| `manifest` | `{"cpu": "...", "et_soc1": "0.20.0", "srcversion": "...", "libetrt": "ab12cd34"}` | `et-lab-manifest`, a fixed short list of keys |
| `ci_runner` | `{"units": 1, "active": 1, "jobs": 0}` or `null` | et-lab-health's `ci runner` lines, summarised |
| `logins` | `{"sessions": 5, "people": 2}` (counts only; the detail is in `people`) | `loginctl` |
| `device_procs`, `device_people`, `ci_jobs` | 1, 1, 0: device processes (all users), how many people own them, CI jobs | `ps` comm counts (§2.3) |
| `nodewatch` | `{"present": true, "beat_at": "...", "beat_age_min": 0.4, "sessions": 5, "gaps_48h": [{"from": "...", "to": "...", "min": 14}], "events_48h": [{"t": "...", "type": "REBOOT", "what": "reboot"}], "logins_48h": {"in": 7, "out": 6}}` | `~/nodewatch/heartbeat.log`, `events.log` (§2.3: only these fields; not nodewatch's tmux, Claude and own-session columns, which are about the account that runs it) |

### 1.3 `cards.<id>`

| Field | Example | Source |
|---|---|---|
| `host`, `devnum`, `pci`, `lock` | `"aifoundry1"`, 1, `"0000:02:00.0"`, `"etsoc-shire1.lock"` | sysfs `devnum`; `lab.json` |
| `excluded`, `note` | `true`, `"overheats; excluded from all work and never touched"` (aifoundry1 card 0 only) | `lab.json` |
| `present` | `true`, or `false` when `lab.json` expects the card and sysfs has no bound device | `/sys/bus/pci/drivers/ET/` |
| `static` | `{"firmware": "1.3.1", "bl": "0.20.0", "pmic": "1.5.0", "minion": "0.23.0", "tdp_w": 65, "clock": "DVFS 600–800 MHz, in practice 600 (die above 65 °C)", "policy": "dvfs", "idle_c": [73, 80], "idle_w": [31, 36]}` | `lab.json`, from `docs/findings/14-card-behaviour.md` and `AGENT.md` §4 (not collectable without the card) |
| `link` | `{"speed": "16.0 GT/s", "width": 8, "max_speed": "16.0 GT/s", "max_width": 8, "ok": true}` | sysfs `current_link_*`, `max_link_*` |
| `power_state`, `enabled` | `"D0"`, `true` | sysfs `power_state`, `enable` (not for card 0, §2.4) |
| `errors` | `{"ce": {"PmicCeEvent": 18, "ThermThrottleCeEvent": 10}, "uce": {}, "ce_new": {"ThermThrottleCeEvent": 2}}` | sysfs `err_stats/ce_count`, `uce_count`; `ce_new` is the change since the last run |
| `aer` | `{"card_total": 0, "port_total": 1140744, "port_per_h": 3980}` | sysfs `aer_dev_correctable` on the card and its root port; the rate from the last run |
| `kernel_log` | `{"error_events": 11, "refused_opens": 9, "enables": 2, "window_h": 188.2}` | et-lab-health's per-card line |
| `activity` | `{"mgmt": 261442, "ops": 3377811, "used": false, "last_used_at": "...", "last_used_by": "user-a" }` | sum of sysfs `mgmt_vq_stats/msg_count` and `ops_vq_stats/msg_count`; `used` is a change since the last run, net of the dashboard's own sample (§2.6). Where the card has a usage log, "used since the last check" comes from it instead (§1.8) |
| `holder` | `{"held": true, "who": [{"node": "/dev/et0_ops", "login": "user-a", "etime_s": 723, "comm": "sgemm_host", "since_ms": ..., "system": false}]}`, node holders first | `et-who` (node, user, elapsed time, and the program's base name cut to 15 characters, as ps comm; never the rest of the command line), completed from `et-usage`'s `now` (the program that opened the nodes, the start of the hold) and joined by `et-usage`'s holds that `et-who` did not list |
| `telemetry` | `{"source": "experiment", "at": "...", "age_min": 38, "die_c": 74, "die_max_c": 78, "pmic_c": 63, "board_w": 35.5, "minion_mhz": 600, "noc_mhz": 400, "ddr_mhz": 933, "from": "claims-v3/aifoundry2/nocr/p3/marks.jsonl"}` | a live sample (§2.6), else the newest experiment file on that host (§2.3) |
| `sample` | `{"enabled": false, "last_try": "...", "result": "skipped: held", "next_after": "..."}` | collector state. `policy` is `dvfs`, `pinned` or `fixed`; `source` is `live`, `experiment` or `none`; `result` is `ok`, `skipped: held`, `skipped: experiment`, `skipped: someone active`, `skipped: too soon`, `failed: no output`, `failed: timeout` or `disabled` |
| `guard` | `{"present": true, "this_boot": true, "minion_mhz": 600, "noc_mhz": 400, "tdp_w": 0}` (aifoundry3) | `/run/et-board-clock-guard.ok` against the boot id |
| `level`, `reasons` | `"ok"`, `"warn"`, `"bad"`, `"excluded"`, `"unknown"`; short reasons | the rules of §5 |

### 1.4 `people`

`people` has one entry per login seen on any host (uid 1000 or more; `gdm`, root and other system accounts are
skipped) or holding a card. Everyone is listed the same way; the collector's own account is one login among the others.
Only these fields exist; the collector never records anyone's commands, files, groups or where they connected from.

```json
{"login": "user-a", "status": "active", "doing": ["card", "agent", "build"],
 "hosts": {"aifoundry2": {"sessions": 5, "closing": 1, "ttys": 12, "idle_min": 22, "procs": 214, "status": "active",
                          "doing": ["card", "agent", "build"]}},
 "card_holds": [{"card": "aifoundry2", "etime_s": 723, "comm": "sgemm_host", "since_ms": ...}],
 "cards_24h": [{"card": "aifoundry2", "held_s": 5820.4, "runs": 95, "last_ms": ..., "open": true}],
 "device_procs": 0, "idle_min": 22, "stale_hosts": []}
```

`status` is `active` (a terminal used in the last 30 minutes, or a session with no terminal), `idle` (30 minutes to
24 hours), `away` (over 24 hours), or `processes only` (only closing sessions, or processes with no session: counts
only). Each `hosts.<h>` entry also carries that machine's own `status`; the top-level one is the person's best. On the
page, "logged in" is a session that is not closing, and a machine that is not up has unknown counts, never zero.

`doing` is a list of coarse categories, in this order: `card` (holds a card now: `et-who` or `et-usage`), `agent` (an
AI coding agent: `claude`, `codex`, `aider`, `gemini`, `goose`, `cursor-agent`, `opencode`, `crush`, `qwen`, `cline`),
`build` (`cc1`, `cc1plus`, `as`, `ld`, `collect2`, `make`, `cmake`, `ninja`, `gcc`, `g++`, `clang`, `rustc`, `cargo`,
`ccache`, the cross compilers' truncated names `riscv64-*`, ...), `sim` (`sys_emu`), `python` (`python*`, `ipython`,
`jupyter*`), `editor` (`vim`, `nvim`, `emacs`, `nano`, `micro`, `hx`, `code-server`, ...), or `shell` (processes, none of
these). The probe matches the names on the host (§2.3) and prints only the category keys; `null` means an older probe.

### 1.5 `alerts` and `status`

```json
{"id": "host:aifoundry1:disk:/home", "level": "warn", "scope": "host", "host": "aifoundry1", "card": null,
 "title": "/home 99% used", "detail": "ZFS pool rpool is 95% full", "since": "...", "source": "et-lab-health",
 "known": false, "ack": null}
```

Levels are `bad`, `warn`, `info`. Ranking: level, then scope (`collector` > `host` down > `card` > `host`),
then the newest `since`. `since` is the first run that raised the same `id` (kept in state). An alert whose `id`
matches a known condition in `lab.json` or an acknowledgement in `~/.config/lab-dashboard/ack.json` keeps its text but
drops to `info` with `known` or `ack` filled in, and does not count toward the traffic light. `status.level` is the
worst remaining level, or `ok`; the page turns it into `stale` by itself (§4.4). The rules are in §5.

### 1.6 `lab.json` (in the repository; static facts only)

```json
{"collector_host": "aifoundry2", "tz": "America/Los_Angeles",
 "hosts": {"aifoundry1": {"ssh": "aifoundry1", "tree": "~/nekko", "ettelem": "~/nekko/build/ettelem/ettelem",
                          "cards": {"aifoundry1-c0": 0, "aifoundry1-c1": 1}},
           "aifoundry2": {"local": true, "tree": "~/claude/et-soc1-prototyping",
                          "ettelem": "~/claude/et-soc1-prototyping/build/ettelem/ettelem", "cards": {"aifoundry2": 0}},
           "aifoundry3": {"ssh": "aifoundry3", "tree": "~/nekko", "ettelem": "~/nekko/build/ettelem/ettelem",
                          "cards": {"aifoundry3": 0}}},
 "cards": {"aifoundry1-c0": {"excluded": true, "firmware": "1.4.1", "...": "..."}, "...": {}},
 "known": [{"id": "card:aifoundry1-c0:ce", "note": "card 0 overheats; excluded (AGENT.md §4)"},
           {"id": "card:aifoundry1-c0:aer-port", "note": "its root port logs ~4,000 corrected errors an hour"}]}
```

`collector_host` is aifoundry2 and `tz` the lab's zone (`America/Los_Angeles`), in which the page draws card use.
The `ssh` names are the plain host names; if other ssh targets are needed they go in
`~/.config/lab-dashboard/config.json`, never here (AGENT.md §10: no access paths in the repository).

### 1.7 `history` (48 hours, for sparklines and the timeline)

A fixed grid of 288 ten-minute slots ending at the current slot, `null` where there is no value:

```json
{"t0_ms": 1790626200000, "step_min": 10, "n": 288,
 "hosts": {"aifoundry2": {"up": [1, 1, ...], "load": [...], "mem_avail_gib": [...], "sessions_all": [...],
                          "beats": [10, ...], "warn": [...]}},
 "cards": {"aifoundry2": {"hold": ["", "", "user-a", ...], "used": [0, 1, ...], "die_c": [null, 74, ...],
                          "board_w": [...], "ce_new": [...]}}}
```

The host series `load`, `mem_avail_gib`, `sessions_all` and `beats` come from nodewatch's per-minute heartbeat
(bucketed on the host, §2.3), so they are full from the first run and keep filling while a host is unreachable. `up`,
`warn` and every card series come from the collector's own `history.jsonl` (§2.7). `up` is 1 answered, 3 down
(Tailscale: offline), 2 waiting for a Tailscale approval, 0 no answer (ssh timed out or failed); within a slot the first
of those wins. A slot's `hold` is the holder's login (`""` free, `null` unknown), `used` is 1 when the card's message
counters moved. The card rows of the page's "Last 48 hours" are drawn only for cards without a usage log (§4.2).

`fingerprint` is the first 12 hex digits of the sha256 of the material state only: per host `reachable`, `error`,
`state`, the boot id and the reboot time, the set of health WARN checks, failed units, reboot pending and the usage
logger's state; per card `present`, `link.ok`, error kinds, holders' logins, in use now or not, the set of logins that
used it in the last 24 hours (§1.8), the sample's failure; per person the login, `status` and the machines; and every
alert's `id` and `level` (without `card:*:used`). Loads, memory, idle minutes, ages, times, counts of runs and
held time are left out, so the page is republished when something happened, not when a number drifted (§3.2).

### 1.8 `usage`: card use, the last 24 hours (from `et-usage`)

Each host's `et-usage --json --since 26h` (`tools/lab/et-usage/`, its `--json` format) read by the probe
(§2.3), checked and converted (logins must pass the login rule or become `"?"`; program names are cut to ps comm's
characters, `[A-Za-z0-9._+-]`, 15 at most, and pass the scrubber; card numbers become card ids), kept per host in
`state.json` with the rest of the host's data (so a machine that stops answering keeps its last log, marked stale), and
cut to the window `[generated - 24 h, generated]`:

```json
{"hours": 24, "start_ms": ..., "end_ms": ..., "tz": "America/Los_Angeles", "logins": ["owner", "user-a"],
 "hosts": {"aifoundry2": {"logger": "running", "installed": true, "error": null, "stale": false, "as_of_ms": ...,
                          "alive_ms": ..., "started_ms": ..., "logging_since_ms": ..., "coverage_ms": [[a, b], ...],
                          "logged_s": 83700, "skipped": 0, "merged_gap_s": null}},
 "cards": {"aifoundry2": {"host": "aifoundry2", "logged": true, "stale": false,
   "intervals": [{"user": "user-a", "start_ms": ..., "end_ms": ..., "held_s": 2700.0, "node_s": 2690.2, "runs": 3,
                  "programs": {"mmbench_launch": 3}, "open": false, "n": 1}],
   "activity_min": [[812.0, 60.0, 571]],
   "users": {"user-a": {"held_s": 3360.0, "node_s": 3300.1, "runs": 4, "programs": {...}, "first_ms": ..., "last_ms": ..., "open": false}},
   "held_s": 5880.3, "node_s": 5700.2, "runs": 111, "people": 3,
   "now": [{"user": "owner", "comm": "sgemm_host", "nodes": ["mgmt", "ops"], "lock": true, "start_ms": ...}],
   "daily": [{"date": "2026-09-30", "day_ms": ..., "users": {"user-a": {"held_s": ..., "node_s": ..., "runs": 4}}}],
   "since_check": {"since_ms": ..., "users": ["owner"], "runs": 3, "programs": {"sgemm_host": 3}}},
  "aifoundry3": {"host": "aifoundry3", "logged": false}}}
```

- `logger`: `running`, `stale` (the daemon's state file is older than 3 minutes), `not running` (installed, no log and
  no state), `not installed` (no `et-usage` on the host), `error` (it failed, timed out or printed something else), or
  `no data` (no answer yet). A card is `logged` when its host's logger is `running` or `stale`.
- `coverage_ms`: the spans the logger was running, cut to the window. Time outside them is "not logged", never idle;
  for a machine that no longer answers, the time since its last answer is outside them too.
- `intervals`: per card and login, et-usage's merged holds (5 s gap), clipped to the window (sums scaled). A card with
  more than 500 is merged further, per login, the gap doubling from 30 s, keeping the sums (`n` counts the merged
  holds). `runs` counts node-holding processes. `activity_min`: minutes (from `start_ms`) in which the card's queue
  message counters moved, with the interval and the message count.
- `held_s`: the card's busy time, the union of all logins' intervals; `users`: per login totals over the window;
  `daily`: the 7 last dates (the host's), by login; `now`: who holds it now (only while the logger is running);
  `since_check`: who used it after the previous run.

---

## 2. The collector: `collect.py` and `remote.sh`

`collect.py` is Python 3 standard library only (3.12 on aifoundry2). It runs on aifoundry2, because `ssh aifoundry2`
from aifoundry2 is refused; aifoundry2 is probed locally.

```
collect.py [--out DIR] [--hosts a1,a2,a3] [--card-sample] [--sample-dry] [--from-raw DIR] [--no-backoff] [--health] [--quiet]
```

`--out` defaults to `~/.cache/lab-dashboard`. `--from-raw DIR` parses saved probe outputs instead of running them
(tests). `--card-sample` turns on the telemetry step for this run (§2.6); `--sample-dry` runs its gates and prints
the command it would run, without running it. Exit 0 when `data.json` was written (even with hosts missing), 3 when
the privacy check refused it (§6), 2 on a usage error.

### 2.1 Order of a run

1. Take `collect.lock` in the output directory (one collector at a time: a hand run waits up to 60 s for a cron
   run, then exits 4). Load `lab.json`, `~/.config/lab-dashboard/config.json` (optional overrides) and `state.json`.
   A sample in-flight marker left in `state.json` by a collector that stopped mid-run disables that card's sample
   (§2.6). Before any probe that may take a sample, write the marker and save `state.json`.
2. In parallel (a thread pool of 5):
   - one probe per host: `ssh -o BatchMode=yes -o ConnectTimeout=8 -o ServerAliveInterval=5 -o ServerAliveCountMax=2 <target> 'nice -n 10 ionice -c3 bash -s'`
     with `remote.sh` plus et-lab-health on stdin (§2.3), or the same `bash -s` locally for aifoundry2; each
     under a 50 s subprocess timeout (60 s for a probe that may take the card sample, which starts only in the
     probe's first 10 s; et-lab-health and et-usage have 20 s each, and normally take about a second);
   - `timeout 10 tailscale status --json` (local, read-only): only each lab host's `Online` and `LastSeen` are kept
     (§2.8, §6). Until 30 September the collector also ran `claudes status` and `spacesheep sessions list` for the
     owner's own sessions; it no longer does.
3. Parse each result independently (§2.5), merge with the previous state, derive each machine's state (§2.8),
   `people`, `usage` (§1.8), alerts, levels, history and the fingerprint.
4. Walk every string through the privacy check (§6); write `data.json`, append one line to `history.jsonl`, save
   `state.json`, and keep the last raw output of each host in `raw/<host>.txt` (mode 0600, overwritten each run,
   for debugging only).

A run takes 1–10 s of wall time (each probe 0.4–1 s; 0.6 s for all three hosts on 30 September at 15:30, with no
et-usage installed yet) and under a second of CPU on each host. A machine that is down costs its probe's 8 s connect
timeout, beside the others.

### 2.2 Failures and partial results

- A host that fails keeps its last good block from `state.json`, marked `"stale": true, "as_of": <last_ok_at>`, with
  `reachable: false` and an `error` word. The page greys it and says "last data 11:40".
- Tailscale SSH's check mode prints a `login.tailscale.com` URL and waits. The collector recognises that text in
  stderr, kills its own ssh client at the timeout, records `error: "approval needed"` (the host is up: its tailscaled
  answered), and never stores or shows the URL. An approval lasts about 12 hours, so this will be the most common
  failure; after one "approval needed" the collector tries that host once an hour instead of every run, and
  `update.sh now` always tries.
- Any other ssh failure: `timeout`, `refused`, or `ssh failed` with the exit code. With Tailscale's view it becomes the
  machine's state (§2.8): `down` when Tailscale says the peer is offline (`bad` at once), else `unreachable` (a
  warning, `bad` from the second run in a row). Down and unreachable machines are probed again every run, so a return
  shows within one cron cycle; only "approval needed" waits an hour between tries.
- Inside `remote.sh` every command runs under `timeout -k 2 <s>` with stdin from `/dev/null`, so one slow command
  costs its own section only. A section that cannot be parsed adds a line to `collector.errors` and leaves its fields
  `null`.
- `tailscale status` failing leaves the states to ssh alone: a failed probe is then `unreachable`, never `down`.

### 2.3 What `remote.sh` reads (all read-only)

`remote.sh` prints `@@<section>` headers and plain lines, ending with `@@end`. It never opens `/dev/et*`, never
reads a card attribute outside the list in §2.4, never writes anywhere except the optional sample's stamp file
(§2.6), and never calls `tmux`.

| Section | Command | Kept |
|---|---|---|
| `meta` | `hostname`, `date +%s%z`, `/proc/uptime`, `/proc/loadavg`, `nproc`, boot id | as §1.2 |
| `mem`, `disk`, `kernel`, `systemd`, `temps` | `/proc/meminfo`; `df -P -B1 / /home`; `uname -r`, `/var/run/reboot-required.pkgs` and its mtime; `systemctl is-system-running`, `systemctl --failed --no-legend --plain`; hwmon `name` and `temp*_input` for `coretemp`, `k10temp`, `nvme` | as §1.2 |
| `sessions`, `pts`, `procs` | `loginctl list-sessions -o json`; `stat -c '%U %X' /dev/pts/[0-9]*`; `ps -eo pid=,sid=,uid=,user:32=,cgroup=,comm=` | per login: sessions, closing, ttys, newest tty use; process and device-process counts; and the coarse categories of §1.4, matched by `awk` on the host from each process's `comm` and printed as keys only (`agent,build`), so no process name leaves the host. Left out: the probe's own logind session (its cgroup scope), its own process session and its ancestors (the ssh or cron chain, and on aifoundry2 the collector itself). `RemoteHost`, `who -u` and utmp hosts are never read |
| `etwho` | `et-who` (plain; it runs the lab's `sudo -n et-holders`) | from lines starting `/dev/et` or `lock:`, the node, user, elapsed time and the program's name (the base name of the first argument, `[A-Za-z0-9._+-]` only, 15 characters at most, as ps comm); the rest of the command line is cut off in the shell, before the output leaves the host |
| `usage` | `command -v et-usage` and then `timeout 20 nice -n 10 et-usage --json --since 26h`, cut at 2 MB, and its exit status as `rc N`; or the word `absent` | §1.8; the logins, program names and times of card holds, as `et-usage` shows them to every user of the host |
| `cards` | per `/sys/bus/pci/drivers/ET/0000:*`: §2.4 | as §1.3 |
| `guard` | `/run/et-board-clock-guard.ok` and the boot id | as §1.3 |
| `nodewatch` | `tail -n 2900 ~/nodewatch/heartbeat.log`, bucketed by `awk` on the first 15 characters of the timestamp (one ten-minute slot): count, max load, min memavail, max sessions (all users); the last line's boot, load, memavail and sessions; from `events.log` in the last 48 h only the time, the type and one word for REBOOT, START and WARN, and a count of LOGIN/LOGOUT | never the `path[...]` peers, `from=`, the `(machine/login)` part, argv, `state/`, or nodewatch's tmux, Claude and own-session columns (they are about the account that runs nodewatch) |
| `telemetry` | `find <tree>/build/claims-v3 <tree>/build/sparseparity-energy -maxdepth 5 -mmin -10080 -type f` for `tel-*.jsonl`, `tel.jsonl`, `marks.jsonl`, `energy.json`, skipping any path with a `-dry/` or `-raw/` component, grouped by the `claims-v3/<card>/` component; per card and kind the newest file's last line (cut to 2 KB) | a file counts only for a card of the host it is on (aifoundry2 holds copies of aifoundry1's data) |
| `manifest` | `et-lab-manifest` | the keys named in §1.2 |
| `health` | `tools/lab/et-lab-health` rev 3, sent inside the probe as a quoted heredoc and run with `nice -n 10 sh` under `timeout 20`, **hourly** per host (`DASH_HEALTH=1`; `update.sh now` runs it on every host): it runs `sudo -n et-holders` a second time and spawns about 300 processes, so the other runs keep the last lines from `state.json` | every line; `host`, `logins` and `holders` lines are replaced by the collector's own fields, `ci runner` lines are summarised, the rest pass through the scrubber (§6) |
| `sample` | only when asked (§2.6) | the ettelem JSON lines and the gate results |

The repository's rev 3 of `et-lab-health` is used rather than the installed rev 2, because rev 3 reads logins from
logind, reads the kernel log once, and runs safely with no terminal (`tools/lab/README.md`). Streaming it installs
nothing.

### 2.4 Per-card sysfs: what may be read

For aifoundry2, aifoundry3 and aifoundry1 card 1: `devnum`, `vendor`, `device`, `current_link_speed`,
`current_link_width`, `max_link_speed`, `max_link_width`, `power_state`, `enable`, `err_stats/ce_count`,
`err_stats/uce_count`, `mgmt_vq_stats/msg_count`, `ops_vq_stats/msg_count`, `aer_dev_correctable` (card and root
port). These are the driver's own counters in host memory.

For aifoundry1 card 0: only what `et-lab-health` already reads (link, `err_stats`, the root port's
`aer_dev_correctable`). Its tile otherwise shows the constants from `lab.json`.

Never, on any card: `utilization_percent` (it syncs queue pointers from the card over MMIO), `resource*`, `config`,
or any write (`clear`, `soc_reset/*`, `reset`, `remove`, `rescan`).

### 2.5 Parsing

Each section has its own parser function returning a dict, wrapped in `try`/`except` so one bad section never stops
the run. Logins are accepted only if they match `^[A-Za-z0-9._-]{1,32}$`. `ps` uses `user:32` so long names are not
truncated. `@@usage` is JSON after the probe's own lines: `absent`, else the object and `rc N`; anything but a version-1 object is
the logger state `error` with a short reason (never its text). `tailscale status --json` is matched to the lab hosts
by the first label of each peer's MagicDNS name (or, lacking one, its host name), exactly, and only `Online` and
`LastSeen` are taken. Health lines are `LEVEL`, a 16-character check name, and text; the per-card kernel-log line
("11 card error events / 9 refused second opens / enabled 2 times in the last 188.2 h") is also parsed into numbers.
ettelem lines are parsed by key, because blocks are missing when their query fails: die mean `temp_c.minshire[0]`
(the claims-v3 definition), die high `temp_c.minshire[2]`, `temp_c.pmic`, `board_w`, `mhz.minion`, `mhz.noc`,
`mhz.ddr`. `tel.jsonl`'s `summary` is "<die °C> <MHz>"; `marks.jsonl` has `die_c` and `mhz`.

### 2.6 The optional card sample (off by default)

Off unless `config.json` has `"card_sample": true` or the run has `--card-sample`. All tests in the build pass keep
it off or use `--sample-dry`. The main session takes the first real sample.

The collector asks for a sample of card N on host H only when its own state allows it: the card is not aifoundry1
card 0 (refused in `collect.py` and again in `remote.sh`), the last try on that card was at least
`card_sample_every_min` ago (default 30, never below 10), at most one card per host per run, and the card is not in
the `disabled` state. It passes the card's submission-queue total from the last run (`state.cards.<id>.sq`) and
that run's boot id, and on a host with several cards the boot id a person confirmed in `config.json`
(`"sample_boot": {"aifoundry1": "<boot id>"}`). `remote.sh` then checks, in this order, right before the sample; the
first that fails stops it, and a check whose own command fails or times out fails:

1. **card**: bound to the ET driver at the expected PCI address with the expected `devnum`, not excluded; on a host
   with more than one card bound (or on aifoundry1) only through `ET_DEVICES` naming the card, and on aifoundry1
   only card 1;
2. **boot** (several cards only): `/proc/sys/kernel/random/boot_id` equals the confirmed one. Card identity rests on
   `lab.json`'s PCI address and `devnum`; moving a card (the pending reseat of aifoundry1's card 0) needs a power
   cycle, which changes the boot id, so a reseat stops sampling until a person checks the numbering again;
3. **lock**: `/run/lock/etsoc-shire<N>.lock` matches the card, exists, is a plain file and is root's. It is opened
   read-only below and never created: a lock file we created would be ours, mode 0600 under the probe's umask, and
   every other user's `flock` on it would fail until a reboot;
4. **stamp**: the host's own rate limit, `~/.cache/lab-dashboard/sample-<card>.stamp` older than
   `card_sample_every_min`;
5. **binary**: the host's own build: `ldd` succeeds with nothing missing and `libDM.so` from `/opt/et/lib`, and a
   `CMakeCache.txt` beside it (if any) says `deviceLayer_DIR` under `/opt/et`. With `ET_DEVICES` (several cards) the
   device layer is static, so `ldd` cannot show it: the `CMakeCache.txt` must exist and its `CMAKE_CACHEFILE_DIR`
   must be the binary's own directory, and both the binary and `/opt/et/lib/libdeviceLayer.a` must contain the
   string `ET_DEVICES` (a stock device layer has none, and would send the sample to card 0);
6. **experiment**: none of the collector account's own runners (a plain `pgrep -f` over `tools/claims-v3`,
   `queue.sh`, `run_passes`, `series.sh`, `card_run`, `energy.sh`, `workloads/*/run_*`, `tools/ettelem/*.sh`, `run_*.sh|py`:
   any mention counts) and none of its device processes. This gate is internal: the page does not show these runs as
   anyone's; they appear as card use like everyone else's;
7. **others**: no other user's device process and no CI job (`Runner.Worker`);
8. **people**: no other user active (a non-closing session with no terminal, or a terminal used in the last 30
   minutes);
9. **quiet**: the card's submission counters equal the last run's, from the same boot. This catches a runner
   between two launches (`pciebench/run_pcie.sh` takes `flock -n` per launch), which holds nothing and may show in
   no process list;
10. **etwho**: `et-who --check` exits 0 (nothing held on any card of the host), last, so the card was seen free as
    close as possible to the lock;
11. **time**: the probe is at most 10 s old, so the collector's 45 s probe timeout never stops a probe mid-sample.

Then, and only then, `remote.sh` touches the stamp (if it cannot, the sample is skipped), prints `start`, and runs:

```
( cd /tmp; exec 9</run/lock/etsoc-shire<N>.lock || exit 98; flock -n 9 || exit 97
  exec env LD_LIBRARY_PATH=/opt/et/lib [ET_DEVICES=1] timeout -k 3 10 nice -n 10 <ettelem> sample --seconds 2 --every-ms 500 )
```

(`ET_DEVICES=1` and `etsoc-shire1.lock` on aifoundry1; no `ET_DEVICES` and `etsoc-shire0.lock` on the one-card hosts.)
The lock descriptor is inherited by `timeout` and ettelem, so the lock is held for exactly the sample. The card's
message counters are read before the sample and again after it, so the next run's `used` flag does not count our
own sample. Then it prints `ran rc=<exit> msgs_before=... msgs_after=...` and the last telemetry lines.

Failures never retry within a run, and nothing is drained: the collector may not run `dev_mngt_service`.

- 97 (the lock is held) or 98 (it would not open): `skipped`.
- No JSON output (ettelem fails to start about one time in three right after another instance): `failed: no
  output`; after two in a row the card waits 60 minutes.
- Exit 124 (the timeout's SIGTERM stopped it; ettelem finishes the request in flight first) or 137 (still in a
  request 3 s later, so SIGKILL landed mid-request: the queue is likely poisoned and the next opener may crash):
  the card's `sample` becomes `disabled` and a `bad` alert (`card:<id>:sample-failed`) says which, what a person
  should check, and on 137 to tell the lab admin. Only `update.sh sample-reset <card>` (run by a person) clears it.
- The probe failed after `start` (or after every gate passed) with no `ran` line, or the collector itself stopped
  while the in-flight marker was set: whether ettelem finished is unknown, so the sample is `disabled` the same way.
  A probe that failed before the sample only advances `last_try`.

### 2.7 State, history and files under `~/.cache/lab-dashboard/`

| File | Content | Kept |
|---|---|---|
| `data.json` | the page's data | overwritten each run |
| `history.jsonl` | one compact line per run: `{"t": <s>, "h": {<host>: {"up": 1, "warn": 3}}, "c": {<card>: {"hold": "", "used": 0, "die": 74, "w": 35.5, "ce": 0}}}` | 7 days, trimmed each run |
| `state.json` | per host last good block, `last_ok_at`, `fails_in_row`, back-off; per card last counters, last sample and failures; alert first-seen times; last deploy time and fingerprint | overwritten each run |
| `raw/<host>.txt` | the last probe output (mode 0600) | overwritten each run |
| `update.log` | one line per run (§3.4) | rotated at 1 MB to `update.log.1` |
| `lock`, `HALT` | the run lock; the deploy stop (§3.3) | |
| `HALT.sticky`, `HALT.verified`, `halt.times`, `autoresume.last` | a halt only a person may clear; runs in a row that verified the space private; the last 20 halts; the last auto-resume (§3.3) | |

The directory is created with mode 0700.

### 2.8 Each machine's own state (liveness)

Added on 30 September 2026, after aifoundry1 went off the network at 14:33 and the page still showed its last data as
current. Every run gives each machine one state, kept in `state.json` with its times:

| State | When | Kept |
|---|---|---|
| `up` | the probe answered | `last_ok_ms` (the last answer) |
| `down` | no answer, and Tailscale (on aifoundry2, `tailscale status --json`) says the peer is offline | `down_since_ms`: the first failed run, or Tailscale's `LastSeen` when that is earlier (never before the last answer); `ts_last_seen_ms` |
| `approval needed` | Tailscale SSH's check prompt (§2.2) | the first failed run |
| `unreachable` | any other failure: Tailscale online (or not known), ssh timed out, was refused or failed | the first failed run; `fails_in_row` |

aifoundry2, where the collector runs, is always up while it runs. A reboot is an event, not a state: when a machine
answers with another boot id than at its last answer, or with an uptime shorter than the time since its last answer,
the collector records `reboot = {at: now - uptime, planned: <the last answer said a reboot was pending>}` and shows it
for 24 hours (§5). Down and unreachable machines are probed every run (with ssh's 8 s connect timeout), so a return
shows within one cron cycle; a down machine also leaves the hourly back-off of "approval needed". The machine rows of
the 48-hour history keep the difference (`up` 3 down, 0 no answer, 2 approval). Testing: `testdata/`, then
`testdata/run2` (`--now 1790798100`: aifoundry1 down, aifoundry2 rebooted unplanned, aifoundry3 unreachable) and
`testdata/run3` (`--now 1790798700`: aifoundry1 back and rebooted as planned, aifoundry3 unreachable a second run, so
`bad`), in one `--out` directory; the three fingerprints differ.

---

## 3. The updater and the automatic refresh: `update.sh`

```
update.sh run                  # what cron runs: collect, render, deploy if changed; quiet; exit 0 unless broken
update.sh now [--card-sample]  # the same at once, always deploys, prints the headline, the alerts and the page address
update.sh status               # last run and deploy, HALT, the cron line, the last 10 log lines, the space's visibility
update.sh --install-cron       # add the user crontab line; --uninstall-cron removes it
update.sh ack <alert-id> [days] [note]   # acknowledge an alert (default 7 days); unack <alert-id>
update.sh resume               # clear HALT after a person checked the space's visibility
update.sh sample-reset <card>  # re-enable a card's sample after a timeout was looked at
update.sh create-space         # once: first private deploy, records the uuid (for the main session)
```

The whole script body is a `main` function called on the last line, so bash has parsed it all before it runs; an
edit to the file while cron runs it cannot splice two versions together (the "never edit a running script" trap,
AGENT.md §6). It sets `PATH` itself (`~/.local/bin` for `spacesheep` and `node`, `/snap/bin`,
`/usr/local/bin`, then the system paths), because cron's is minimal.

### 3.1 A run

1. `flock -n ~/.cache/lab-dashboard/lock` (cron: exit 0 quietly if another run holds it; `now` waits up to 60 s
   with `flock -w 60` and says so).
2. `timeout 120 nice -n 10 python3 collect.py` (exit 3, a privacy refusal, stops the run: nothing is rendered or
   deployed, and the log says which pattern matched, not the text).
3. `python3 render.py ~/.cache/lab-dashboard/data.json $D/index.html`, where `D=$(mktemp -d)`.
4. Deploy decision: skip when there is no `~/.config/lab-dashboard/space` (log "no space configured"), when `HALT`
   exists (then `halt_check`, §3.3), when the fingerprint equals the last deployed one and the last deploy is younger
   than `heartbeat_min` (60) less 2 minutes of slack, or, for `run`, when the last deploy is younger than
   `min_deploy_gap_min` (10) less 1 minute: at most one deploy per cron cycle. `now` always deploys.
5. Before the deploy, the space's row in `spacesheep list --json` must say private (§3.3); otherwise no deploy.
6. `spacesheep deploy $D --space $UUID -m "lab HH:MM"`; no `--title`, `--slug` or `--visibility` on an update.
7. The visibility guard after the deploy (§3.3).
8. `rm -rf $D` (it also removes the `.spacesheep.json` the CLI leaves), append the log line, release the lock.

The lock is fd 9 of `update.sh`; every child (collect, render, the spacesheep calls) runs with `9>&-`, so a child
that lingered could never hold the lock and silently skip every later run. `collect.py` takes its own
`collect.lock` as well, so a hand run of `collect.py` never races a cron run.

A deploy failure (network, rate limit) is logged and retried by the next run; there is no retry loop.

### 3.2 Cadence

- Cron: `2-59/10 * * * * <checkout>/tools/lab/dashboard/update.sh run >/dev/null 2>&1 # lab-dashboard`. Minute 2 of
  each ten keeps it off the minute boundary where nodewatch and other per-minute jobs run. `--install-cron` changes
  only the tagged line: it refuses when `crontab -l` fails for any reason but "no crontab for", keeps a copy in
  `~/.config/lab-dashboard/crontab.bak`, keeps blank lines, and checks afterwards that every other line is unchanged
  (restoring the copy if not). The crontab also holds other lines of the account (nodewatch's, for one).
- A deploy happens when the fingerprint changes, or every 60 minutes regardless, and a cron run never deploys twice
  within 10 minutes (a change seen sooner waits for the next run). The fingerprint is the state the page reports, not
  its drifting numbers (§1.7): each machine's state (up, down, unreachable, approval needed), its boot id and reboot,
  WARN checks, failed units, reboot pending, the usage logger's state; each card's presence, link, error kinds (not
  counts), holders, whether it is in use now, the set of logins that used it in the last 24 hours, and sample failure;
  each person's status and machines; the alert ids and levels (without `card:*:used`); and HALT. Left out: load,
  memory, ages, the `used` flag, telemetry times, session counts, run counts and held time. So a machine going down
  or coming back, a reboot, a card taken or freed, or a new person on a card republishes the page at the next run
  (within 10 minutes), while more runs by the same people on a busy card do not.
- Expected versions a day: 24 heartbeats, plus one per change. A quiet day is 30–60. A day when a queue takes a card
  in bursts, so that "in use now" flips from check to check, can reach one version per cron cycle, 144 a day, and the
  10-minute floor keeps it there (plus any `update.sh now`).
- The page is about 250 KB (about 55 KB gzipped) with a quiet day's card use; et-usage's data is capped at 500
  intervals a card (§1.8). 30–60 versions a day are 8–15 MB of the Free plan's 500 MB, which the report deploys
  share; a 144-version day about 36 MB. The CLI (1.9.1) has no
  command that shows the quota or deletes a version: only deleting the space frees them. Check the account's usage
  on spacesheep.dev every few weeks, and delete and recreate the space (`update.sh create-space` after removing
  `~/.config/lab-dashboard/space`) when it grows too large.
- Every version keeps a copy of its data, login names included. Only deleting the space removes them; the README
  says so.

### 3.3 The visibility guard and `HALT`

Before every deploy, the space's row in `spacesheep list --json` must say `"visibility": "private"`; if the list fails
or lacks the space, the run skips the deploy and logs "visibility unverified".

After every deploy:

1. The space's row in `spacesheep list --json` must say `"visibility": "private"`.
2. A signed-out request to `https://$UUID.spacesheep.app/` with a browser user agent must contain `auth-request` and
   must not contain the page's canary (`lab-dashboard-private-canary`, a hidden element of `page/body.html`) or its
   `<title>`. The canary is the sturdy test: a public space's answer also contains `auth-request`.

**A list that says "not private" is read again before anything halts** (`confirm_exposure`). On 30 September 2026 the
guard halted twice (14:42 and 15:22) on one read of the list saying "public" for a space that was private: reads
minutes later said private and a signed-out request got the sign-in page. So: the run logs the space's row (its `id`,
`visibility` and `updated_at` only), reads the list twice more 5 s apart (logging each row), then makes the signed-out
request. If any re-read says anything but private, or the request is not the sign-in bootstrap (the page, another
page, or no clear answer), it halts. If both re-reads say private and the request gets the sign-in page, it logs
"visibility misread once" and skips this run's deploy without halting. A signed-out request that serves the page halts
at once, with no re-read.

To halt: run `spacesheep share $UUID --visibility private` at once, write the reason into
`~/.cache/lab-dashboard/HALT`, log it, and stop deploying (runs still collect). While `HALT` is set, every run checks
the space (`halt_check`): the list must say private and the signed-out request get the sign-in page. After two runs in
a row that verify it, the run clears `HALT` itself ("auto-resume", logged; the next run deploys), at most once in 24
hours (`autoresume.last`). A second halt within 24 hours of the one before (`halt.times`) writes `HALT.sticky`: then
only a person's `update.sh resume` clears it, as does a halt that auto-resume may not clear. `update.sh status` and
the local `data.json` (a `collector` alert) show the halt; `status` also shows the verified count and a sticky halt.

Testing without spacesheep: a stub `LAB_DASH_SPACESHEEP` whose list answers a scripted sequence, a stub
`LAB_DASH_FETCH`, `LAB_DASH_REREAD_S=0`, scratch `LAB_DASH_CACHE` and `LAB_DASH_CONFIG`, and
`LAB_DASH_COLLECT_ARGS="--from-raw <testdata> --now ... --owner owner"`. On 30 September: public once then private
(misread: no halt, no share, no deploy; the next run deploys); public every time (halt; stays halted); the canary served
after a deploy (halt at once); two verified runs (auto-resume), then a second exposure within 24 hours (sticky; stays
after two verified runs); a change 1 minute after a deploy (skipped by the 10-minute floor).

What the guard cannot see: `spacesheep share --email` grants a person access while the space stays "private". Setting
the space private again is a visibility change, which AGENT.md reserves for the owner; the guard does it only to this
dashboard's own private space.

### 3.4 The log

`~/.cache/lab-dashboard/update.log`, one line per run:

```
2026-09-30T13:12:04-0700 run took=7.9s hosts=3/3 alerts=bad0/warn3/info7 fp=3fa2c1d09e4b deploy=skipped(unchanged; last 13:02)
```

---

## 4. The page: `page/` and `render.py`

### 4.1 Build

`render.py <data.json> <out.html> [--fixture]` does what `scripts/build-report.py` does, without the math step:
it reads `docs/reports/sources/report.template.html` and `docs/reports/sources/chartkit.js` (the shared template and
chart toolkit, unchanged), `page/body.html`, `page/script.js` and `page/meta.json`, and substitutes them. It
serialises the data with `json.dumps(...).replace('</', '<\\/')`, so no string in the data can close the script
element. The output is one self-contained HTML file with no external script, style, font or image; the page never
calls `fetch()`.

The template brings the colour tokens (light and dark, with `data-theme` overrides), the heading anchors that mirror
`#hash` to the viewer (`ss-hash`), and the footer link to the reports hub. The header's row of section links is a
`<nav id="toclist">`, so the template adds no contents list of its own; the body adds its own `<style>` block,
starting with `main{max-width:1280px}`, and a hidden SVG with the hatch pattern (`#cu-hatch`) the charts share.

### 4.2 Layout, top to bottom

1. **Header.** "AI Foundry lab" with a traffic light: a coloured dot plus a word, `HEALTHY`, `WARNINGS`,
   `NEEDS ATTENTION` or `STALE` (colour is never the only signal; the pill text is `--ink` on a tinted
   background, because `--warn` as text fails contrast on the light page). Beside it: "data as of 13:12 PDT (4 min
   ago) · checked every 10 min, republished on any change and at least every 60 min · next check about 13:22". A
   theme control (auto, light, dark) and "How to update" (a link to the page's "About this page").
2. **Overview strip: the lab at a glance.** Three machine boxes side by side (stacked on a phone). Each box's pill
   is the machine's state when it is not up (`DOWN` in the bad colour, `UNREACHABLE`, `APPROVAL NEEDED`) with "down
   since 14:33 (last answer 14:32; Tailscale last seen 14:33)", else its alerts (`2 WARNINGS`) or `OK`. Its cards are
   chips, in the registry's mark and colour, with the card's status word (`FREE`, `IN USE: <login> · <program> · since
   14:02`, `EXCLUDED`, `UNKNOWN: machine down` or `: no answer`, `NO DATA` when the page itself is stale, `MISSING`)
   and its last die temperature with its age; then the logins present on that machine as name chips with an active,
   idle or away dot (for a machine that is not up: "People: unknown now; at 14:32:" and the old chips, greyed). A
   click scrolls to that machine's panel and sets `#focus=<host>`. Below, a KPI row (`.kpis`): machines answering
   (and which are down); people logged in (overall, and per machine: "aifoundry1 unknown (down)"); active now; cards
   in use now (who, on which card); card use in the last 24 hours (people, time held); alerts by level.
3. **Alerts** (`h2`). The ranked list: level pill, scope chip (machine or card, with the card's mark), title, the
   time it started, and a `details` for the detail and source. Known and acknowledged alerts are folded into
   "4 known conditions" at the end. No alerts: one line, "No warnings." The header's headline names a down machine
   ("aifoundry1 DOWN since 14:33").
4. **Card use, last 24 hours** (`h2`, new on 30 September). From `usage` (§1.8), in the lab's time zone (PDT), whatever
   the viewer's: a legend (each login's colour, "others", "not logged" hatched, activity ticks, "now"), then one lane
   per card, aifoundry1 card 0 included (labelled excluded, since any use of it matters). A lane has the card's mark
   and name and its time held; a 24-hour axis with a tick every hour and a label every 3 (6 on a phone), midnight
   with the weekday; one bar per login's hold, coloured by login, at least 2 px wide so a run of seconds stays visible
   (bars of one login closer than 3 px are drawn as one, and say so), the login written in bars wide enough; thin
   ticks under the bar for minutes in which the card's queues moved; hatched spans outside the log's coverage, each
   with its reason (before its log begins, the logger was not running, machine down since 14:33, not known since the
   machine last answered); a dashed "now" line. A card whose machine has no log is one hatched lane saying "usage
   logging not installed on aifoundry3". Tooltips (`CK.tip`) give the login, start–end (with seconds under 10
   minutes), the held and node-open time, runs and programs; `CK.keynav` walks a lane's bars and gaps in time order,
   one tab stop per lane. Colours: the six series tokens, in their fixed order, go to the (at most six) logins with the
   most card time, in alphabetical order among them, so a colour follows a name; everyone else is "others" (`--ref`).
   The same colour marks a login everywhere on the page, and a name always travels with it (legend, labels,
   tooltips, tables); the six tokens pass the palette validator in both themes (light-mode contrast below 3:1 for three
   of them, hence the labels and tables). Under the chart: per card, "held 2 h 10 min of the 24 h (9%) by 3 people;
   busiest: user-a (1 h 40 min, 12 runs)", who holds it now, the minutes its queues moved, and what was not logged;
   "By person and card", a sortable table (login, card, held, share of 24 h, runs, programs, last use); and "The last
   7 days", a table of the time held per card and day with a small bar stacked by login (hover for who), "not logged"
   before a log began.
5. **Machines and cards** (`h2`). One panel per machine (a three-column grid at 1100 px and wider, one column below):
   - the header: name, the state or alerts pill, "up 11 d 21 h", kernel and a "reboot pending" chip; for a machine
     that is not up, a note "DOWN: down since 14:33 (last answer 14:32; Tailscale last seen 14:33). Everything below is
     the last known, at 14:32, not the present." and greyed vitals and tiles; after a reboot, "Rebooted 14:50 (a reboot
     was pending)" or "unplanned";
   - vitals, each with a 48-hour sparkline: load per thread, available memory, login sessions (all users), disk use
     bars for `/` and `/home` (and the ZFS pool), CPU and NVMe temperature, failed units;
   - **card tiles** (two on aifoundry1): the card's mark and label, status word and holder; a temperature gauge
     (a horizontal scale from 20 to 120 °C with marks at 65 °C, where the governor holds 600 MHz, and at 90 and
     100 °C, the card's normal idle band shaded, the value marker and its number, "38 min ago, from an experiment
     file" or "live sample 13:02" or "no reading in 7 days"); board watts against the idle band; clock with a
     policy chip (`DVFS`, `PINNED 600`, `FIXED 600`); firmware; link ("16 GT/s x8" with a check or "x4 of x8");
     corrected and uncorrected event counts with the change since the last check; the root port's corrected errors
     per hour; then the card's own lane of the 24-hour card use, smaller, with "Last 24 h: held 2 h 10 min (9%) by
     user-a, user-b" (or, with no usage log, the 48-hour strip of who held it at each check). A click opens the
     tile's detail: every number with its source, the sample state, the kernel-log counts, the last use, the guard
     marker on aifoundry3. aifoundry1 card 0's tile is muted and says "excluded (overheats): never touched; driver
     counters only";
   - the host footer: now (people logged in and active, device processes, CI jobs; "unknown" for a machine that is
     not up), the card-use logger's state, nodewatch (heartbeat age, gaps, logins); and "et-lab-health: 1 WARN,
     4 INFO" as a `details` with every line.
6. **People** (`h2`). A sortable, filterable table (`CK.sortTable`, stacked into labelled blocks under 600 px):
   login, status, doing (the categories of §1.4 as chips, "on a card" first), machines (with session and terminal
   counts, and per machine what they do when on several), idle, card now (card, program, since), card use in the last
   24 hours (per card, time and runs, with the login's colour), processes. Everyone the same way; no row is "you".
7. **Last 48 hours** (`h2`). A timeline chart: one row per machine (answered; down: Tailscale offline; no answer: ssh;
   approval needed; nodewatch gap; "alive (nodewatch only)" where the collector has no check but nodewatch's heartbeat
   ran), and one per card only for cards with no usage log (who held it at each check, in the login's colour; used;
   free; no data), with a line saying which cards are in "Card use" instead; a shared time axis, tooltips (`CK.tip`)
   and keyboard focus (`CK.keynav`); under it small multiples of die temperature and board watts per card (points
   only where a reading exists) and of login sessions per machine.
8. **About this page** (`h2`). Where the data comes from, the cadence, the privacy rules in two sentences, how to
   update it (§7), and the collector's `code`, `took_s` and `errors`.

The body has six `h2` headings; the header's section links are the page's own `#toclist`, so the template adds no
contents list of its own.

### 4.3 Interaction and state

- UI state in the hash, limited to the characters the viewer accepts (`[A-Za-z0-9_.=%&/-]`): `#focus=aifoundry1-c1`
  opens and scrolls to that tile or panel; the template's `ss-hash` message mirrors it to the viewer, which restores
  it after every reload, so a selection survives the automatic refresh. Plain heading anchors keep working.
- The theme control sets `document.documentElement.dataset.theme` and remembers the choice in `localStorage`
  (inside `try`/`catch`); `?theme=` also works. Nothing is set when no choice was made, so `DARK=1` and `DARK=os` in
  `check_page` behave.
- Sparklines and the timeline have tooltips; the people table sorts and filters; alerts and host health lines
  expand. All of it works from the keyboard.
- `CK.reduced` turns off the gauge animation.

### 4.4 Refresh on the page

The viewer reloads the frame on every deploy. The page only keeps time and covers the cases the viewer misses:

- It shows `generated_at` in a `<time datetime>` element in the viewer's zone, and the age, updated every 30 s.
- `STALE` replaces the traffic light, with a banner, when the age exceeds `collector.stale_after_min` (80: the
  60-minute heartbeat, one missed run, 10 minutes' slack). The light then reads "STALE · was NEEDS ATTENTION" (what
  the data said), every card reads `NO DATA` ("was free at 13:12") instead of `FREE`, and "next check" reads
  "unknown, the collector may be stopped". The banner says the collector on aifoundry2, its cron job or the deploy
  may be stopped, and how to check (`update.sh status`). A tab that crosses the threshold while open re-renders.
- "Next check about HH:M2" is the next slot of the cron schedule after now.
- The light is a live region (`role="status"`): it is rewritten only when its word changes.
- A fallback reload, only when `location.protocol` is `https:` and the host name ends in `.spacesheep.app` (so a
  local `file://` render, as in `check_page`, never navigates): on `visibilitychange` to visible after the tab was
  hidden for more than 2 minutes, or when a 60 s timer notices the clock jumped (the machine slept), or when the age
  passes `stale_after_min`; and never more than once in 5 minutes (the time is kept in `sessionStorage`, inside
  `try`/`catch`). It reloads with `location.replace(location.origin + '/' + location.hash)`, which loads the newest
  version; never `location.reload()` (it would reload the framed, fixed version), a relative URL or `?v=`.
- No timer fires in the first 6 s after load, so `check_page` sees a still page.

### 4.5 Look

The repository's report look: `system-ui` 16 px, `tabular-nums` for numbers, `.card` panels, `.kpis`, `.chip`
pills, colour tokens only (no hex values in page code), status as dot plus word. Every `p`, `span`, `b` or `td` with
an id is filled, with "—" for a missing value. No sideways scroll at 390 px: the grid collapses to one column, card
tiles to one per row, the table stacks, and the timeline keeps its labels outside the plot. Dark mode through the
template's tokens.

---

## 5. Health rules

The collector computes levels; the page only displays them. Thresholds live in `collect.py` as one table. Titles
carry clock times, not ages ("aifoundry1 DOWN since 14:33", "held by user-c since 12:48"), so they stay true on
a page that is shown for a while. "New since the last check" and a hot die need this run's data: they are never
raised from a machine that did not answer. aifoundry1 card 0 gets no telemetry at all (§2.4), not even an old
experiment file's.

| Scope | `bad` | `warn` | `info` |
|---|---|---|---|
| collector | privacy refusal; `HALT` set | a parse error; a host skipped for back-off | card sampling on |
| host reach | down (Tailscale: offline), from the first run; unreachable 2 runs in a row | unreachable once; "approval needed" | |
| host | disk or pool ≥ 97%; nodewatch heartbeat older than 30 min while the host answers | any et-lab-health WARN not known or acknowledged (disk ≥ 85%, degraded systemd, pool state, lock file, driver); memory available < 10%; load per thread > 1.5; nodewatch heartbeat older than 5 min; a reboot that was not planned (no reboot pending at the answer before it), for 24 h; the card-use logger stopped (`stale`), installed but not running, or failing | reboot pending; a planned reboot, for 24 h; card-use logging not installed; ZFS scrub errors; CI runner jobs running; each INFO health line worth showing |
| card | missing from the bus; uncorrected events (new); link down; a live die ≥ 100 °C; the sample disabled (a timeout, a kill, or a sample cut off: §2.6) | link below its maximum; new corrected events since the last run; a live die ≥ 90 °C; held by the same process over 2 h; any hold of an excluded card (aifoundry1 card 0), now (`held`) or in the last 24 hours (`used-24h`) | held (who, which program, since when); used since the last check (who, programs, from the usage log where there is one); the aifoundry1 card 0 conditions (known) |

A card's level is its worst alert (`excluded` for aifoundry1 card 0, `unknown` when its host did not answer); a
host's is its worst alert including its cards'; the cluster's is the worst of all. Known conditions shipped in
`lab.json` are aifoundry1 card 0's corrected events and its root port's error rate. Acknowledgements are made with
`update.sh ack` by whoever runs the dashboard; an acknowledgement expires after its days. Until 30 September there
were also rules for the owner's own sessions (tmux, Claude, claudes logins) and "our experiment"; they are gone with
that data.

---

## 6. Privacy and safety rules

Hard rules; the build pass implements each one and the README repeats them.

**The page and the space**

- The space is **private** (`--visibility private` at creation), checked after every deploy (§3.3). It is listed in
  MIRROR.md's private table so `check-mirror.py` checks that it is not served anonymously; its page is never
  mirrored into the repository.
- The page names lab users, so it is never made public and never linked from a public page.

**What is never collected** (the probe drops it on the host where possible, and the collector rejects it anyway)

- IP addresses, host names of peers, tailnet identities: `who -u`'s host column, loginctl `RemoteHost`, nodewatch's
  `from=`, `(machine/login)` and `path[...]` fields, its `state/` files, the Tailscale check URL. Of `tailscale status
  --json` only each lab host's `Online` flag and `LastSeen` time are kept: never addresses, MagicDNS or host names,
  tags, users, or any other peer (they are dropped while parsing, and the raw output is not stored).
- Anyone's command lines, arguments, working directories, files, home directories, groups, sudo or root status, and
  where they log in from. A person appears as a login name with session, terminal and process counts, idle time,
  card holds and card use, and **what they are doing as coarse categories** (on a card, AI agent, building,
  simulator, Python, editor, shell only: §1.4). The categories are worked out by `remote.sh` on the host from `ps`'s
  `comm` (the process name, 15 characters); only the category keys leave the host, never a process name. The one
  exception: the program name (`comm`) of a process that holds a card, and card use (login, card, times, program
  names, run counts) from `et-usage`, which `et-who` and `et-usage` already show to every user of that host.
  Device processes and CI jobs appear only as counts. Root and system accounts are not listed as people; a card held
  by root shows as "system or CI".
- Nobody is singled out: the collector's own account is one login among the others, with no "you", no row of its
  own, and none of its sessions, agents' titles or accounts (until 30 September the page showed the owner's Claude
  logins and sessions from `claudes status` and `spacesheep sessions list`; the collector no longer runs them).

**The privacy check.** Before `data.json` is written, `collect.py` walks every string: free text (health lines, log
lines, program names) first goes through a scrubber that removes IPv4 and IPv6 addresses, e-mail addresses, URLs,
`*.ts.net` names and `/home/<name>/` paths other than the collector account's tree; then a checker refuses the whole file
(exit 3) if any of those patterns remains anywhere. Logins must match `^[A-Za-z0-9._-]{1,32}$`.

**The repository boundary.** Only code, `lab.json`, the page source, the made-up `fixture.json` and `testdata/`
(invented logins such as `owner` and `user-a`, invented Tailscale output), and docs go into the repository. The collected data, history,
state, raw outputs, log, the space uuid and any ssh overrides stay in `~/.cache/lab-dashboard/` and
`~/.config/lab-dashboard/`. The survey outputs in the session scratchpad are not copied anywhere.

**The hosts and the cards**

- Read-only everywhere: no card node is opened, no card attribute outside §2.4 is read, nothing is written on a host
  but the sample stamp (§2.6). No root; the only privileged step is the lab's `sudo -n et-holders` inside `et-who`.
- Cheap and quiet: one ssh per host per run, `nice -n 10 ionice -c3`, every command under `timeout`, about a second
  of CPU per host. The collector's own ssh session is left out of the counts.
- Nobody's tmux or Claude is touched: the dashboard never calls `tmux` or `claudes`.
- The card sample (§2.6) follows the card etiquette: off by default; never aifoundry1 card 0; `et-who --check` free;
  no framework runner or device process of the collector's account, no other user's device process or CI job, no
  other user active; the card's lock with
  `flock -n`; `timeout -k 3 10`; a 2 s sample; at most once per 10 minutes per card (default 30); on aifoundry1 only
  a build whose libraries honour `ET_DEVICES=1`; no retry, no drain, and a timeout disables sampling of that card
  until a person clears it.
- `spacesheep update` is never run; the CLI's update notice is ignored.

---

## 7. Updating on demand

- **On aifoundry2:** `tools/lab/dashboard/update.sh now` (in the checkout, `~/claude/et-soc1-prototyping`). It
  collects, renders, deploys even if nothing changed, checks visibility, and prints the headline, the alerts and the
  page's address; open viewer tabs update within seconds. `update.sh now --card-sample` also takes the telemetry
  sample, still behind every gate of §2.6.
- **From another machine:** `ssh aifoundry2 claude/et-soc1-prototyping/tools/lab/dashboard/update.sh now`.
- **Asking Claude** in the aifoundry2 session ("refresh the lab dashboard", "why is aifoundry1 amber?", "take a card
  sample on aifoundry3"): Claude runs `update.sh now` (with `--card-sample` only when asked), reads
  `~/.cache/lab-dashboard/data.json`, and answers from it. `update.sh ack` and `update.sh status` are there for the
  same use.
- **When a machine shows "approval needed":** run `ssh aifoundry1 true` on aifoundry2 and approve the URL it prints
  (or ask Claude to hand it over), then `update.sh now`.

---

## 8. Build order and acceptance (one pass)

1. `lab.json`, `remote.sh`, `collect.py` with `--from-raw`; `testdata/` with invented raw outputs, one per host,
   including an unreachable host, a held card, a stale nodewatch and an et-lab-health WARN.
   - `python3 collect.py --from-raw testdata --out $T` writes a `data.json` with every field of §1, and injecting an
     IP address or an e-mail into a raw file makes it exit 3.
2. A real collection with the sample off: `python3 collect.py --out $T` finishes in under 15 s with all three hosts
   or with a clear `error`, and a local `strace -f -e trace=openat` of the aifoundry2 probe shows no `/dev/et` path
   opened. `--card-sample --sample-dry` prints each card's gates and the command, and runs nothing.
3. `page/` and `render.py`; `fixture.json`. `check_page.sh` on the fixture page and on a real one at 1280 and 390 px,
   with `DARK=1` and `DARK=os`: no errors, no empty fields, no sideways overflow.
4. `update.sh` with no space configured: a `run` renders and logs "no space configured", `now` says the same,
   `--install-cron` and `--uninstall-cron` round-trip the crontab (tested and removed; the main session installs it
   for real), a second `run` while one holds the lock exits at once. `bash -n update.sh remote.sh`, and `shellcheck`
   if present.
5. `README.md`. Then the main session: `update.sh create-space`, the first deploys with the visibility guard, a check
   that an open viewer tab reloads on a CLI deploy (a changing build stamp), the first real card sample, the cron
   line, MIRROR.md's private row, and the registers (a request in 02, an artifact in 04, `docs/lab-access.md`).

## 9. Left out, or for later

- **Fetching data instead of redeploying**: rejected. A relative fetch inside the viewer's `/v/<sha>/` frame is
  frozen to that version, root files are cached for 300 s, and a private page's fetch fails wherever third-party
  cookies are blocked (Safari).
- **spacesheep's `edit` or `live_push`** to change only the data block, or push to open tabs without a new version:
  possible later, not needed now.
- **A per-host cron agent** that keeps card history while ssh needs approval: nodewatch already keeps the host
  series; card series pause while a host is unreachable.
- **Installing et-lab-health rev 3** on the hosts would let the probe call it instead of streaming it; that is an
  admin step for the owner and the lab.
