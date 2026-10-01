# et-usage: who used the ET-SoC-1 cards, and when

A small logger for the AI Foundry lab hosts. `et-usaged` (a daemon under systemd, as the `et-usage` system user)
records every process that holds a card node or a card lock; `et-usage` (any user) prints who used each card, for how
long and with which programs, and gives the lab dashboard its data (`et-usage --json`). Written 30 September 2026;
hardened the same day after a review (security, card safety, correctness).

| File here | Installed as | Mode |
|---|---|---|
| `et-usaged` | `/usr/local/sbin/et-usaged` | 0755 root |
| `et-usage` | `/usr/local/bin/et-usage` | 0755 root |
| `et-usaged.service` | `/etc/systemd/system/et-usaged.service` | 0644 root |
| (written by `install.sh` if absent) | `/etc/default/et-usaged` (`ET_USAGED_ARGS=...`, per host) | 0644 root |
| | `/var/log/et-usage/<YYYY-MM-DD>.jsonl`, one file per local date | dir 0755, files 0644, user et-usage |
| | `/var/log/et-usage/open.json`, the open holds (for a crash); `.et-usaged.lock` (one writer) | 0644 et-usage |
| | `/run/et-usage/now.json`, the current holders (removed when the service stops) | dir 0755, file 0644, et-usage |
| `install.sh` | run as root from this directory | |
| `test/test_et_usage.py` | the tests (as any user, on scratch files) | |

## What it logs

For each process that holds a card's `/dev/et<N>_mgmt` or `/dev/et<N>_ops`, or holds the flock on
`/run/lock/etsoc-shire<N>.lock`, one record when it stops holding that card: its login and uid, pid, `comm` (the
kernel's 15-character program name), its parent's `comm`, which nodes it held, whether it held the lock, and when
(start, end). With `flock -n <lock> timeout 10 <prog>`, that is three records: `flock` and `timeout` (lock only) and
the program (nodes and lock). A process that only waits in `flock` (without `-n`) for another user's lock, or holds the
lock file open without locking it, holds nothing: a lock-file fd counts only while it holds the lock (the `lock:` line
of its `/proc/<pid>/fdinfo`, present for the flock holder and every process sharing its open file, absent for a
waiter). Every 60 s, the change in the driver's submitted-message counters (`act`); every 10 min a heartbeat (`beat`).

How: inotify watches on the nodes, on the lock files of the cards that have a node, and on `/dev` and `/run/lock`
(for a node removed or recreated by a driver reload); on an event, after 20 ms, and every 15 s as a safety net, a
scan of every process's `/proc/<pid>/fd` links. Scans: at most 10 a second, and a scan starts at least 10 times its
predecessor's CPU time after it (at most 10% of a core, however many files the host has open; CPU time, so a busy
host that merely delays the scan does not slow it); events on lock files alone (every `flock -n` poll) start at most
one a second.

## What it never does

- **Never opens a card node** in any way (not `open()`, not `O_PATH`, not a read). `inotify_add_watch` and `lstat`
  look the path up and check permissions; they do not open the device. Checked with `strace` on aifoundry2 (30 Sep):
  its only opens under `/dev` are the directory itself (to list names).
- **Never reads a card attribute** other than `devnum` and `{mgmt,ops}_vq_stats/msg_count` (driver counters in host
  memory); never `utilization_percent` (it syncs queue pointers from the card), `resource*`, `config`; never writes
  to sysfs. Cards given to `--skip-counters` have their counters never read; a PCI function given to `--skip-pci`
  (aifoundry1's card 0, `0000:01:00.0`) has nothing at all read, not even `devnum` (the lab's rule, DESIGN.md §2.4,
  and card numbers can move if a card fails its probe). Every run on a host, the service's or a manual `--once` or
  `--foreground`, also skips what `/etc/default/et-usaged` skips; if that file exists but cannot be parsed, no counter
  is read at all.
- **Never reads a process's arguments**, environment, working directory or files: only `/proc/<pid>/stat` (comm,
  parent, start time), the `Uid:` line of `status`, `comm`, the fd link names, the fdinfo of an fd on a lock file,
  and `maps`: at start, and at most every 10 s after a node open that no scan explained, the maps of every process
  are searched for the node paths (a node mapped into memory stays held after its fd closes); only a match (card and
  node) is kept, nothing else from them.
- **Never runs as root** under systemd: the `et-usage` user with `CAP_SYS_PTRACE` and `CAP_DAC_READ_SEARCH` only (to
  read other users' fd links, fdinfo and maps). Never runs a program and never talks to the network
  (`PrivateNetwork=yes`, AF_UNIX only).
- **Never trusts names others control.** `/run/lock` is world-writable: lock names are never globbed there (only
  `etsoc-shire<N>.lock` for a card N that has a node), a path counts only if `lstat` says it is a regular file (or,
  for a node, a device), never a symlink, and watches use `IN_DONT_FOLLOW`. Program and user names are made printable
  (control and escape characters become `?`) where they are read, so no record, `now.json`, terminal line or
  dashboard field carries them.
- **Never grows without bound.** A process's fd table is streamed and read up to `--max-fds` (65,536) entries, and
  its `maps` in 256 KB pieces up to 16 MB (`stats.maps_truncated`; `vm.max_map_count` is 1,048,576 on the lab hosts,
  so one process's maps can be GBs: read whole, 100,000 mappings of a long path took 200 MB, over `MemoryMax=64M`); at
  most 4,096 holding processes are tracked (a fork flood beyond is counted in `stats.holds_dropped`); `now.json` lists
  at most 1,000 holds. The log directory stays under `--max-log-mb` (500): the oldest days are removed first (never
  today's). If today's file alone is over it, or the log's filesystem has under `--min-free-mb` (512 MB) free, the
  daemon writes no records until there is room (`now.json` says `"paused"`, and counts them in `stats.dropped`). Low
  free space never removes a file: the disk is shared (on aifoundry1 `/var/log` and `/home` are one ZFS pool, 95%
  full), and a user who fills it must not erase the history.

## Privacy

The logs name the lab's users and the programs they ran on the cards, with times. They are world-readable **by
design**: every user of the host can already see the same thing live with `et-who` (which shows even the full
command lines; this log keeps only the 15-character program name). Nothing leaves the host except through
`et-usage --json` when the lab dashboard asks for it. Tell new users that card use is logged (the New user page and
`et-lab-start` do).

## The records (format version 1)

JSON lines; times are epoch seconds (3 decimals); the file date is the host's local date of the record's `at` (or
`end`). A reader skips records of another `v` and ignores record types and fields it does not know.

```json
{"t":"start","v":1,"at":1790807400.125,"host":"aifoundry2","boot":"<boot id>","pid":4321,"cards":[0],"watch":["/dev/et0_mgmt","/dev/et0_ops","/run/lock/etsoc-shire0.lock"],"sees_all":true}
{"t":"hold","v":1,"card":0,"pid":5555,"user":"alice","uid":1001,"comm":"sgemm_host","parent":"timeout","nodes":["mgmt","ops"],"lock":true,"start":1790807401.310,"end":1790807403.902}
{"t":"hold","v":1,"card":0,"pid":null,"user":"?","uid":null,"comm":"?","parent":"?","nodes":["ops"],"lock":false,"start":1790807410.101,"end":1790807410.104,"unseen":true,"opens":1,"lock_user":"alice"}
{"t":"act","v":1,"card":0,"at":1790807460.000,"s":60.0,"mgmt":12,"ops":340}
{"t":"beat","v":1,"at":1790808000.000,"holding":1}
{"t":"watch","v":1,"at":1790808100.000,"cards":[0],"watch":["..."],"added":["/dev/et0_ops"],"gone":[]}
{"t":"clock","v":1,"at":1790808200.000,"step":-3.2}
{"t":"stop","v":1,"at":1790809000.000,"why":"SIGTERM"}
```

- `start`: `sees_all` is true when the daemon can read every process's fd links (false: it sees only its own user's
  processes; install.sh fails on false).
- `hold`: one per (process, card). `start` is the time of its open event (a holder whose open no event showed, such as
  a child that inherited the fd and was found by the 15 s scan, has `"late":true` and starts at that scan); `end` is
  the close event that ended it, or the last scan that saw it. `lock` is true if it held the flock at some point.
  `"pre":true`: held when the daemon started (`start` = the daemon's start). `"cut":true`: still held when the daemon
  stopped (`end` = the stop). `"lost_end":true`: still held when the daemon died without SIGTERM (SIGKILL, the OOM
  killer, a host hang or power loss); the next start writes it from `open.json`, `end` = the last time the dead daemon
  recorded it held (at most a minute before it died, usually a second). `"map":true`: at some point held the node only
  through a memory mapping. A process is identified by pid and its start time, so a reused pid is a new hold.
- **Unseen holds** (`"user":"?"`, `"unseen":true`): a node opened and closed between two scans (in under ~20 ms), so no
  scan saw who. Per card and node the daemon compares the batch's open and close events with the holders that
  appeared and went; a node opens once at a time (the driver answers EBUSY, which makes no event), so a holder's own
  close and reopen is not counted. Unseen opens of a card less than 0.5 s apart join one record (at most 60 s long,
  written about a second after its last close): `opens` = how many, `start` = the first open, `end` = the last close,
  so a poller at 20 Hz writes one record a minute, not ten a second. `lock_user` is a hint, not the user: every
  process holding that card's lock around the event belonged to that login (records with different hints never
  join). An open and close of only a lock file writes nothing (every failed `flock -n` does that).
- `act`: the change of the submitted-message counters (the `SQ*`/`HpSQ*` lines of `msg_count`, as the dashboard counts)
  over `s` seconds; only when one moved. A counter that went down (a driver reload), or rose by more than a million
  messages a second (the driver frees the queue arrays before it removes their sysfs group, so a read during an MM
  reset can see garbage), restarts the baseline and writes nothing.
- `watch`: the watched set changed (a node removed or recreated). `clock`: the wall clock stepped (it is checked
  before any time is taken in a pass, and after each scan); open holds were moved with it so their lengths stay right.

`now.json`: `{"v":1,"host":...,"at":...,"started_at":...,"pid":...,"boot":...,"cards":[0],"holds":[{"card":0,"pid":5555,"user":"alice","uid":1001,"comm":"sgemm_host","parent":"timeout","nodes":["ops"],"lock":true,"start":...}],"sees_all":true,"stats":{"scans":...,"events":...,"overflows":...,"unseen":...,"last_scan_ms":...,"max_scan_ms":...,"last_scan_cpu_ms":...,"fd_truncated":...,"maps_truncated":...,"holds_dropped":...,"dropped":...}}`,
rewritten (tmp + rename) on each change and every 60 s. `nodes` and `lock` there are what it holds now. Also
`holds_more` (holds beyond the 1,000 listed) and `paused` (why records are not being written), when they apply.

`open.json` (in the log directory): the open holds as the hold records they will be, rewritten at most once a second
on a change and every minute; removed on a clean stop. If the daemon dies without SIGTERM, the next start writes its
holds with `lost_end` before its own `start` record, so the dead run's coverage reaches their end.

## The CLI

```
et-usage                        # the last 24 h per card: who, how long, which programs; who holds a card now
et-usage --since 7d --daily     # a week, with a line per day (also 2h, 30m, 2026-09-30, "2026-09-30 14:00", an epoch)
et-usage --card 0 --user alice
et-usage --raw --since 1h       # the records themselves
et-usage --json --since 26h [--gap 5]   # for the dashboard
```

Times print in the host's local time. `--json` gives one object: `v`, `host`, `now`, `since`, `daemon`
(`state`: `running` if now.json is under 3 min old, `stale`, or `absent`; `alive_at`, `started_at`, `stopped_at`
after a clean stop, and `paused` when it is not writing records), `logging_since` (the oldest record kept), `coverage`
(the spans the daemon ran: a `start` with no `stop`, or 15 min without a record, ends a span at its last record; a
running daemon's last span reaches now only if its last record is under 15 min old, so a daemon that hung and came
back shows the hang as not logged; a recorded forward clock step does not split a span; time outside is "not logged",
never "idle"), and per card: `intervals` (per user, the union of their holds, gaps of up to `--gap` s merged, with
`node_s`, `lock_s`, `procs`, `programs`, `"open":true` for a hold still open, `"lost_end":true` if one of its holds
lost its end in a crash, and on a `"?"` interval `lock_user` when all its hints name one login), `activity`
(`[at, s, mgmt, ops]`), `users` (totals: `held_s`, `node_s`, `lock_s`, `runs`, `programs`, `first`, `last`, and for
`"?"` `lock_users`: `{login: opens}`), `held_s`, `node_s`, `now`, `daily` (the last 7 local dates, per user). Also
`skipped` (unreadable or other-version lines), `gap_s`, `logged_s` and `daily_logged_s` (logged seconds per date).
`held_s` counts the union of a user's holds (flock, timeout and the program at once count once); `runs` counts
node-holding processes (an unseen record counts its `opens`; a `lost_end` hold and the same hold written again
count once).

Bounds: the whole `--json` output stays under 200 KB. Past that, intervals are merged across longer gaps (then
`merged_gap_s` is set, at the top and on every card), the activity is summed in bins (`activity_bin_s`: 300, 900,
... s; an entry is `[the bin's last at, total s, mgmt, ops]`), and as a last resort programs lists are cut to their
largest entries plus `"(others)"` and `now` lists to their first entries (`now_more`: how many more). The log is
read streamed, newest first, up to `--max-read-mb` (64 MB; 0 for all): about 2.5 s and 100 MB of memory for 42 MB of
log on aifoundry2. If the budget cuts the log, `truncated_before` gives the time before which nothing was read (there
is no coverage before it); `et-usage` says so.

## Install, check, remove (root, on each host)

```
sudo tools/lab/et-usage/install.sh                      # aifoundry2, aifoundry3
sudo tools/lab/et-usage/install.sh --skip-counters 0 --skip-pci 0000:01:00.0   # aifoundry1; refuses without both
sudo tools/lab/et-usage/install.sh --check              # installed files (sha256), user, capabilities, now.json, journal
sudo tools/lab/et-usage/install.sh --uninstall          # stop, disable, remove programs and unit; keep logs and config
sudo tools/lab/et-usage/install.sh --purge              # also the logs, /etc/default/et-usaged and the et-usage user
tools/lab/et-usage/install.sh --check-source            # any user: could anyone but root and you change these files?
```

Install is idempotent. It refuses unless only root and the admin running sudo can change the files it installs (each
file and every directory above them: not writable by another user or by a group with other members;
`--trust-source` overrides), creates the `et-usage` system user if absent, copies only changed files (install to
`.new`, then rename), writes `/etc/default/et-usaged` only if absent, makes `/var/log/et-usage` (0755, et-usage),
reloads systemd, enables the service and starts it (restarts it if a file changed), then checks that it is active,
that `now.json` appears within 10 s from the service's pid with `"sees_all": true` and the card nodes watched, that
today's log has its start record, and that `et-usage` runs as `nobody`. After a change, run `--check` on each host.
Do not run `et-usaged` by hand as root without `--once` or `--stdout`: it refuses to write the service's log
directory (a root-owned file there would stop the service appending), and a second writer of one directory exits.

The unit (`systemd-analyze verify` clean on systemd 255; `systemd-analyze security` 4.7): `User=et-usage`,
`AmbientCapabilities` and `CapabilityBoundingSet` both exactly `CAP_SYS_PTRACE CAP_DAC_READ_SEARCH`, `Nice=10`,
`IOSchedulingClass=idle`, `NoNewPrivileges`, `ProtectSystem=strict` with only the log directory writable,
`ProtectHome`, `PrivateTmp`, `PrivateNetwork`, the kernel protections, `MemoryMax=64M`. Not `DynamicUser` (its logs
directory would be under `/var/log/private`, 0700). Not `PrivateDevices`, `DevicePolicy`, `DeviceAllow` or
`ProtectClock` (implies a device allow-list): a device allow-list also refuses the inotify watch on `/dev/et*`. Not
`ProtectProc`/`ProcSubset`: the scan needs every process. A crash loop stops after 10 starts in 10 min.

## Cost

Idle, it sleeps in `select`. A scan reads one link per open fd of every process: about 1.5-2.6 µs each in Python on
aifoundry2, plus some per process (30 Sep, as root: the 2,200-3,000 open files of today's hosts take about 5-10 ms,
7,300 about 20-40 ms). Scans happen on card events and every 15 s; the pacing above holds them to at most 10% of one
core even on a host with 100,000 open files (measured before the pacing: 13% of a core with 7,400 fds visible and 20
node opens a second, 89% with 100,000), and a `flock -n` poll loop to one scan a second. An ordinary run costs a few
scans; a queue of short runs back to back costs up to that 10% (5-13% was measured on today's hosts before the
pacing); idle, well under 1%. Memory about 18 MB as a test user (VmHWM), flat with a process of a million fds or 200 MB of maps. Log
volume about 200 bytes per hold record, about 3 records per `flock ... timeout ... prog` run, plus about 6 KB a day
of heartbeats and counters; a queue of 50 ms runs back to back all day would write about 560 MB, which the 500 MB
cap keeps in check, with 90-day retention by age (never one of the newest 90 files, so a clock far ahead empties
nothing).

## Tests

`python3 tools/lab/et-usage/test/test_et_usage.py --dir <scratch dir>` as any user (about 50 s): unit tests of the
daemon's core (pid reuse, clock steps during `select` and during a scan, rotation at local midnight, the unseen-open
accounting and its races, a holder's own reopen, a stale carried open, unseen records merged per burst and per lock
holder, scan pacing, lock names only for cards with a node and never through a symlink, printable names, the counter
race, the host's defaults file, retention with a clock 400 days ahead, the size cap and free-space floor (which removes no
file), `maps` read in pieces and only to 16 MB, `open.json` recovery); the daemon run in `--foreground` on scratch files, twice (the flock pattern, a holder present at start,
quick unseen opens, counters up, down and skipped, a node deleted and recreated while held, a forked late holder, 40
short runs, 40,000 opens, a holder in another PID namespace, SIGTERM while holding; a waiter in `flock` and an unlocked
open of the lock, a program named with terminal escapes, 300 junk lock names and a symlinked one, a lock poller, a
process with a million fds, SIGKILL and restart, a second writer, `--once` with a defaults file), under an audit hook
that fails the test if it opens a node, any sysfs file outside the allowed list, a skipped card's counters, or
anything of a `--skip-pci` card; `et-usage` on those logs and on synthetic ones (gap merging, coverage with a stopped
span, a silence, a crash, a hang and a clock step, daily across midnight, time zones, open holds, stale and absent
daemons, a busy day, the 200 KB bound on one and two cards, `lock_user`, `lost_end`, escapes in names, 42 MB of log
and the read budget); the unit file (`User=`, the two capabilities, `systemd-analyze verify`) and
`install.sh --check-source`.
