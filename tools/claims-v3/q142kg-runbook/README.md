# The pool-8 card day's runbook for E173 and E174: v3.1's steps ported, with the C-log gate (Q142(kg))

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only: nothing here has reached a lab box. It ports Q142(s)'s runbook v3.1
([`../q141k-runbook/v3.1/`](../q141k-runbook/v3.1/), lab `0d2cb5dd`) to the two pool-8 runs of this lane: [E173](../e173/README.md) on aifoundry2
and [E174](../e174/README.md) on aifoundry1 card 0. It answers the Q142(r)/(p)/(d) critic's `next` rank 2 (the kits run through v3.1's steps) and
the Q142 critic's fault 3: v3.1's C gate stopped a collection whose check of C did not finish, but did not require a check for every session that
should carry one, so a session with no C log was skipped.*

## What it does to predicting power and heat

Nothing by itself: it is the path by which E173's and E174's sessions reach their registered scorers with every C log checked. A session whose C
log is missing, or whose check did not finish, stops the collection before scoring, so no blind power or heat number of pool 8 is scored on a
launch whose C state is unread.

## What is ported, and what is v3.1's unchanged

[`rb_common.sh`](rb_common.sh) **sources v3.1's `rb_common.sh` unchanged**, so `rb_run.py`, `nopath_q142s.py` and `ccdone_q142s.py` are v3.1's
committed files and every v3.1 rule holds: the 15 s hard-killed probe; every call under its bound (60 s a read, 600 s a copy or a wait, 60 s a
launch, which detaches on the box and returns at once, 5,400 s a desk collector); a login link kills the call, appends `<HH:MM:SS> <host> needs a
check` to `$RB_LOCK` and exits 11; nothing prompts; every call is logged in `$RB_OUT/runbook.log`. It adds one function, the C gate, and
overrides four things only:

| what | v3.1 | here |
|---|---|---|
| `RB_BASE`, the commit every box tree must descend from | v3.1's | `c8064454` (E173's and E174's registrations); the kits' own bytes are checked file by file by each kit's harness check, so a box without the kit commit refuses there; pass `RB_BASE=<the kit's commit>` on the day |
| the window | `s02_window.sh` (E163-E169's plans) | [`s02_window_q142kg.sh`](s02_window_q142kg.sh) `<YYYY-MM-DD> <last start HH:MM> <last end HH:MM>`, Pacific: `$RB_OUT/window-q142kg.env` with the day, the last start and end, and E174's launch deadline (the last end less 5 minutes) |
| `ours_live`, the count of our card sessions on a box (in the remote prelude) | any `queue_eNNN.py` or `session_eNNN.sh` of ours | also E171-E174's `queue_e17N.py`, `run_e17N.py`, `session_e17N.sh` and `block_e17N` by name, with v3.1's exclusions (a `--dry` command line, a `V3_DRY` environment) |
| the C gate, at each collection (added) | `s22_collect.sh`'s `cc_gate`: every check of C the collector wrote must have finished | `rb_cc_gate`: first [`cclist_q142kg.py`](cclist_q142kg.py) lists every session that must carry a C log (smoke, stoptest-board, and every BURST session the queue started that ran a work launch, read from `queue.jsonl` and each session's `launches.jsonl`; the scorers' own rule, `../e173/p8gov.required_c_logs`), and a session with none stops the step (14); then v3.1's `ccdone_q142s.py` reads every listed check (there, finished, written since the collection began), else 14 |
| the step's name | `<step>_v3.1` | `<step>_q142kg`, in the log, the messages and the dry listing's header |

**If both pool-8 lanes share one `$RB_OUT`:** the k6 lane's runbook (lab `9a2630ff`, 04:30:38 PST, `../q141k-runbook/k6/`) writes v3.1's
`window.env` from the same go. With no `window-q142kg.env`, `rb_window` reads that file, so E173's start and end gates read the same day's times.
E174's launch refuses (10) because that file carries no E174 deadline. Run `s02_window_q142kg.sh` once and this runbook's own file wins.

The exit codes are v3.1's: 0 done; 10 refused; 11 a login link; 12 the probe got no answer; 13 past its bound; 14 non-zero (a check of C that did
not finish, a required C log missing); 15 a holder after 30 minutes; 16 a gate says stop; 17 not yet, call again.

## The two step drivers

- [`../e173/box/step_e173.sh`](../e173/box/step_e173.sh): `look`, `tree`, `dry start|wait`, `launch [subset]`, `wait`, `collect` (v3.1's s05, s14,
  s15, s16, s20 and s22 for aifoundry2). The collection runs [`../e173/collect_e173_bounded.sh`](../e173/collect_e173_bounded.sh), then the C gate,
  then v3.1's desk-path gate.
- [`../e174/box/step_e174.sh`](../e174/box/step_e174.sh): `look`, `sync`, `check`, `launch [subset]`, `wait`, `pull`, `collect` for card 0, E170's
  form (the box steps' scripts in `../e174/box/`; the launch takes the window's times as arguments and refuses outside them or while anything of ours
  runs on aifoundry1, E172 included). The collection runs [`../e174/collect_e174.sh`](../e174/collect_e174.sh), then the C gate, then the desk-path
  gate.

The order on the day, the cards' stops and the card-minutes are in each kit's README. E174 starts only after E172 has ended: never two sessions of
ours on aifoundry1.

## Checked at the desk

| check | result |
|---|---|
| [`selftest_steps_q142kg.sh`](selftest_steps_q142kg.sh): a stand-in `ssh` and `rsync` first on `PATH` take every call; the bounds shortened with v3.1's own desk-test overrides (`RB_<CLS>_S`) | [`logs/selftest-steps.txt`](logs/selftest-steps.txt): **28 of 28**: the window; the dry listing calls nothing; look free 0, the identity stop 16, held 17; a login link at the probe and in a call 11 with the lock line; a hung probe 12, a call past its bound 13; E174's launch refused 10, the identity stop 16, launched 0, E173's launch past the last start 16 with no call; E174's wait halted 16, ended 0, running 17; the sync failing 14, a link in it 11; the tree clean 0, the device-command preflight NO-GO 16; the C gate: every listed session checked 0, a session without a C log 14, a stale check 14, a resumed s2 with a work launch and no check 14; `ours_live`'s pattern; no stand-in process left |
| [`logs/dry-listing.txt`](logs/dry-listing.txt): every step of both drivers with `RB_DRY=1` (each call printed, nothing run), a logging stand-in `ssh` and `rsync` on `PATH`, a made-up window | **16 of 16 steps exit 0; 0 stand-in calls**; no desk path in it |
| [`logs/dmcmd-audit-desk.txt`](logs/dmcmd-audit-desk.txt): `dmcmd_audit.py` on the 26 desk files (both kits' generators, scorers, harness checks, collectors, dry-pass drivers, self-tests and step drivers, and this directory's four scripts), no allow-list | **GO**, no send site |

## Files

| file | what |
|---|---|
| `rb_common.sh` | the part every step sources: v3.1's, the C gate and the four overrides above |
| `s02_window_q142kg.sh` | the day's window, from the owner's go |
| `cclist_q142kg.py` | the sessions of a collected run that must carry a C log; it reads and writes nothing else |
| `selftest_steps_q142kg.sh` | the desk test above |
| `logs/` | the desk test, the dry listing, the desk audit |

## What this cannot say

The steps are tested against stand-ins, not against the boxes: nothing here has run on aifoundry1 or aifoundry2. The patterns were written before
E172's kit was committed and name its processes generically. The k6 lane's kit (lab `14fcb30d`, 04:19:20 PST; E171's `1b80da20`) runs
`queue_e172.sh`, `session_e172.sh`, `block_e172.sh` and `run_e172.py`. `ours_live` matches each of them (the first two by v3.1's
`(queue|session)_eNNN` rule, the others by name), and so does `launch_e174.sh`'s refusal, `(queue|session|block|run)_e1NN`. E174's look counts the
`session end` lines in E172's `build/e172/session.log`, which is where that kit writes them.

SPDX-License-Identifier: Apache-2.0
