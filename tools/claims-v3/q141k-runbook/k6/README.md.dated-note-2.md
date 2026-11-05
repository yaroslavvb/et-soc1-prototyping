# The k6 runbook, dated note 2: step 3b (all 22 hash lists at the go) and step 22 v3; the drivers the card day runs (Q142(v2) fix pass)

*Written Thu 5 Nov 2026 (week 45), about 08:30 PST, on the Intel, desk only, after the code it describes was committed (lab `e2b48f5a`,
08:27:12 PST) and before any E171 or E172 data. It sits beside [`README.md`](README.md) (`9a2630ff`) and its
[dated note 1](README.md.dated-note-1.md) (`1a76a870`), which stay as committed. Registered by dated notes 2 beside
[`E171.md`](../../e171/E171.md.dated-note-2.md) and [`E172.md`](../../e172/E172.md.dated-note-2.md) (`c9a3e40a`, before the code). It answers the
readiness critic (critic-q142xk: its fault 3, "s03 does not check SHA256SUMS-v2") and the first verifier of v2 (`verify-q142v2-code`: its
faults 1 and 4). Like the runs, it serves item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open).*

## The steps the card day runs (supersedes note 1's "use v2" and the readiness critic's "the v2 drivers only")

| step | file | what is new |
|---|---|---|
| 2 | `s02_window_k6.sh` | unchanged |
| 3 | `s03_desk_k6.sh` | unchanged: the pull, the ancestry of `14fcb30d`, the paths clean, 5 lists |
| **3b** | **`s03b_lists_k6.sh`** | **new: the readiness critic's 22 hash lists and this pass's 2, committed and in the work tree; 16 on any mismatch** |
| 5, 7-13, 20 | `s05_look_k6.sh`, `s07_a3_sync_k6.sh` ... `s13_a1_launch_k6.sh`, `s20_wait_k6.sh` | unchanged |
| **22** | **`s22_collect_k6_v3.sh e171`, then `e172`, then `ka`** | **v3: the pooled read through `score_p8_600_v3.py`; E172's pull only when aifoundry1 is quiet** |

Never `s22_collect_k6.sh` (v1) or `s22_collect_k6_v2.sh` (v2) on the card day. The dry listing of all of them in order is
`logs/dry-listing-v3.txt` (`list_steps_k6_v3.sh`, every step exit 0, no call).

## Step 3b, `s03b_lists_k6.sh`

It runs `lists22_k6.py` on the clone at HEAD, after s03's pull, and reads, for each list: the list file's own sha256 (pinned in the checker:
the 22 as committed in their creation commits, none changed since), its work-tree copy, its entry count, and every entry's committed blob and
work-tree file. **The 22 lists** are the readiness critic's set (its `work/lists_check.py`): blind7 91, blind6 80, frozen-sha256-e168.json 9 and
-scorer.txt 18, predict_q140e's FROZEN 26, M10's registration 174, M10 68 and SHA256SUMS-a2 10, POOL8-SHA256SUMS 209 and -62 62, the predictor's
SHA256SUMS 16 and -a2 9, the freeze's 160, the pool's 89, p8-600's SHA256SUMS 5 and SHA256SUMS-v2 4, frozen-sha256-e173.json 26 and -e174.json 32,
and the harness files of E171-E174, 97, 99, 135 and 110 (their box binaries left out: each kit's own box check reads those). **This pass's
two**: p8-600's `SHA256SUMS-v3` (4) and `SHA256SUMS-drivers-v3` (39): every runbook and kit file the card day's steps run at the desk, by path,
after this pass (k6's 13 steps and common file, v3.1's runner and gates, the kg runbook's common files, C-log lists and v2 and v3 drivers, the
kits' collectors, E172's box scripts, `score_e174.py` and E164's scrub), 35 of which no other list pins (the other 4: v3.1's
`nopath_q142s.py` and `ccdone_q142s.py`, `launch_e172.sh`, `collect_e173_bounded.sh`). The checker itself and its test are
in no list; the step prints the checker's sha256 (`8a201b20...` at `e2b48f5a`).

It prints `LISTS22: 22 of 22 PASS`, `LISTS-V3: 2 of 2 PASS` and `ALL LISTS PASS`, else stops the day with 16 ("a hash list does not match")
before any box step. Its desk test, `selftest_lists22_k6.sh` (`logs/selftest-lists22.txt`, run at `e2b48f5a`): **11 of 11** (all pass at HEAD;
at `1a76a870` the 22 pass and this pass's two are missing, 4; at `37f11663` 12 of 22, 4; a changed work-tree file of either kind, or a list's own
work-tree copy, 4, the file named; a revision that is not a commit, 2; the step 0 on the clone, 16 with a changed work tree, 10 when its
stand-in is set without `RB_DESKTEST=1`, and its dry listing runs nothing). One run of the checker takes about 1.5 s on the Intel.

## Step 22 v3, `s22_collect_k6_v3.sh`

v2's routes, line for line, except two (E172.md.dated-note-2.md, sections 2.1 and 2.5):
- **ka**: `score_p8_600_v3.py ka-pooled`: a session that kept fewer than 2 passes reads NOT SCORED (v2 refused it and the step stopped with 16);
  two files with the same measured D are refused (16). `score_p8_600_v2.py scale-c` is unchanged at each collection.
- **e172**: one 60 s read on aifoundry1 before the pull, with the runbook's prelude (`ours_live`, `jobs_live`): while a card session of ours
  (E174's queue on card 0, or E172's own) or a dry pass of either runbook (E174's box check) runs there, nothing is pulled and the step exits
  17: collect E172 after E174 has ended or been skipped.

Its desk test, `selftest_runbook_k6_v3.sh` (`logs/selftest-v3.txt`): **39 of 39**: v2's 35 checks, now through v3 (KA5 with the real
`score_p8_600_v3.py`), and Q1 (a dry pass live on aifoundry1: 17, no rsync, nothing collected), Q2 (E174's queue live: 17), Q3 (the dry pass
ended: the quiet read first, then the pull, 0) and KA6 (a NOT SCORED pooled read: 0). Q2 stands in the box's `pgrep` for the remote scripts, as
`../../q142kg-runbook/selftest_steps_q142kg_v2.sh` does: the Mac's own `pgrep` leaves out its ancestors, and a desk case's process is one. Run
end to end in a sandbox with the real scorer, C gate, v2 scale-c and v3 ka-pooled (not committed): 10 of 10 as expected.

## Device commands

`dmcmd_audit.py` on every k6 step file, `lists22_k6.py` and the scorer's v2 and v3, no allow-list: **GO, 11 send sites, every one READ**, with
E128's guard (`logs/dmcmd-audit-v3.txt`); without the guard, NO-GO only at `s09_a3_reads_k6.sh:20` (`logs/dmcmd-audit-v3-bare.txt`), as for v2.
The new files send no device command.

## At the go, after this note (the readiness critic's "at the desk first", updated)

1. `s02_window_k6.sh` and `../../q142kg-runbook/s02_window_q142kg.sh`, once each, the same day and times.
2. `s03_desk_k6.sh`, then **`s03b_lists_k6.sh`** (this replaces "all 22 hash lists by `work/lists_check.py`").
3. E174's order is written: [`../../e174/E174.md.dated-note-2.md`](../../e174/E174.md.dated-note-2.md), section 1 (no sentence is owed).
4. The drivers: this table, and `step_e173_v3.sh` and `step_e174_v3.sh` (`../../q142kg-runbook/README.md.dated-note-2.md`).

SPDX-License-Identifier: Apache-2.0
