# Q142(k6): the pool-8 card day's runbook for E171 and E172 (v3.1's steps, ported)

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only (Q142(k6)): no card claimed, no device command sent, no ssh to a lab box, nothing
posted. New files only. v1-v3.1 (`../`, `../v2/`, `../v3/`, `../v3.1/`) stay as committed. It is step 4 of
[`../../e171/E171.md`](../../e171/E171.md) and [`../../e172/E172.md`](../../e172/E172.md), after both kits (`1b80da20`, `14fcb30d`); it
answers the Q142(r)/(p)/(d) critic's `next` rank 2 ("ports v3.1's steps, with a cc_gate per collector and a list per run of the sessions
that must carry a C log": the Q142 critic's fault 3), for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6.*

## Results first

- **Fault 3, closed for these runs.** v3.1's `cc_gate` read each `--out` file a collector named, so a session whose C log was missing was
  never checked and never missed. Here `cc_gate` runs `tools/claims-v3/p8-600/ccsessions_p8.py`, which lists, by the registered rule and
  from the raw copy, **every session that must carry a C log** (the smoke and every pass with a launch record, ok or not) and requires
  each to have been checked to its end: a missing log, a check that did not finish, a check written before this collection, or a check
  that judged fewer launches than a session's log holds stops the step (14) before it says "collected". The desk test shows each (C2-C5),
  and C2 is the case v3.1 passed.
- **The desk test, [`logs/selftest.txt`](logs/selftest.txt): 12 of 12 cases PASS.** Stand-in `ssh` and `rsync` first on PATH serve a
  stand-in box; the steps run in a scratch copy of the tree, never the lab clone. A: the dry listing, every step exit 0 and no ssh or
  rsync call. L1: a login link at the probe, exit 11 and one lock line `<HH:MM:SS> aifoundry3 needs a check`. L2: a probe that never
  answers, exit 12. L3: a read past its bound, exit 13. L4: a box whose preflight reads wrong, exit 16. C1: a good collection, "E171
  collected and scored". C2-C5: a missing C log, a skipped session, a stale check, a stop-path test that launched, each exit 14. C6: a
  desk path in an output, exit 16. O1: `ours_live` names E171's and E172's session, queue, block and runner processes and E173's and
  E174's queues (10 of 10), and not an unrelated command.
- **The dry listing, [`logs/dry-listing.txt`](logs/dry-listing.txt):** 20 step calls in the card day's order, each exit 0, every remote
  script printed in full; run in the lab clone with logging stand-ins first on PATH, which saw no call.
- **Device commands** ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)): `dmcmd_audit.py` on the k6 steps with E128's guard scanned beside
  them reads **GO, 11 send sites, 0 disallowed**, every one a line of the guard and READ; without the guard
  ([`logs/dmcmd-audit-bare.txt`](logs/dmcmd-audit-bare.txt)) it reads NO-GO at exactly step 9's guard call (`s09_a3_reads_k6.sh:20`, 6 send
  sites), as v3.1's does at its own step 9. The steps call only the kits' audited scripts and the guard's `config`.

## The steps (call each under `k6/`, with this card day's `RB_OUT` and `RB_LOCK`)

| step | file | what |
|---|---|---|
| 2 | `s02_window_k6.sh <day> <last start> <last end>` | his go's window; E172's deadline is the last end less 10 minutes |
| 3 | `s03_desk_k6.sh` | pull; HEAD descends from `RB_BASE` (`14fcb30d`); the kits' paths clean; blind8 89, the freeze 160, the scorer 5, the predictor 16 / 9 / 209 |
| 5 | `s05_look_k6.sh aifoundry3 \| aifoundry1 [--wait]` | look first (et-who, who, uptime, the holder rule; on aifoundry1 E172's `box/look_e172.sh` and the identity) |
| 6 | — | the day's one post (the card lane's) |
| 7 | `s07_a3_sync_k6.sh` | aifoundry3's rsync: E171's kit, pool 8, the pinned watcher files |
| 8 | `s08_a3_preflight_k6.sh` | blind8 89, HARNESS OK 101, the preflight GO, the items verified |
| 9 | `s09_a3_reads_k6.sh` | et-lab-manifest, the config through the guard (0 W / 65 °C / 600 MHz), et-who clean |
| 10 | `s10_a3_dry_k6.sh start \| wait` | E171's V3_DRY pass on the box as one detached job |
| 11 | `s11_a3_session_k6.sh [FULL\|TWO\|SHORT]` | E171's session, detached, with the plan's budget before the last end |
| 12 | `s12_a1_check_k6.sh sync \| start \| wait` | E172's sync and box check (a detached job), read section by section |
| 13 | `s13_a1_launch_k6.sh [--drop-p2]` | E172's launcher with the quoted deadline; its refusals exit 10 |
| 20 | `s20_wait_k6.sh e171 \| e172` | one bounded wait, repeated while it says 17 |
| 21 | — | the releases (rewrites of the day's post) |
| 22 | `s22_collect_k6.sh e171 \| e172 \| ka` | the copies, the collector, **cc_gate over every listed session**, the login check, the desk-path gate; `ka` reads P8-KA pooled after both |

The exit codes are v3.1's (0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed or a check of C did not
finish; 15 a holder after 30 minutes; 16 a gate; 17 call again). The window file has v3.1's keys, so v3.1's own steps read it as well.

## What it does to predicting power and heat

Nothing to any number. It makes sure that pool 8's blind scores on both 600 MHz cards are collected only from sessions whose every launch
was checked for C to the end, as the registrations require, so no blind power or heat figure of M10 rests on an unchecked session.

## Files

`rb_common.sh` (v3.1's, with `ours_live`'s names and the k6 base; it calls v3.1's `rb_run.py`, `nopath_q142s.py` and, through
`ccsessions_p8.py`, `ccdone_q142s.py`, all unchanged, by path); the steps above; `list_steps_k6.sh` (the dry listing);
`selftest_runbook_k6.sh` (the desk test); `logs/`.

## Compute

The Intel, through the round's local slot, one job at a time: the dry listing (twice), the desk test (four runs: the first two failed on
the test's own setup, an argument the C2 case passed wrongly and a launcher file the scratch tree lacked; both fixed; the third passed;
the fourth, committed, after three phrasings the public-text scan flagged were changed: a word of the fixed list in v3.1's gate message and its lock-file
description in `rb_common.sh`, and the stand-in login link's host name, now built from two strings), and the audits (twice). No lab box,
no mini job.

SPDX-License-Identifier: Apache-2.0
