# E220's run kit: MM1-v3.2's card-transfer blind day on two cards - arm A on aifoundry1 card 1 in E215 arm B's kit form with E213's A2 and A3, arm B on aifoundry2 card 0 in E216's kit form (Q233; kitted, not run)

*Fri 20 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q233, lane `kit-e220`), on top of reg-e220's registration ([E220.md](E220.md), found
by content: the commit that added it; its subtree `46dde0fd...`; `SHA256SUMS-e220-registration` `dc5d053f...`, 29 entries; MM1-v3.2's land
`4e386f75` the model's freeze line). Every file here is new; no registered file was changed and no registered maker was run in a writing form
(the frozen scorer's self-tests run through `rb/scorer_check_e220.py`, into a scratch folder only). No card was claimed or opened, no device
command was sent, nothing was posted, no E220 datum exists. The card lanes' brief: [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md). The interpreter
of every desk run: `/usr/bin/python3` 3.12.3 on aifoundry2. Every figure below is a desk figure (a check of code, or a desk read of committed
records); nothing is measured.*

## fix-e220: verify-e220's findings answered before any E220 datum

*Fri 20 Nov 2026, about 10:50-12:30 PST, round Q233's lane `fix-e220`, on aifoundry2, desk only. No card command, no simulator run, nothing
posted, nothing committed in LAB. verify-e220 was Q233's verifier of the registration and this kit: HOLDS WITH FIXES, 10:47 PST. No forecast,
point, band, tie, rule, plan, order, stop, card time, cap or scorer changed. The registration's files are byte for byte as verified
(subtree `46dde0fd`, `SHA256SUMS-e220-registration` `dc5d053f`). Its commit now also carries dated note 1
(`tools/claims-v3/e220-notes/E220.md.dated-note-1.md`, outside the registered folder).*

| finding | answer | where |
|---|---|---|
| **F1** (high): step 6n's literal reading labels arm A 52 of 84 and arm B 42 of 74 'ran before' from E221's card-less desk copy (`W/out/data-e221/work/reg-tree/`) | **Dated note 1, section 1, by the orchestrator's ruling 1.** A point is labelled only by a session record on the arm's card: MM1-v3.2's measured points there, a committed data folder naming the card, or a session's own file in a lane folder naming the card (never a dry pass). A capped listing that cannot be cleared counts (the conservative side). A folder naming no card never counts. The judgement now writes these labels, and the literal reading's are REPORTED beside (`literal_reading_REPORTED`). Desk runs at 11:25 PST: **arm A 84 of 84, arm B 74 of 74 never ran** (literal: 32 of 84 and 32 of 74). xy03b reads never run: the mask `0x3030` is named only in card-less copies. | `desk/neverrun_card_e220.py` (`note1()`); new `desk/selftest_note1_e220.py` (`logs/note1-judgement-e220.txt`, SELFTEST-NOTE1-E220 13 of 13 PASS); `logs/neverrun-desk-e220a.txt`, `logs/neverrun-desk-e220b.txt` |
| **F2** (high): row R refuses E221's real release line (`RELEASE aifoundry2 card 0: E221 a2c0-Sk ended (runner rc 0, ...)`, no `ended HH:MM:SS`): exit 16. With a no-end word in it, it became a comment and the rest opened early | `rb/releases_e220b.py` reads a line holding RELEASE, released or ended but no end time as **ended at its post's own time**. That time is at or after the true end, so the rest counted from it is never shorter. Such a line is checked before the no-end words, so it is never a comment; with no day it is UNCLASSIFIED (16). On the round's real records: 13 lines naming aifoundry2 card 0, and only E221's a2c0-S1 RELEASE (10:55:47) changes kind, to a session end at 10:55:47 (rest open from 11:35:47). | `rb/releases_e220b.py`; new case **GR2** in `desk/selftest_rb_e220b.py` (E221's real form as is, with a no-end word, and with no day); `SELFTEST-RB-E220B 95 of 95 PASS` (Fri 20 Nov 2026 11:42:30 PST; new case GR2 among them) |
| **F3** (medium): CX-E reads LARGER HERE at equal rms with normal errors 9.5% (A) and 33.1% (B) of the time, because the aifoundry3 errors are heavy-tailed | **Dated note 1, section 2** (no rule change). The false LARGER HERE rate at equal distribution (this card's errors resampled from the twins' aifoundry3 errors): **A 0.0032, B 0.0019, pooled CXP-E 0.0033**. At equal rms with normal errors: 0.108, 0.338 and 0.499 (the pooled figure was not registered). Every CX verdict is printed beside both: `tools/claims-v3/e220-notes/cx_null_e220_note1.py beside <the scorer's .json>`, in each arm's step 13 row of the brief | `tools/claims-v3/e220-notes/` (lands with the registration) |
| **F4** (medium): the no-SIGKILL claim is wider than the code. k6's `q141k-runbook/v3.1/rb_run.py` `kill_tree()` sends SIGTERM then SIGKILL (`os.killpg`, and `os.kill` with the signal in a loop variable), and the reader missed both forms | **The claim is narrowed to device processes** (section 6), and the reader is widened. It now catches `os.killpg`, `os.kill` and `send_signal` with a signal held in a variable, SIGKILL named in code, more shell forms and `timeout -s KILL`. Code is read apart from comments, docstrings and strings, and each sending line is classed by what it can reach. `NOKILL-E220: 0 lines that could send SIGKILL toward a device process; 12 lines that send SIGKILL to the desk's own call tree only` (kill_tree() in the four versions of rb_run.py); 16 lines state the rule | `desk/nokill_e220.py`; `logs/nokill-e220.txt` |
| **F5** (low): arm A's undesk and uncollect on its stop paths are by hand | No end script was added (no new code on the card day). Arm A's row E in the brief now names the four calls by hand on every stop path. Before the lane returns, `onelab.sh show` must list no flag of card-e220a | `CARD-LANE-BRIEF.md` row E (arm A) |
| **F6** (low): no step 2 ran after the KITPIN was set | Both step 2s ran for real in this lane's scratch clone at the final kit commit, with the final pins (fix-e220's result). The ready lane runs them again at the landed HEAD | fix-e220's logs |
| **F7** (nit): `rb/rest_rule_e220a.sh`'s header still describes aifoundry3 and E215 arm A's last session | **This note corrects it:** the header's words are E215 arm A's. The code is the box-neutral rule, and arm A's row 7 and `rb/s09_reads_e220a.sh` call it on aifoundry1 (card 1's lock, `~/claude/work/ee-*/` on aifoundry1). The file is unchanged, so its hash and the tests that ran it stand | here |
| **F8** (info): the die gate could push arm A's G block past the 60-minute rule; arm B's s03 plans at 69.48 W against its 70 W stop | None needed (the registered subset covers the first; D1's measured 59.3 W the second) | |

**The fix-e220 desk tests** (each inside `W/slot.sh`, the kit's logged runs also inside `W/nodev.sh`, the quiet-desk flag absent at the start of
every run that used a stand-in; logs in `logs/` and fix-e220's own):

- the release reader on the round's real records and E221's real form (fix-e220's T02: 9 of 9 PASS; its first run read 4 of 9 because the
  stand-in posts were dated before the real record's last end, a fault of the test);
- the note-1 judgement (SELFTEST-NOTE1-E220 13 of 13 PASS);
- both never-run desk runs; the widened no-SIGKILL read (its two first tries flagged `os.kill(pid, 0)` and SIGKILL inside strings: fixed);
- both preflights (dmcmd_audit_v2 GO, 11 and 12 sites, the findings equal kit-e220's);
- arm B's runbook test: `SELFTEST-RB-E220B 95 of 95 PASS` (Fri 20 Nov 2026 11:42:30 PST; new case GR2 among them);
- arm A's runbook test: `SELFTEST-RB-E220A 32 of 32 PASS` (Fri 20 Nov 2026 11:45:25 PST; its NR case runs step 6n with the note-1 judgement).

**Not re-run** (no file they run changed; of their scripts only `rb/post_e220b.py` names a changed file, in its docstring, and the function
it names, `desk/neverrun_card_e220.py check-labels`, is unchanged): the runners' tests, the real paths, the real bytes, the builds, the dry
audit, the dry pass, the A2 test, the post readings and the scorer check.

## Results first (the final desk runs, each inside `W/slot.sh` and `W/nodev.sh`, with the quiet-desk flag absent; logs in `logs/` and `a2/logs/`)

| arm | desk test | its last line |
|---|---|---|
| A | the runner on its doubles (`selftest_run_e220a.py`) | `SELFTEST-RUN-E220A 73 of 73 PASS` |
| A | the real path on card 1's stand-ins (`desk/realpath_e220a.sh`) | `REALPATH-E220A 19 of 19 PASS` |
| A | the parsers on card 1's committed bytes (`desk/realbytes_e220a.py`) | `REALBYTES-E220A 20 of 20 PASS` |
| A | the build on this desk (`desk/desktest_build_e220a.sh`) | `DESKTEST-BUILD-E220A 9 of 9 PASS` |
| A | the runbook with a stand-in aifoundry1 (`rb/selftest_rb_e220a.sh`; fix-e220: re-run) | `SELFTEST-RB-E220A 32 of 32 PASS` |
| A | A2's steps with fwgate's stand-ins, the stand-in box BOOTED AFTER E82's firmware read (`a2/desk/selftest_a2_e220a.sh`) | `SELFTEST-A2-E220A 39 of 39 PASS` |
| A | the dry listings (`rb/list_steps_e220a.sh A`; `a2/rb/list_steps_e220a_a2.sh`) | `dry listing: 15 steps listed, 0 exited non-zero, 0 box calls`; `dry listing (A2, arm A): 15 steps listed, 0 exited non-zero, 0 box calls` |
| A | the device-command preflight (`preflight_e220a.sh`; A2's files) | `dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)`; `dmcmd_audit: GO (1 send site(s), 0 disallowed; allow-list: none)` |
| A | the never-run search at the desk (`desk/neverrun_card_e220.py --arm A`; fix-e220: dated note 1's reading) | `NEVER-RUN-E220 arm A: 84 of 84 registered points never ran on aifoundry1 card 1 by dated note 1's reading (a session record on the card) (scan 0926a7ed7058, 105922 files, lab 3f82e7875350); ran before, labelled: none; the literal reading (REPORTED, not a label): 32 of 84 never ran, 52 read ran before, 52 of them with desk files only` |
| B | the build on this desk (`desk/desktest_build_e220b.sh`) | `DESKTEST-BUILD-E220B 6 of 6 PASS` |
| B | the runner on its doubles (`desk/selftest_run_e220b.py`) | `SELFTEST-RUN-E220B 14 of 14 PASS` |
| B | the real path at the real pace (`desk/realpath_e220b.py`) | `DESKTEST-REALPATH-E220B 29 of 29 PASS` |
| B | every dry branch of the runner against the real-path cases (`desk/dryaudit_e220b.py`) | `DRY-AUDIT-E220B 33 of 33 COVERED` |
| B | the runbook (`desk/selftest_rb_e220b.py`; fix-e220: case GR2 added, re-run) | `SELFTEST-RB-E220B 95 of 95 PASS` |
| B | the parsers on this card's committed bytes (`desk/realbytes_kit_e220b.py`) | `REALBYTES-E220B 14 of 14 PASS` |
| B | step 13's readings (`rb/post_e220b.py --selftest`) | `SELFTEST-POST-E220B 10 of 10 PASS` |
| B | the dry pass of the whole session at scale 0.02 (`box/dry_e220b.sh`) | `DRY PASS a2c0 E220 (runner rc 0; 0 runs not clean)` |
| B | the dry listing (`rb/list_steps_e220b.sh`) | `dry listing: 28 steps listed, 0 run, 0 box calls` |
| B | the device-command preflight (`preflight_e220b.sh`) | `dmcmd_audit: GO (12 send site(s), 0 disallowed; allow-list: none)` |
| B | the never-run search at the desk (`desk/neverrun_card_e220.py --arm B`; fix-e220: dated note 1's reading) | `NEVER-RUN-E220 arm B: 74 of 74 registered points never ran on aifoundry2 card 0 by dated note 1's reading (a session record on the card) (scan 2570e22288b7, 105922 files, lab 3f82e7875350); ran before, labelled: none; the literal reading (REPORTED, not a label): 32 of 74 never ran, 42 read ran before, 41 of them with desk files only` |
| both | fix-e220: dated note 1's reading in the judgement (`desk/selftest_note1_e220.py`, on stand-in scans and on the two desk runs above) | `SELFTEST-NOTE1-E220 13 of 13 PASS` |
| both | fix-e220: the no-SIGKILL read, widened (`desk/nokill_e220.py`) | `NOKILL-E220: 0 lines that could send SIGKILL toward a device process (want 0); 12 lines that send SIGKILL to the desk's own call tree only (...); 16 lines state the rule` |
| both | the sized plain timeouts (`desk/timeout_e220.py --check`) | `TIMEOUT-E220 CHECK PASS` |
| both | the frozen scorer's two self-tests, written nowhere but a scratch folder (`rb/scorer_check_e220.py`) | `SCORER-CHECK-E220: stand-ins PASS (byte-identical to selftest-standins.json); real bytes OK (byte-identical to selftest-real.json)` |

**Five final runs were run twice, each after a correction named here (the table holds the second runs; the first runs' raw logs are in the
lane's OUT/kit-e220/logs/final-*.txt):** arm B's real path first read 28 of 29 (MAIN's last check counted the G block's 16 runs against its 9
distinct points - every one of the 74 points, the 9 G points among them, was read; the check now counts distinct points); arm B's runbook test
first read 93 of 94 (R8 expected E212's S3 re-run among the lab's data of this card, which the rest rule read on E216's day; on E220's day it
reads E216's session of Thu 19 Nov); arm B's dry pass was first REFUSED inside W/nodev.sh (the real et-who cannot read the card there: section
3 item 4); the no-SIGKILL read first flagged its own docstring's list of the forms it reads (it now skips itself); arm B's never-run desk run
ran again once the judgement REPORTED its hits' kinds (section 3 item 3; the labels the same). Only the dry pass's stand-in and the never-run
judgement's REPORTED field touch what a card day runs.

## The round's lessons, and where each is met

| the lesson | where it is met | its desk test |
|---|---|---|
| REAL-PATH desk tests with stand-ins for every device tool, inside W/nodev.sh, through the smoke, the stop path and at least two points (one G) per arm | arm A: `desk/realpath_e220a.py` (RA1 the short sequence t01, xg09t, p02a: the opening smoke s01, the stop-path test, two points; RA1G the G block on the real path: s03, xg08, n01); arm B: `desk/realpath_e220b.py` (MAIN: the whole 103-run schedule at the real pace; GWALK, GHANG, GTRIP at the G block) | both real-path logs |
| A STAND-IN BOOTS AFTER THE FIRMWARE READ | arm A's step 4 is A2's: fwgate's identity gate on this boot; `a2/desk/selftest_a2_e220a.sh` boots its stand-in aifoundry1 after E82's read (and once before it, the continuity case); `rb/selftest_rb_e220a.sh` OB: k6's look on that boot stops; arm B: `desk/selftest_rb_e220b.py`'s reboot-gate cases (a boot after the read) | the A2 and runbook logs |
| EVERY HOST-OUTPUT PARSER FED REAL COMMITTED BYTES FROM EACH ARM'S CARD | arm A (card 1): E215 arm B's and E213 arm B's committed sessions through the parser and the reducer, E217's four card-1 sessions through the host parser and the identity reader (`desk/realbytes_e220a.py` RB-E215B/BR, RB-E213B/BR, RB-E217); arm B (aifoundry2 card 0): E209's and E216's sessions, E216's ten gemmLnc stdouts of rgm211's host on this card through the walk check, THE MASK on E216's real fwgate record (`desk/realbytes_kit_e220b.py` RB1b, RB3, RB4, RB7b, RB8b) | both real-bytes logs |
| NO SIGKILL ANYWHERE | the runners send SIGTERM to their own sampler only; every host under a plain `timeout`, never `-k`; a host past its TERM is HUNG (arm A) or a LEFTOVER (arm B), never killed; each real-path case asserts no SIGKILL, kill -9 or timeout -k in its records | the real-path logs; `grep` of the kit (KIT.md section 6) |
| THE PLAIN TIMEOUT SIZED SO THAT NO FROZEN GEMM'S CHECK OF C IS CUT OFF (E218's R0 lesson, f04 run 77) | `desk/timeout_e220.py` sizes each point's plain timeout from committed process lengths on each arm's card (card 1: E215 arm B, E213 arm B; aifoundry2: E216, E209; E218's f04 on aifoundry3 the case that was cut): `timeout 10` where the frozen GEMM is at most 0.5 s, else ceil(2.0 + 7.5 + 1.25 t + 0.6 + 1.0): **xf04 (gemmL15x16x32, 1.31 s a GEMM on arm A, 1.23 s on arm B) gets `timeout 13` on both arms**, every other process 10 (`desk/timeouts-e220.json`); both runners and both schedules read it; arm B's schedule check refuses a run without a plain timeout of 10-20 s | `timeouts-e220.txt`; both runner tests (the 13 s timeout on xf04 alone) |
| STEP 7'S CONFIG READ ONLY ONCE THE REST HAS OPENED | arm A `rb/s09_reads_e220a.sh` (the rest rule on aifoundry1 first, the model session's ~/claude/work/ee-*/ among its sources, no card command until it opens); arm B `rb/s09_reads_e220b.sh` (the rest rule, the release-records guard, then fwgate's look) | arm A R7, R7e; arm B the rest cases |
| THE ONE-LAB RULE, with undesk and uncollect on every stop path, the two arms' desk spans kept apart | CARD-LANE-BRIEF.md section 2 and both tables' row E; arm B `rb/end_e220b.sh` | arm B's runbook test (E rows) |
| STEP 2 NEVER REWRITES A REGISTERED FILE IN LAB | both step 2s run the registration's checks in their `--check` form and the frozen scorer's self-tests through `rb/scorer_check_e220.py` into RB_OUT; arm A's step 2 reads at its end that nothing under E220's or MM1's folders is newer than its start marker | arm A P1W, P1X; arm B P17 |
| THE SEALED-FORECAST CHECK AT STEP 0 | arm A `rb/s00_step0_e220a.sh` S1; arm B `rb/s00_sealed_e220b.sh` (and step 2's check 10) | arm A S0; arm B P10-P12b, Z1-Z4 |
| dmcmd_audit_v2 GO | `preflight_e220a.sh`, `preflight_e220b.sh` (no allowance); A2's files | the dmcmd logs |
| THE COLLECTION'S SCRUB TESTED ON RECORDS THAT CARRY A HOME PATH | arm A RB-SCRUB (card 1's and aifoundry3's sessions rebuilt to the box's raw bytes, the home in them), RB-HOLDERS; arm B RB7, RB7b, RB9 (THE MASK and THE SCRUB on E209's and E216's real fwgate records) | both real-bytes logs; both runbook tests |
| THE CARD LANES NAMED EXACTLY card-e220a AND card-e220b | the brief; the never-run scanner subtracts `W/out/card-e220*` and any path holding `-e220-` | both never-run desk logs |

## 1. The kit

**Arm A (aifoundry1 card 1)**: E218's kit (E215's form) made card 1's by E215 arm B's rules: `e220a_common.py` (the arm's identity: aifoundry1
card 1, `/dev/et1_*`, `etsoc-shire1.lock`, ET_DEVICES=1, the start config TDP 65 W / 65 C / 600 MHz; the stops 72 W on 3 samples and 80 C; the
die gate min(63, rest + 3) C; the drop line 69 W; the rule 60 and cap 70 minutes; the sequence from `plan-e220.json > arms > A > runs`: s01 the
opening smoke, t01 at 001, 068 and 086, s03 at 087, the G block's 26 runs 088-113 last; the sized timeouts), `e220a_ident.py` and
`ident_e220a.py` (card 1's identity, the identity gate per process at the WHOLE ELF), `run_e220a.py` (the TWO-CARD HOLDER RULE: another login on
card 1, anything of ours on card 0, another login on card 0 at the start: refused), `build_e220a.sh` (aifoundry1 only; THE ET_DEVICES GATE),
`check_e220a.py`, `ettelem_guard_e220a.sh` (aifoundry1 with ET_DEVICES=1 only; `sample --reset-ms` refused), `session_e220a.sh`,
`reduce_e220a.py`, `collect_e220a.py`, `fake_card_e220a.py`, `preflight_e220a.sh`, `harness-e220a.json`; the runbook `rb/*_e220a.sh` on k6's
library (unchanged) and A2's steps 4, 9 and 12 in `a2/`. **THE REST RULE** (`rb/rest_rule_e220a.sh`) reads the model session's
~/claude/work/ee-*/ on aifoundry1.

**Arm B (aifoundry2 card 0)**: E216's kit made E220's by `make_box_e220b.py`: the schedule `box/a2c0-E220.json` from `plan-e220.json > arms >
B > runs` in E208's form (103 runs: s01 E208's three smoke arms; t01 at 1 and 86, role anchor; s03 at 87 as a family-G burst; the G block's 16
runs last; each run's planning peak PP32, its sized `timeout_s`; the drop line 67 W; the stops 70 W on 3 samples, 70 C, the latch 70 C; the die
gate 55 C for at most 180 s; the timing rule 60 and cap 70), `box/run_e220b.py` (E208's runner imported unchanged; each run's host under its own
plain timeout), the box files, the runbook `rb/*_e220b.sh`; **`rb/releases_e220b.py`**, E216's copy-and-guard route for E212's release record
made a kit tool (every `W/out/orch/*releases*.txt` copied in the rest rule's form; the guard at steps 7 and 9); `rb/post_e220b.py` for E220's
scorer (`score_e220.py --b`).

**Both arms**: `desk/timeout_e220.py` and `desk/timeouts-e220.json` (the sized plain timeouts); `desk/neverrun_card_e220.py` (step 6n: the
registration's scanner and report at their pins, the judgement and the labels in the scorer's form); `rb/scorer_check_e220.py` (step 2's
scorer check: the frozen scorer's two self-tests into a scratch folder, byte-compared with the committed outputs, refusing a folder inside
the lab clone).

## 2. Readings stated here before any datum

1. THE SIZED TIMEOUT: as above; the bound for a class S process is PRE 1.0 + 7.5 + 0.8 + POST 0.6 = 9.9 s under `timeout 10` (the longest
   committed pre-launch, post-run and process lengths on card 1: 0.414 s, 0.495 s, 7.285 s; on aifoundry2: 0.543 s, 0.486 s, 7.476 s).
2. Arm B's s03 is a smoke row (D1), not a registered point of arm B: the frozen scorer's arm B reader does not read its run. A failed s03 is
   THE KERNEL STOP at run 087, the G block NO DATA; step 13's `post_e220b.py after` REPORTS the stop (desk-tested: KWALK3, KCHECK3, KSLOW).
3. Arm B's t01 runs as role 'anchor' (a tie, never in a rule): in E208's reducer an anchor's die slope changes only dP_corr; the scorer reads
   dP_w, p_mean_w and the J readings, so no scored number changes.
4. Arm A's die gate and stops are E220.md's; the first run of the G block follows s03 after its own rest; a family dropped by s03 is no stop.

## 3. Found while kitting (REPORTED)

1. Arm A's real build cannot pass at this desk (its device layer carries no ET_DEVICES): the build's desk test reads its refusal at the
   ET_DEVICES gate (both kernels built and gated first); the real-path and runbook desk tests run the later steps on a stand-in record beside
   the real ELFs and hosts.
2. E221's release record writes every line as a `#` comment, which the rest rule skips; `rb/releases_e220b.py` adds a rule-form line after any
   such line that names aifoundry2 card 0 with its day and its end (none did at the desk run: 6 records, 11 lines naming aifoundry2 card 0: 6
   read as they are, 1 session end added in the rule's form - E212's S3 re-run, as E216's copy wrote it - and 4 comments). **fix-e220
   (verify-e220's F2):** E221's real release line names no end time, so the tool refused it (16), and with a no-end word in it would have kept
   it as a comment. It now ends such a session at its post's own time. At 11:01 PST the round's records read 13 lines naming aifoundry2 card 0:
   6 read as they are, 2 session ends added (1 at the post's own time, E221's a2c0-S1 at 10:55:47) and 5 comments.
3. **THE NEVER-RUN READING HAS MOVED SINCE THE REGISTRATION (for the orchestrator, before either card lane's step 6n).** At the lane's first
   desk run (06:27 PST) arm A read 84 of 84 and arm B 74 of 74 points never run on their cards. At 07:38:29 PST E221's data lane copied its
   registration tree into `W/out/data-e221/work/reg-tree/` (a folder naming no card); its `desk/configs-e221.json` and `desk/scan-e221.json`
   name E220's shape tokens, and the registered literal reading (E220.md 4, N1: a token named in a lane file whose folder names no card
   counts as run on every card) now labels many points 'ran before' (the final desk runs' lines in `logs/neverrun-desk-e220a.txt` and
   `logs/neverrun-desk-e220b.txt`; arm B: 42 of 74). A label takes the point out of every rule. **The kit does not change the registered
   reading**; `desk/neverrun_card_e220.py` now REPORTS beside the labels which labelled points have no session record among the hits counted
   for the card (desk files only: plans, config lists, scan records, desk logs; a dry pass is never a session) - E216's reading of such hits,
   here REPORTED only, so that a dated note before any datum can decide (or the data lane's copy can move out of the lanes' folders).
   **DECIDED (fix-e220):** dated note 1 (the orchestrator's ruling 1) is the reading. The judgement labels only points with a session record on
   the arm's card, and REPORTS the literal reading beside: section "fix-e220", F1.
4. **The dry pass of arm B at the desk** runs inside W/nodev.sh, where the real `et-who --check` cannot read the card (no card nodes: rc 2), so
   its quiet-box look reads a stand-in `et-who` that says every card free (the build desk test's form; the dry pass opens no device); on the
   card day step 8 runs it on the box with the real `et-who`.
5. Arm A's runbook desk test's final run (08:32-08:49 PST) predates the REPORTED hit-kind field of step 6n's judgement (item 3); the labels,
   the line's first words and every file that test reads are unchanged by it; both arms' never-run desk runs ran with the final version.

## 4. Files

Every file is new, under `tools/claims-v3/e220/`; every one but the two step 2s (`rb/s03_desk_e220a.sh`, `rb/s03_desk_e220b.sh`) and the list
itself is in `SHA256SUMS-e220-kit`. The step 2s pin the list by its count and its own sha256 (KITPIN); the land record's anchor lines pin the
step 2s.

## 5. Device commands

Reads only: dmcmd_audit_v2 GO on each arm's files with no allowance (no WRITE, not the statistics reset); A2's one firmware-revisions READ on
arm A (fwgate's, both locks held); fwgate's look and guard on arm B. No firmware, OTA, flash, PMIC write, governor, TDP, threshold or clock set,
reset, PCIe recovery, driver reload or power cycle anywhere in the kit.

## 6. No SIGKILL

**Narrowed by fix-e220 (verify-e220's F4): no SIGKILL toward a device process.** The claim kit-e220 made here was "0 sending lines" with
k6's library among the files read. That holds only for the device side.

- **What is sent to a device process.** No file of the kit (both arms, A2), of E208's runner (`src/`) or of k6's library sends SIGKILL to a
  device process. Every device process runs under its own plain `timeout 10`, or `timeout 13` for xf04, which sends SIGTERM only. A host past
  its TERM is HUNG (arm A) or a LEFTOVER (arm B), and nothing is ever killed.
- **The one SIGKILL in the code the kit runs.** k6's runner `q141k-runbook/v3.1/rb_run.py` (called unchanged by arm A's runbook through k6's
  `rb_common.sh`) sends it in `kill_tree()`. On a login link (KILL 2 s after TERM) or past a call's bound (KILL 10 s after TERM; the probe 2 s
  after), it sends SIGTERM and then SIGKILL to that call's own process tree on the desk: its process group, its descendants by ps, and the pids
  it saw in that group. That tree is aifoundry2's ssh client, rsync, git or desk Python.
- **Why that reaches no device process.** Arm A runs no device process on aifoundry2: its card is aifoundry1 card 1, reached only through ssh,
  and the remote session does not die with the ssh client. Arm B's runbook does not use rb_run.py.
- **The reader, widened** (`desk/nokill_e220.py`). It adds `os.killpg`, `os.kill` and `send_signal` with a signal held in a variable, SIGKILL
  named in code, `kill -SIGKILL` / `-s 9` / `-n 9`, `pkill`/`killall -KILL` and `timeout -s KILL`. It reads code apart from comments,
  docstrings and strings, and classes each line by what it can reach. Its last line: `NOKILL-E220: 0 lines that could send SIGKILL toward a
  device process (want 0); 12 lines that send SIGKILL to the desk's own call tree only (k6's rb_run.py kill_tree(), ...); 16 lines state the
  rule`. The 12 are three lines in each of the four versions of rb_run.py in `tools/claims-v3/q141k-runbook/`, of which arm A runs v3.1's.

## 7. What the desk cannot show

The cards' own readings (the config reads, the clocks, the board power, the governor's steps); aifoundry1's own build of arm A (the ET_DEVICES
reading); the model session's activity on aifoundry1 on the day (THE REST RULE reads it then).

## 8. Labels, compute, incidents

Every figure here is desk. The desk tests ran one slot job at a time but for the incidents logged in `OUT/kit-e220/logs/progress.txt` (two
slot jobs of the lane's at once for about a minute, twice; three short `--check` reads outside the slot; one `bash -c` handed to slot.sh at
the lane's start; many edits made by inline heredoc scripts in Bash calls rather than script files): none touched a card or another lane.
fix-e220's desk runs are in its own progress log (one slot job at a time; the quiet-desk flag absent at every stand-in run's start).
