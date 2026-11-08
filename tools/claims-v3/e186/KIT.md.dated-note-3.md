# E186's kit, dated note 3: step 11 v3, which runs step 11 v2 unchanged and then reads october-forecast-model's note M2 through its own gate, with the dry listing v3 and the runbook desk test v3 (Q158; before any datum)

*Sun 8 Nov 2026 (week 45), PST, on the Intel, desk only (Q158): no card was claimed, no device command was sent, no lab box was reached,
nothing was posted. **No E186 datum exists** (`git log --all` shows no `docs/reports/data/*e186*`; note M2, M2-2). It carries out the
registration's dated note M2 ([`E186.md.dated-note-M2.md`](E186.md.dated-note-M2.md), committed with it) for the kit: a gate of its own
and a step 11 v3 that runs note M2's reader after note M1's. New files only: [`KIT.md`](KIT.md), its dated notes
[1](KIT.md.dated-note-1.md) and [2](KIT.md.dated-note-2.md), [`KIT-BRIEF.md`](KIT-BRIEF.md) with its dated note 1, and every kit file stay as
committed, and every step but step 11 is as kit note 1 runs it. **No rule's statistic, threshold or words change, and no forecast, plan, cap,
stop or device command changes.** A reading of note M2's arms is a reported arm's, never a rule's.*

## Results first

- **Step 11 v3** ([`rb/s22_collect_e186_v3.sh`](rb/s22_collect_e186_v3.sh)) runs step 11 at its latest version, v2
  ([`rb/s22_collect_e186_v2.sh`](rb/s22_collect_e186_v2.sh)), first and unchanged, so the collection, COPY-BACK EXACT, the history check v2, the
  pairing check, the scorer and note M1's reader through its gate are v2's, in v2's order. On v2's 0 only, it runs **note M2's gate**
  ([`rb/check_m2_e186.py`](rb/check_m2_e186.py)) and then **note M2's reader**, after note M1's. Any other exit of v2 is v3's exit, and nothing
  of note M2 runs.
- **The gate:** note M2's list, [`SHA256SUMS-e186-m2`](SHA256SUMS-e186-m2), at the count and its own sha256 that step 11 v3 pins (8 entries,
  `e23bb2df...`), every entry at its bytes, the reader and its json among them, nothing uncommitted, the scorer's file there. Then the reader
  by note M2's own run line, on a copy of the scorer's file in RB_OUT: the reader never sees the data directory, and only its two outputs
  are put there.
- **A failed gate, or a reader's refusal, reads "M2 NOT READ"** in the step's last line and in `<out>/arm-m2-e186.status.txt`; it **never
  stops the step and never changes the session's scoring**, and the step exits 0 as v2 did. One case stops it (16) before the data commit:
  **M2-WROTE-OTHER**, a data directory changed beside the reader's two outputs.
- **Step 2 reports note M2's list, never refuses on it:** step 2 v1's line for "a later october-forecast-model note's list"
  (`SHA256SUMS-e186-m[2-9]*`), run inside step 2 v2, reads it and records its rc and count, as it was written to (section 3).
- **Tests** (desk checks of code; section 5): SELFTEST-ARM-M2-E186 **11 of 11**; SELFTEST-RB-E186-V3 **11 of 11**; the dry listing v3, 19 steps,
  0 failing, no call; `dmcmd_audit` **GO**, 0 send sites, in both sets. No added file shadows a module (the history check's HISTORY OK).

## 1. Step 11 v3

[`rb/s22_collect_e186_v3.sh`](rb/s22_collect_e186_v3.sh), in order:
1. the window rule (`e186_window`, as every E186 step reads it); a desk-test stand-in (`K6E186_S22V2`, `K6E186_M2READER`) set without
   `RB_DESKTEST=1` refuses (10) before any call;
2. **step 11 v2, unchanged** (`bash rb/s22_collect_e186_v2.sh`): its exit is v3's if it is not 0, with the line `step 11 v2 exited <rc> (its
   lines above): note M2's gate and reader were not run`;
3. **note M2's gate and reader** (`rb/check_m2_e186.py`, in the desk class: its own bounds, the reader 50 s and git's status 60 s, so no bound
   of the runbook's can stop the step after v2), with the data directory `build/e186-out/<day>-e186-one-number-r3-aifoundry3` and a work
   directory `RB_OUT/m2-work`;
4. the reading: **read** (`M2-READ`), or **M2 NOT READ** with the gate's or the reader's own words, in `arm-m2-e186.status.txt` and the last
   line; **M2-WROTE-OTHER** stops the step (16): read the data directory before any commit.

The data commit then carries `arm-m2-e186.json`, `arm-m2-e186.txt` and `arm-m2-e186.status.txt` beside note M1's files; the data README records
the reading, or "M2 NOT READ" with its words.

## 2. Note M2's gate

[`rb/check_m2_e186.py`](rb/check_m2_e186.py) (Python's own modules only; run from the lab's top) checks, before the reader runs: the list at
its own sha256 and its count as step 11 v3 passes them; every entry's file at its bytes; the reader `arm_m2_read_e186.py` and its json
`m2-october-forecast-model-e186.json` among the entries; no uncommitted change to any entry or to the list (git status); the scorer's file
`scored-e186.json` in the data directory. Then it copies the scorer's file into the work directory (refused inside the repo), runs
`/usr/bin/python3 -B tools/claims-v3/e186/arm_m2_read_e186.py --scored <work>/scored-e186.json --out <work>/arm-m2-e186` bounded at 50 s,
copies the reader's two outputs into the data directory, and checks that nothing else there changed. It prints one of `M2-READ ...`
(exit 0), `M2 NOT READ: <why> (the gate refused; the reader never ran ...)` (4), `M2 NOT READ: the reader refused, rc <n> ...` or killed at
its bound (5), or `M2-WROTE-OTHER <files> ...` (16); 10 is usage. Note M1's gate (`rb/check_history_e186.py m1`) is unchanged and runs first,
inside step 11 v2.

## 3. Step 2, the history check and note M2's files

- **Step 2 is unchanged.** Step 2 v1 (inside step 2 v2) reads every later dated M-note's list it finds, `SHA256SUMS-e186-m[2-9]*`, with
  `shasum -a 256 -c`, and records the result in its last line and log (`SHA256SUMS-e186-m2 rc 0 (8 OK)` on a scratch clone holding this
  commit, before it was made): reported, never a gate. A list off its bytes on the day is no stop at step 2; step 11 v3's gate then reads M2 NOT READ.
- **The history check (v1 and v2, unchanged) reads every file under `tools/claims-v3/e186/` as one of E186's paths,** so a later change
  other than an addition to one of note M2's or this note's files stops step 2 and step 11 (16), where note M1's five files and list are
  exempt in v1 (reported there). Note M2 and this note are additions only, so the case arises only if a later commit breaks that rule; the
  stop is then the history check's, before any card time.
- **Shadowing:** the three Python files added here (`arm_m2_read_e186.py`, `selftest_arm_m2_e186.py`, `rb/check_m2_e186.py`) shadow no
  module the system python finds and share no module name with another of E186's or the day's modules: the history checks read HISTORY OK
  at this commit (section 5).

## 4. The runbook as it now runs (KIT.md section 3's table, with kit note 1's rows and this note's)

| KIT.md box step | file (this note's in bold) |
|---|---|
| 1, the window | `rb/s02_window_e186.sh <day> <last start> <last end>` (v1) |
| 2, the desk check | `rb/s03_desk_e186_v2.sh` (kit note 1; step 2 v1 inside it, first; note M2's list reported) |
| 4, the look, FIRST | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` |
| 3, the post, after the look | not scripted (KIT-BRIEF.md section 3) |
| 5, the sync | `rb/s07_a3_sync_e186_v2.sh` (kit note 1) |
| 6, the build and the box's checks | `rb/s08_a3_build_e186.sh start`, then `wait` while it says 17, or 14 with "no reading" (v1) |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` |
| 8, the dry pass | `rb/s10_a3_dry_e186.sh start`, then `wait` (v1) |
| 9, the session | `rb/s11_a3_session_e186.sh FULL yes` (or `PASSES no`) (v1) |
| 10, the wait | `rb/s20_wait_e186.sh`, while it says 17 (v1) |
| 11, the release, then the collection | **`rb/s22_collect_e186_v3.sh`** (step 11 v2 first, then note M2's gate and reader) |

**On the day, step 11 runs only as v3;** its v2 and v1 files are never run by hand (v3 runs v2 inside it, and v2 is v1's with kit note 1's
changes). The dry listing of both paths is [`rb/list_steps_e186_v3.sh`](rb/list_steps_e186_v3.sh): v2's, with step 11 v3 in both paths.

## 5. The checks (desk checks of code; nothing measured)

| check | result | log |
|---|---|---|
| note M2's reader on synthetic sessions only (the planned session, each arm's own centres, 0.1 W and 0.3 W off, the fallback, a train NOT SCORED, a changed json, a changed list, no trains, its outputs alone) | **SELFTEST-ARM-M2-E186 11 of 11 PASS** | `logs/selftest-arm-m2-e186.txt` |
| step 11 v3 and the dry listing v3 with a fake ssh and rsync and a stand-in box (the dry listing; a stand-in refused without RB_DESKTEST; the REAL step 11 v2 to its C gate, 14, the gate never called; v2 stood in: 16 passed through; M2 read, the outputs byte for byte a by-hand run, the scorer's file unchanged; the list one line short, the reader and its line rewritten together, the json changed and not committed: M2 NOT READ, exit 0; the reader's refusal: M2 NOT READ, exit 0; a stand-in reader writing beside its outputs: M2-WROTE-OTHER, 16) | **SELFTEST-RB-E186-V3 11 of 11 PASS** | `logs/selftest-rb-e186-v3.txt` |
| the dry listing v3, both paths | 19 steps, 0 failing, no call; its two step 11 v3 blocks kept | `logs/dry-listing-step11-e186-v3.txt` |
| `dmcmd_audit`, kit note 3's runbook files with the steps v3 runs, E186's runbook file and k6's common file (`rb_common.sh`); and the desk files | GO, 0 send sites, 0 disallowed, in both sets: this note adds no device command | `logs/dmcmd-audit-note3-e186.txt` |

The dry listing's other blocks are the dry listing v2's (`logs/dry-listing-e186-v2.txt`, kit note 1) but for the sample's times, step 2's
line listing note M2's list (reported, never a gate) and the post's line; re-make the whole listing with
`bash tools/claims-v3/e186/rb/list_steps_e186_v3.sh <an empty scratch dir>`. In a dry listing, step 2 v1's count for that later list reads
a capture a dry listing never writes, so it prints one `grep` complaint on its error stream and goes on (exit 0); a real step 2 writes the
capture and is not affected.

## 6. Builds on (the stock-take's rule, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sun 8 Nov 2026 at 12:44 PST: public rows H27 and H28 (the kits' meter and stops); newer
   pieces by commit: E186's registration (`a41408d9`), note M1 (`3adb8bfe`), the kit (`523002be`), A1 (`17cf100f`), the kit's notes 1
   (`88750359`) and 2 (`e8e9f4e1`).
2. **Used** (unchanged, run or sourced; sha256 in [`SHA256SUMS-e186-note3`](SHA256SUMS-e186-note3)): step 11 v2 and everything it runs (kit
   note 1); the runbook file `rb/rb_e186.sh` and k6's common file (`rb_common.sh`); the dry listing v2 (kit note 1), which v3 follows line for line but its step
   11 lines and one echo's words; the runbook desk test v2's setup (kit note 1), which the desk test v3 follows. *Check against the same
   operation:* the desk test v3's case C runs the real step 11 v2 to the same C gate stop (14) as kit note 1's case C.
3. **Not used:** any card time; any rule or forecast; note M2's figures beyond its reader's run.
4. **Tiers:** public tier; it cites public pieces only.
5. **Readiness:** a verifier checks this block against INVENTORY.md and the cited commits.

## 7. What the desk cannot show, and what remains

1. Note M2's reader has read only synthetic sessions: its first real reading is the session's step 11 v3.
2. A later change to note M2's or this note's files stops step 2 (section 3): additions only.
3. A verifier of note M2 and this note, then the readiness critic; card time waits on his go (`KIT-BRIEF.md` with its dated notes 1 and 2).

## Labels

Note M2's arms are **reported** and their forecasts **blind** for E186 (E186.md.dated-note-M2.md). Every desk test here is a check of code at
the desk, not a measurement: nothing is held out or post hoc, and no E186 datum exists.

## Compute

On the Intel through the round's local slot, one job at a time: the reader's self-test (about 2 s), the runbook desk test v3 (about 20 s),
the dry listing (about 4 s) and the audit (seconds). No bench job, mini, lab box or card was used. The desk tests wrote only under the
round's scratch.

SPDX-License-Identifier: Apache-2.0
