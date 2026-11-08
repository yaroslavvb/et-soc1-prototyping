# E185's kit, dated note 4 (Sun 8 Nov 2026, before any E185 datum): step 2 v5 runs the day-2 check v2 before step 2 v4 (v1's check on the perimeter of what the day's scorer and collector load, by a run-time trace, and no untracked module in any of the day's directories), and october-forecast-model's M1 reader runs behind the check v2's gate; no box file, rule, forecast, threshold, plan, cap, stop or order of box steps changes

*Beside [KIT.md](KIT.md) (`460c352f`, git 21:17:55 PST Sat 7 Nov 2026) and its dated notes [1](KIT.md.dated-note-1.md) (`ad2ed873`, git
22:45:02 PST Sat 7 Nov), [2](KIT.md.dated-note-2.md) (`408a9a9e`, git 06:48:51 PST Sun 8 Nov) and [3](KIT.md.dated-note-3.md)
(`1e74546a`, git 08:37:53 PST Sun 8 Nov); it edits nothing there. Written on the Intel, desk only (no card, no device command, no ssh to a
lab box, no post in the lab's channel, no Modal), by the lane `fix-fx` of Q158, begun at 11:31 PST Sun 8 Nov 2026 by the clock; its
commit's own time is git's. It answers the adversarial verifier of kit note 3, of E183's kit note 2 and of E186's A1 and kit note 1
(`verify-fx`, Sun 8 Nov 2026 10:42-11:3x PST: **holds with fixes**, 0 critical, 0 major, 2 minor faults and 6 nits, none blocking): its
faults 1 and 2 here (E185's side) and in E183's kit note 3 ([`../e183/KIT.md.dated-note-3.md`](../e183/KIT.md.dated-note-3.md)), its nit 8
in the brief's dated note 2 ([`CARD-LANE-BRIEF.md.dated-note-2.md`](CARD-LANE-BRIEF.md.dated-note-2.md), the same in both kits), and its
nits 3-7, which are E186's, in E186's kit note 2 ([`../e186/KIT.md.dated-note-2.md`](../e186/KIT.md.dated-note-2.md)). **No E185 datum
exists** (`git log --all` on `docs/reports/data/*e185*` and `*-e185-*`: nothing). **No box file changes:** `frozen-e185.sha256`'s 30
entries, the runner, the session, the block, the smoke gate, the stops and the device commands are the kit's as committed, and so is every
step that reaches the box.*

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| **the day-2 desk test v2**, on a scratch clone of a local bare upstream (itself a clone of the lab) and a helper clone of it; stand-in ssh, rsync and scp refuse any call | **SELFTEST-DAY2-V2 PASS, 20 of 20**; 0 calls to any box, 0 lines in the lock file | [`rb/logs/selftest-day2-v2.txt`](rb/logs/selftest-day2-v2.txt) |
| **the dry listing v5** | every step exits 0, no ssh or rsync call; the look before the day's post; step 2 v5 listed twice (step 2, and again just before step 14); the M1 gate v2 after step 14 and the data commit | [`rb/logs/dry-listing-v5.txt`](rb/logs/dry-listing-v5.txt) |
| **device commands**, the runbook with step 2 v5 and the day-2 check v2 before step 2 v4 (v4, v1 and v3 still scanned: they run inside v5) | **GO, 11 send sites**, every one a READ; bare, NO-GO at exactly step 9's guard call; **both bodies byte for byte kit note 3's** | [`rb/logs/dmcmd-audit-v5.txt`](rb/logs/dmcmd-audit-v5.txt), [`rb/logs/dmcmd-audit-bare-v5.txt`](rb/logs/dmcmd-audit-bare-v5.txt) |
| **every step 2 for real** at this note's commit: step 2 v5 and v4, E183's v4 and v3, E186's v2, and the checks v2 and v1 by hand, each with its own window written that day | run by the lane first on a scratch clone holding this same commit, then on the lab clone after it | the lane's own runs (the records give each exit status and time) |

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Sun 8 Nov 2026 at 11:58:12 PST: public rows H07, H08,
   H09, H24, H25 and H28 (opaque pointers), the pieces whose committed files the day's scorer and the check of C load (E78-E125's committed
   runs, the bench's sources, pool 8's lists, M11 and E176, the kits' meter and stops).
2. **Used.**
   - **Kit note 3** (`1e74546a`): [`rb/check_day2_v1.py`](rb/check_day2_v1.py), loaded by its path and run unchanged inside the check v2
     (its anchor `6860643c`, its rules, its functions and its exit codes); [`rb/s03_desk_e185_v4.sh`](rb/s03_desk_e185_v4.sh), run unchanged
     inside step 2 v5; `rb/list_steps_e185_v4.sh`, the form of the dry listing v5; `rb/selftest_day2_v1.sh`, the form of the desk test v2.
   - **verify-fx's cases**, re-made on this test's clone: L3, L4, L5, S7, U3 and U5; its L2 in the form its fault states (a file rewritten
     together with its line in a list the scorer opens outside v1's perimeter: M5's `fit_m5.py` in M10's `SHA256SUMS`).
   - **E185's collection and score, run end to end**: E185's runbook desk test v2 (`rb/selftest_rb_e185_v2.sh`, kit note 1), whose case E2
     collects and scores a stand-in session made of E181's committed passes with M11's scorer v5; E183's runbook desk test v2; both M1
     readers' self-tests (the trace, below).
   - *The same operation, earlier:* on the intact tree the check v2 and v1 read alike (P0: both 0, and step 2 v5 runs v4's lines inside
     it); every one of v1's paths is among v2's (case C); v2 differs only where its wider perimeter or its untracked read refuses.
3. **Not used.** Any change to a box file or a box step; aifoundry1 or aifoundry2; any E185 datum (none exists); E186's checks (E186 runs its
   own history check v2, kit note 1); anything of the private tier.
4. **Tiers.** Public tier only. No private-tier check is used, so there is no sha256 line.
5. **Readiness.** This block is the note's own.

## The runbook as it now runs (kit note 3's table, with this note's changes)

| step | file | from this note |
|---|---|---|
| **0, before step 1** | **`/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull`** | **new:** the day-2 check v2 by hand, in place of v1's (the brief's dated note 2, section 1) |
| 1, the window | `rb/s02_window_e185.sh <day> <last start> <last end>` | unchanged |
| 2, the desk check | **`rb/s03_desk_e185_v5.sh`** | **new:** the day-2 check v2 with its own pull, then step 2 v4 unchanged on the same tree (the check v1, then step 2 v3), then HEAD unchanged |
| 3-13 | as kit note 2's table | unchanged |
| **before 14** | **`rb/s03_desk_e185_v5.sh` again**, with the same `RB_OUT` | step 14 only on its 0 (the brief's dated note 2, item 3) |
| 14, the collection | `rb/s22_collect_e185_v2.sh` | unchanged |
| **after the data commit** | **`/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py m1 e185 --data <E185's data dir> --rb-out <E185's RB_OUT>`** | **new:** v1's M1 gate with the check v2's tree check |

**Step 2 v4 is never run alone on E185's card day** (it runs inside v5), nor v3, v2 or v1; the check v1 runs only inside v4, and the M1
gate only as v2's.

## Fault by fault

### verify-fx's minor fault 1: the day-2 check's perimeter missed files the day's scorer and collector load

- **What it was.** The check v1 holds what its 32 lists, E183's harness and E185's runbook pins name (6 directories and 133 named files).
  M11's scorer v5, which scores E185's registered rules, with `arms_e185.py`, loads lab files outside that: by verify-fx's import-time trace
  160, among them 6 imported modules named by no list (`tools/claims-v3/hpl/surface_hpl.py`, `hpl/surface_hpl_t.py`, `kspeed/e83/predict_e83.py`,
  `e119/make_predictions_e119.py`, and two predictors under `docs/reports/data/`), and it opens 12 hash lists v1 does not read, 6 of them
  outside the day's paths. E185's collection runs `tools/claims-v3/ccheck/ccheck.py`, named only by a list v1 does not read. So a committed
  change to one of them passed v1 and both step 2s. Its precondition is a committed in-place edit, which the lab forbids; none of them has
  changed since `6860643c`.
- **What this lane found beside it, by a run-time trace.** verify-fx traced each script's imports and opens through `--help`. This lane ran
  E185's runbook desk test v2 (its case E2 collects and scores, end to end, a stand-in session made of E181's committed passes, through step
  14 v2: the copy-back, the check of C, the gates, the scrub and M11's scorer v5 with E185's rules), E183's runbook desk test v2 (its case
  C1 runs step 11 v2: the copy-back check, the collector v2, the reduction v2 and the scorer) and both M1 readers' self-tests, with a tracer
  on the scratch clone's `PYTHONPATH` recording, for every Python process they started, the files it opened, the directories it listed and
  the modules it loaded (scratch only; nothing of it is committed). The desk tests' own helpers (`selftest_*.py`, `fake_card_*.py`) are
  left out. **At run time the scorer also opens the two pooled sessions `score_e185.sh` names**, E176's committed pass (its `marks.jsonl`,
  `runs.jsonl` and `telemetry.jsonl.gz`) and E181's (its measured pass's three, and its smoke pass's `telemetry.jsonl.gz`), **and the check
  of C opens the bench's `rtl-sim/fma_toggle_v2/accum.c`**: 8 more files outside v1's perimeter. **In all 168 files (24 of them Python
  modules), none changed since `6860643c`** (the last commit touching any is `d4e5119d`, git 11:21:42 PST Fri 6 Nov 2026). Every other
  day-2 step traced loads nothing outside v1's perimeter: E183's copy-back check, collector, reduction, scorer and harness check; E185's
  scrub, launch gate and check-of-C gate; the runbook's own runner. The scripts put 18 in-repo directories on `sys.path`, 4 of them
  (`kspeed/e83`, `e119` and two predictors' data directories) outside v1's directories; no day-2 step lists a committed directory except
  the import system's own reads of those (E183's reduction puts `workloads/enercat`, a core directory, there for one import).
- **What the check v2 does** ([`rb/check_day2_v2.py`](rb/check_day2_v2.py), Python's own modules only, run with `-I`): it reads v1's own
  bytes against their committed sha256 (`8b49ddee...`), loads v1 by its path and runs v1's tree check on a wider perimeter:
  - **v1's 32 lists and 15 more**, each at its pinned count, its own sha256 and with every entry OK: the 12 lists the scorer opens (pool 8's
    predictor's `SHA256SUMS` 16 and its freeze's 160; aifoundry3's idle-floor `SHA256SUMS` 7 and `-note1` 4; M10's `SHA256SUMS` 174; M11's
    `SHA256SUMS-h2-reader` 16, `-h2-reader-v2` 129 and `-h2-refit` 6; the pool-8 scorers' `SHA256SUMS` 5, `-v2` 4 and `-v3` 4; k6's
    `SHA256SUMS-drivers-v3` 39); **this note's closure list** [`rb/SHA256SUMS-day2-closure-v2`](rb/SHA256SUMS-day2-closure-v2) (168: the
    traced files above, each at its sha256); and kit note 3's and E183's kit note 2's lists (16 and 15).
  - **Each list itself and every file it names joins the day's paths**: no change but an addition since `6860643c` (per commit and on the
    tree, as v1 reads it), nothing uncommitted, no added file that shadows a module. **The day's paths are now 6 directories and 592 named
    files outside them** (v1: 133), and the 18 traced `sys.path` directories join the 156 directories the additions check reads.
- **Desk cases** (each committed; v1 alone still 0, the fault re-made, and v2 16): L3 (`hpl/surface_hpl.py`, and step 2 v5 and E183's
  step 2 v4 16), L4 (E78's committed `runs.csv`), L5 (`ccheck.py`), L2 (`fit_m5.py` with its line in M10's `SHA256SUMS`: M10's list off its
  own bytes), E1 (E181's committed measured-pass marks), A2 (the bench's `accum.c`), S7 (an added `kspeed/e83/statistics.py`: shadowing);
  CL (`predict_e83.py` with its line in the closure list): v1 and v2 16, the list being in E185's directory.

### verify-fx's minor fault 2: an untracked module beside a named file outside the core directories

- **What it was.** v1's status read covers the core directories and the named files themselves, so an untracked (never committed) module
  planted beside a named file elsewhere, in a directory a day-2 script imports from, was never seen (U3: `e164/json.py`; U5:
  `hpl/statistics.py`).
- **What the check v2 does.** It reads `git status --porcelain -z --untracked-files=all` over all 156 of the day's directories and stops (16)
  on any untracked `.py`, `.pyc`, `.pyo`, `.pyd`, `.so`, `.dylib` or `.pth` file, or a package's `__init__` file, naming each. Another
  untracked file outside the core directories (a working note, a data file) is counted, not refused; inside them v1's status read still
  refuses any. **Ignored files are not read:** the lab ignores only `__pycache__/`, `obj_dir/`, `node_modules/`, `/build/`, `/external/` and a
  few named files, and none of those holds a module a day-2 script imports in its place (the system python here keeps its byte-code cache
  outside the tree, `sys.pycache_prefix`, and a cached file is only ever read beside its own source, which the history and status reads hold).
- **Desk cases:** U3, U5, U7 (a package `e164/json/__init__.py`) and U8 (an extension module `hpl/statistics.cpython-39-darwin.so`): v1 0,
  v2 16, each named; U6 (a working note `hpl/notes.md`): v1 and v2 0, counted; W (a working note under `e183/`): E183's step 2 v4 and
  E185's step 2 v5 16 (the brief's "writes or commits").

### The M1 readers' gate v2

`check_day2_v2.py m1 e185|e183` is v1's gate word for word (the run's M1 files unchanged since `6860643c`, its M1 list at its count and own
bytes, for E185 step 2 v3's last M1 line in its `RB_OUT` log, the data directory committed and clean, then the note's own run line, its exit
status printed, and only its two outputs written), with the check v2's tree check (no pull) in place of v1's. The readers, their files and
their readings are unchanged. Desk cases: R1 (E185's gate v2 0, the reader run, its two outputs the only new files), R2 (the data directory
not committed: 16, not run), R4 (E183's gate v2 0, the reader's rc 1 printed, nothing written), R6 (a scorer module changed and committed:
v1's gate 0, the fault re-made; v2's 16, not run).

### What it does not close

- **The perimeter is the trace's.** A code path the desk tests do not reach (a branch only a real E185 session's data would take) could open
  a file outside it. The trace ran the scorer end to end on E181's committed passes standing in for E185's, so the inputs E185's rules read
  were among those traced.
- An addition that is not a module passes, by design: no day-2 step lists a committed directory except the import system's reads of its
  `sys.path` directories, where an added or untracked module is refused.
- The check is code in the lab clone too. The day-2 go names the commit that added this note, and before step 0 the card lane checks this
  note's list and E183's kit note 3's against it (the brief's dated note 2, section 1).

## What the card day reads from this note

- Step 0 is the day-2 check v2 by hand; step 2 is v5, run as step 2 and again just before step 14 (step 14 only on its 0); the M1 reader
  runs only through the gate v2, after the data commit.
- The go's anchor lines and the rest of the day's order: [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md) with its dated notes
  [1](CARD-LANE-BRIEF.md.dated-note-1.md) and [2](CARD-LANE-BRIEF.md.dated-note-2.md).

## What does not change

KIT.md, kit notes 1-3 and their files and lists; the check v1, its desk test and its log; step 2 v4, v3, v2 and v1; the box list
(`frozen-e185.sha256`); the session, runner, block, smoke gate, stops, device commands, budget and cap; every step that reaches the box;
E185.md and A1; note M1, its reader and its reading; M11's scorer v5; E181's and E176's data. The new files are new.

## Files ([`SHA256SUMS-e185-kit-note4`](SHA256SUMS-e185-kit-note4), 20 entries)

This note; [CARD-LANE-BRIEF.md.dated-note-2.md](CARD-LANE-BRIEF.md.dated-note-2.md); [`rb/check_day2_v2.py`](rb/check_day2_v2.py),
[`rb/SHA256SUMS-day2-closure-v2`](rb/SHA256SUMS-day2-closure-v2), [`rb/s03_desk_e185_v5.sh`](rb/s03_desk_e185_v5.sh),
[`rb/list_steps_e185_v5.sh`](rb/list_steps_e185_v5.sh) and [`rb/selftest_day2_v2.sh`](rb/selftest_day2_v2.sh); the logs
`rb/logs/selftest-day2-v2.txt`, `dry-listing-v5.txt`, `dmcmd-audit-v5.txt` and `dmcmd-audit-bare-v5.txt`. The list also pins the unchanged
files step 2 v5 runs or names: `rb/check_day2_v1.py`, `rb/s03_desk_e185_v4.sh`, `rb/s03_desk_e185_v3.sh`, `rb/rb_common_e185.sh`,
`rb/s02_window_e185.sh`, `rb/s22_collect_e185_v2.sh`, `SHA256SUMS-e185-kit-note3`, the brief `CARD-LANE-BRIEF.md` and its dated note 1. It
holds no file of note M1.

    bash tools/claims-v3/e185/rb/selftest_day2_v2.sh <a scratch directory outside the repo> > selftest-day2-v2.txt
    bash tools/claims-v3/e185/rb/list_steps_e185_v5.sh <an empty scratch directory> > dry-listing-v5.txt

## Labels

- **Registered:** every list, pin, step, gate, plan, cap and stop named here (E185.md with A1, M11's A7-4, KIT.md and its notes); this
  note's step 0, step 2 v5 and its re-run before step 14, and the M1 gate v2, before any datum.
- **Desk checks of code, not measurements:** every test result here, the run-time trace among them.
- **Reported:** october-forecast-model's arm (note M1); its forecasts are blind for E185 (frozen before any datum).
- Nothing here is held out or post hoc.

## Compute

The Intel, through the round's local slot, one job at a time at nice 10: the run-time trace of the desk tests (about 3 minutes), the
development and committed runs of the desk test v2 (about 3 minutes each), the dry listings, the audits, the public-text scans and every step
2 at the commit. The scratch clones are removed after use. No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0
