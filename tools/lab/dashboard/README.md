# tools/lab/dashboard: the lab dashboard's collector and updater

A public page on spacesheep.dev (the owner's decision of 30 September 2026) that shows the AI Foundry lab at a glance: the three machines and whether each is up,
the four cards and who holds them, who is logged in and what they are doing, and who used each card in the last 24
hours (from `et-usage`, `tools/lab/et-usage/`), refreshed every 10 minutes. It is the same for everyone: the account
that runs the collector is one login among the others. The design, with the data model, the
health rules and the reasons behind each choice, is [DESIGN.md](DESIGN.md). This file is the manual.

| File | Role |
|---|---|
| `collect.py` | the collector: probes the three hosts in parallel, parses, applies the privacy filter, derives alerts, history and a fingerprint, writes `data.json` |
| `remote.sh` | the read-only probe run on each host (`bash -s` over ssh; locally on aifoundry2) |
| `update.sh` | collect, render, deploy when something changed, keep the space public (or, in the private mode, private), log; cron, acknowledgements |
| `lab.json` | static facts: hosts, cards, firmware, clock policy, idle ranges, a card's dated `note` (with `note_page`, the slug of the page it links), known conditions. No personal data, no access paths |
| `page/` | the page and its `render.py` (see `page/README.md`); `update.sh` runs `page/render.py <data.json> <out.html>` |
| `testdata/` | invented probe outputs (`raw-<host>.txt`, `tailscale.json`) for `collect.py --from-raw`; `run2/` and `run3/` are the two runs after it (a machine down, one unreachable, reboots). The `@@usage` sections are real `et-usage --json` output: `testdata/make_usage.py <scratch>` makes them from the logs that `tools/lab/et-usage/test/test_et_usage.py --dir <scratch> --keep` leaves, laid out over an invented day |
| `tests/` | `test_collect.py` (the collector's rules and the probe's process filter, no host contacted) and `guard_test.sh <workdir>` (`update.sh`'s visibility guard against a stub spacesheep; nothing is deployed) |

Everything collected lives outside the repository: `~/.cache/lab-dashboard/` (mode 0700: `data.json`,
`history.jsonl`, `state.json`, `raw/<host>.txt`, `update.log`, `deploy.state`, `lock`, `collect.lock`, `HALT`,
`EXPOSED`, `halt.last`, `halt.times`) and
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
tools/lab/dashboard/update.sh resume               # clear HALT (private mode: once the space is private again; nothing else clears it)
tools/lab/dashboard/update.sh create-space         # once: the first deploy; records the uuid
python3 tools/lab/dashboard/collect.py             # collect only (prints a summary); --help for its options
```

From another machine: `ssh aifoundry2 claude/et-soc1-prototyping/tools/lab/dashboard/update.sh now`. Asking Claude in
the aifoundry2 session ("refresh the lab dashboard", "why does aifoundry1 show a problem?") works the same way: Claude runs
`update.sh now` and answers from `~/.cache/lab-dashboard/data.json`. Alert ids (for `ack`) are in `data.json` and on
the page, for example `host:aifoundry1:disk:/home`.

**Cadence.** The cron line is `2-59/10 * * * * .../update.sh run` (minute 2 of every ten, off the minute boundary
where per-minute jobs run). A run deploys only when the fingerprint changed (a state change, not a drifting number:
a machine down or back, a reboot, a card taken or freed, a new person on a card in the last 24 h) or the last deploy
is 60 minutes old, and never twice within 10 minutes; `now` always deploys. The spacesheep viewer reloads open tabs
on every deploy; the page reads STALE after 80 minutes without a new version. Runs never overlap: `run` exits at once
if another run holds the lock, `now` waits up to 60 s. `et-lab-health` runs hourly on each host (`now` runs it
everywhere). Expect 30–60 versions a day, at most 144 on a day when a queue
takes a card in bursts (DESIGN.md §3.2); the CLI cannot delete old versions, only the whole space.

**Machine states.** Each machine is `up`, `DOWN` (no answer, and Tailscale on aifoundry2 says it is offline: a
`bad` alert at once, "down since" Tailscale's last-seen time), `UNREACHABLE` (online on Tailscale, or its view not
available, but ssh timed out or failed: a warning, `bad` from the second run; `PROBE FAILED` for aifoundry2's own
probe) or `APPROVAL NEEDED`. A reboot (a new boot id) is shown for 24 hours: a note when a reboot was pending and the
machine answered up to it, a warning when none was pending or when it came back from an outage ("rebooted at 15:07,
after being down since 14:41"), and a note "whether it was planned is not known" when the collector had not seen an
earlier boot (its first run, or right after an upgrade). A machine that is not up keeps its last data on the page,
greyed and labelled "last known at 14:32" (its uptime too); its cards read `UNKNOWN: machine down`, its people's status
is unknown and their counts are too, and its old alerts are listed as "last known data" without counting in the light.
Down and unreachable machines are tried every run; a failure other than the approval prompt clears the approval
back-off. A failed `tailscale status` is a collector warning (states then come from ssh alone).

**When a machine shows "approval needed".** Tailscale SSH's check approval lasts about 12 hours. The collector
recognises the prompt, stops its own ssh client, never keeps the URL, and then tries that host once an hour (`now`
always tries). Run `ssh aifoundry1 true` on aifoundry2, approve the URL it prints, then `update.sh now`. Meanwhile the
host's last data stays on the page, marked stale, and nodewatch keeps its host history.

**Every deploy keeps a copy of the page, login names included.** Only deleting the space removes them.

## What it reads, and what it never does

`remote.sh` reads `/proc`, the driver's sysfs counters (the list in DESIGN.md §2.4), `et-who` (the lab's
`sudo -n et-holders`, the only privileged step), `et-usage --json` (the card-use log, when installed), logind
sessions, terminal idle times, process counts and categories (from `ps` comm, on the host), nodewatch's logs, the
newest experiment telemetry files in the host's tree, `et-lab-manifest`, and the repository's `et-lab-health` rev 3
(sent inside the probe, installed nowhere). On aifoundry2 the collector also reads `tailscale status --json`, keeping
only each lab machine's online flag and last-seen time. One ssh per host per run, under `nice -n 10 ionice
-c3`, every command under `timeout`; a run takes about 1–4 s of wall time for all three hosts.

It never opens a `/dev/et*` node (checked with `strace` on aifoundry2), never reads `utilization_percent` (it syncs
queue pointers from the card), never reads anything of a card `lab.json` marks `excluded` (aifoundry1's card 0 until
2 October 2026; aifoundry2's card from then until 6 October 2026, and again since 7 October 2026, while its cooling is
out) but its link, `err_stats` and its root port's error count, never writes on a host (except the sample's stamp file), never calls `tmux`, and never runs
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
6. **experiment**: none of the collector account's own runners (`tools/claims-v3`, `queue.sh`, `run_passes`, `series.sh`, `card_run`,
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

**The page is public** by the owner's decision of 30 September 2026 ("AI Foundry pages should be public (stop making
the dashboard private)"), although it names lab users. Every run reads the space's row in `spacesheep list` and, if it
is not public (a deploy can change a space's visibility), shares it public again and logs it; a failed list skips that
run's deploy. `update.sh status` names the mode. Because the page is public, the collector's rules below matter all the
more: no addresses, command lines, file paths or connection sources, whatever the mode.

`"visibility": "private"` in `~/.config/lab-dashboard/config.json` (or `LAB_DASH_VISIBILITY=private`, which wins) turns
on the **private mode**, for a page that must not be public. Every run checks the space,
whether or not it deploys, and so does each deploy, right after and again 45 s later: `spacesheep list` must say
private and an anonymous request must get the sign-in bootstrap, never the page's hidden canary or title (both are always
made; a run deploys only when both pass). An anonymous request that gets the page halts at once. A list that says "not
private" is read twice more, 5 s apart, and the anonymous request made again, before anything halts: if both re-reads
say private and the request gets the sign-in page, the run logs it (with the space's rows: id, visibility, updated_at),
skips its deploy and sets the space private anyway. To halt, `update.sh` sets the space private again (and logs whether
that worked), writes `HALT` and stops deploying; nothing resumes by itself: a person runs `update.sh resume` after
checking the space (it refuses while the list says anything but private or the page is served anonymously). While
halted, every run checks again and sets the space private again if it is exposed; if that fails it writes `EXPOSED`
and the run exits 1 until it works (`update.sh status` shows it). For 24 hours after a resume the page carries a warning
that deploys were halted and why. Whether the two halts of 30 September (14:42, 15:22) were real exposures after a
deploy or misreads of the list is not known: the later reads came after the halt had set the space private; the logged
rows are there to settle it. The guard cannot see `spacesheep share --email`, which grants a person access while the
space stays private. In the public mode a `HALT` left from the private mode stops the deploys (each run still keeps the
space public, never private) until `update.sh resume`, which clears it without a check.

A person appears as a
login name with session, terminal and process counts, idle time, card holds and card use (with program names, as
`et-who` and `et-usage` show them to every user), and what they are doing in coarse categories (on a card, AI agent,
building, simulator, Python, editor, shell only), worked out on the host from process names that never leave it;
never their commands, files, groups or where they connect from. The
collector scrubs free text (IP addresses, e-mail addresses, URLs, tailnet names, other people's home paths) and then
refuses to write `data.json` at all (exit 3) if any such pattern remains anywhere. Nothing it collects goes into this
repository; `lab.json` and `testdata/` hold only lab facts and invented people (`owner`, `user-a`, `user-b`) and invented Tailscale output. Other ssh targets
than the plain host names go in `~/.config/lab-dashboard/config.json` (`{"ssh": {"aifoundry1": "..."}}`), never here.

## Testing

```
python3 collect.py --from-raw testdata --out $T --now 1790797500 --owner owner        # the parsers and rules, no ssh
python3 collect.py --from-raw testdata/run2 --out $T --now 1790798100 --owner owner   # then: aifoundry1 down, aifoundry2
python3 collect.py --from-raw testdata/run3 --out $T --now 1790798700 --owner owner   #   rebooted, aifoundry3 unreachable, ...
python3 collect.py --out $T                                                            # a real collection into a scratch directory
python3 collect.py --out $T --sample-dry                                               # the sample's gates, nothing run
```

```
python3 tests/test_collect.py                       # the collector's rules, the privacy patterns, the probe's process filter
bash tests/guard_test.sh ~/claude/work/<topic>      # update.sh's visibility checks against stubs, both modes (51 checks)
```

`update.sh` reads test hooks from the environment, so its deploy logic can be exercised without deploying:
`LAB_DASH_CACHE`, `LAB_DASH_CONFIG` (scratch directories), `LAB_DASH_SPACESHEEP` (a stub CLI), `LAB_DASH_RENDER`
(a stub renderer), `LAB_DASH_FETCH` (a stub anonymous fetch that prints a status line, then a body),
`LAB_DASH_CRONTAB` (a stub crontab), `LAB_DASH_COLLECT_ARGS` (extra `collect.py` options), `LAB_DASH_REREAD_S` (the
guard's re-read pause, 5 s), `LAB_DASH_RECHECK_S` (the second check after a deploy, 45 s; 0 skips it).
`tests/guard_test.sh` uses them for the guard's paths (DESIGN.md §3.3 lists its cases). Keep `LAB_DASH_CONFIG`
pointed at a scratch directory with `{"card_sample": false}` for any test: the real `config.json` may switch the card
sample on.

## The "Start here" section (2 October 2026)

The dashboard is the lab's main starting point: its "Start here" cards and the top nav link the new-user page, the lab
problems report, the chip diagram and the observability hub (`et-soc1-limits-of-observability`, whose own "Start here"
holds the reading paths: nothing of it is copied here). The history page is reached by clicking a machine's live
temperature panel or a 48-hour chart title; there is no separate History button.

## "Unseen (?)" and the live monitor (2 October 2026)

et-usage lists a node open too short for its scanner to attribute (a few ms) as user `?`, shown as "unseen (?)". Since
2 October the lab's live monitor (`tools/lab/live`) reads each free card's temperature once a second, about 3,600 such
opens an hour, which made an "unseen" person hold every card all day. `collect.py` (`is_monitor_noise`) leaves them out of
the card-use table: unseen opens on a steady once-a-second cadence, unseen opens with no lock holder named at more than
0.3 a second over two minutes or more, and a day total of 2,000 unseen opens or more. Bursts under someone's lock at other
rates and the few real unseen opens a day stay. Tests: `tests/test_collect.py`.

## A card's note, and the Worklog (6 October 2026)

**A card's note.** `lab.json` gives a card a `note`; the page shows it under the card's name. With `note_page` beside it
(a page slug such as `aifoundry-lab-6-october`, never a URL: `page/render.py` refuses a data file holding one, and the
collector scrubs them), the note links `https://spacesheep.dev/@yaroslavvb/<slug>`; `page/script.js` builds the address
and keeps only the slug's safe characters. Write the note dated, so a reader knows when it was true:
aifoundry2's card carried "Back in service 6 Oct 2026: fans at full speed in the BIOS; idles at about 64 °C" from 6 to
7 October, linking that day's page. Since 7 October (16:46 PDT) it is `excluded` again, with a note that links the page
of that day's runaway (`aifoundry2-idle-runaway-7-october`). An `excluded` card shows the excluded line, and its note
below it only when the note has a `note_page`.

**The Worklog.** The section above "About this page" lists the lab's published pages, newest day first, with the oldest
days folded into a `<details>`. It is static markup in `page/body.html` (the same for every reader, and it carries links,
which the collector's `data.json` cannot). To add a day: copy one `.wl-row` block to the top of `.wl`, newest first, one
short line per page; when more than about five days are shown, move the oldest `.wl-row` into the `<details>`. The dates
and addresses come from [`docs/reports/MIRROR.md`](../../../docs/reports/MIRROR.md)'s index.
