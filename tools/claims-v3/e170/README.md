# E170's run kit: blind pool 7 on aifoundry1 card 0 under its own governor, at the 800 MHz cap, checked at the desk, ready for the box steps after E164 (Q141(w))

*Wed 4 Nov 2026 (week 45), PST, on the Intel, Q141(w) (the card half's desk lane for card 0). Desk only: no card claimed, no device command sent, no
lab box reached, nothing measured. It answers **item 6 of the kinds page's section 11**
([§ 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)): Q139's critic's rank 1 (M9 against M6 on new
kinds) on a third card, and the question of a card nobody has measured. The complaint that kept card 0 out is E84's PMIC over-power alarm
([E84's README](../../../docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/README.md)); the owner said on 4 Nov that it has been fixed (what the
fix was is not known). The rules are registered in [`E170.md`](E170.md) (lab **`b5ca3e78`**, 14:41:25 PST), the scorer and its self-test in
**`574dc5b5`**, this kit and amendment [E170-A1](E170.md.dated-note.md) in **`57e1c6c4`** (15:13:43 PST). After the desk verifier: amendment
[E170-A2](E170.md.dated-note-A2.md) (E165's live peaks, the files as built, the subset's slot), then the kit's corrections in the commit that changes
this README (§ Corrected after the verifier, below).*

## What it does to predicting power and heat

Nothing yet: it makes E170 runnable. E170 then gives **M9's first blind power score on a card no model has seen**: the burst board power of 39 pool-7
tiles at the 800 MHz cap on aifoundry1 card 0, predicted from the bytes through M9's frozen aifoundry2 relation with card 0's term (the session's own
zeros level, κ0 0.9463 from E118 against E72), against Q140(l)'s end-to-end pinned error on aifoundry2 (0.82 W rms); rank 1's M9 − M6 on the burst D;
whether κ0 holds (X0); the burst heat law on a third card. Before: card 0 has no blind power score; the 600 MHz blind record is 0.24-0.32 W rms per
card, aifoundry2's governed bursts 0.80-0.87 W pinned board end to end. No frozen prediction changes here. E165's session on aifoundry2 (lab
`4c6665f0`) read M9's part at 0.98 W rms on these same 39 tiles there, five single-high-bit tiles of half B measuring 1.80-2.52 W above it:
information for the forecast only ([E170-A2](E170.md.dated-note-A2.md) § A2-2).

## Ready, and what waits

| step | state |
|---|---|
| registration, card term, rules, admission, stops, order | **committed** (`b5ca3e78`), descending from pool 7 `75802201` / `3c9bb2ba`, M9 `1f244140` / `8dfafae3`, M9's aifoundry2 part `5b98bd5c` / `245caffe` / `5c98c0c5`, the heat replicates and G4, E165 and E164 |
| the scorer, self-tested on E160's committed session | **committed** (`574dc5b5`): E160's 9 registered rules field for field (53 fields, 0 differ), E160-C, R0, every pass and the complete runs, through the reduction E170 imports; the card term against the frozen `burst()`; E170's rules at known answers: [`selftest-score.txt`](selftest-score.txt), ALL PASS |
| the scorer of record, A1 | **committed** (`57e1c6c4`): [`score_e170_a1.py`](score_e170_a1.py), each session read against its own protocol's order ([E170-A1](E170.md.dated-note.md) § A1-1) |
| the run kit | **committed** (`57e1c6c4`, corrected after the verifier): every file the box runs pinned in [`harness-e170.json`](harness-e170.json) (107 files and 3 binaries) |
| device commands | **GO**: 33 send sites, all READ, 0 disallowed, E165's one reviewed exception (`run_hpl.py:622`, the residency query E170's guard refuses before the reader starts) ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt); after the verifier's fixes, the same 33 findings line for line: [`logs/dmcmd-audit-a2.txt`](logs/dmcmd-audit-a2.txt)); NO-GO on that line only without it ([`logs/dmcmd-audit-noexcept.txt`](logs/dmcmd-audit-noexcept.txt), [`logs/dmcmd-audit-noexcept-a2.txt`](logs/dmcmd-audit-noexcept-a2.txt)); the desk files: GO, no send site ([`logs/dmcmd-audit-desk.txt`](logs/dmcmd-audit-desk.txt), [`logs/dmcmd-audit-desk-a2.txt`](logs/dmcmd-audit-desk-a2.txt)) |
| the kit's self-test | [`logs/selftest-kit-a2.txt`](logs/selftest-kit-a2.txt) after the verifier's fixes, ALL PASS (the state gate's helpers on E118's committed read, the guard's 11 refusals, A1's mapping, `protocol_why`'s refusals, `bash -n` on 9 scripts, the launch's 15 cases in a sandbox (its 9 first refusals, the round's window, a run queue of ours between passes, the two slots), the step driver's dry listing); [`logs/selftest-kit.txt`](logs/selftest-kit.txt) is `57e1c6c4`'s |
| the dry pass on the Intel | [`logs/drypass-intel-a2.txt`](logs/drypass-intel-a2.txt) after the verifier's fixes; [`logs/drypass-intel.txt`](logs/drypass-intel.txt) is `57e1c6c4`'s (below) |
| a verifier over the registration, scorer and kit | **done** on `b5ca3e78`, `574dc5b5` and `57e1c6c4`: holds with fixes, eight minor findings, each answered in [E170-A2](E170.md.dated-note-A2.md) or § Corrected after the verifier |
| everything on the box | waits for **E164's end** on card 1 and the day's post (below) |

## Card-minutes and the cap

**About 30 card-minutes; the cap is 40, the slot 45 minutes.** 135 bursts at E160's 11.94 s a burst is 26.9 min, plus the state reads, the two
stop-path tests and the ramped smoke, about 2.5 min (E165's took 0.97 min; E170's smoke adds a 30 s rest and two 2 s launches). `run_e119.py` starts a
run only if its planned time fits the cap, so a slow day cuts half B's tail, never a run in flight. **The registered subset**
(`protocol-subset.json`: passes 1, 2, 4 and 5, 90 bursts, about 18 min + 2.5): `launch ... subset`, cap 25, **a 30-minute slot** (E170.md). The day's
post carries aifoundry1's clause for card 0 (section 30: the aifoundry1 clause covers both cards), for example
`using aifoundry1 card 0 for 1 h, until ~HH:MM PST`.

## The order on the box and the window

- **After E164 has ended** (its session's `session end`, its queue's last line): never two of our sessions on aifoundry1. `launch_e170.sh` refuses
  (exit 3) while anything of ours holds either card's node or lock, runs a device process, or runs a queue or session (`queue_`, `session_`,
  `block_` or `run_e1NN`: between its passes E164's queue sleeps holding nothing); `queue_e170.py`'s state gate refuses a held node or lock again.
- **The window** (section 30): no card session starts after **18:15 PST**; every run ends by **19:00 PST**. The launch itself refuses (exit 6) when
  it is past 2026-11-04 18:15 PST or the deadline is after 2026-11-04 19:00 PST, and reads the clock again just before it launches. Pass the launch the
  deadline **`2026-11-04 18:55 PST`**: the slot ends at `min(launch + 45 min, 18:55)` (the subset's `min(launch + 30 min, 18:55)`), the session's own
  cap 3 min before that, the closing read after it.
- **On the box, in the queue's order**: card 0's state gate (et-holders; the host's boot before E84's read; the module uptime's continuity with
  E84's identity read; `ettelem config` 65 W / 65 °C at 600 MHz), then the die and board stop-path tests, then the ramped smoke (rest,
  `int8.anchor7_zeros`, `fp32.randn_a24k`), then the session (half A, then half B, the hottest kinds last). **A NO-GO from the state gate, or a failed
  stop-path test or smoke, ends the queue with QUEUE-HALT** (status "halted"), and card 0 stays idle. **A safety stop or the alarm inside the session
  (exit 4) ends the session, and the queue then ends** (status "ended"; `queue.jsonl`'s `s1_end` rc 4, the reason in `s1/end.json`). Nothing runs after
  either.

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
5. **Read [E170-A2](E170.md.dated-note-A2.md) § A2-1 first** (E165's live peaks: the hottest admitted tiles may read up to about 61 W on card 0, about
   5 W under the stop; E170 runs as registered). **Launch**: `bash tools/claims-v3/e170/box/step_e170.sh launch '2026-11-04 18:55 PST'` (or
   `... '2026-11-04 18:55 PST' subset`), which runs
   `ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '2026-11-04 18:55 PST'" < tools/claims-v3/e170/box/launch_e170.sh`
   ([`box/launch_e170.sh`](box/launch_e170.sh)). Its refusals open nothing: exit 2 (no deadline, not a date), 6 (past 18:15 PST, or a deadline after
   19:00 PST), 4 (too little time), 3 (card 0 held, anything of ours on aifoundry1 including a run queue or session, et-holders unreadable), 5 (a queue
   already ran), 9 (the harness not OK). It detaches `queue_e170.py` and prints `launched T0=…`.
6. **Wait**: `bash tools/claims-v3/e170/box/step_e170.sh wait`, repeated (exit 17 = still running; 16 = the queue halted: read QUEUE-HALT; 0 =
   ended: read `queue.jsonl`'s `s1_end` rc, 0 done, 1 an error such as a stale sampler, 4 a safety stop or the alarm, and `s1/end.json`'s reason)
   ([`box/wait_e170.sh`](box/wait_e170.sh)). Read the state gate, both stop tests and the smoke check before counting the session as started.
   Then the day's post drops aifoundry1's clause (or appends " — released" if it is the last held).
7. **Pull**: `bash tools/claims-v3/e170/box/step_e170.sh pull`: a bounded copy of `aifoundry1:nekko/build/e170/` into `build/e170-raw/`.
8. **Collect and score at the desk**: `E170_DATE=2026-11-04 nice -n 10 bash tools/claims-v3/e170/collect_e170.sh build/e170-raw`
   ([`collect_e170.sh`](collect_e170.sh)): the C check of every session (`ccheck.py check --jobs 2`), the runs and logs into
   `docs/reports/data/2026-11-04-e170-blind7-card0/`, E164's scrubber with its `--check` (exit 7 if another login is left: nothing may be committed),
   gzip, then `score_e170_a1.py` into `results.json`, `results.md` and `score.txt`. Read that it printed `results.md written`. Then the public-text
   scan, then `commit_lab.sh`.

## The dry pass on the Intel

[`drypass_intel_e170.sh`](drypass_intel_e170.sh), run as `bash tools/claims-v3/e170/drypass_intel_e170.sh <a new scratch dir>`: the whole queue on
`run_hpl.py`'s toy card, no device opened, no lock, no ssh. Results ([`logs/drypass-intel.txt`](logs/drypass-intel.txt); again after the verifier's
fixes, [`logs/drypass-intel-a2.txt`](logs/drypass-intel-a2.txt)): the state gate recorded as skipped (dry); stoptest-die exit 4 for "die" before any
launch; stoptest-board exit 4 for "board" inside its launch; the ramped smoke exit 0 and its check clean (the toy's C log is skipped, as in E165);
`s1` the 45 runs of passes 1 and 4, exit 0; the queue's end. `score_e170_a1.py` then reads the dry `s1`: 45 runs, passes 1 and 4, one pass of half A,
so every rule but C and S reads NOT SCORED, as registered. The toy card models aifoundry2's higher draw: its hottest dry burst reads about 62 W, at the
lock's line (61.96 W in the committed log, S PASS; 62.06 W in an earlier dry run, S FAIL). The committed `score_e170.py` main refuses that session,
which is A1's fault. The dry pass runs `queue_e170.py` directly; the launch's checks are the self-test's (§ 6 of `selftest_kit_e170.py`).

## Corrected after the verifier

*Wed 4 Nov 2026, PST, before any E170 data and before the claim. The desk verifier read `b5ca3e78`, `574dc5b5` and `57e1c6c4` and found the design
holds with fixes: eight minor findings. The registration's part is [E170-A2](E170.md.dated-note-A2.md), committed first; the kit's part is this
README's commit.*

| finding | what it said | where it is answered |
|---|---|---|
| F1 | E165's live peaks put six half-B tiles over the base of E170's card-0 estimate; two would read 60.2 and 60.8 W on card 0, over the 60 W line | E170-A2 § A2-1: disclosed, run as registered (the stops bound it; a cut would select on M9's own error), read before step 5 |
| F2 | no 18:15 PST start gate in the kit: the launch refused only a deadline too close | `box/launch_e170.sh`: exit 6 past 2026-11-04 18:15 PST or for a deadline after 19:00 PST, the start read again just before the launch. This README said "the 18:15 start gate binds first" with no gate behind it |
| F3 | E164's queue sleeps 10 s between passes holding no node or lock, so a launch in that gap would pass | `box/launch_e170.sh`: exit 3 while a `queue_`, `session_`, `block_` or `run_e1NN` process of ours runs (moot today: E164 had ended) |
| F4 | a stop or the alarm inside the session ends the queue as "ended", not with QUEUE-HALT | this README's § The order on the box and step 6, and E170-A2 § A2-3. It said "Any NO-GO, stop, alarm or failed gate ends the queue with QUEUE-HALT" |
| F5 | E170.md names `queue_e170.sh` and `smoke_gate_e170.py`, and gives the subset a 30-minute slot where the kit gave 45 | E170-A2 § A2-3 (the files as built); `box/launch_e170.sh` now gives the subset 30 minutes, as E170.md registered (A1-2 had written 45 for every plan) |
| F6 | the lane's result said every random-like float tile is left out; `fp32.randn_a24k` is admitted | E170-A2 § A2-4 |
| F7 | `logs/selftest-kit.txt` reads "8 scripts parse"; the kit has 9 `.sh` files (`drypass_intel_e170.sh` came after that log) | [`logs/selftest-kit-a2.txt`](logs/selftest-kit-a2.txt): 9 parse |
| F8 | E170.md's "F PASS" does not weigh card 0's once-a-second governor falls (E114) | E170-A2 § A2-2, with E165-F2's FAIL on aifoundry2's mid-burst dips |

What changed in the kit: `box/launch_e170.sh` (the window, the run-queue refusal, the subset's slot; it prints the plan's slot and cap), its pin in
`harness-e170.json` (107 files, one hash changed), `selftest_kit_e170.py` § 6 (six new cases and three checks), this README, and new logs beside the
old ones. Nothing else in the kit changed: `queue_e170.py`, `run_e170.py`, the guard, the protocols and the scorers are as committed.

## Files

| file | runs where | what |
|---|---|---|
| [`E170.md`](E170.md), [`E170.md.dated-note.md`](E170.md.dated-note.md), [`E170.md.dated-note-A2.md`](E170.md.dated-note-A2.md) | desk | the registration (`b5ca3e78`), amendment A1 and amendment A2 |
| [`e170_common.py`](e170_common.py), [`make_predictions_e170.py`](make_predictions_e170.py) → `predictions-e170.json`, `.txt` | desk and box | the pins, the card term, the admission estimate; the machine registration (`b5ca3e78`) |
| [`score_e170.py`](score_e170.py), [`selftest_score_e170.py`](selftest_score_e170.py) → `selftest-score.txt` | desk | the scorer and its self-test on E160 (`574dc5b5`) |
| [`score_e170_a1.py`](score_e170_a1.py) | desk | the scorer of record (A1) |
| [`run_e170.py`](run_e170.py), [`queue_e170.py`](queue_e170.py), [`ettelem_guard_e170.sh`](ettelem_guard_e170.sh), [`preflight_e170.sh`](preflight_e170.sh), [`check_e170.py`](check_e170.py) | box | the runner (E84's card-0 runner under E119's and E105's, with E165's pool checks), the queue (the smoke's and stop tests' gates are its `check_smoke` and `check_stoptest`), the guard, the audit, the harness check |
| [`make_protocol_e170.py`](make_protocol_e170.py) → `protocol.json`, `protocol-subset.json`, `protocol-dry.json`, `protocol-stoptest-{board,die}[-dry].json`, `protocol.txt` | desk | the protocols |
| [`make_harness_e170.py`](make_harness_e170.py) → [`harness-e170.json`](harness-e170.json) | desk | the hashes the box checks |
| [`box/`](box/) | the box and the Intel | the box steps above |
| [`collect_e170.sh`](collect_e170.sh) | desk | the collector |
| [`selftest_kit_e170.py`](selftest_kit_e170.py), [`drypass_intel_e170.sh`](drypass_intel_e170.sh), [`logs/`](logs/) | desk | the kit's self-test, the dry pass, the audits (`*-a2.txt`: after the verifier's fixes) |

**The Intel's batch rule** (section 28): every desk run here was at `nice -n 10` on one core and short (the scorer's self-test about 100 s, the kit's
about 3 s, the dry pass about 5 min of a mostly sleeping queue); no lab box and no mini were used. The verifier's fixes changed no scorer, so the
scorer's self-test was not run again.

## What this cannot say

The kit is ported and dry-run, not run: nothing here has opened card 0. The box steps read what the desk cannot: the binaries, the module uptime, the
configuration, the holders and the host's room. If "the fix" reset or reflashed card 0, the module uptime shows it and E170 does not start (NO-GO on
the day, card 0 idle): the running image could not be named without the firmware-revisions query, which is never sent.

SPDX-License-Identifier: Apache-2.0
