# E224's run kit: MM1-v3.3's blind day in two arms - arm A on aifoundry1 card 1 and arm B on aifoundry2 card 0, in E220's kit form (Q237; kitted, not run)

*Fri 20 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q237, lane `kit-e224`), on top of reg-e224's registration ([E224.md](E224.md), found
by content: the commit that added it; its subtree `a46c1682...`; `SHA256SUMS-e224-registration` `9420b5d1...`, 31 entries; its first freeze
line `OUT/reg-e224/FROZEN.txt`, sha256 `54277e52...`, posted on the owner's coordination thread at 15:45:40 PST). Every file here is new; no
registered file was changed and no registered maker was run in a writing form (the frozen scorer's self-tests run through
`rb/scorer_check_e224.py`, into a scratch folder only). No card was claimed or opened, no device command was sent, nothing was posted, no E224
datum exists. The card lanes' brief: [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md). The interpreter of every desk run: `/usr/bin/python3` 3.12.3 on
aifoundry2. Every figure below is a desk figure (a check of code, or a desk read of committed records); nothing is measured.*

**The form.** E220's kit (`tools/claims-v3/e220/`, landed in 2f0ab9cd; its fix-e220 answers and ready-e220's checks; both arms RAN FULL on these
two cards this afternoon, data fd074f9e and 257496b7) is the template: every kit file of E220's was copied under E224's names by
`OUT/kit-e224/scripts/s02_port.py` (e220 -> e224 in names and text; dated note 1's path kept) and then made E224's by named edit scripts (`s03`
-`s25` in the lane's folder), each an exact replacement that refuses to land when its old text is not there once.

## Results first (the final desk runs, each inside `W/slot.sh` and `W/nodev.sh`, with the quiet-desk flag absent; logs in `logs/` and `a2/logs/`)

| arm | desk test | its last line |
|---|---|---|
| A | the runner on its doubles (`selftest_run_e224a.py`) | `SELFTEST-RUN-E224A 73 of 73 PASS` |
| A | the real path on card 1's stand-ins (`desk/realpath_e224a.sh`) | `REALPATH-E224A 19 of 19 PASS` |
| A | the parsers on card 1's committed bytes, E220 arm A and E221 among them (`desk/realbytes_e224a.py`) | `REALBYTES-E224A 23 of 23 PASS` |
| A | the build on this desk (`desk/desktest_build_e224a.sh`) | `DESKTEST-BUILD-E224A 9 of 9 PASS` |
| A | the runbook with a stand-in aifoundry1 (`rb/selftest_rb_e224a.sh`) | `SELFTEST-RB-E224A 32 of 32 PASS` |
| A | A2's steps with fwgate's stand-ins, the stand-in box BOOTED AFTER E82's firmware read (`a2/desk/selftest_a2_e224a.sh`) | `SELFTEST-A2-E224A 39 of 39 PASS` |
| A | the dry listing (`rb/list_steps_e224a.sh A`) | `dry listing: 15 steps listed, 0 exited non-zero, 0 box calls` |
| A | the dry listing of A2's steps (`a2/rb/list_steps_e224a_a2.sh`) | `dry listing (A2, arm A): 15 steps listed, 0 exited non-zero, 0 box calls` |
| A | the device-command preflight (`preflight_e224a.sh`) | `dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)` |
| A | the device-command audit of A2's files | `dmcmd_audit: GO (1 send site(s), 0 disallowed; allow-list: none)` |
| A | the never-run search at the desk (`desk/neverrun_card_e224.py --arm A`: the registered scan and the kit's wider scan) | `NEVER-RUN-E224 arm A: 64 of 64 registered points never ran on aifoundry1 card 1 by session records (E224.md 4, dated note 1's reading), in the registered scan and the kit's wider scan (E220's and E222's folders read) both (scans efb7f05f7980 / 57f39ce5476d, 10...` |
| B | the build on this desk (`desk/desktest_build_e224b.sh`) | `DESKTEST-BUILD-E224B 6 of 6 PASS` |
| B | the runner on its doubles (`desk/selftest_run_e224b.py`) | `SELFTEST-RUN-E224B 14 of 14 PASS` |
| B | the real path at the real pace (`desk/realpath_e224b.py`) | `DESKTEST-REALPATH-E224B 29 of 29 PASS (on the kit's final code: 28 in the full run of 17:12:35-17:52:44 PST, STEP in its own run of 17:53:09-17:57:35 after the fix of its check)` |
| B | every dry branch of the runner against the real-path cases (`desk/dryaudit_e224b.py`) | `DRY-AUDIT-E224B 33 of 33 COVERED` |
| B | the runbook (`desk/selftest_rb_e224b.py`) | `SELFTEST-RB-E224B 95 of 95 PASS` |
| B | the parsers on this card's committed bytes, E220 arm B and E221 among them (`desk/realbytes_kit_e224b.py`) | `REALBYTES-E224B 22 of 22 PASS` |
| B | step 13's readings (`rb/post_e224b.py --selftest`) | `SELFTEST-POST-E224B 10 of 10 PASS` |
| B | the dry pass of the whole session at scale 0.02 (`box/dry_e224b.sh`) | `DRY PASS a2c0 E224 (runner rc 0; 0 runs not clean)` |
| B | the dry listing (`rb/list_steps_e224b.sh`) | `dry listing: 28 steps listed, 0 run, 0 box calls` |
| B | the device-command preflight (`preflight_e224b.sh`) | `dmcmd_audit: GO (12 send site(s), 0 disallowed; allow-list: none)` |
| B | the never-run search at the desk (`desk/neverrun_card_e224.py --arm B`) | `NEVER-RUN-E224 arm B: 63 of 63 registered points never ran on aifoundry2 card 0 by session records (E224.md 4, dated note 1's reading), in the registered scan and the kit's wider scan (E220's and E222's folders read) both (scans e399315311a6 / 37c8f832d115, 10...` |
| both | step 6n's judgement on a stand-in lab, both scans run for real (`desk/selftest_note1_e224.py`) | `SELFTEST-NOTE1-E224 7 of 7 PASS` |
| both | the no-SIGKILL read (`desk/nokill_e224.py`) | `NOKILL-E224: 0 lines that could send SIGKILL toward a device process (want 0); 12 lines that send SIGKILL to the desk's own call tree only (k6's rb_run.py kill_tree(), TERM then KILL past a call's bound or on a login link: the desk's ssh, rsync, git or desk Py...` |
| both | the sized plain timeouts (`desk/timeout_e224.py --check`) | `TIMEOUT-E224 CHECK PASS` |
| both | the frozen scorer's two self-tests, written nowhere but a scratch folder (`rb/scorer_check_e224.py`) | `SCORER-CHECK-E224: stand-ins PASS (byte-identical to selftest-standins.json); real bytes OK (equal to selftest-real.json but the lab's HEAD and its pick: REPORTED 4d154605790f NO PICK)` |

## The round's lessons, and where each is met

| the lesson | where it is met | its desk test |
|---|---|---|
| REAL-PATH desk tests with stand-ins for every device tool, inside W/nodev.sh, through the smoke, the stop path and at least two points (one G) per arm | arm A: `desk/realpath_e224a.py` (RA1: t01, d25, p1r with the opening smoke s01 and the stop-path test; RA1G the G block on the real path: s03, d30, g03); arm B: `desk/realpath_e224b.py` (MAIN: the whole 105-run schedule at the real pace; GWALK, GTRIP at the G block) | both real-path logs |
| A STAND-IN BOOTS AFTER THE FIRMWARE READ | arm A's step 4 is A2's (fwgate's identity gate on this boot); `a2/desk/selftest_a2_e224a.sh` boots its stand-in aifoundry1 after E82's read (and once before it); `rb/selftest_rb_e224a.sh` OB; arm B's runbook test's reboot-gate cases | the A2 and runbook logs |
| EVERY HOST-OUTPUT PARSER FED REAL COMMITTED BYTES FROM EACH ARM'S CARD | arm A (card 1): E215 arm B, E213 arm B, **E220 arm A (fd074f9e: RB-E220A, RB-E220AR)**, **E221's three a1c1 sessions (RB-E221)** and E217's four (`desk/realbytes_e224a.py`); arm B (aifoundry2 card 0): E209, E216, E212's S3 re-run, **E220 arm B (257496b7: RB1c, RB3, RB4's 17 gemmLnc stdouts, RB7c THE MASK on its real fwgate record, RB8c)** and **E221's a2c0-S1 and -S2 (RB2b, RB3)** (`desk/realbytes_kit_e224b.py`) | both real-bytes logs |
| NO SIGKILL TOWARD ANY DEVICE PROCESS (the no-kill audit classing every signal line by its target) | `desk/nokill_e224.py` (E220's widened reader over E224's kit, A2's files, E208's runner and k6's library) | `logs/nokill-e224.txt` |
| THE PLAIN TIMEOUT 10 SIZED SO THAT NO FROZEN GEMM'S CHECK OF C IS CUT OFF (E218's R0 lesson) | `desk/timeout_e224.py` sizes each process from committed process lengths on each card (card 1: E215 arm B, E213 arm B, **E220 arm A**; aifoundry2: E216, E209, **E220 arm B**; E218's f04 on aifoundry3): **every E224 process `timeout 10`** (the longest frozen GEMM d24, 0.2934 s at 600 MHz; the class-S bound PRE 1.0 + 7.5 + W 0.8 + POST 0.7 = 10.0 s, at its edge: REPORTED) | `logs/timeouts-e224.txt`; both runners' tests (every host at 10) |
| STEP 7'S CONFIG READ ONLY ONCE THE REST HAS OPENED | arm A `rb/s09_reads_e224a.sh` (THE REST RULE on aifoundry1 first, the model session's `~/claude/work/ee-*/` among its sources); arm B `rb/s09_reads_e224b.sh` (the rest rule, the release-records guard, then fwgate's look) | the runbook tests' rest cases |
| THE ONE-LAB RULE, with undesk and uncollect on every stop path, the two arms' desk spans kept apart | CARD-LANE-BRIEF.md section 2 and both tables' row E; arm B `rb/end_e224b.sh` | arm B's runbook test (E rows) |
| STEP 2 NEVER REWRITES A REGISTERED FILE IN LAB | both step 2s run the registration's checks in their `--check` form (each in memory; `rules_e224.py` takes no `--work`; the models' staging in RB_OUT) and the frozen scorer's self-tests through `rb/scorer_check_e224.py` into RB_OUT; arm A's step 2 reads at its end that nothing under E224's or MM1's folders is newer than its start marker | arm A P1, P1W, P1X; arm B P17 |
| THE SEALED-FORECAST CHECK AT STEP 0 | arm A `rb/s00_step0_e224a.sh` S1; arm B `rb/s00_sealed_e224b.sh` (and step 2's check 10): the record `W/out/orch/sealed-e224.txt` against `tools/claims-v3/sealed-e224/e224-freeze-lines.md` | arm A S0; arm B P10-P12b, Z1-Z4 |
| THE STEP 6n JUDGEMENT FROM SESSION RECORDS ON THE ARM'S CARD ONLY (E220's note 1), WITH E220's OWN SESSIONS COUNTED ONCE COMMITTED | `desk/neverrun_card_e224.py`: the registered scan (session records only: E224.md 4) and **the kit's wider scan** (the same scanner at its pin, its never-opened rule narrowed in memory to E224's own names, so E220's committed sessions on these cards and its card lanes are read) | `desk/selftest_note1_e224.py`; both never-run desk runs; arm A's runbook NR case |
| dmcmd_audit_v2 GO | `preflight_e224a.sh`, `preflight_e224b.sh` (no allowance); A2's files | the dmcmd logs |
| THE COLLECTION'S SCRUB TESTED ON RECORDS THAT CARRY A HOME PATH | arm A RB-SCRUB, RB-HOLDERS; arm B RB7, RB7b, **RB7c (E220 arm B's real fwgate record)**, RB9 | both real-bytes logs; both runbook tests |
| THE CARD LANES NAMED EXACTLY card-e224a AND card-e224b | the brief; E224's registered scanner never opens a name holding `e224` (`W/out/card-e224a`, `card-e224b`) | `desk/selftest_note1_e224.py` N5; arm A's runbook NR case |

## 1. The kit

**Arm A (aifoundry1 card 1)**: E220 arm A's files under E224's names: `e224a_common.py` (the arm's identity: aifoundry1 card 1, `/dev/et1_*`,
`etsoc-shire1.lock`, ET_DEVICES=1, the start config TDP 65 W / 65 C / 600 MHz; the stops 72 W on 3 samples and 80 C; the die gate min(63, rest
+ 3) C; the drop line 69 W; **the rule 65 and cap 75 minutes**; the sequence from `plan-e224.json > arms > A > runs`: s01 the opening smoke,
t01 at 001, 062 and 097, s03 at 098, the G block's 8 runs 099-106 last; every tile the points name - randn, zeros, ones and family P's eight
pattern tiles, the last against E212's and E217's `src/SRC-SHA256SUMS`; the doubles' figures from forecast-e224.csv and forecast-e224.json >
extra_rows; the sized timeouts), `e224a_ident.py` and `ident_e224a.py`, `run_e224a.py` (the TWO-CARD HOLDER RULE), `build_e224a.sh` (aifoundry1
only; THE ET_DEVICES GATE), `check_e224a.py` (the harness: 60 files, forecast-e224.json and the three tile manifests among them),
`ettelem_guard_e224a.sh`, `session_e224a.sh`, `reduce_e224a.py`, `collect_e224a.py`, `fake_card_e224a.py`, `preflight_e224a.sh`,
`harness-e224a.json`; the runbook `rb/*_e224a.sh` on k6's library (unchanged) and A2's steps 4, 9 and 12 in `a2/`. **THE REST RULE**
(`rb/rest_rule_e224a.sh`) reads the model session's `~/claude/work/ee-*/` on aifoundry1.

**Arm B (aifoundry2 card 0)**: E220 arm B's files under E224's names, the schedule `box/a2c0-E224.json` made by `make_box_e224b.py` from
`plan-e224.json > arms > B` in E208's form (105 runs: t01 at 1, 60 and 96 as role anchor; s03 at 97 as a family-G burst at the card's committed
62.25 W, R4; the G block's 8 runs last; every point's registered data in the box root's form - random and int8 full from E208's `src/tiles`,
zeros and ones E208's `src/tiles` files (byte-equal to the registered kinds tiles: the check reads it), family P's patterns
`src/tiles/<e212|e217>/<fmt>/<name>.bin` synced from E212's and E217's committed tiles at the registered sha256; each run's planning peak PP32,
its plain `timeout_s` 10; the drop line 67 W; the stops 70 W on 3 samples, 70 C, the latch 70 C; the die gate 55 C for at most 180 s; **the
timing rule 65 and cap 75**), `box/run_e224b.py` (E208's runner imported unchanged), the box files, the runbook `rb/*_e224b.sh`,
`rb/releases_e224b.py` (E216's copy-and-guard route for the release records, with E220's fix for E221's release form) and `rb/post_e224b.py`
(step 13's REPORTED readings, now read through E220's pinned arm B reader, as E224's scorer reads it).

**Both arms**: `desk/timeout_e224.py` and `desk/timeouts-e224.json`; `desk/neverrun_card_e224.py` (step 6n: the registered scan, the kit's wider
scan, the judgement, the labels in the scorer's form) and its self-test `desk/selftest_note1_e224.py`; `rb/scorer_check_e224.py` (step 2's scorer
check); `desk/nokill_e224.py`.

## 2. Readings stated here before any datum (no point, forecast, band, rule, plan, stop or scorer changes by them)

1. **THE WIDER SCAN.** E224's registered scanner never opens a name holding `e220`, `e222` or `e224` (E220 AND E222 BLINDNESS at the
   registration). E220's two card days ran this afternoon on E224's two cards, and their data are committed, so the registered scan alone cannot
   see them. Step 6n therefore runs the registered scan unchanged and the kit's wider scan (the same scanner, loaded at its registered sha256 in a
   subprocess, its never-opened rule narrowed in memory to E224's own names). A point either reads run on its arm's card by a session record is
   labelled 'ran before'. The wider scan opens E220's and E222's committed folders and lane folders only after reg-e224's freeze line was posted
   (15:45:40 PST), as the brief allows. E224 avoided every shape E220 registered or scheduled, so no label is expected.
2. **THE SCORER CHECK, FIELD BY FIELD.** The frozen scorer's real-bytes self-test writes the lab's HEAD and the pick it reads there
   (`pick_reader_on_the_lab`: lab_head, verdict, why). Both move after the registration (any commit; E222's scores once committed, when it reads
   PICKED). Step 2 compares its stand-in record byte for byte and its real-bytes record field by field, every field but those three (REPORTED),
   and wants the made record's verdict OK. E220's check compared both byte for byte; its scorer's record named no lab state.
3. **THE SCORER TAKES `--lab`.** E224's scorer requires the lab to read THE PICK from; step 13 passes the lab clone (`$RB_REPO`). The desk tests
   that score through it pass a stand-in lab made by the scorer's own `make_lab` whose committed E222 scores pick `MM1-v3.3 = MM1-v3.2` (arm A's
   runner test, so that the bands and H10-H12 are read; H1-H9 then read NOT APPLICABLE), or the lab clone (arm B's tests: NO PICK, R0 read).
4. **STEP 13's arm B READINGS** (`rb/post_e224b.py after`, REPORTED, never a verdict) read each point's route-c and route-m readings and the
   flags through E220's pinned arm B reader (`score_e220.read_b`, the reader E224's scorer imports at its pin), because E224's scorer output
   names only the count of points read.
5. **THE TILES ON EACH BOX.** Arm A's harness syncs every tile the points name and the three manifests; arm B's box root holds E208's
   `src/tiles` and family P's eight under `src/tiles/e212/` and `src/tiles/e217/`; `make_box_e224b.py check` reads each against points-e224.json
   > tile_sha256 and kernel-e224.json > tiles_sha256.
6. **THE CLASS-S BOUND AT ITS EDGE.** With E220's committed sessions read, the largest post-run time on aifoundry2 is 0.501 s (POST 0.7 after the
   rule's rounding), so the class-S bound reads 10.0 s, exactly the registered plain timeout (E220's read 9.9 s). The tool refuses only above 10;
   the measured longest processes are 9.837 s (card 1) and 9.581 s (aifoundry2). REPORTED: a host that ran longer than its committed peers would
   end on its timeout's TERM (rc 124, the check of C cut, R0's FAIL), as E218's f04 did.
7. **ARM B's s03** (gemmLnc6x5x10, R4 accepted by the orchestrator): planned 69.48 W by MM1-v3.2 x (1 + 2 eps_G) over the 67 W line, run as a
   smoke on the card's committed record (never above 62.25 W); the schedule carries 62.25 W as its planning peak (E220's D1 form).

## 3. Found while kitting (REPORTED)

1. **E224's registered scanner cannot see E220's sessions on E224's cards.** It never opens a name holding `e220`, `e222` or `e224` (the
   registration's blindness rule), and E220's two arms ran on these two cards this afternoon (committed fd074f9e, 257496b7). Step 6n adds
   the kit's wider scan (section 2, reading 1). At the desk both scans read every point never run on its card (the results above); the wider
   scan read E220's two data folders and its two card lanes, about 3,400 files more.
2. **The frozen scorer's real-bytes self-test names the lab's HEAD and pick**, so a byte-for-byte comparison at step 2 would refuse every
   card day after the registration (reading 2: field by field, the moving fields REPORTED).
3. **E224's scorer requires `--lab`, and its output names only how many points each arm read** (no per-point `measured` map, `route_m_REPORTED` a
   list). The kit's step 13 passes the lab clone; the desk tests and step 13's arm B readings read the points through E220's pinned readers
   (`score_e220.read_a`, `read_b`), the ones E224's scorer imports (readings 3 and 4).
4. **E224's plan form is not E220's**: the tie's and smokes' rows are `extra_rows` (no D1 departure rows), the rule and cap `rule_min` and
   `cap_min`, the counts `runs_scored_and_ties` and `smoke_processes`; the tie's and smokes' frozen forecasts live in `forecast-e224.json` >
   `extra_rows`, not in the CSV. The kit reads E224's form; arm A's harness syncs the JSON (60 files).
5. **E220's s03 on arm A has a frozen row in E224** (gemmLnc2x1x37 at 600 MHz, MM1-v3.2: 1,495.5 cycles an op, 24.07 W): the doubles use it
   (E220's doubles gave s03 toy figures).
6. **The class-S timeout bound reads 10.0 s** with E220's sessions read (reading 6): at the registered plain timeout, not over it.
7. **The port carried lane names E220's own port had renamed** (E216's fix lane as "fix-e220b", E218's kit lane as "kit-e220a"); the kit's
   words name them by their history again (`fix-e216`, `verify-e216`, `kit-e218`; E220's own `fix-e220`, `verify-e220`).
8. **Arm A's runner test read 69 of 73 on its first full run** (16:38-17:01 PST): CR's copied tree lacked forecast-e224.json and the two tile
   manifests (the common module reads them); LG3 and E2 read the scorer's per-point map, which E224's scorer does not write; E2's "every arm B
   rule NO DATA" met arm B's H1-H9 reading NOT APPLICABLE under the stand-in pick MM1-v3.2. Each fixed in the test; CR and LG3 re-ran 2 of 2
   (17:02-17:03), and the final run is the table's.
9. **Arm B's s03** keeps E220 arm B's planning peak 62.25 W (the card's committed record; R4 accepted), over the 67 W line by MM1-v3.2's own
   planning peak (69.48 W): the schedule says so in its note.
10. **Three final runs needed a second run, each after a test-only fix named here** (the first runs' raw logs are in the lane's
    `OUT/kit-e224/logs/final-*.txt`): arm B's real path read 28 of 29 (STEP's sample-window check read run 8, E220's p03b's place, not y3a's run
    7; fixed, STEP run again alone: 1 of 1; the kit's log holds both runs and says so); arm A's real path read 18 of 19 (RA1G wanted every G
    run's check of C "approx", and E224's first G run in the lnc2 sequence, d30, is int8, whose check is exact; fixed: exact or approx, R0's
    rule; then 19 of 19); arm B's dry pass was REFUSED inside W/nodev.sh by the real `et-who --check` (no card node there: rc 2), as E220's kit
    found, and ran with E220's stand-in `et-who` first on PATH (every card free; the dry pass opens no device): DRY PASS.
11. **The ported docstrings' section numbers**: where a ported comment cites "E224.md 3" or "E224.md 6" for the smoke's rules or the run's
    form, the words are E220.md's sections carried over; E224.md's own sections are 2 (the kernel), 3 (the points), 4 (never run), 6 (the cards,
    the order, the stops and the smoke s03) and 7 (the scoring). No code reads a section number.
12. **Two comment lines in each step 2** (`rb/s03_desk_e224a.sh` line 8, `rb/s03_desk_e224b.sh` line 22, E220's words) still say both
    self-tests are compared "byte for byte"; the code they describe (`rb/scorer_check_e224.py`) compares the real-bytes record field by field
    (section 2, reading 2), as its own docstring, line 26 of arm A's step 2 and the brief say. Left unchanged so that both runbook tests' final
    runs read the files as committed.

## 4. Files

Every file is new, under `tools/claims-v3/e224/`; every one but the two step 2s (`rb/s03_desk_e224a.sh`, `rb/s03_desk_e224b.sh`) and the list
itself is in `SHA256SUMS-e224-kit`. The step 2s pin the list by its count and its own sha256 (KITPIN); the land record's anchor lines pin the
step 2s.

## 5. Device commands

Reads only: dmcmd_audit_v2 GO on each arm's files with no allowance (no WRITE, not the statistics reset); A2's one firmware-revisions READ on
arm A (fwgate's, both locks held, `--both-nodes-ok`); fwgate's look and guard on arm B (one read on NEEDS-READ). No firmware, OTA, flash, PMIC
write, governor, TDP, threshold or clock set, reset, PCIe recovery, driver reload or power cycle anywhere in the kit.

## 6. No SIGKILL

No SIGKILL toward a device process (E220's fix-e220 F4 reading, kept). No file of the kit (both arms, A2), of E208's runner (`src/`) or of k6's
library sends SIGKILL to a device process; every device process runs under its own plain `timeout 10` (SIGTERM only); a host past its TERM is
HUNG (arm A) or a LEFTOVER (arm B), and nothing is ever killed. The one SIGKILL in the code the kit runs is k6's `q141k-runbook/v3.1/rb_run.py`
`kill_tree()`, which reaches only that call's own local process tree on the desk (aifoundry2's ssh client, rsync, git or desk Python), for arm A
only; arm A runs no device process on aifoundry2, and arm B's runbook does not use rb_run.py. `desk/nokill_e224.py` classes every sending line
by its target (its last line in the results).

## 7. What the desk cannot show

The cards' own readings (the config reads, the clocks, the board power, the governor's steps); aifoundry1's own build of arm A (the ET_DEVICES
reading); the model session's activity on either box on the day (THE REST RULE reads it then); E222's pick (committed later tonight or not).

## 8. Labels, compute, incidents

Every figure here is desk. The desk tests ran one slot job at a time but for the incidents logged in `OUT/kit-e224/logs/progress.txt`.
