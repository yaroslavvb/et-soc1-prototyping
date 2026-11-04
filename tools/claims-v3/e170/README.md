# E170's run kit: blind pool 7 on aifoundry1 card 0 under its own governor, at the 800 MHz cap, checked at the desk, ready for the box steps after E164 (Q141(w))

*Wed 4 Nov 2026 (week 45), PST, on the Intel, Q141(w) (the card half's desk lane for card 0). Desk only: no card claimed, no device command sent, no
lab box reached, nothing measured. It answers **item 6 of the kinds page's section 11**
([§ 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)): Q139's critic's rank 1 (M9 against M6 on new
kinds) on a third card, and the question of a card nobody has measured. The complaint that kept card 0 out is E84's PMIC over-power alarm
([E84's README](../../../docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/README.md)); the owner said on 4 Nov that it has been fixed (what the
fix was is not known). The rules are registered in [`E170.md`](E170.md) (lab **`b5ca3e78`**, 14:41:25 PST), the scorer and its self-test in
**`574dc5b5`**, this kit and amendment [E170-A1](E170.md.dated-note.md) in the commit that adds this README.*

## What it does to predicting power and heat

Nothing yet: it makes E170 runnable. E170 then gives **M9's first blind power score on a card no model has seen**: the burst board power of 39 pool-7
tiles at the 800 MHz cap on aifoundry1 card 0, predicted from the bytes through M9's frozen aifoundry2 relation with card 0's term (the session's own
zeros level, κ0 0.9463 from E118 against E72), against Q140(l)'s end-to-end pinned error on aifoundry2 (0.82 W rms); rank 1's M9 − M6 on the burst D;
whether κ0 holds (X0); the burst heat law on a third card. Before: card 0 has no blind power score; the 600 MHz blind record is 0.24-0.32 W rms per
card, aifoundry2's governed bursts 0.80-0.87 W pinned board end to end. No frozen prediction changes here.

## Ready, and what waits

| step | state |
|---|---|
| registration, card term, rules, admission, stops, order | **committed** (`b5ca3e78`), descending from pool 7 `75802201` / `3c9bb2ba`, M9 `1f244140` / `8dfafae3`, M9's aifoundry2 part `5b98bd5c` / `245caffe` / `5c98c0c5`, the heat replicates and G4, E165 and E164 |
| the scorer, self-tested on E160's committed session | **committed** (`574dc5b5`): E160's 9 registered rules field for field (53 fields, 0 differ), E160-C, R0, every pass and the complete runs, through the reduction E170 imports; the card term against the frozen `burst()`; E170's rules at known answers: [`selftest-score.txt`](selftest-score.txt), ALL PASS |
| the scorer of record, A1 | **this commit**: [`score_e170_a1.py`](score_e170_a1.py), each session read against its own protocol's order ([E170-A1](E170.md.dated-note.md) § A1-1) |
| the run kit | **this commit**: every file the box runs pinned in [`harness-e170.json`](harness-e170.json) (107 files and 3 binaries) |
| device commands | **GO**: 33 send sites, all READ, 0 disallowed, E165's one reviewed exception (`run_hpl.py:622`, the residency query E170's guard refuses before the reader starts) ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)); NO-GO on that line only without it ([`logs/dmcmd-audit-noexcept.txt`](logs/dmcmd-audit-noexcept.txt)); the desk files: GO, no send site ([`logs/dmcmd-audit-desk.txt`](logs/dmcmd-audit-desk.txt)) |
| the kit's self-test | **this commit**: [`logs/selftest-kit.txt`](logs/selftest-kit.txt), ALL PASS (the state gate's helpers on E118's committed read, the guard's 11 refusals, A1's mapping, `protocol_why`'s refusals, `bash -n`, the launch's 9 refusals in a sandbox, the step driver's dry listing) |
| the dry pass on the Intel | **this commit**: [`logs/drypass-intel.txt`](logs/drypass-intel.txt) (below) |
| a verifier over the registration, scorer and kit | **owed** (section 30: "verified before it runs") |
| everything on the box | waits for **E164's end** on card 1 and the day's post (below) |

## Card-minutes and the cap

**About 30 card-minutes; the cap is 40, the slot 45 minutes.** 135 bursts at E160's 11.94 s a burst is 26.9 min, plus the state reads, the two
stop-path tests and the ramped smoke, about 2.5 min (E165's took 0.97 min; E170's smoke adds a 30 s rest and two 2 s launches). `run_e119.py` starts a
run only if its planned time fits the cap, so a slow day cuts half B's tail, never a run in flight. **The registered subset**
(`protocol-subset.json`: passes 1, 2, 4 and 5, 90 bursts, about 18 min + 2.5): `launch ... subset`, cap 25. The day's post carries aifoundry1's
clause for card 0 (section 30: the aifoundry1 clause covers both cards), for example `using aifoundry1 card 0 for 1 h, until ~HH:MM PST`.

## The order on the box and the window

- **After E164 has ended** (its session's `session end`, its queue's last line): never two of our sessions on aifoundry1. `launch_e170.sh` refuses
  (exit 3) while anything of ours holds either card's node or lock or runs a device process; `queue_e170.py`'s state gate refuses it again.
- **The window** (section 30): no card session starts after **18:15 PST**; every run ends by **19:00 PST**. Pass the launch the deadline
  **`2026-11-04 18:55 PST`**: the slot ends at `min(launch + 45 min, 18:55)`, the session's own cap 3 min before that, the closing read after it.
  The full plan needs the launch by about **18:19** (36 min before the deadline) and the subset by about 18:29; the 18:15 start gate binds first.
- **On the box, in the queue's order**: card 0's state gate (et-holders; the host's boot before E84's read; the module uptime's continuity with
  E84's identity read; `ettelem config` 65 W / 65 °C at 600 MHz), then the die and board stop-path tests, then the ramped smoke (rest,
  `int8.anchor7_zeros`, `fp32.randn_a24k`), then the session (half A, then half B, the hottest kinds last). **Any NO-GO, stop, alarm or failed gate
  ends the queue with QUEUE-HALT**; nothing after it runs, and card 0 stays idle.

## Box steps, after E164's end

Each runs on the Intel from the top of the lab clone, through Q141(k)'s bounded runner (a 15 s probe, a bound on each call, a login link killing
the call and appending `<HH:MM:SS> aifoundry1 needs a check` to `$RB_LOCK`; [`box/step_e170.sh`](box/step_e170.sh)). First:
`export RB_OUT=<this card day's directory, outside the repo> RB_LOCK=<the round's tailscale-needed file>`.

1. **Look**, read only: `bash tools/claims-v3/e170/box/step_e170.sh look` ([`box/look_e170.sh`](box/look_e170.sh)): the host's boot against E84's
   read (it must precede 2026-10-31 15:42:00 PDT), et-who (card 0's own lines empty; nothing of ours on card 1), E164's `session end`, the logins,
   `/home`'s room, the three binaries against their pins (`4f0956ce…`, `990807f4…`, `87c1c38c…`), the locks, our device processes (none).
2. **Sync**: `bash tools/claims-v3/e170/box/step_e170.sh sync`: one `rsync -a -c -R` of `tools/claims-v3/e170/`, pool 7, the chain E170 imports
   (E84's runner, `run_kspeed.py` and its predictions, E101s, E105, E119 and its predictions, E111, `run_hpl.py`, E165's common module,
   `e78_common.py`, `e101_common.py`, `kinds.json`), Q139(k)'s `ccheck/`, the audit and its table, the workload's sources and the frozen predictor
   into `aifoundry1:nekko/`. No compiled source changes, so nothing is rebuilt: if a binary differs, stop (a rebuild needs a dated amendment first).
3. **Check on the box**: `bash tools/claims-v3/e170/box/step_e170.sh check` ([`box/check_box_e170.sh`](box/check_box_e170.sh)): `check_e170.py`
   HARNESS OK 107 + 3 binaries; `preflight_e170.sh` GO; the tiles and frozen inputs; pool 7's SHA256SUMS 91 OK; the box's dry pass (the die stop-path
   test, rc 4; the smoke, rc 0; the session listed, 135 runs). Never during a session of ours on aifoundry1.
4. **The day's one post** (the main session, under the Discord lock, section 15): aifoundry1's clause for card 0.
5. **Launch**: `bash tools/claims-v3/e170/box/step_e170.sh launch '2026-11-04 18:55 PST'` (or `... '2026-11-04 18:55 PST' subset`), which runs
   `ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '2026-11-04 18:55 PST'" < tools/claims-v3/e170/box/launch_e170.sh`
   ([`box/launch_e170.sh`](box/launch_e170.sh)). Its refusals open nothing: exit 2 (no deadline, not a date), 4 (too little time), 3 (card 0 held,
   anything of ours on aifoundry1, et-holders unreadable), 5 (a queue already ran), 9 (the harness not OK). It detaches `queue_e170.py` and prints
   `launched T0=…`.
6. **Wait**: `bash tools/claims-v3/e170/box/step_e170.sh wait`, repeated (exit 17 = still running; 16 = the queue halted: read QUEUE-HALT; 0 =
   ended) ([`box/wait_e170.sh`](box/wait_e170.sh)). Read the state gate, both stop tests and the smoke check before counting the session as started.
   Then the day's post drops aifoundry1's clause (or appends " — released" if it is the last held).
7. **Pull**: `bash tools/claims-v3/e170/box/step_e170.sh pull`: a bounded copy of `aifoundry1:nekko/build/e170/` into `build/e170-raw/`.
8. **Collect and score at the desk**: `E170_DATE=2026-11-04 nice -n 10 bash tools/claims-v3/e170/collect_e170.sh build/e170-raw`
   ([`collect_e170.sh`](collect_e170.sh)): the C check of every session (`ccheck.py check --jobs 2`), the runs and logs into
   `docs/reports/data/2026-11-04-e170-blind7-card0/`, E164's scrubber with its `--check` (exit 7 if another login is left: nothing may be committed),
   gzip, then `score_e170_a1.py` into `results.json`, `results.md` and `score.txt`. Read that it printed `results.md written`. Then the public-text
   scan, then `commit_lab.sh`.

## The dry pass on the Intel

[`drypass_intel_e170.sh`](drypass_intel_e170.sh), run as `bash tools/claims-v3/e170/drypass_intel_e170.sh <a new scratch dir>`: the whole queue on
`run_hpl.py`'s toy card, no device opened, no lock, no ssh. Results ([`logs/drypass-intel.txt`](logs/drypass-intel.txt)): the state gate recorded as
skipped (dry); stoptest-die exit 4 for "die" before any launch; stoptest-board exit 4 for "board" inside its launch; the ramped smoke exit 0 and its
check clean (the toy's C log is skipped, as in E165); `s1` the 45 runs of passes 1 and 4, exit 0; the queue's end. `score_e170_a1.py` then reads the
dry `s1`: 45 runs, passes 1 and 4, one pass of half A, so every rule but C and S reads NOT SCORED, as registered. The toy card models aifoundry2's
higher draw: its hottest dry burst reads about 62 W, at the lock's line (61.96 W in the committed log, S PASS; 62.06 W in an earlier dry run, S FAIL).
The committed `score_e170.py` main refuses that session, which is A1's fault.

## Files

| file | runs where | what |
|---|---|---|
| [`E170.md`](E170.md), [`E170.md.dated-note.md`](E170.md.dated-note.md) | desk | the registration (`b5ca3e78`) and amendment A1 |
| [`e170_common.py`](e170_common.py), [`make_predictions_e170.py`](make_predictions_e170.py) → `predictions-e170.json`, `.txt` | desk and box | the pins, the card term, the admission estimate; the machine registration (`b5ca3e78`) |
| [`score_e170.py`](score_e170.py), [`selftest_score_e170.py`](selftest_score_e170.py) → `selftest-score.txt` | desk | the scorer and its self-test on E160 (`574dc5b5`) |
| [`score_e170_a1.py`](score_e170_a1.py) | desk | the scorer of record (A1) |
| [`run_e170.py`](run_e170.py), [`queue_e170.py`](queue_e170.py), [`ettelem_guard_e170.sh`](ettelem_guard_e170.sh), [`preflight_e170.sh`](preflight_e170.sh), [`check_e170.py`](check_e170.py) | box | the runner (E84's card-0 runner under E119's and E105's, with E165's pool checks), the queue, the guard, the audit, the harness check |
| [`make_protocol_e170.py`](make_protocol_e170.py) → `protocol.json`, `protocol-subset.json`, `protocol-dry.json`, `protocol-stoptest-{board,die}[-dry].json`, `protocol.txt` | desk | the protocols |
| [`make_harness_e170.py`](make_harness_e170.py) → [`harness-e170.json`](harness-e170.json) | desk | the hashes the box checks |
| [`box/`](box/) | the box and the Intel | the box steps above |
| [`collect_e170.sh`](collect_e170.sh) | desk | the collector |
| [`selftest_kit_e170.py`](selftest_kit_e170.py), [`drypass_intel_e170.sh`](drypass_intel_e170.sh), [`logs/`](logs/) | desk | the kit's self-test, the dry pass, the audits |

**The Intel's batch rule** (section 28): every desk run here was at `nice -n 10` on one core and short (the scorer's self-test about 100 s, the kit's
about 2 s, the dry pass about 5 min of a mostly sleeping queue); no lab box and no mini were used.

## What this cannot say

The kit is ported and dry-run, not run: nothing here has opened card 0. The box steps read what the desk cannot: the binaries, the module uptime, the
configuration, the holders and the host's room. If "the fix" reset or reflashed card 0, the module uptime shows it and E170 does not start (NO-GO on
the day, card 0 idle): the running image could not be named without the firmware-revisions query, which is never sent.

SPDX-License-Identifier: Apache-2.0
