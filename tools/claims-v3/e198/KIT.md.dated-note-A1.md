# E198's kit, dated note A1: the runbook on the lab's runner copy, with no kill path (Mon 16 Nov 2026, before any E198 datum)

*Mon 16 Nov 2026 (week 46), from 03:00 PST, on aifoundry2, desk only (Q196, lane `a1-e198`), beside [KIT.md](KIT.md) and with
[E198.md.dated-amendment-A1.md](E198.md.dated-amendment-A1.md), which registers the change.
- No card was claimed or opened, no device command was sent, no lab box was reached, nothing was posted, no simulator ran.
- aifoundry2 has a card of its own, so every desk test that ran a runner, a session, a stand-in or a built host ran in the round's CPU slot
  (`W/slot.sh`) inside the no-device sandbox (`W/nodev.sh`), with THE QUIET DESK FLAG read absent first.
- **New files only, all under `tools/claims-v3/e198/`;** every committed file stays as committed.
- **No E198 datum exists.**

Nothing here changes an arm, a value, the order, a window, a threshold, a stop, a cap, a rest, the reduction, a rule or a forecast.*

*Dated fix before the land (Mon 16 Nov 2026, from 04:43 PST, desk only: Q196, lane `fix-a1e198`): verify-a1e198's findings answered in
A1's own files, every desk test re-run on the final bytes (section 9). The results below are the re-runs.*

## Results first (desk checks of code on committed records and stand-ins; nothing is measured)

Python everywhere: `/usr/bin/python3` 3.12.3 on aifoundry2 (numpy 1.26.4 for the registered reducer); bubblewrap 0.9.0; cmake 3.28.3 and the
desk's riscv gcc "() 15.1.0" for the runbook test's real build. Every log is under [`logs/a1/`](logs/a1/).

| check | result | log |
|---|---|---|
| **THE LAB'S RUNNER COPY** re-made from E193's runner (`desk/make_runner_e198a1.py --check`) | **RUNNER-A1 CHECK PASS**: 9 hunks (K9 the dated fix's), each applied once; 11 lines removed and 31 added, all inside the hunks; no `timeout -k`, SIGKILL or `.kill(` in the copy | `runner-a1-check.txt` |
| **THE REAL-PATH DESK TEST AFTER A1** (`desk/desktest_realpath_e198a1.py`) | **DESKTEST-REALPATH-E198-A1 100 of 100 PASS** (after the dated fix: run r1 of `fix-a1e198`, 05:16:23-05:25:56 PST; before it a1-e198's r2 read 98 of 98): v1's cases on A1's files (PB2 the whole real path with the collection, the reducer, the checker and the scorer; K1, X1, W1, NWI, NWL, IA0, IB0, H0, NOC1, NOM1, B4, GE; Y1 and Y1B SAME through `check_e198a1.py`; AUDIT, 30 rows) and A1's **HG** (with K9 and the timeout and wrapper alive), **HGE**, **HG2** and **KILLWORDS** (section 6) | `desktest-realpath-e198a1.txt` |
| **THE REAL-BYTES TEST** on the copy's filter and reader (`desk/realbytes_e198a1.py`) | **REALBYTES-E198-A1 16 of 16 PASS** (re-run on the fixed copy in the dated fix's quick set; its time in the log's first line): the copy's X04 filter is E193's three lines, byte for byte, 20 lines lower (14 before the fix: K3, K7 and K9 add six lines above it); every v1 check on the same committed bytes | `realbytes-e198a1.txt` |
| **THE IDENTITY GATE both ways** (`ident_e198.py selfcheck --real`, unchanged by A1, re-run) | **E198-IDENT SELF-CHECK PASS: 17 of 17** on the committed aifoundry1 card-1 stderr (7156ac15) | `ident-selfcheck-e198a1.txt` |
| **THE RUNBOOK'S DESK TEST AFTER A1** (`rb/selftest_rb_e198a1.sh`), its build REAL | **SELFTEST-RB-E198-A1 22 of 22 PASS** (after the dated fix: `fix-a1e198`'s run, 05:27:11-05:28:36 PST; before it a1-e198 read 21 of 21): its scratch the registration, the kit as committed (its subtree checked) and A1 as one commit. v1's cases on A1's steps: A, W1-W6, P1/SE/D1, SC, LK/LKH/RG, SY, BU (the REAL build: X04-BUILT, the listing on the copy SAME x3), R0/R1, DP, BA, BW/BD, L4/L4N (the real `session_e198a1.sh` found by its real name), C, RS, CR (the reducer, the checker and the scorer on the real-path test's collected sitting), Z. A1's cases: **A1H** (an A1 file changed later: step 2 (A1) 16), **KB** (the build job under a plain `timeout 900`), **V1G** (v1's step 9 refuses on A1's day, 10), **BN** (A1's not-ended lines: step 9 (A1) refuses B, 10), **WN** (DEVICE-NOT-ENDED: 17 while the session ends, 16 once ended), **CK** (step 11 (A1) refuses beside `session_e198a1.sh`, 10), and the dated fix's **A1A** (a file ADDED under `tools/claims-v3/e198/` after A1's commit: step 2 (A1) 16, "after-A1", naming it; the history check alone passes it) | `selftest-rb-e198a1.txt` |
| **the runbook's dry listing after A1** (`rb/list_steps_e198a1.sh`) | **26 steps listed, 0 exited non-zero, 0 box calls** | `dry-listing-e198a1.txt` |
| `dmcmd_audit` (v1, unchanged) on the A1 session's files (`preflight_e198a1.sh`) | **GO, 19 send sites, 0 disallowed, every one a READ** (the same 19 as v1: A1 adds no device command) | `dmcmd-audit-e198a1.txt` |
| **THE KILL AUDIT** (`desk/killaudit_e198a1.py`: a grep and an ast reading, no strace) | **KILLAUDIT-E198-A1 PASS** (after the dated fix). 125 grep hits on the A1 path and 8 in the rest of E198's folder, and 10 and 3 AST hits (every Python file read as code: 28 on the A1 path, 6 in the rest), every one classified; none is a SIGKILL, `kill -9` or `timeout -k` around a device process (section 5) | `killaudit-e198a1.txt` |
| the quick set | **CHECKS-E198-A1 PASS** (each quick-set log was re-made on the final bytes; its time is in its first line): every A1 `.sh` parses and every `.py` parses; harness-e198-a1.json re-made and equal (51 files), HARNESS OK; the three executables executable (775 on this clone's disk; git records 100755) | `checks-e198a1.txt` |

## 1. What A1 adds to the kit, file by file

**A rule of the note:** A1 changes no committed file. Where the runner is called, A1 gives a new file and the card lane runs it in place of
v1's ([CARD-LANE-BRIEF-e198-a1.md](CARD-LANE-BRIEF-e198-a1.md)). v1's files stay in the tree, as committed, and are not run for E198 after
A1.

| A1's file | in place of (v1) | what changes |
|---|---|---|
| `run_x04_e198a1.py`, `run_x04_e198a1.diff`, `desk/make_runner_e198a1.py` | E193's `run_x04.py` (run by reference) | THE LAB'S RUNNER COPY, its diff and its maker (E198.md.dated-amendment-A1.md 2); since the dated fix nine hunks, K9 the sampler stopped after a device process not ended |
| `session_e198a1.sh` | `session_e198.sh` | the runner is the copy, given E193's `arms.tsv` by `--arms`. The harness is harness-e198-a1.json, the preflight A1's, and the build record must name `build_e198a1.sh`. **A device process not ended** gets the session's line "A DEVICE PROCESS DID NOT END", no closing config read (nothing else is sent to the card) and kill nothing. The start line names A1 |
| `harness_e198a1.py`, `harness-e198-a1.json` | `harness_e198.py`, `harness-e198.json` | the box files A1 changes; 51 files (v1: 49): `build_e198a1.sh`, `check_e198a1.py`, `harness_e198a1.py`, `preflight_e198a1.sh`, `run_x04_e198a1.py` and `session_e198a1.sh` in place of `build_e198.sh`, `harness_e198.py`, `preflight_e198.sh` and `session_e198.sh`. `harness-e198-a1.json` sha256 `a45356edc5e4fd68139ef86a582f8204523ec81dcbea43f3b5d7c1f7fe13224b` (after the dated fix; before it `01b3c302...`, never landed) |
| `build_e198a1.sh` | `build_e198.sh` | the listing is the copy's own `--dry` through `check_e198a1.py`; the harness A1's; the record gains "a1 build_e198a1.sh" |
| `check_e198a1.py` | `check_e198.py`'s use (imported, unchanged) | the sixth exact mapping, `timeout 10` for `timeout -k 1 10`, counted. It is stricter: the listing must name no `timeout -k`, and every device call must take the mapping |
| `preflight_e198a1.sh` | `preflight_e198.sh` | `dmcmd_audit` on A1's file set |
| `rb/rb_e198a1.sh` | `rb/rb_e198.sh` (sourced, unchanged) | A1's harness sha256, A1's job names (`a1-build-e198a1`, `a1-dry-e198a1-<S>`), the amendment's file |
| `rb/s03_desk_e198a1.sh` (step 2, OUTSIDE A1's list) | `rb/s03_desk_e198.sh` | **A1's pins**: A1's list at its count and own sha256 (A1PIN), beside the registration's, the kit's (46, `38de3b38...`) and E193's two. Also: A1's commit found by its content and after the kit's; **nothing under `tools/claims-v3/e198/` added, changed or removed after A1's commit (the dated fix: else 16, "after-A1")**; the copy re-made and equal; harness-e198-a1.json; `preflight_e198a1.sh`; A1's desk-test logs |
| `rb/s07_a1_sync_e198a1.sh` (step 5) | `rb/s07_a1_sync_e198.sh` | the sync list and the box's checks by `harness_e198a1.py` |
| `rb/s08_a1_build_e198a1.sh` (step 6) | `rb/s08_a1_build_e198.sh` | the job `a1-build-e198a1` runs `build_e198a1.sh` under a **plain `timeout 900`**. v1's `timeout -k 15 900` would have sent a KILL to the build's process tree, which runs the built host for its refusal checks. The two-a-day count reads both names |
| `rb/s10_a1_dry_e198a1.sh` (step 8) | `rb/s10_a1_dry_e198.sh` | the dry pass of `session_e198a1.sh`, the listings through `check_e198a1.py` |
| `rb/s11_a1_session_e198a1.sh` (step 9) | `rb/s11_a1_session_e198.sh` | A1's jobs and record; launches `session_e198a1.sh`; every v1 refusal (its patterns read the copy's own "device process not ended ... tell the lab admin" lines) |
| `rb/s20_wait_e198a1.sh` (step 10) | `rb/s20_wait_e198.sh` | finds `session_e198a1.sh` by its real name. **DEVICE-NOT-ENDED**: 17 with "REPORT IT ... NOW" while the session still ends, 16 once it has ended |
| `rb/s22_collect_e198a1.sh` (step 11) | `rb/s22_collect_e198.sh` | refuses while `session_e198a1.sh` or `session_e198.sh` runs. v1's pattern `session_e198\.sh` does not match A1's name, so v1's step 11 could have collected a running A1 sitting |
| `rb/list_steps_e198a1.sh`, `rb/selftest_rb_e198a1.sh` | v1's two | the dry listing and the runbook's desk test on A1's steps (with the dated fix's case A1A) |
| `desk/desktest_realpath_e198a1.py`, `fake_card_e198a1.py` | v1's test and stand-ins (imported, unchanged) | v1's cases on A1's files, plus the hang cases HG, HGE and HG2 and KILLWORDS (HG with the dated fix's K9 and the timeout and wrapper alive). The test sends no KILL: a stand-in holder gets SIGTERM, a case past its bound gets SIGTERM |
| `desk/realbytes_e198a1.py` | `desk/realbytes_e198.py` | the copy's filter and reader |
| `desk/killaudit_e198a1.py` | (new) | THE KILL AUDIT (section 5; with the dated fix's code reading of every Python file) |
| `desk/dry-e198a1-{smoke,A,B}.txt`, `desk/dry-branches-e198a1.tsv` | v1's | the copy's dry listings on the stand-in box, written by the real-path test; the audit of every dry-flag line (30 rows: 18 session, 12 runner) |
| `CARD-LANE-BRIEF-e198-a1.md`, `DATA-README-FORM-e198-a1.md` | v1's | the card lane's steps after A1; the README's form with E198's own freeze lines (GAP 4) |
| `logs/a1/*.txt` | v1's `logs/` | every check above |
| `SHA256SUMS-e198-amendment-A1` | (new) | every A1 file but itself and step 2 (A1) |

**Unchanged and still used:**
- the box files: `privdev_e198.sh`, `warden_e198.py`, `holdercheck_e198.sh`, `x04host_e198.sh`, `ettelem_guard_e198.sh`, `dropruntime_e198.py`,
  `ident_e198.py`, `ident_inner_e198.sh` and `check_e198.py`;
- the steps: step 1 (`s02_window_e198.sh`), step 4 (`s05_look_e198.sh`), step 7 (`s09_a1_reads_e198.sh`), step 13 (`s24_reduce_e198.sh`) and
  the history check (`rb/check_history_e198.py`: A1's files are additions, which it accepts);
- `collect_e198.py`, `score_e198.py`, E193's and E191's files.

**v1 cannot launch on A1's day by mistake:** v1's step 9 reads only v1's jobs (`a1-dry-e198-<S>`, `a1-build-e198`), and A1's jobs carry their
own names. The runbook test's V1G shows it: v1's step 9 refuses (10) on A1's day and launches nothing.

## 2. The session after A1 (`session_e198a1.sh`), against `session_e198.sh`

Each step of KIT.md section 1 stands. Only these differ:
- step 1's harness, preflight and build record;
- steps 5 and 6's runner, now the copy with `--arms`;
- the device-process-not-ended handling.

That handling: after each runner call, the session reads that call's `run.log` for the runner's own "device process not ended" line. If it
is there, the session writes "A DEVICE PROCESS DID NOT END in the <smoke|x04> run (<the line>): nothing was killed; it is left for the lab
admin and nothing else is sent to the card (E198 A1); tell the owner and the lab admin at once". Its closing config read is then skipped,
with a line saying so. The sitting then ends as v1's would:
- in the smoke, the smoke gate fails: GATE-STOP, rc 3;
- in the main run, "main run stopped", the registered stop: rc 1.

## 3. The listing check after A1 (`check_e198a1.py`), and the build

E193's registered listings are line for line the copy's, after check_e198.py's five exact mappings and A1's sixth (`timeout 10` for
`timeout -k 1 10`, on every device call). The desk check ran before the logged tests (03:2x PST, the lane's own log):

| listing | device calls | rule 6 taken | result |
|---|---|---|---|
| smoke (`--smoke --blocks S,D,W,T,C`) against `dry-e193-smoke-all.txt` | 10 | 10 | SAME |
| sitting A against `dry-e193-A.txt` | 234 | 234 | SAME |
| sitting B against `dry-e193-B.txt` | 135 | 135 | SAME |

- Against E193's runner's own listings, the copy's differ only on device-call lines (379 of them), each `timeout 10` for `timeout -k 1 10`.
- The negative control: E193's runner through `check_e198a1.py` reads DIFFERS ("the listing names 'timeout -k'"), and through
  `check_e198.py` reads SAME, as v1 found.
- The real-path test's Y1 and Y1B and the runbook test's real build (BU) and dry pass (DP) read the same through the session and the build.

## 4. The runbook after A1 (the card lane's table: [CARD-LANE-BRIEF-e198-a1.md](CARD-LANE-BRIEF-e198-a1.md))

| box step | A1's file (v1's when unchanged) |
|---|---|
| 1, the window | `rb/s02_window_e198.sh` (v1) |
| 2, the desk check | **`rb/s03_desk_e198a1.sh`** |
| 4, the look | `rb/s05_look_e198.sh` (v1) |
| 5, the sync | **`rb/s07_a1_sync_e198a1.sh`** |
| 6, the build | **`rb/s08_a1_build_e198a1.sh`** (plain `timeout 900`) |
| 7, the reads | `rb/s09_a1_reads_e198.sh` (v1: its config read under a plain `timeout 10`) |
| 8, the dry pass | **`rb/s10_a1_dry_e198a1.sh`** |
| 9, the sitting | **`rb/s11_a1_session_e198a1.sh`** |
| 10, the wait | **`rb/s20_wait_e198a1.sh`** (DEVICE-NOT-ENDED) |
| 11, the collection | **`rb/s22_collect_e198a1.sh`** |
| 13, the reduction and the scorer | `rb/s24_reduce_e198.sh` (v1) |

## 5. THE KILL AUDIT (a grep and a code reading; no strace)

`desk/killaudit_e198a1.py` reads every file on the A1 path: 79 files, made up of
- what the box runs or reads: harness-e198-a1.json's 51 files and the tree's E191 guard;
- what A1's steps run or source at the desk, k6's and v3.1's runbook files among them;
- A1's desk tests and stand-ins.

It matches every line of a code file against the kill patterns:
- SIGKILL; the word KILL;
- `kill -9`, `-KILL`, `-s KILL` or a computed `-s`;
- `timeout -k`, `--kill-after`, `-s KILL`; `"timeout", "-k"` in a list;
- `kill -n 9` or `kill -n KILL` (bash's numeric form: the dated fix);
- `.kill()`, `os.kill(`, `os.killpg(`, `pthread_kill(`;
- `subprocess.run`, `call`, `check_call` or `check_output`, or `communicate`, with a `timeout=`, whose expiry sends the child a SIGKILL;
- bubblewrap's `--die-with-parent`, whose parent-death signal is a KILL;
- `pkill`, `killall`.

Every hit must be classified by its table with a reason; an unclassified hit, or one around a device process, fails. It also reads the
copy as code (ast), and lists the 49 other files of E198's folder the same way (the count at the commit, as the audit prints it; the
first version of this note said 40). **Since the dated fix it also reads every Python file of both scopes as code (ast): 28 on the A1
path and 6 in the rest.** Each call of `subprocess.run`, `call`, `check_call` or `check_output` with a `timeout=`, each
`.communicate(timeout=)`, each `.kill()`, `os.kill()`, `os.killpg()` or `signal.pthread_kill()`, and each `.send_signal()` of another
signal than TERM, INT or HUP is an AST hit, classified by the same table on the call's own lines joined into one, so a call split over
lines cannot hide (verify-a1e198's finding 4: its break tests M6, M7 and M9 passed the grep alone). **PASS: 125 grep hits on the A1
path, every one classified** (117 before the dated fix; the 8 more are the audit's and the runner maker's own new words, TEXT-MATCH, 6,
and the real-path test's new HG words, DESKTEST, 2):

| class | hits | what they are |
|---|---|---|
| TEXT-MATCH | 66 | the words as text a checker looks for: this audit's own patterns, the runner maker's, `check_e198a1.py`'s mapping, E193's desk arms comparer's listing string |
| DESKTEST | 27 | A1's desk tests' own words and sandboxes: stand-ins over /dev/null, never on a box. bubblewrap's `--die-with-parent` ends a case's stand-ins only if the test itself dies; the HG case shows no stand-in is left when its sandbox ends |
| DOC | 20 | prose: comments, docstrings, echoed sentences that say no KILL is sent |
| NOTRUN | 3 | E193's runner (lines 29, 272 and 382): synced to the box as part of E193's registration, never run for E198 after A1 |
| NOTDEV | 3 | Python's `subprocess.run(..., timeout=)` (a KILL to the child past its bound) on children that open no device node, each ending by itself first: the runner's holder check `holdercheck_e198.sh` (ends within 28 s; bound 30 s; E193's line, unchanged), the warden's `et-who` (bound 25 s), and a desk-side `ps` in k6's runner |
| DESK | 3 | k6's bounded runner (v3.1 `rb_run.py`, `kill_tree`: TERM, then KILL) ending a DESK-side call past its bound or on a login link: the ssh, rsync or git client on aifoundry2, never a device process. The box side of a cut call gets no KILL: a launch has detached, and a read runs under its own plain `timeout` |
| EXIST | 2 | signal 0 (`os.kill(pid, 0)`): sends nothing |
| SELF | 1 | `x04host_e198.sh` line 25 re-raises on its own process (`$$`), after the host has ENDED, the signal the host died of, so `timeout` reads the status it would have read. It signals no device process, and it can reach a KILL only if something outside E198's code killed the host |

- **The rest of E198's folder: 8 hits, all NOTRUN (v1 files superseded by A1):**
  - v1's step 6's `timeout -k 15 900` (its line and its header);
  - v1's real-path test's SIGKILL to its stand-in `sleep` holders and to a case at its bound, and its `--die-with-parent`;
  - v1's runbook test's `--die-with-parent`.
- **The AST hits: 10 on the A1 path and 3 in the rest, every one classified:** the runner copy's holder check, the warden's `et-who` and
  k6's desk-side `ps` (NOTDEV, 3); the warden's and k6's `os.kill(pid, 0)` (EXIST, 2); k6's `kill_tree` (DESK, 2); the A1 real-path
  test's TERM to a case past its bound and the stand-in sampler's TERM to itself (DESKTEST, 2); E193's runner's holder check (NOTRUN,
  1); v1's real-path test's kills of its stand-ins (NOTRUN, 3 in the rest). None is a device process.
- **Text files:** 18 hold a kill word and are never run (E193's registered listings, request.md, the READMEs, the v1 listings, this note).
- **The copy read as code:**
  - the device command is the list literal `['timeout', '10', a.host, ...]`;
  - no call of `.kill()`, `os.kill()` or `os.killpg()`;
  - the three `send_signal` calls send `signal.SIGTERM`: lines 316 and 324 in `end_device()`, line 493 the sampler (the clean-up's,
    reached since K9 also after a device process not ended);
  - the one timed `subprocess.run` is the holder check's (line 397).
- **The runtime half** is the real-path test's HG cases (section 6).

## 6. THE REAL-PATH DESK TEST AFTER A1: the hang cases

v1's cases ran on A1's files and read as v1 states them:
- PB2: the smoke, two whole passes, the card-0 holder seen through the warden, the runtime line guarded, the collection, the reducer, the
  checker and the scorer;
- K1, X1, W1, NWI, NWL (the copy run directly without the guard: it raises on the inside form, as E193's runner does), IA0, IB0, H0, NOC1,
  NOM1, B4, GE;
- Y1 and Y1B (SAME through `check_e198a1.py`), and AUDIT.

A1's cases (stand-in hosts that catch TERM; each writes its own end line, which a process ended by a KILL could not write):

| case | the stand-in host | what the copy and the session did | the proof nothing was killed |
|---|---|---|---|
| HG | the smoke's first device process; it outlives its TERM and ends by itself 140 s after it started | at 25 s: "device process still running 25 s ... device process not ended: tell the lab admin", `device_not_ended` (25); the stop "spin2: device process not ended 25 s after it started, its timeout's TERM at 10 s (nothing killed: tell the lab admin)"; `end_device()` SIGTERM, then "still running 15 s after SIGTERM", then "60 s after", then "device process not ended: the card lock goes only when this runner exits"; the session: "A DEVICE PROCESS DID NOT END in the smoke run", closing read skipped, GATE-STOP at the smoke gate (rc 3) | at the session's end the host is ALIVE (state S), and so are its `timeout` and the host wrapper (a KILL aimed at the timeout would have ended both); its signal log holds TERMs only (one, at 9.979 s: the runner's three TERMs to the timeout reached nothing); it wrote "ended by itself at 140.029 s (its life of 140 s): 1 TERM(s) received, exit 0"; **K9:** right after "device process not ended: the card lock goes only when this runner exits" the runner wrote "E198 A1: the sampler is stopped all the same (SIGTERM), so it does not hold the management node", the smoke's stand-in sampler logged "ended (SIGTERM)" before the session ended, no sampler was alive at the session's end and the end knob ended none; nothing of the case left. The manifest verifies; `smoke/telemetry.jsonl` is at its manifest sha256 (before K9 it moved after the manifest); only the host wrapper's output and index may move after it, the reason step 11 may still wait (CARD-LANE-BRIEF-e198-a1.md 4) |
| HGE | the main run's first device process; it ends by itself 60 s after it started, inside `end_device()`'s 60 s wait | the stop as HG ("main run stopped", rc 1); `end_device()` reads it ended (`device_ended`, exit 124); the clean-up releases the lock and stops the sampler with SIGTERM | its own end line at 60 s, TERMs only; nothing left at the session's end; the manifest verifies |
| HG2 | the main run's first device process; it ends 1.5 s after its TERM (v1's `timeout -k 1 10` would have killed it at 11 s) | exit 124, the registered stop "spin2: device process killed by timeout (tell the lab admin)"; no not-ended line | "ended by itself at 11.5 s (1.5 s after its first TERM): 1 TERM(s) received" |

**Runs:** a1-e198's r1 (03:30:49-03:40:22 PST) read 97 of 98. Its one FAIL was the test's own KILLWORDS check, which found a docstring
line of `fake_card_e198a1.py` naming `timeout -k 1 10`. The line was reworded with no code change and re-run as r2: 98 of 98 PASS
(03:42:19-03:52:02 PST). **After the dated fix** (K9 in the copy; HG's assertions for K9 and for the timeout and the wrapper):
`fix-a1e198`'s r1, the logged run, 100 of 100 PASS (05:16:23-05:25:56 PST). The runs before the fix are the negative control for the
new HG assertions, read post hoc from their records: in a1-e198's r2 and the verifier's re-run the sampler was alive at the session's
end, the end knob ended it, and `smoke/telemetry.jsonl` moved after the manifest, so each new K9 assertion would have read FAIL there.

## 7. What the desk cannot show (KIT.md 9, unchanged; for the verifier and the readiness critic)

- The box-only items of KIT.md section 9 carry over unchanged (ready-e198's GAPS 2 and 3): the private /dev binding card 1's real nodes; the
  box's et-who through the warden; the real host on card 1; the box's build.
- **A real host that outlives its TERM** cannot be made at the desk. The stand-ins catch TERM in Python.
  - The real host installs no signal handler (`main.cpp`; E197.md 17 item 9 read the same of the lab's runtime library on aifoundry2), so
    TERM ends it by default, unless it is stuck in the driver.
  - A host stuck in the driver would not end on a KILL either until it left the driver. That is a case for the lab admin under either
    runner.
- **What the lab admin finds after a device process not ended:**
  - the process (`timeout`, the host wrapper, the host; the host holds card 1's ops node); the host has had one TERM, its timeout's at 10 s
    (GNU timeout ignores the runner's later TERMs: E198.md.dated-amendment-A1.md 2 (3));
  - no sampler of ours: since the dated fix (K9) the runner's clean-up stops it with SIGTERM all the same, so card 1's management node is
    free (before K9 it stayed until its own `--seconds`, up to about 79 minutes in sitting A);
  - card 1's lock, free once the runner has exited, while `et-who` still shows the host left running on card 1's ops node.

## 8. If A1's files change again before the land (the re-make list)

1. any box file (session, copy, build, check, preflight, harness script): `harness_e198a1.py --make`, then THE KILL AUDIT, the quick set, and
   both long desk tests on the final bytes;
2. the copy: `desk/make_runner_e198a1.py --write`, then everything in item 1, and this note's and the amendment's sha256s (the copy, the
   diff, harness-e198-a1.json, the README form's row);
3. `SHA256SUMS-e198-amendment-A1` by its rule (every file under `tools/claims-v3/e198/` that the kit's commit did not have, but itself, step
   2 (A1) and `*.pyc`), then step 2 (A1)'s A1PIN (its count and the list's own sha256);
4. step 2 (A1) and the history check on the committed result; the land dir's LAND.md anchors.

The dated fix (section 9) followed this list: items 1-4 were done on the fixed files.

## 9. The dated fix before the land (Q196, lane `fix-a1e198`, Mon 16 Nov 2026 from 04:43 PST; desk only)

verify-a1e198 read A1 as HOLDS WITH FIXES: one minor finding and seven nits (E198.md.dated-amendment-A1.md 9 lists all eight and their
answers). They were answered in A1's own files before anything landed; every file below is one of A1's 41, and no committed file changed.

| A1's file | what the dated fix changed | finding |
|---|---|---|
| `desk/make_runner_e198a1.py`, `run_x04_e198a1.py`, `run_x04_e198a1.diff` | hunk K9 (the clean-up stops the sampler with SIGTERM also after a device process not ended); K3 now also covers its next line, and K3 and K7 say what GNU timeout does with a TERM sent after it has passed one on or sent its own | 1, 2 |
| `harness-e198-a1.json` | re-made for the copy's new bytes (51 files; `a45356ed...`) | 1 |
| `desk/desktest_realpath_e198a1.py`, `fake_card_e198a1.py` | HG asserts K9 (the sampler ended on the clean-up's SIGTERM before the session ended, none alive at its end, the end knob unused, the telemetry final before the manifest) and that the host's `timeout` and wrapper are alive at the session's end; the knob's doc | 1, 6 |
| `desk/killaudit_e198a1.py` | item 5, every Python file read as code; `kill -n`, `call`/`check_call(timeout=)` in the grep | 4 |
| `rb/s03_desk_e198a1.sh` (step 2 (A1)) and `rb/selftest_rb_e198a1.sh` | step 2 (A1) refuses any file under `tools/claims-v3/e198/` added, changed or removed after A1's commit (16, "after-A1"); the runbook test's case A1A shows it, the history check alone passing the same addition | the verifier's open issue (a later addition passed, rc 0) |
| `E198.md.dated-amendment-A1.md`, this note, `CARD-LANE-BRIEF-e198-a1.md`, `DATA-README-FORM-e198-a1.md` | the texts for findings 1, 2, 3, 5 and 8; the copy's new sha256 in the README form's row | 1, 2, 3, 5, 8 |
| `logs/a1/*.txt`, `desk/dry-e198a1-*.txt`, `SHA256SUMS-e198-amendment-A1` | every check re-run on the final bytes; the dry listings came out byte for byte as before (K9 changes no dry line); the list re-made by its rule, and step 2 (A1)'s A1PIN with it | all |

**Break tests on the fixed files** (`fix-a1e198`'s own, 05:28:36-05:28:46 PST, in the round's CPU slot inside the no-device sandbox;
each case a copy tree with one mutation, read by `desk/make_runner_e198a1.py --check` and `desk/killaudit_e198a1.py`): 18 cases, every
one as expected.
- The base: both PASS (10 AST hits).
- The verifier's twelve, re-typed against the fixed files. Caught by the maker: M1 (the `-k` back), M2 (`p.kill()` in `end_device()`),
  M3 (the sampler stopped with SIGKILL), M10 (`END_WAIT_S` changed) and M11 (the device window changed). Caught by the kill audit: M1, M2,
  M3, M4 (`kill -9` in the session), M5 (`--die-with-parent`), M7 (`subprocess.call(..., timeout=5)`: now caught), M8 (`timeout -s
  KILL`), M9 (`kill -n 9`: now caught) and M12 (`pkill -KILL`). M6, the warden's own timed call split over two lines, reads PASS as it
  should: it is the same allowed call, and the AST half finds it (10 AST hits, as in the base) where the grep alone lost it.
- Five more for the fix. M6B, a NEW timed `subprocess.run` around a host with its `timeout=` on a later line: the audit fails it (AST).
  M13, K9 reverted: the maker fails it. M14, `os.kill(sampler, 9)` on K9's path: both fail it. M15, `kill -n KILL`: the audit fails it.
  M16, a `subprocess.check_call` whose `timeout=` sits on its own line: the audit fails it (AST).

Finding 7 (LAND.md passes the paths one by one) is in the land dir, outside the tree.

SPDX-License-Identifier: Apache-2.0
