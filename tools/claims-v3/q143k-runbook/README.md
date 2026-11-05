# Q143(k): the bounded runbook for M11's E176 session (v3.1's steps, ported from k6)

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only: no card claimed, no device command sent, no ssh to a lab box, nothing posted. New
files only; v1-v3.1 and k6 (`../q141k-runbook/`) stay as committed. It wraps E176's kit box steps ([`../e176/README.md`](../e176/README.md),
kit `03582d2f`), in the form the go checklist's rule 4 set and v3.1 and k6 carried: every remote call after a 15 s hard-killed probe and under
a bound; a printed login link killed at once, with `<HH:MM:SS> <host> needs a check` appended to `RB_LOCK` (exit 11); nothing that prompts.
For the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8.*

## Results first

- **The desk test, [`logs/selftest.txt`](logs/selftest.txt): 20 of 20 cases PASS** (18 s). Stand-in `ssh` and `rsync` first on PATH serve a
  stand-in box, and a scratch copy of the runbook's files stands in for the tree; no lab box is reached. The cases:
  - **A:** the dry listing; every step exits 0, with no ssh or rsync call.
  - **The bounds:** L1, a login link at the probe (exit 11, one lock line); L2, a probe that never answers (12); L3, a read past its bound
    (13); L4, a box whose binaries are missing, so its box list reads 26 of 29 (16).
  - **The wait:** W1, the session's end after the runbook's offset (0); W2, no session process and no end (14); W3, the smoke or its gate
    failed (16); W4, the start gate G0 refused the measured pass (16).
  - **The launch:** S1, fewer than 76 minutes before the last end (16, before any box call); S2, an earlier E176 smoke on the box without
    `--later-try` (10); S3, E171's session ended 10 minutes ago, so the card has not rested (10).
  - **The collection, with a stand-in collector:** C1, the check of C finished and the scorer reads rc 0 ("E176 collected and scored");
    C2, the check of C crashed (14); C3, a failed copy (14); C4, the scorer not rc 0 (14); C5, a check file from an earlier try (14); C6, a
    desk path in an output (16); C7, the stand-in named without `RB_DESKTEST=1` (10).
  - **O1:** `ours_live` names E176's session, block and runner, E177's queue, runner and session, and k6's E171-E174 names: 10 of 10, and 0
    of 3 unrelated commands.
- **The dry listing, [`logs/dry-listing.txt`](logs/dry-listing.txt):** 12 step calls in order, each exit 0, every remote script printed in
  full. It ran in the lab clone with logging stand-ins first on PATH, which saw no call.
- **Device commands** ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)): `dmcmd_audit.py` on the steps, with E128's guard scanned beside them,
  reads **GO, 11 send sites, 0 disallowed**, every one a line of the guard and READ. Without the guard
  ([`logs/dmcmd-audit-bare.txt`](logs/dmcmd-audit-bare.txt)) it reads NO-GO at exactly step 9's guard call, as v3.1's and k6's do. The
  steps call only E176's audited kit scripts and the guard's `config`.

## The steps (call each with this session's `RB_OUT`, a directory outside the repo, and `RB_LOCK`, the lock file of checks)

| step | file | what |
|---|---|---|
| 2 | `s02_window_q143k.sh <day> <last start> <last end>` | the window; E176 needs 76 minutes before the last end |
| 3 | `s03_desk_q143k.sh` | pull; HEAD descends from `RB_BASE` (`03582d2f`); E176's, M11's and the runbook's paths clean; M11's seven lists (58, 6, 9, 7, 7, 6, 4); E176's kit list (7) and the box list's 26 repo entries |
| 5 | `s05_look_q143k.sh aifoundry3 [--wait]` | look first (et-who, who, uptime, the holder rule; `ours_live`'s count), at most 30 minutes of polls |
| 6 | (not scripted) | the day's one post with aifoundry3's clause (section 15's rules, under the post's lock) |
| 7 | `s07_a3_sync_q143k.sh` | aifoundry3's rsync: E176's kit and every repo file of its box list, from the pushed commit only |
| 8 | `s08_a3_preflight_q143k.sh` | on the box: the box list 29 OK, `preflight_e176.sh` GO, the runner's `--list` with no tile problem |
| 9 | `s09_a3_reads_q143k.sh` | et-lab-manifest, the config through E128's guard (0 W / 65 °C / 600 MHz), et-who clean |
| 10 | `s10_a3_dry_q143k.sh start \| wait` | E176's V3_DRY session (every file checked; the dry smoke's NO-GO is expected), the full block on the toy (0), G0 at 53.4 °C (7), the session gate at a past start (8) |
| 11 | `s11_a3_session_q143k.sh [--later-try]` | E176's session, detached, refused on a short window, a dry pass or session of ours there, the dry job not ended rc 0 today, an earlier smoke without `--later-try`, or less than 40 minutes since the card's last session end of ours today (E171's or E176's) |
| 20 | `s20_wait_q143k.sh` | one bounded wait; 17 = call again; 16 on a gate (G0-REFUSED reported on its own) |
| 21 | (not scripted) | the release (a rewrite of the day's post) |
| 22 | `s22_collect_q143k.sh [<earlier M11 pass dir> ...]` | `collect_e176.sh`, `cc_gate` (v3.1's `ccdone_q142s.py`), the login scrub check, and the desk-path gate; "E176 collected and scored" |

The exit codes are v3.1's: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed, or a check of C did not
finish; 15 a holder after 30 minutes; 16 a gate; 17 call again. The window file has v3.1's keys.

**The order on aifoundry3:** only after E171 has ended and been collected. Pool 8's card day owns the card until then, and nothing here
reads or touches its lanes, locks, queues or post. After E171, at least 40 minutes of rest; step 11 refuses earlier.

## Not covered here

E177, on aifoundry2, has no kit (see `../e176/README.md`, "E177"). `rb_common.sh` and `s05` know aifoundry2, and `ours_live` names E177's
expected processes, so a later E177 port can reuse them.

## What it does to predicting power and heat

Nothing to any number. It makes sure M11's first per-session reading of heat over minutes is collected only from a session whose every
launch was checked for C to the end, with no desk path in its outputs, and launched only on a rested card in its window.

## Files

- `rb_common.sh`: k6's, with `ours_live`'s names and the q143k base. It calls v3.1's `rb_run.py`, `nopath_q142s.py` and `ccdone_q142s.py`
  by path, unchanged.
- The steps above.
- `list_steps_q143k.sh`, the dry listing; `selftest_runbook_q143k.sh`, the desk test.
- `logs/`.
- [`SHA256SUMS-q143k`](SHA256SUMS-q143k) pins them.

## Compute

The Intel, through the round's local slot, one job at a time on one core:
- the dry listing (12:42);
- the desk test, twice (12:43:25-12:43:42; then, after S2 and S3 were made to check their refusal's own text, 12:44:13-12:44:31, the
  committed log). The first run's S3 had passed on E176's own fresh session end, which the wait cases leave on the stand-in box;
- the audits (12:45).

No lab box, no mini job.

SPDX-License-Identifier: Apache-2.0
