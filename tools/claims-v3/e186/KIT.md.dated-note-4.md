# E186's kit, dated note 4: step 11 v4, which runs step 11 v2 unchanged and then note M2's reader v2 through its gate v2; kit note 3's sentence on a list off its bytes corrected (the history check stops first); with the dry listing v4 and the runbook desk test v4 (Q158; before any datum)

*Sun 8 Nov 2026 (week 45), PST, on the Intel, desk only (Q158, `fix-arms`): no card was claimed, no device command was sent, no lab box was
reached, nothing was posted. **No E186 datum exists** (`git log --all` shows no `docs/reports/data/*e186*`; note M2's dated note 1, section 5).
It carries out note M2's dated note 1 ([`E186.md.dated-note-M2.md.dated-note-1.md`](E186.md.dated-note-M2.md.dated-note-1.md), committed with
it) for the kit, and answers the round's adversarial verifier of note M2 and kit note 3 (`verify-arms`, 13:12-14:01 PST today: holds with
fixes), its fault 1, which is the kit's. New files only: [`KIT.md`](KIT.md), its dated notes [1](KIT.md.dated-note-1.md),
[2](KIT.md.dated-note-2.md) and [3](KIT.md.dated-note-3.md), [`KIT-BRIEF.md`](KIT-BRIEF.md) with its dated notes 1 and 2, and every kit file
stay as committed, and every step but step 11 is as kit note 1 runs it. **No rule's statistic, threshold or words change, and no forecast,
plan, cap, stop or device command changes.** A reading of note M2's arms is a reported arm's, never a rule's.*

## Results first

- **Step 11 v4** ([`rb/s22_collect_e186_v4.sh`](rb/s22_collect_e186_v4.sh)) is step 11 v3 ([`rb/s22_collect_e186_v3.sh`](rb/s22_collect_e186_v3.sh))
  line for line with four changes, each marked "kit note 4": its step's name; note M2's list v2,
  [`SHA256SUMS-e186-m2-v2`](SHA256SUMS-e186-m2-v2), pinned at its count and own sha256 (9 entries, `db3b69256b39edadb62d7a487744a7f4df4501a5220f1fc86a255fdcdd78f941`) in place of v1's
  list; **note M2's gate v2** ([`rb/check_m2_e186_v2.py`](rb/check_m2_e186_v2.py)) in place of v1's, which runs **note M2's reader v2**
  ([`arm_m2_read_e186_v2.py`](arm_m2_read_e186_v2.py)) in place of v1; and the reading's words, which name the reader v2. As in v3, step 11 v2
  runs first and unchanged; any exit of v2 but 0 is v4's, and nothing of note M2 runs then.
- **The gate v2** is the gate v1 line for line, with the reader v2 in its place, step 11 v4 named in two messages, and its read line naming
  the reader v2.
- **Kit note 3's sentence on a list off its bytes is corrected** (section 3): on the day a change to any of note M2's files or lists is
  refused by the history check (16), in step 2 and again inside step 11 v2, before note M2's gate runs; it never reads "M2 NOT READ".
- **Tests** (desk checks of code; section 5): SELFTEST-ARM-M2-E186-V2 **16 of 16 PASS** (note M2's dated note 1); SELFTEST-RB-E186-V4
  **14 of 14 PASS**; the dry listing v4, 19 steps, 0 failing, no call; `dmcmd_audit` **GO**, 0 send sites, in both sets. No added file shadows a module (the
  history checks' HISTORY OK).

## 1. Step 11 v4

[`rb/s22_collect_e186_v4.sh`](rb/s22_collect_e186_v4.sh), in order (v3's, with v4's gate, list and reader):
1. the window rule (`e186_window`, as every E186 step reads it); a desk-test stand-in (`K6E186_S22V2`, `K6E186_M2READER`) set without
   `RB_DESKTEST=1` refuses (10) before any call;
2. **step 11 v2, unchanged** (`bash rb/s22_collect_e186_v2.sh`): its exit is v4's if it is not 0, with the line `step 11 v2 exited <rc> (its
   lines above): note M2's gate and reader were not run`;
3. **note M2's gate v2 and reader v2** (`rb/check_m2_e186_v2.py`, in the desk class: its own bounds, the reader 50 s and git's status 60 s), with
   the data directory `build/e186-out/<day>-e186-one-number-r3-aifoundry3` and a work directory `RB_OUT/m2-work`;
4. the reading: **read** (`M2-READ`, by the reader v2), or **M2 NOT READ** with the gate's or the reader's own words, in
   `arm-m2-e186.status.txt` and the last line; **M2-WROTE-OTHER** stops the step (16): read the data directory before any commit.

The data commit then carries `arm-m2-e186.json`, `arm-m2-e186.txt` and `arm-m2-e186.status.txt` beside note M1's files, under the names kit
note 3 gave them; the data README records the reading, or "M2 NOT READ" with its words. Step 11 v3 is never run that day.

## 2. Note M2's gate v2

[`rb/check_m2_e186_v2.py`](rb/check_m2_e186_v2.py) (Python's own modules only; run from the lab's top) checks, before the reader runs: the
list v2 at its own sha256 and its count as step 11 v4 passes them; every entry's file at its bytes; the reader v2 and its json
`m2-october-forecast-model-e186.json` among the entries; no uncommitted change to any entry or to the list (git status); the scorer's file
`scored-e186.json` in the data directory. Then it copies the scorer's file into the work directory (refused inside the repo), runs
`/usr/bin/python3 -B tools/claims-v3/e186/arm_m2_read_e186_v2.py --scored <work>/scored-e186.json --out <work>/arm-m2-e186` bounded at 50 s,
copies the reader's two outputs into the data directory, and checks that nothing else there changed. It prints one of `M2-READ ... (note
M2's reader v2)` (exit 0), `M2 NOT READ: <why> (the gate refused; the reader never ran ...)` (4), `M2 NOT READ: the reader refused, rc <n>
...` or killed at its bound (5), or `M2-WROTE-OTHER <files> ...` (16); 10 is usage. The reader v2's own refusals are v1's (2 a pinned file
differs, 3 no trains) and one more, 4: a non-finite number left to write. Note M1's gate (`rb/check_history_e186.py m1`) is unchanged and
runs first, inside step 11 v2.

## 3. A list off its bytes: the history check stops first (verify-arms' fault 1)

- **What kit note 3 said.** Its section 3's first bullet ends *"A list off its bytes on the day is no stop at step 2; step 11 v3's gate then
  reads M2 NOT READ"*, and the brief's note 2, item 5, says the same (*"any value there is no stop at step 2. A list off its bytes is read at
  step 11 v3 as M2 NOT READ"*). For every cause inside the repository that is wrong.
- **What happens.** Every file note M2's list names, every file its list v2 names, and both lists lie in E186's core directories
  (`tools/claims-v3/e186/` and `tools/claims-v3/m12/`). So a change to any of them, committed or not, is refused by the history check (16):
  - **in step 2 v2,** by step 2 v1's history check, before the line that reports the lists is reached: the round's verifier ran step 2 v2
    with note M2's list one byte off, not committed and then committed, and both read 16, "no box step today"; this note's check on a
    scratch clone holding its commit (never pushed) did the same with the list v2, 16 both times, the history check naming the list;
  - **in step 11 v2** (inside step 11 v3 and v4), by the history check v2 after COPY-BACK EXACT and before any scoring; step 11 v3 or v4 then
    exits 16 with step 11 v2 and never reaches note M2's gate (the verifier's case on a staged session with the real step 11 v2, and this
    note's desk case HV: note M2's list v2 one byte off, not committed, 16, the list named).

  This is what kit note 3's own second bullet says. The stop fails closed, and it arises only if a later commit breaks the additions-only
  rule or a file is left changed in the clone; at step 11, the brief's note 1 reads a 16 from the history check v2 (the raw copy stays,
  nothing is scored, a dated note first).
- **So the gate's "M2 NOT READ" comes from its other causes:** no scorer's file; the reader's refusal (its own pins, a scorer's file with no
  trains, a non-finite number left to write) or its 50 s bound; a work directory inside the repo; and a change made in the seconds between
  step 11 v2's history check and the gate, which the gate's own reading of the list is left to see. The desk tests' cases G1-G3 (kit note
  3's and this note's) read "M2 NOT READ" only because step 11 v2 is stood in there.
- **Step 2's line for a later M-note's list stays a report:** step 2 v1 reads every `SHA256SUMS-e186-m[2-9]*` list it finds (note M2's list
  and its list v2) and records each list's rc and count; no value there stops step 2 of its own, because the history check, which runs
  first, is the stop.

## 4. The runbook as it now runs (KIT.md section 3's table, with kit notes 1 and 3's rows and this note's)

| KIT.md box step | file (this note's in bold) |
|---|---|
| 1, the window | `rb/s02_window_e186.sh <day> <last start> <last end>` (v1) |
| 2, the desk check | `rb/s03_desk_e186_v2.sh` (kit note 1; step 2 v1 inside it, first; note M2's lists reported) |
| 4, the look, FIRST | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` |
| 3, the post, after the look | not scripted (KIT-BRIEF.md section 3) |
| 5, the sync | `rb/s07_a3_sync_e186_v2.sh` (kit note 1) |
| 6, the build and the box's checks | `rb/s08_a3_build_e186.sh start`, then `wait` while it says 17, or 14 with "no reading" (v1) |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` |
| 8, the dry pass | `rb/s10_a3_dry_e186.sh start`, then `wait` (v1) |
| 9, the session | `rb/s11_a3_session_e186.sh FULL yes` (or `PASSES no`) (v1) |
| 10, the wait | `rb/s20_wait_e186.sh`, while it says 17 (v1) |
| 11, the release, then the collection | **`rb/s22_collect_e186_v4.sh`** (step 11 v2 first, then note M2's gate v2 and reader v2) |

**On the day, step 11 runs only as v4;** its v3, v2 and v1 files are never run by hand (v4 runs v2 inside it). The dry listing of both
paths is [`rb/list_steps_e186_v4.sh`](rb/list_steps_e186_v4.sh): v3's, with step 11 v4 in both paths.

## 5. The checks (desk checks of code; nothing measured)

| check | result | log |
|---|---|---|
| note M2's reader v2 on synthetic sessions only (v1's eleven cases; a train's interval NaN, a train's hi infinite, a kind's D_w NaN, a kind with `c_kept` false; every output strict json) | **SELFTEST-ARM-M2-E186-V2 16 of 16 PASS** | `logs/selftest-arm-m2-e186-v2.txt` |
| step 11 v4 and the dry listing v4 with a fake ssh and rsync and a stand-in box (v3's cases with v4; HV, the real step 11 v2 with note M2's list v2 one byte off: 16 from the history check v2, the gate never called; NT and CK, the reader v2 through the gate v2 on a NaN train and on a kind whose check of C failed: "not read" in all four arms, the json strict) | **SELFTEST-RB-E186-V4 14 of 14 PASS** | `logs/selftest-rb-e186-v4.txt` |
| the dry listing v4, both paths | 19 steps, 0 failing, no call; its two step 11 v4 blocks kept | `logs/dry-listing-step11-e186-v4.txt` |
| `dmcmd_audit`, this note's runbook files with the steps v4 runs, E186's runbook file and k6's common file (`rb_common.sh`); and the desk files | GO, 0 send sites, 0 disallowed, in both sets: this note adds no device command | `logs/dmcmd-audit-note4-e186.txt` |

The dry listing's other blocks are the dry listing v3's (kit note 3) but for the sample's times and step 2's line, which lists note M2's
two lists (reported, never a gate); re-make the whole listing with `bash tools/claims-v3/e186/rb/list_steps_e186_v4.sh <an empty scratch
dir>`. In a dry listing step 2 v1's count for each later list reads a capture a dry listing never writes, so it prints one `grep` complaint for
each such list on its error stream and goes on (exit 0), as kit note 3 says; a real step 2 writes the capture and is not affected.

## 6. Builds on (the stock-take's rule, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sun 8 Nov 2026 at 14:21 PST: public rows H27 and H28 (the kits' meter and stops); newer
   pieces by commit: E186's registration (`a41408d9`), note M1 (`3adb8bfe`), the kit (`523002be`), A1 (`17cf100f`), the kit's notes 1
   (`88750359`) and 2 (`e8e9f4e1`), note M2 and the kit's note 3 (`8c808677`).
2. **Used** (unchanged, run or sourced; sha256 in [`SHA256SUMS-e186-note4`](SHA256SUMS-e186-note4)): step 11 v3, which v4 follows line for
   line but its four changes, and step 11 v2 with everything it runs (kit note 1); note M2's gate v1, which the gate v2 follows line for line
   but its reader; the runbook file `rb/rb_e186.sh` and k6's common file (`rb_common.sh`); the dry listing v3 (kit note 3), which v4 follows
   but its two step 11 lines; the runbook desk test v3's setup and cases (kit note 3), which the desk test v4 follows. *Check against the same
   operation:* the desk test v4's case C runs the real step 11 v2 to the same C gate stop (14) as kit note 3's case C, and its case HV the
   real history check v2 to the same 16 the round's verifier read.
3. **Not used:** any card time; any rule or forecast; note M2's figures beyond the reader's run.
4. **Tiers:** public tier; it cites public pieces only.
5. **Readiness:** the round's critic reads this block against INVENTORY.md and the cited commits.

## 7. What the desk cannot show, and what remains

1. Note M2's reader v2 has read only synthetic sessions: its first real reading is the session's step 11 v4.
2. A later change to any of note M2's files, or to this note's, stops step 2 and step 11 (section 3): additions only.
3. Note M1's reader keeps v1's reading of a non-finite figure and of a kind whose check of C failed; note M2's dated note 1, section 3,
   registers how the records read those cases (on the day, only K09 in the fallback can meet them).
4. The round's critic; card time waits on his go (`KIT-BRIEF.md` with its dated notes 1-3).

## Labels

Note M2's arms are **reported** and their forecasts **blind** for E186 (E186.md.dated-note-M2.md with its dated note 1). Every desk test here
is a check of code at the desk, not a measurement: nothing is held out or post hoc, and no E186 datum exists.

## Compute

On the Intel through the round's local slot, one job at a time: the reader v2's self-test (seconds), the runbook desk test v4 (under a
minute), the dry listing (seconds) and the audit (seconds). No bench job, mini, lab box or card was used. The desk tests wrote only under
the round's scratch.

SPDX-License-Identifier: Apache-2.0
