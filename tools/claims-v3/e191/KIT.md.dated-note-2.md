# E191's kit, dated note 2 (Sun 15 Nov 2026, before any E191 pass datum): the host's result read from a source no runtime print can split (runner v2, its common module v2, doubles v2, session v2), the real-bytes desk test on the day's committed stdout, the real-path and runner desk tests re-run in aifoundry1's split form, the dry-vs-real audit with a stdout part, the relaunch rule, step 2 v2 and the second session's runbook; no rule, forecast, threshold, plan, cap, stop or reading changes

*Beside [KIT.md](KIT.md) (`eb1ac923`); it edits nothing there, nor in [E191.md](E191.md) or its dated note 1. It is numbered 2 after E191's
dated note 1 (`8c8f825f`), whose kit lines KIT.md carries; there is no KIT.md.dated-note-1.md. Written on aifoundry2, desk only, by the lane
`note2-e191` of Q184, from about 10:29 PST Sun 15 Nov 2026 by the clock, and fixed before the land by the lane `fix-n2e191` after its
verifier (section 14); its commit's own time is git's. **Written after E189's data commit
`fa9098c4` (Sat 14 Nov 2026, 20:34:12 PST)**, so by E191's dated note 1 section 3 it registers only the kit's mechanics and gates made
stricter for safety, each named so in section 9; **nothing here changes a forecast, a band, a rule, a threshold, K, the order, the plan, the
card time, the cap, a registered stop line or the scorer**, and nothing here reads E189's or E191's measured numbers for any of them. It
answers **E191's first session** (`card-e191`, Q182: aifoundry1 card 1, T0 1794766494, 10:14:54 PST; its record `1a4bc1e3`), which **stopped
at its smoke gate by a defect of this kit before any pass** (0.02 card-minutes; every rule NOT DECIDED). **No E191 pass datum exists**
(`git log --all` on `docs/reports/data/*e191*` names only that record's directory, which holds no `passes/`). E191.md's dated amendment A1
([`E191.md.dated-amendment-A1.md`](E191.md.dated-amendment-A1.md)), committed with this note, allows a second session that day; the card
lane's brief's dated note 1 ([`CARD-LANE-BRIEF.md.dated-note-1.md`](CARD-LANE-BRIEF.md.dated-note-1.md)) carries both out. No card was
claimed, no device command was sent, no lab box was reached, nothing was posted; every desk test that ran a host, a runner, a stand-in
session or a stand-in box ran in the round's CPU slot and a sandbox with no `/dev/et*` and an empty `/run/lock`, the real-path and runbook
tests in private PID namespaces, the real-path test under a private hostname. New files only, all under `tools/claims-v3/e191/`.*

## Results first (desk checks of code on committed records; nothing is measured)

Every test ran on aifoundry2 (Linux, /usr/bin/python3 3.12.3, g++-13 13.3.0, bubblewrap 0.9.0) on Sun 15 Nov 2026. The lane `note2-e191`
ran them first, from 10:48 PST, at `1a4bc1e3` and `fe08ed67`. After the verifier's fixes (section 14) the lane `fix-n2e191` re-ran every
one of them on the code as committed here, from 12:38 PST, in one scratch clone at `96ef447ce326` (GitHub main then) with the note's
files: every log below is that re-run's, and each names that base in its first line, the dry listing's included. RB10 alone reads a fixed
base, the lab's records as committed at `fe08ed67` (git's blobs; section 3).

| check | result | log |
|---|---|---|
| **THE REAL-BYTES TEST** (`desk/realbytes_e191.py`): the reader fed the bytes the lab committed. RB1 the day's own `stdout.txt` (1a4bc1e3, its SHA256SUMS line matching) reads the host's PASS line, 2,048 of 2,048 records, 0 bad, 0 mismatches, one runtime line dropped, the smoke's test good, while v1's reader reads `{}` (status None: the defect reproduced); RB2 the unchanged adapter, the frozen scorer's reader and the reducer's reader on it; RB3 the runtime line at every byte offset of seven committed lines; RB4 two runtime lines; RB5 its own line before and after (and aifoundry1 card 0's committed config read with "Opening device 0"); RB6 truly failed hosts still read FAILED (ten forms); RB7 E189's 31 committed host lines read exactly as v1 read them; RB8 sparse parity in aifoundry1's form; RB9 the self-tests; RB10 every one of the lab's occurrences of the runtime line as committed at `fe08ed67` (git's blobs) is of the form dropped, and the one inside a host's line is the day's | **REALBYTES-E191 10 of 10 PASS** | [`logs/realbytes-e191.txt`](logs/realbytes-e191.txt) |
| **the REAL path, v2** (`desk/realpath_e191_v2.py`, `.sh`): every v1 case (RP1-RP25, RW1) on runner v2 with stand-in hosts that print aifoundry1's split line; RPS1 v1's runner on the same stand-ins (the negative control: the day's stop reproduced on the real path); RPS2-RPS4 no runtime line, its own line, two of them; RPS5 an unknown text inside the line (fails safe); RPS6 a failed host; RPS7 a host that died after it opened the card; RPS8 the files | **REALPATH-E191-V2 34 of 34 PASS** | [`logs/realpath-e191-v2.txt`](logs/realpath-e191-v2.txt) |
| **the runner's desk test, v2** (`selftest_run_e191_v2.py`): every case of `selftest_run_e191.py` (R1-R19, E2E, R2E/R3E and the cut-tail control, I1-I10, B1-B2, D1, F1-F7, W1-W4, Q1-Q5) on runner v2 with doubles v2 (the split form), then S1-S4 on the dry path | **SELFTEST-RUN-E191-V2 66 of 66 PASS** | [`logs/selftest-run-e191-v2.txt`](logs/selftest-run-e191-v2.txt) |
| **the dry-vs-real audit, v2** (`desk/dryaudit_e191_v2.py`): part 1, every line of runner v2 that reads the dry flag, with the real-path case that ran it; part 2 (section 116's lesson), every line that reads a device process's standard output, with the real-bytes and real-path cases that fed it real or split bytes, and no stdout read through v1's reader | **DRY-AUDIT-E191-V2 32 of 32 COVERED** | [`logs/dry-audit-e191-v2.txt`](logs/dry-audit-e191-v2.txt) |
| **the runbook, v2** (`rb/selftest_rb_e191_v2.sh` under `rb/selftest_rb_e191_v2_ns.sh`): the second session's whole order on a stand-in aifoundry1 left as the first session left it: A2, P1v2, P2v2, H4v2, H5v2, F1, S5v2, B6, G1, D2, G2, WT0 (v1's step 10 reads session v2 as RUN-GONE: the negative control), WT1-WT4, RS2, LL2a (THE LAST LAUNCH: RB_OUT with no T0, the box's last launch not the first session's), LA2 (the REAL session v2 stopping at its box check), LL2b (THE LAST LAUNCH: the box's last launch not RB_OUT's T0), G4a-G4b (the relaunch rule), C3v2, C2v2, C4v2, SC0v2, SC3v2, Z | **SELFTEST-RB-E191-V2 19 of 19 PASS** | [`logs/selftest-rb-e191-v2.txt`](logs/selftest-rb-e191-v2.txt) |
| the dry listing v2, every step of the second session with stand-ins | **12 steps, 0 exiting non-zero, 0 box calls**; its command lines pass note 1's item 4 (`desk/drylisting_check_e191_v2.py`) | [`logs/dry-listing-e191-v2.txt`](logs/dry-listing-e191-v2.txt) |
| `dmcmd_audit` on the second session's files (`preflight_e191_v2.sh`) | **GO, 16 send sites, 0 disallowed, every one a READ**, no allow-list, no exception | [`logs/dmcmd-audit-e191-v2.txt`](logs/dmcmd-audit-e191-v2.txt) |
| the quick set v2 (`desk/checks_e191_v2.sh`) | **CHECKS-E191-V2 16 of 16 PASS**: every .py compiles and every .sh parses; the three self-checks; harness v2 re-made and at its 49 files, v1's at its 42; the preflight v2; runner v2 reads no stdout through v1's reader; THE DOUBLES' FORM against the committed bytes; the runbook's command lines; no new file shadows a module; the never-run check (a) | [`logs/checks-e191-v2.txt`](logs/checks-e191-v2.txt) |

## 1. What stopped the first session

On aifoundry1 the device runtime prints `Opening device <n>` on a host's **standard output** when the host opens card `<n>` (lab readers
have skipped that line since September: `workloads/memhier/analyze.py` line 125; the lab's committed data at `fe08ed67` hold 794 such lines,
each at a line's start: the real-bytes test's RB10). The ledger host prints its one JSON line in two parts: the head (`workloads/ledger/host/main.cpp`
lines 478-492, its command line's fields) **before** it opens the card, and the tail (line 621 on: its launches, records, checks and status)
after. Both go to one stdio stream, so on Sun 15 Nov 2026 the runtime's line fell **inside** the host's line. The bytes, committed in
`1a4bc1e3` as `session/smoke/copy-64m-random/stdout.txt` (570 bytes, sha256 `8a232ca7...`), are two lines:
`{"ledger":1,...,"data":"random","width":32Opening device 1` and `,"launches":1,...,"status":"PASS"}`. Kit v1's reader,
`e191_common.last_json` (lines 134-141), takes the LAST line that begins with `{`: the broken head, which does not parse, so it returned `{}`.
`run_e191.py` line 691 read the smoke's status through it (None: FAILED), and the smoke gate ended the session. Line 791 reads each pass's
host line the same way, so every ledger pass would have read `{}` too: through the registered adapter, "no JSON line from the ledger host",
a FAILED RUN, and v1 then overwrote the pass's raw stdout (`host-raw.json`) with that empty reading. E189's smoke on aifoundry3 printed one
unbroken line from the same host source (that box's runtime prints no such line), and the kit's doubles and stand-ins printed clean JSON, so
no desk test met it: KIT.md section 8 named the real hosts' first meeting with card 1 as desk-unreachable, and the readiness check's GAPS 1.

## 2. The fix chosen: the host's line reassembled and verified (runner v2, `e191_common_v2.py`)

**Not chosen: a result file of the host's own.** Neither host writes its result line to a file (the ledger host's line goes to stdout only;
sparse parity's `--records-out` file holds its records, not its line), and a flag that made one would change the registered command lines
(E191.md 4; `plan-e191.json`'s arguments, which E189's host check reads). **Chosen: the host's line reassembled from its standard output**
(`e191_common_v2.host_result`), in three steps:
1. **drop_runtime**: every runtime line, the exact text `Opening device <n>` with its newline (`RUNTIME_LINE`), is removed wherever it fell:
   at a line's start (ettelem's form, sparse parity's) or inside the host's line (the ledger host's). A JSON string cannot hold a raw
   newline, so the removal never cuts into the host's own text; the dropped lines are kept, in order, in the record;
2. the host's line is the LAST line left that begins with `{` (v1's own rule: a stream with no runtime line reads exactly as v1 read it,
   the real-bytes test's RB7), and it must parse as a JSON object;
3. **its own fields are verified**: the ledger host's line names `"ledger": 1`, the command's `--prog` and `"device": "card"`, and the head
   fields its command line sets (copy: bytes, passes, data, width; sha256: block, repeat; sort: keys, reps, order; sizes read as `main.cpp`'s
   `parseSize` reads them); at status PASS or FAIL it carries every tail field the adapter, the reducer and the scorer read, each of its
   type, with as many wall times as launches and two span ends a launch (`main.cpp` lines 532-535 push both for every launch, a failed one
   included). Sparse parity's line names `"workload": "sparseparity"` and, at PASS or FAIL, carries `reps_requested` (the command's
   `--reps`), `reps_done`, `launch_s`, `launch_epoch_ms` and `kernel`. **A line that fails a check is not read** (`{}`, with the reason): the
   smoke gate fails, a pass is a FAILED RUN; never a wrong datum. Any other text left is counted and kept in the record; inside the host's
   line it leaves the line unparseable, so it fails safe (RB6, RPS5, S2).

**Runner v2** (`run_e191_v2.py`) is `run_e191.py` with thirteen exact replacements, each applied once, and nothing else (the lane's
generator refused any replacement that did not match exactly once; before the land the fix lane corrected one line of the header the first
replacement writes, which had called v1's docstring unchanged: section 14). The thirteen, one a row:

| where (v1's line) | v1 | v2 |
|---|---|---|
| 1-3 (the docstring's head) | v1's first lines | a header naming this note, then v1's docstring, with the two edits of the next rows |
| 6 (the docstring's wrapper sentence) | `session_e191.sh starts it, detached.` | `session_e191_v2.sh starts it, detached (v1: session_e191.sh started run_e191.py).` |
| 8-10 (the docstring's usage lines) | `python3 -B tools/claims-v3/e191/run_e191.py session ...`, twice | `run_e191_v2.py` in both |
| 99 | `import e191_common as C` | `import e191_common_v2 as C` (every v1 name by import, plus the reader) |
| 198 | the doubles `fake_card_e191.py` | `fake_card_e191_v2.py` |
| 538 (the config read) | `C.last_json(r.stdout)` | `C.config_json(r.stdout)`: the runtime lines dropped, then v1's reader (no reading changes: RB5) |
| 687-691 (the smoke) | `C.last_json(text)` | `C.host_result(text, kind, argv)`; the self-test's `SELFTEST PASS` read on the text with runtime lines dropped |
| 698-703 | smoke.json, the smoke line, the gate's words | smoke.json gains `host_line` (the reader's record); the smoke line adds "the host's line: n runtime line(s) dropped (...)"; a gate failure adds "(the host's line was not read: ...)" |
| 771 (each pass) | the host's stdout into `host-raw.json` or `host.json` | into `stdout.txt` (kept whole, raw) |
| 791-798 | `C.last_json(text)`; host-raw.json and host.json (ledger) | `C.host_result(...)`; host-raw.json and host.json written from the verified line as v1 wrote them; sparse parity's host.json is its verified line (v1: its raw stdout); a line not read is logged |
| 805 | the flags | a flag "the host's line was not read: ..." (a flag only: the reading is the adapter's FAILED RUN) |
| 825 | run.json | gains `host_line` |
| 867 | the session's start line | names "kit note 2" (step 10 v2 and step 11 v2 read it) |

The files the reducer and the frozen scorer read keep their form (`host-raw.json`: the ledger host's line as `json.dumps` writes it, as v1
wrote it; `host.json`: the adapter's fields, or sparse parity's line), so neither reads anything new; the frozen scorer's reader and the
reducer's reader read the verified dict (RB2, RPS8, S1). **Session v2** (`session_e191_v2.sh`) is v1's wrapper running runner v2; its name
is counted by k6's and E191's `ours_live` (`session_e[0-9]*.sh`). **Doubles v2** (`fake_card_e191_v2.py`) print the hosts' standard output
as aifoundry1's real hosts do: the ledger host's head in the real host's key order before it "opens" the card, the runtime's line there, the
tail after (the quick set's THE DOUBLES' FORM: the same keys in order and the runtime line after the same ten bytes as the committed
`stdout.txt`); sparse parity's runtime line on a line of its own before its line; `E191_FAKE_RUNTIME` = split (the default), line, none,
twice or garble.

## 3. THE REAL-BYTES DESK TEST (`desk/realbytes_e191.py`)

CONTEXT section 116's lesson: the kit's real-path test feeds the reader the REAL stdout bytes committed from a card, not only stand-in JSON.
This test reads the committed records only (no host runs) and states each verdict first (its docstring): RB1 the day's `stdout.txt` (and the
day's `smoke.json`, whose `status` null and `good` false v1 wrote) reads PASS through v2 and `{}` through v1; RB2 the reassembled line
through the unchanged adapter (PASS, `reps_consistent` ok), the frozen scorer's `last_json` and the reducer's `last_json` on `host-raw.json`
as runner v2 writes it; RB3 the runtime line inserted at every byte offset of the day's line and of E189's six committed ledger smoke lines
(3,787 forms, each read as the whole line; v1 misreads 3,780 of them, every offset but 0); RB4 two runtime lines at once (device 1 and
device 0); RB5 the runtime line on its own line before or after, and E170's committed aifoundry1 config read (`Opening device 0` then its
line) read by `config_json` exactly as by v1; **RB6 a truly failed host still reads FAILED**: the day's bytes with a mismatch and status
FAIL (the adapter's FAILED RUN), the head and the runtime line with no tail, nothing, the head alone, v1's cut line, an unknown text where
the runtime line was, another command's line, a field missing, a span end missing, the host's REFUSED line; RB7 E189's committed real bytes
(7 smoke runs, 20 ledger passes with their SHORT copy bursts, 4 sparse parity passes): v2 reads each exactly as v1 read it; RB8 E189's
sparse parity line with the runtime line before it and at every 50th byte inside; RB9 the two committed self-test outputs; RB10 all 801
occurrences of `Opening device` in the lab's raw text files as committed at `fe08ed67` (GitHub main when this note was written), read from
git's blobs, so that no later record moves them (the second session's raw `stdout.txt` files will hold the runtime line inside the ledger
host's line, and its records quote the dropped text; the verifier's finding 5): 794 runtime lines at a line's start, 6 quoted inside JSON
strings (escaped newlines, never on a host's stdout), 1 inside a host's line (the day's, in `1a4bc1e3`'s record), none of another form.

## 4. The real-path desk test, re-run in aifoundry1's form (`desk/realpath_e191_v2.py`, `desk/realpath_e191_v2.sh`)

`desk/realpath_e191.py` (unchanged beside it) with its stand-in tree made from harness v2's 49 files, runner v2 imported from it, and its
stand-in hosts running doubles v2, so every v1 case (RP1-RP25 under the hostname aifoundry1, RW1 under aifoundry2: the box check, the lock,
the holders, THE IDENTITY GATE (a) and (b), the stop-path test, the smoke, six passes, the 30 s bound and the lock kept after it, the
sampler's freshness, et-who unreadable, the early stop, the kernel and record gates) now meets the split line on the real path, and the
note's cases: **RPS1 the negative control**, v1's runner (`run_e191.py`, from the same stand-in tree) on the same stand-ins: rc 16,
"smoke gate failed: copy-64m-random: rc 0, status None", its smoke `stdout.txt` holding the split line, no pass: the day reproduced; RPS2
no runtime line (aifoundry3's form); RPS3 the runtime line on its own line; RPS4 two runtime lines; RPS5 an unknown text inside the line: the
smoke gate fails safe, the raw stdout kept; RPS6 a failed host in pass 1 (status FAIL read: a FAILED RUN; the other five PASS); RPS7 a host
that died after it opened the card in pass 1 (a FAILED RUN flagged "the host's line was not read"; the session goes on); RPS8 the files of
RP1's session (each pass's raw `stdout.txt` with the runtime line inside the ledger's line; the reassembled line in `host-raw.json`, sparse
parity's verified line in `host.json`, each read by the frozen scorer's reader as PASS; `host_line` in run.json and in each device-opening
smoke.json).

## 5. The runner's desk test, re-run (`selftest_run_e191_v2.py`)

Every case of `selftest_run_e191.py` (unchanged beside it; its docstring names each) runs on runner v2 with doubles v2: the stop lines on
live samples, the die gate, the cap, the end bound, the gates, SHORT and FAILED RUN, the refusals, the identity cases I1-I10, the bound B1-B2,
the sampler's freshness F1-F7, et-who W1-W4, the early stop Q1-Q5, the dry check D1, and end to end through the unchanged reducer,
`collect_e191.py` and the frozen scorer (E2E, R2E/R3E, the cut-tail control), every ledger host in the split form; then S1 (a plain session:
every pass PASS from its reassembled line, the files of section 2), S2 (an unknown text inside the line: the smoke gate fails safe), S3 (no
runtime line), S4 (a host that dies after it opened the card in pass 1). The box's step 8 v2 runs this dry path.

## 6. The dry-vs-real audit, v2 (`desk/dryaudit_e191_v2.py`)

Part 1 is `desk/dryaudit_e191.py`'s map (unchanged beside it) read on runner v2: every line that reads the dry flag, with the real-path v2
case that ran its real branch (the runbook test v2's LA2 for main()'s registered launch). **Part 2 is new (section 116's lesson):** every line
of runner v2 that reads a device process's standard output (the config read, the self-test, the smoke's hosts, each pass's host, the
sampler's lines) and the ones that read ps, date or et-who, each with the cases that fed it real committed bytes (RB1-RB10) or the real
path's split stand-ins; **any line that reads a stdout through v1's `last_json` fails the audit**. A new dry branch or a new stdout read is
NOT COVERED until mapped.

## 7. THE RELAUNCH RULE (kit mechanics; E192's G4 reading), in step 9 v2

A launch that **opened no device** is not a session: its log reads "no device opened" (the box check, card 1's lock, a holder or an
unreadable et-who, an early stop asked for before the first card command), its `queue.json` has `t_first_ms` null and no "config start"
line: no card command was sent, its card time is 0, and every rest rule skips it. **Step 9 v2** reads the box before anything launches when
RB_OUT already holds a launch's T0: such a launch may be launched **ONCE more from the same RB_OUT, inside the same window**, every gate of
step 9 v2 passing again (the brief's note: the look reads FREE first); RB_OUT then holds `e191-relaunch.txt` (the refused T0 and its line),
and a second refused launch ends the day (10, before any call). A launch that sent a card command is the RB_OUT's one session: step 9 v2
refuses (10) another from it. The refused launch's T0 and its line go into the lane's result and the data README, dated; it is not
collected. (The readiness check's GAPS 2: our own live collector's moment on the management node, about 0.4% by its duty cycle, would have
ended the day with no data; now it costs one relaunch.)

**THE LAST LAUNCH (a gate made stricter for safety; added before the land, after the verifier's finding 2).** Right after k6's guard and
before the rest rule, step 9 v2 reads the box's last E191 launch, `build/q141k/e191.T0` (every launch writes it before anything else), and
launches only when it is the last launch this RB_OUT knows: RB_OUT's `e191-T0.txt`, or, when RB_OUT holds none, the first session's T0
1794766494 (`1a4bc1e3`). Any other T0 is a launch that went out while its ssh call was lost (step 9 v2 then exits 14 before it writes
`e191-T0.txt` or `e191-relaunch.txt`). Such a launch may have opened a device and run as a session, so without this gate a later launch from
the same RB_OUT, once the rest had passed, could follow it as a third session. Step 9 v2 refuses (10) and launches nothing; the box is read,
read-only, before anything else. Step 10 v2 already makes the same comparison (RUN-UNKNOWN). The runbook test shows both forms: LL2a
(RB_OUT holding no T0) and LL2b (RB_OUT holding one).

## 8. The runbook for the second session (E191.md's dated amendment A1)

Run from the lab clone, each step with a **new RB_OUT** (absent or empty before step 1; the first session's RB_OUT is never reused), the
one `RB_LOCK` and, for step 2 v2, `RB_GITLOCK`. Exit codes are k6's.

| step | file | from this note |
|---|---|---|
| B | `W/book.sh take aifoundry1 <lane>`: its time is A1's **G2** | (the card lane's) |
| 0 | THE LOAD RULE; `check_day2_v2.py tree --pull` under the lab-git lock; the anchor lines of this note's land | unchanged, with this note's lines |
| H | `W/hold.sh add <lane>` | unchanged |
| 1 | `rb/s02_window_e191.sh 2026-11-15 <G2+1:30> <G2+3:30>` (each rounded up; G2 at 20:29:00 or earlier) | unchanged; a new RB_OUT |
| 2 | **`rb/s03_desk_e191_v2.sh`** | **new**: v1's step 2 now stops at its own never-run check (c) |
| 4, then 3 | the look; the post waived (his words, 10:22:36 PST) | unchanged |
| 5 | **`rb/s07_a1_sync_e191_v2.sh`** | **new**: harness v2's 49 files; both harnesses read on the box |
| 6 | **start NOT run**; `rb/s08_a1_build_e191.sh wait` alone (A1-4: today's build stands; it re-reads it into this RB_OUT) | v1's wait |
| 7 | `rb/s09_a1_reads_e191.sh` | unchanged (its one re-run rule) |
| 8 | **`rb/s10_a1_dry_e191_v2.sh start`**, then `wait` | **new**: job a1-dry-e191-v2; `E191-DRY-V2 ... note2=1 runtime-dropped=n` |
| 9 | **`rb/s11_a1_session_e191_v2.sh FULL`** | **new**: session v2; a1-dry-e191-v2; the relaunch rule; the last launch (section 7) |
| 10 | **`rb/s20_wait_e191_v2.sh`**, again while it says 17 | **new**: `session_e191*.sh`; NOTE2-SESSION |
| 11 | **`rb/s22_collect_e191_v2.sh`** (no release: no post) | **new**: `docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/`; session v2 only |
| 12 | the README from `rb/data-readme-form-e191.md` for the `-s2` directory (its Files table names each pass's `stdout.txt`), `rb/readme_check_e191.py`, the scan, the data commit | the form unchanged; the brief's note 1 names the differences |
| 13 | **`rb/s24_score_e191_v2.sh`** | **new**: the `-s2` directory |
| E | `W/hold.sh remove <lane>`; `W/book.sh release aifoundry1 <lane>` | unchanged |

**Never run in the second session:** v1's step 2, 5, 8, 9, 10, 11 or 13; step 6's start; runner v1 or session v1. The dry listing v2
(`rb/list_steps_e191_v2.sh`) lists this order; `desk/drylisting_check_e191_v2.py` checks its command lines (session v2's launch carries
ET_DEVICES=1).

**Step 2 v2** is v1's step 2 with: the never-run check (c) in this note's form (every E191 data path in any ref lies in the first session's
record, `docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/`, and none under its `passes/`; anything else, the `-s2` directory among
them, refuses); three more lists pinned (this note's, A1's, and the first session's record's own SHA256SUMS, 22 entries, the bytes the
real-bytes test reads); harness v2 re-made and at its sha256; the common module v2's self-check; the preflight v2; this note's desk tests'
logs as committed. It is in neither list (a file cannot hold the sha256 of a list that holds its own): the go's anchor lines give its
sha256. **Harness v2** (`check_e191_v2.py`, `harness-e191-v2.json`) is v1's 42 files, v1's `harness-e191.json` and the six box files of this
note (runner v2, common v2, session v2, doubles v2, preflight v2, the harness check v2); v1's harness still reads OK on the box (step 6's
wait runs it). **The preflight v2** audits runner v2, both common modules, the identity module, session v2, the build, E189's host check,
both harness checks, E191's guard and both hosts' sources.

## 9. The readings stated here before any E191 pass datum (each kit mechanics, or a gate made stricter for safety, named so)

- **The host's line reassembled and verified (kit mechanics).** The registered quantity is the host's own line (E191.md 8.1: `host-raw.json`
  "the ledger host's own JSON line", the adapter of 8.1 on it); the runtime's line is not part of it. The reader drops only the runtime's
  exact text, `Opening device <n>` and its newline, the one form among the lab's 801 committed occurrences (RB10); for that text it reads
  the host's line or nothing. A runtime text of another form is not dropped. Inside the host's line it leaves the line unparseable (no data:
  RB6, RPS5, S2), unless it falls inside one of the head's three free-text strings (`shire_mask`, `minion_mask`, `first_mismatch`), whose
  forms the reader does not check: there it would be read into that string (the verifier's attack A8n). No rule reads those three (no
  adapter, reducer or scorer number; `first_mismatch` appears only in the words of a failed check's reason), so no reading can change; their
  forms stay unchecked so that a check cannot turn a good run into no data over a field nothing scores.
- **A line not verified is not read (a gate made stricter for safety).** v1 read any last `{` line that parsed; v2 also requires the line's
  own form and its command's fields. It can turn a good run into no data (a smoke gate failure, a FAILED RUN), never a bad run into a datum.
- **Each pass keeps its raw standard output (kit mechanics):** `stdout.txt`, a new file in each pass directory, collected and listed like
  the rest (the README's Files table names it; the checker reads basenames, and the smoke's `stdout.txt` row already names that name).
- **Step 10 v2 and step 11 v2 read session v2 only (gates made stricter for safety):** a T0 whose log does not name "kit note 2" is refused.
- **The relaunch rule (kit mechanics, section 7);** step 9 v2's one session an RB_OUT (a gate made stricter for safety).
- **The last launch (a gate made stricter for safety, section 7):** step 9 v2 launches only while the box's last E191 launch is the last one
  its RB_OUT knows (its `e191-T0.txt`, or with none the first session's T0).
- **The never-run check (c) in this note's form (kit mechanics):** it reads the first session's record as what it is, a record with no pass.
- Everything else is KIT.md section 4, unchanged.

## 10. What does not change

E191.md, its dated note 1 and every registered file, list and anchor; KIT.md and every file of the kit's list (`SHA256SUMS-e191-kit`, 73
entries), the brief, and the first session's record. The adapter, THE STOP LINES, the identity gate, the watch, the holder rule, the 30 s
bound, the sampler's freshness, the early stop, the box check, THE KERNEL GATE, the build, the rest rule, the collector, the reducer, the
scorer, the cap and the window rule; every device command (each a READ). Every new file is new; nothing committed is modified, renamed or
removed. The new Python files (`e191_common_v2.py`, `run_e191_v2.py`, `fake_card_e191_v2.py`, `check_e191_v2.py`,
`selftest_run_e191_v2.py`, `desk/realbytes_e191.py`, `desk/realpath_e191_v2.py`, `desk/dryaudit_e191_v2.py`,
`desk/drylisting_check_e191_v2.py`; standard library only, numpy where the unchanged reducer is imported) shadow no module (the quick set).

## 11. What the desk cannot show (for the verifier and the readiness critic)

1. **The real hosts' standard output on card 1 beyond the smoke's one copy line.** The day's bytes show one form (the runtime line after the
   head of a one-launch copy). A K-launch pass's line, SHA-256's and the sorts' lines, and sparse parity's line on aifoundry1 have never been
   read; the reader is shown on each form at every offset (RB3, RB8) and on the doubles and stand-ins, not on a card. A runtime text of
   another form inside a line fails safe (the smoke gate, or a FAILED RUN with its raw bytes kept), and would need a dated note.
2. **What the runtime prints** is read from the lab's committed records only (RB10, as committed at `fe08ed67`): every one of them is
   `Opening device <n>` with its newline.
3. Everything in KIT.md section 8 that this note does not answer (the device loader's reading of an ELF, other users' processes, the real
   reader's lines without a stop line's reading) stands as written there.

## 12. Labels

- **Registered, before any E191 pass datum:** runner v2's reader and its files, the stricter gates of section 9, the relaunch rule and the
  last launch, step 2 v2's pins, the second session's runbook.
- **Desk checks of code, not measurements:** every test result here (`/usr/bin/python3` 3.12.3 on aifoundry2); the committed records the
  real-bytes test reads (1a4bc1e3's, E189's, E170's and the lab's other data) are **desk reads of committed records**.
- Nothing here is measured, blind, held out or post hoc, and no E191 pass datum exists.

## 13. Files ([`SHA256SUMS-e191-kit-note2`](SHA256SUMS-e191-kit-note2), 71 entries)

This note, the brief's dated note 1; the box files `e191_common_v2.py`, `run_e191_v2.py`, `session_e191_v2.sh`, `fake_card_e191_v2.py`,
`check_e191_v2.py`, `harness-e191-v2.json`, `preflight_e191_v2.sh`; the runbook's `rb/s07_a1_sync_e191_v2.sh`, `rb/s10_a1_dry_e191_v2.sh`,
`rb/s11_a1_session_e191_v2.sh`, `rb/s20_wait_e191_v2.sh`, `rb/s22_collect_e191_v2.sh`, `rb/s24_score_e191_v2.sh`, `rb/list_steps_e191_v2.sh`;
the desk tests `desk/realbytes_e191.py`, `desk/realpath_e191_v2.py`, `desk/realpath_e191_v2.sh`, `selftest_run_e191_v2.py`,
`desk/dryaudit_e191_v2.py`, `desk/drylisting_check_e191_v2.py`, `desk/checks_e191_v2.sh`, `rb/selftest_rb_e191_v2.sh`,
`rb/selftest_rb_e191_v2_ns.sh`; the eight logs (33 new files). It also pins the 38 unchanged files the new ones run, source, import or
read: `run_e191.py`, `e191_common.py`, `e191_ident.py`, `fake_card_e191.py`, `session_e191.sh`, `check_e191.py`, `harness-e191.json`,
`preflight_e191.sh`, `ettelem_guard_e191.sh`, `collect_e191.py`, `score_e191.py`, `selftest_run_e191.py`, `desk/realpath_e191.py`,
`desk/realpath_e191.sh`, `desk/dryaudit_e191.py`, `desk/drylisting_check_e191.py`, `rb/rb_e191.sh`, `rb/s02_window_e191.sh`,
`rb/s03_desk_e191.sh`, `rb/s05_look_e191.sh`, `rb/s07_a1_sync_e191.sh`, `rb/s08_a1_build_e191.sh`, `rb/s09_a1_reads_e191.sh`,
`rb/s10_a1_dry_e191.sh`, `rb/s11_a1_session_e191.sh`, `rb/s20_wait_e191.sh`, `rb/s22_collect_e191.sh`, `rb/s24_score_e191.sh`,
`rb/list_steps_e191.sh`, `rb/rest_rule_e191.sh`, `rb/check_history_e191.py`, `rb/readme_check_e191.py`, `rb/data-readme-form-e191.md`,
`rb/selftest_rb_e191_ns.sh`, `rb/fake_cmake_e191.sh`, `SHA256SUMS-e191-kit`, k6's `rb_common.sh`, and the first session's record's
`SHA256SUMS`. Step 2 v2 (`rb/s03_desk_e191_v2.sh`) is outside it, and so is A1's list (`SHA256SUMS-e191-a1`, 9 entries: the amendment,
E191.md and its registration list, note 1 and its list, this note, the brief's note 1, and the first session's record's README and
SHA256SUMS).

    /usr/bin/python3 -I -B tools/claims-v3/e191/desk/realbytes_e191.py                      # the real-bytes test (seconds; RB10 reads fe08ed67 by git)
    bash tools/claims-v3/e191/desk/realpath_e191_v2.sh <an empty scratch dir>               # inside a no-device sandbox; about 4 minutes
    /usr/bin/python3 -B tools/claims-v3/e191/selftest_run_e191_v2.py <scratch dir>          # inside a no-device sandbox; about 20 minutes
    /usr/bin/python3 -I -B tools/claims-v3/e191/desk/dryaudit_e191_v2.py
    bash tools/claims-v3/e191/rb/selftest_rb_e191_v2_ns.sh <an empty scratch dir>           # inside a no-device sandbox
    bash tools/claims-v3/e191/rb/list_steps_e191_v2.sh <an empty scratch dir>
    bash tools/claims-v3/e191/desk/checks_e191_v2.sh

## 14. Before the land: the verifier's findings, and what changed (the lane `fix-n2e191`, Q184)

The note's verifier (Q184) read the first session's record `1a4bc1e3` with no finding, and read this note and A1 as holding with fixes: two
minor findings and six nits, none of which changes a reading. Each was answered here before the land, in the new files only; nothing
registered changed.

| # | finding | what changed |
|---|---|---|
| 1 (minor) | A1's head said note 1 section 3 lets it register "what that day's sessions are", and A1-3's move of E191.md 13's window anchor from G to G2 was not named a departure | A1's head says how A1 fits section 3 (the registered session carried out once more after the kit's own defect, before any pass datum, no frozen item read or changed); A1-1 names both departures for that day, E191.md 12's fallback row and E191.md 13's window anchor |
| 2 (minor) | step 9 v2's relaunch branch trusted RB_OUT's `e191-T0.txt`: a launch whose ssh call was lost would go unseen | THE LAST LAUNCH (section 7) in `rb/s11_a1_session_e191_v2.sh`, with RB_OUT holding a T0 or none; the runbook test's LL2a and LL2b; the brief's note 1 says to read the box after a 14 from step 9 v2 |
| 3 (nit) | section 2's table had 11 rows for 13 replacements and called v1's docstring unchanged | the two docstring rows added; runner v2's header line now says v1's docstring follows with two edits (one line; the file's line count is unchanged) |
| 4 (nit) | "Results first" named the wrong base for some logs, and the dry listing's log named none | every test re-run at one base, each log naming it in its first line, the dry listing's too |
| 5 (nit) | RB10 read the worktree, so later records would turn it to 9 of 10: the second session's raw `stdout.txt` files (the runtime line inside the host's line) or a later kit's; the fix lane found a second way, runner v2's own records (`host_line` in smoke.json and run.json, the session log's words), which quote the dropped text without its newline, a form RB10 counted as "other" | RB10 reads the lab as committed at `fe08ed67` (git's blobs) |
| 6 (nit) | A1-3 cited E191.md 13 for the 40-minute rest | A1-3 cites KIT.md section 4 and `rb/rest_rule_e191.sh` |
| 7 (nit) | A1 gave 10:23:10 PST as `1a4bc1e3`'s commit time | committed 10:23:05, pushed 10:23:10 PST |
| 8 (nit) | section 9's "the host's line or nothing" holds only for the exact runtime text | section 9 qualified (the three unchecked string fields, read by no rule); no code change |

The files the fixes changed: this note, A1, the brief's note 1, `run_e191_v2.py` (one header line) and `harness-e191-v2.json` (re-made for
it), `rb/s11_a1_session_e191_v2.sh`, `rb/selftest_rb_e191_v2.sh`, `desk/realbytes_e191.py`, every log of "Results first", the two lists and
step 2 v2's two pins.

SPDX-License-Identifier: Apache-2.0
