# tools/lab/dashboard: the lab dashboard's collector and updater

A private page on spacesheep.dev that shows the AI Foundry lab at a glance: the three machines, the four cards, the
people using them and the owner's own sessions, refreshed every 10 minutes. The design, with the data model, the
health rules and the reasons behind each choice, is [DESIGN.md](DESIGN.md). This file is the manual.

| File | Role |
|---|---|
| `collect.py` | the collector: probes the three hosts in parallel, parses, applies the privacy filter, derives alerts, history and a fingerprint, writes `data.json` |
| `remote.sh` | the read-only probe run on each host (`bash -s` over ssh; locally on aifoundry2) |
| `update.sh` | collect, render, deploy when something changed, check that the space is still private, log; cron, acknowledgements |
| `lab.json` | static facts: hosts, cards, firmware, clock policy, idle ranges, known conditions. No personal data, no access paths |
| `page/` | the page and its `render.py` (see `page/README.md`); `update.sh` runs `page/render.py <data.json> <out.html>` |
| `testdata/` | invented probe outputs (`raw-<host>.txt`, `claudes.txt`, `sessions.json`) for `collect.py --from-raw` |

Everything collected lives outside the repository: `~/.cache/lab-dashboard/` (mode 0700: `data.json`,
`history.jsonl`, `state.json`, `raw/<host>.txt`, `update.log`, `deploy.state`, `lock`, `collect.lock`, `HALT`) and
`~/.config/lab-dashboard/` (`space` holds the space's uuid; `config.json`; `ack.json`; `crontab.bak`).

## Using it

All commands run on aifoundry2, in the checkout (`~/claude/et-soc1-prototyping`).

```
tools/lab/dashboard/update.sh now                  # collect, render and deploy at once; prints the headline, the alerts, the address
tools/lab/dashboard/update.sh now --card-sample    # the same, plus the optional card telemetry sample (below)
tools/lab/dashboard/update.sh status               # last data, last deploy, HALT, the cron line, the space's visibility, the log
tools/lab/dashboard/update.sh ack <alert-id> [days] [note]   # acknowledge an alert (7 days by default); unack <alert-id>
tools/lab/dashboard/update.sh --install-cron       # the automatic refresh; --uninstall-cron removes it; --dry-run on either prints only
                                                   # (only the tagged line changes; a copy goes to ~/.config/lab-dashboard/crontab.bak)
tools/lab/dashboard/update.sh sample-reset <card>  # re-enable a card's sample after a timeout was looked at
tools/lab/dashboard/update.sh resume               # clear HALT once the space is private again
tools/lab/dashboard/update.sh create-space         # once: the first private deploy; records the uuid
python3 tools/lab/dashboard/collect.py             # collect only (prints a summary); --help for its options
```

From another machine: `ssh aifoundry2 claude/et-soc1-prototyping/tools/lab/dashboard/update.sh now`. Asking Claude in
the aifoundry2 session ("refresh the lab dashboard", "why is aifoundry1 red?") works the same way: Claude runs
`update.sh now` and answers from `~/.cache/lab-dashboard/data.json`. Alert ids (for `ack`) are in `data.json` and on
the page, for example `host:aifoundry1:disk:/home`.

**Cadence.** The cron line is `2-59/10 * * * * .../update.sh run` (minute 2 of every ten, off the minute boundary
where nodewatch and the claudes watchdog run). A run deploys only when the fingerprint changed (a state change, not a
drifting number) or the last deploy is 60 minutes old; `now` always deploys. The spacesheep viewer reloads open tabs
on every deploy; the page reads STALE after 80 minutes without a new version. Runs never overlap: `run` exits at once
if another run holds the lock, `now` waits up to 60 s. `et-lab-health` runs hourly on each host (`now` runs it
everywhere). Expect 30–60 versions a day (DESIGN.md §3.2); the CLI cannot delete old versions, only the whole space.

**When a machine shows "approval needed".** Tailscale SSH's check approval lasts about 12 hours. The collector
recognises the prompt, stops its own ssh client, never keeps the URL, and then tries that host once an hour (`now`
always tries). Run `ssh aifoundry1 true` on aifoundry2, approve the URL it prints, then `update.sh now`. Meanwhile the
host's last data stays on the page, marked stale, and nodewatch keeps its host history.

**Every deploy keeps a copy of the page, login names included.** Only deleting the space removes them.

## What it reads, and what it never does

`remote.sh` reads `/proc`, the driver's sysfs counters (the list in DESIGN.md §2.4), `et-who` (the lab's
`sudo -n et-holders`, the only privileged step), logind sessions, terminal idle times, process counts, nodewatch's
logs, the newest experiment telemetry files in the host's tree, `et-lab-manifest`, and the repository's
`et-lab-health` rev 3 (sent inside the probe, installed nowhere). One ssh per host per run, under `nice -n 10 ionice
-c3`, every command under `timeout`; a run takes about 1–4 s of wall time for all three hosts.

It never opens a `/dev/et*` node (checked with `strace` on aifoundry2), never reads `utilization_percent` (it syncs
queue pointers from the card), never reads anything of aifoundry1's card 0 but its link, `err_stats` and its root
port's error count, never writes on a host (except the sample's stamp file), never calls `tmux`, and never runs
`spacesheep update`. The card activity flag counts only the submission queues (`SQ*`, `HpSQ*`): the completion
queues also count the card's own asynchronous events, so they move with nobody using the card.

## The optional card telemetry sample

Off unless `--card-sample` is given (or `"card_sample": true` is in `config.json`). `collect.py --sample-dry` runs
every gate on every host and prints the command it would run, running nothing. When on, per host and run, at most
one card, and only when every gate holds, checked on the host right before, in this order (DESIGN.md §2.6 has the
reasons); a gate whose own command fails or times out fails:

1. **card**: not aifoundry1 card 0 (refused in `collect.py` and again in `remote.sh`); at its `lab.json` address with
   its devnum; on a host with more than one card only through `ET_DEVICES` naming it, and on aifoundry1 only card 1;
2. **boot** (several cards): this boot's id equals `config.json`'s `"sample_boot": {"aifoundry1": "<boot id>"}`, set
   by a person who checked the card numbering on this boot. A reseat needs a power cycle, a new boot id, and so a new
   confirmation. `collect.py --sample-dry` prints the current boot id when it is not confirmed;
3. **lock**: the card's `/run/lock/etsoc-shire<N>.lock` exists and is root's (it is opened read-only, never created:
   one we created would be ours, mode 0600, and lock everyone else out);
4. **stamp**: the card's last try on the host is at least `card_sample_every_min` old (default 30, never below 10);
5. **binary**: the ettelem build is the host's own (`libDM.so` from `/opt/et/lib`, `deviceLayer` from `/opt/et`);
   with `ET_DEVICES`, also its own directory's CMake build, and both it and `/opt/et/lib/libdeviceLayer.a` contain
   `ET_DEVICES` (a stock device layer ignores the variable and would sample card 0);
6. **experiment**: none of our runners (`tools/claims-v3`, `queue.sh`, `run_passes`, `series.sh`, `card_run`,
   `energy.sh`, `workloads/*/run_*`, `tools/ettelem/*.sh`, any `run_*.sh|py`) and none of our device processes;
7. **others**: no other user's device process and no CI job (`Runner.Worker`);
8. **people**: no other user active (a session that is not closing, with no terminal or one used in the last 30 min);
9. **quiet**: the card's submission counters have not moved since the last run (a runner between two launches);
10. **etwho**: `et-who --check` shows nothing held;
11. **time**: the probe is at most 10 s old.

Then: `(cd /tmp; exec 9</run/lock/etsoc-shire<N>.lock; flock -n 9; exec env LD_LIBRARY_PATH=/opt/et/lib [ET_DEVICES=1]
timeout -k 3 10 nice -n 10 <ettelem> sample --seconds 2 --every-ms 500)`. No retry and no drain. Two runs with no
output in a row pause that card for 60 minutes. Exit 124 (stopped by the timeout's SIGTERM) or 137 (killed 3 s later,
mid-request: the queue is likely poisoned; tell the lab admin), or a sample cut off with its probe or its collector,
disables that card's sample and raises a `bad` alert until a person runs `update.sh sample-reset <card>`. Note that
ettelem opens the card before it looks at its arguments: even `ettelem --help` opens the management node, so never
run it by hand to see its usage (read `tools/ettelem/ettelem.cpp`).

## Privacy

The page names lab users, so the space is private, is checked before every deploy (`spacesheep list` must say
private, or nothing is deployed) and after it (the list again, and an anonymous request must get the sign-in
bootstrap, never the page's hidden canary or title), and is never linked from a public page. If a check finds the
space not private or the page exposed, `update.sh` sets the space private again, writes `HALT` and stops deploying
until a person runs `update.sh resume`. The guard cannot see `spacesheep share --email`, which grants a person access
while the space stays private. Another person appears only as a login name with session, terminal
and process counts, idle time and card holds; never their commands, files, groups or where they connect from. The
collector scrubs free text (IP addresses, e-mail addresses, URLs, tailnet names, other people's home paths) and then
refuses to write `data.json` at all (exit 3) if any such pattern remains anywhere. Nothing it collects goes into this
repository; `lab.json` and `testdata/` hold only lab facts and invented people (`owner`, `user-a`, `user-b`). Other ssh targets
than the plain host names go in `~/.config/lab-dashboard/config.json` (`{"ssh": {"aifoundry1": "..."}}`), never here.

## Testing

```
python3 collect.py --from-raw testdata --out /tmp/t --now 1790797500 --owner owner   # the parsers and rules, no ssh
python3 collect.py --out /tmp/t --no-sessions                          # a real collection into a scratch directory
python3 collect.py --out /tmp/t --sample-dry --no-sessions             # the sample's gates, nothing run
```

`update.sh` reads test hooks from the environment, so its deploy logic can be exercised without deploying:
`LAB_DASH_CACHE`, `LAB_DASH_CONFIG` (scratch directories), `LAB_DASH_SPACESHEEP` (a stub CLI), `LAB_DASH_RENDER`
(a stub renderer), `LAB_DASH_FETCH` (a stub anonymous fetch that prints a status line, then a body),
`LAB_DASH_CRONTAB` (a stub crontab), `LAB_DASH_COLLECT_ARGS` (extra `collect.py` options).
