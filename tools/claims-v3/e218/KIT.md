# E218's run kit: MM1-v3.2's blind matmul day on aifoundry3 card 0 from aifoundry2, in E215 arm A's kit form - one runner, the opening smoke s01 and the stop-path test, the two families both on rgm136's ELF ('rgm136 gemmL' on rgm136's host; 'rgm136 gemmLnc' on rgm211's host), the G block last with its own smoke s03 in its place and its own stop path, every process gated by its family's ELF, rgm211's host tree gated at its build, every run under a plain `timeout 10` and never killed; the never-run search repeated right before the first card command and every point it finds run labelled 'ran before'; the scrub checked on the dry pass's records before the session (Q230; kitted, not run)

*Thu 19 Nov 2026 (week 47), from 20:58 PST, on aifoundry2, desk only (Q230, lane `kit-e218`). No card was claimed or opened: aifoundry2 has a
card, so every desk test that runs a built host, the runner, a stand-in session or a stand-in reader ran inside the round's slots and its sandbox
(`W/slot.sh bash W/nodev.sh`: no /dev/et*, an empty /run/lock), single-threaded, one slot job at a time, with the quiet-desk flag absent. No
device command was sent, no simulator was run, nothing was posted. **No box was reached**: the read-only look at aifoundry3 the brief allows was
NOT RUN (at about 21:55 PST `book.sh show` listed no booking and the round's one claim file named aifoundry1, not aifoundry3; no gate of the kit
needs the look, so the lane stayed off the box: section 8 says what only the card day shows). **New files only, all under `tools/claims-v3/e218/`**, on top of E218's
registration ([`E218.md`](E218.md): reg-e218's local commit `abfa4e5b` on `022addbb`, applied here to GitHub main `9f8b66bf` as `647b21b2` with
`git am`; its `tools/claims-v3/e218` subtree `deb6726f...`; `SHA256SUMS-e218-registration` `8a8ccaf1...`, 24 entries), which this kit changes in
no byte. **No E218 datum exists. Nothing here changes a point, a forecast, a band, a rule, a threshold, the order, the card time, the cap, a stop
or the scorer.** Where E218.md leaves a reading to the kit, the reading is stated in section 4 before any datum. E215's landed kit (`8bde0182`,
whose arm A ran E215 FULL on this card, 119 of 119 runs, data `8355db15`) is the authority every behaviour below is checked against; the kit is
its arm A code, renamed for E218, with the changes this file names.*

**His words** (Mon 16 Nov 2026, received at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul and "FME" the
tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and
number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other
operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation."

**The orchestrator's answers the kit follows** (`W/out/orch/e218-answers.txt`): (1) **keep the drop** - g07t and y03a stay dropped (D1), 52
points, no re-draw; (2) **the seal slot** - if the model session posts a seal before `card-e218` books, the orchestrator holds aifoundry3
(`orch-hold-e218-seal`), registers the seal in `tools/claims-v3/sealed-e218/`, writes `W/out/orch/sealed-e218.txt` after that commit is on main,
then releases. No `sealed-e218.txt` existed when this kit was written; step 0 reads it on the day.

## Results first (desk checks of code and desk reads of committed records; nothing is measured on a card)

| desk test (each run for real, its log under `logs/`) | what it shows | result |
|---|---|---|
| **the runner** (`selftest_run_e218.py`: the doubles, the real runner, the real sandboxing) | every registered behaviour of the session on the doubles: the families and their gates, the order (the G block last, s03 in its place, nothing after), the smoke's and the family smoke's stop paths, every stop line, the card-time rule and the cap, HUNG and K1, the operator's STOP, the scrub's inputs, the reducer and the frozen scorer on the runner's output (OR, LN, LN2, LG3 ... E2-ok, RF) | SELFTEST-RUN-E218 72 of 72 PASS |
| **the real path** (`desk/realpath_e218.sh`: the real build, the real runner, the real guard, stand-ins only for the card's tools, et-who, the lock, the sampler and the host, inside W/nodev.sh under the hostname aifoundry3) | RA1 the whole real path through s01, the stop-path test and three runs (t01, y06b, y08a); **RA1G the G block on the real path** (the third tie, s03 in its place, g08, g04); RA3 a host hung past its TERM, never killed; RA6/RA6T a changed .text refused by the kernel gate and by the tree gate; RA13 the STOP file; RA14 the identity gate per process on real ELFs | REALPATH-E218 19 of 19 PASS |
| **the real bytes** (`desk/realbytes_e218.py`: every host-output parser fed committed bytes from this card) | RB-E215A/RB-E215AR (E215 arm A's whole session, 119 runs and its smokes), RB-E213A/R (E213 arm A), RB-E211/R, RB-E207/R, RB-SPLICE, RB-CFG, RB-ID, RB-SIM, RB-SMOKE, **RB-SCRUB** (committed sessions rebuilt with the box's home in them and scrubbed back to the committed bytes), RB-HOLDERS | REALBYTES-E218 15 of 15 PASS |
| **the build** (`desk/desktest_build_e218.sh`: this desk's real toolchain) | B1 the real build under aifoundry3's hostname: rgm136 KERNEL OK, rgm211's tree KERNEL OK, the hosts' twelve refusals before the device stage; B3/B3b a changed source refused; B4 aifoundry3's `.comment` form by the loadable identity, and `--whole` refusing it; B5/B6/B6t a changed byte refused; B6b the wrong kernel each way and the gate by family; B7 another box refused; B8 the runner's box check; B9 the guard | DESKTEST-BUILD-E218 9 of 9 PASS |
| **the runbook** (`rb/selftest_rb_e218.sh`: a fake ssh and rsync, a stand-in aifoundry3, the real build) | the dry listing; the window rule; the lab-git lock; step 2 at every pin, **P1W/P1X: step 2 writes nothing in the lab and sees a rewrite with the same bytes**; the history check; the datum check (DA, GS); **S0, step 0's six lines and the sealed-forecast check**; the look; ours_live; the sync and a login link; NO-THIRD-BUILD; the real build; **NR, step 6n with E218's own card lane `card-e218` subtracted**; **R7, step 7 only with a fresh report and once the rest has opened**, R7f a 70 C threshold refused; **D/DS, the scrub check before the session**; HG, SD, LS, NS; LA the real session stopping at its box check; W10; C, C2; **CD the data directory and the frozen scorer with step 6n's labels** | SELFTEST-RB-E218 31 of 31 PASS |
| **the dry listing** (`rb/list_steps_e218.sh A`) | every step of the day in order, nothing run, no box call | dry listing: 15 steps listed, 0 exited non-zero, 0 box calls |
| **the preflight** (`preflight_e218.sh`) | dmcmd_audit_v2 on the session's files, no WRITE allowed | dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none) |
| **step 6n's tool on the round's real folders** (`desk/neverrun_card_e218.py run`) | the registration's scanner over the lab at HEAD and every round card and data lane folder: no registered point found run | 52 of 52 registered points never ran (scan 71371fd4e48d, 95609 files; labelled: none) |
| **the quick set** (`logs/checks-e218.txt`) | the registration's list and its five checks in their `--check` form, the scorer's two self-tests byte-identical and its forecasts print, the two modules' self-checks, the identity gate's pins, the harness re-made (CHECK PASS), the kill scan (no kill call in the kit's code), every Python file compiled and every shell file parsed | QUICK-SET-E218 PASS: 0 not as stated (2026-11-19 23:00:16 PST) |

## What E218 changes against E215 arm A's kit, and why (each before any datum)

1. **One arm.** E218 runs on aifoundry3 card 0 only (E218.md 6): arm B's code, its aifoundry1 box, its ET_DEVICES gate and its A2 form are not
   carried; every step takes the arm `A` and refuses any other (10). The card lane is `card-e218` (exactly: the registration's scanner subtracts
   `W/out/card-e218*`).
2. **Two families, both on rgm136's ELF.** 'rgm136 gemmL' (rgm136's host and ELF: Gt, Y, F, the tie t01 and the session smoke s01) and 'rgm136
   gemmLnc' (rgm211's host with rgm136's ELF, walk mn: G g01-g12 and its smoke s03). rgm211's own ELF runs no E218 point, so E215's 'rgm211 gemmLn'
   and 'rgm211 gemmL' families and their smokes s02 and s04 are gone; the runner gates every process on rgm136's ELF (`ident_e218.FAMILY_KERNEL`).
3. **rgm211's tree is gated at its build** (THE TREE GATE, `ident_e218.tree_gate`): its ELF at kernel-e218.json's `rgm211_host` pins - the whole
   ELF `00402801...` or the loadable identity `1351a569...` (aifoundry3's `.comment` form) - so the host the gemmLnc branch runs is E211's tree as
   pinned; the build record carries both gates' lines, and the runner's box check reads them.
4. **The order and the G block.** s01; t01; pass 1 (the 40 Gt, Y and F points); t01; pass 2 (reversed); t01; then **the G block LAST**: s03 at
   place 84 (`084-G-smoke-s03`), the G points by planning peak ascending (g08 g04 g11 g01 g03 g02 g10 g12 g06 g07 g05 g09), then reversed: 107 runs
   and 2 smoke processes (points-e218.json's `sequence_blocks`, which the common module adapts and its self-check reads against the registered lists).
5. **The doubles read MM1-v3.2's frozen forecasts** (`tools/matmul/mm1/v3.2/out/e218/forecasts-e218.csv` `52e78762...`, the "MM1-v3.2|..."
   columns) and the tie's row of the registration's `forecast-e218-reg.csv`; desk numbers only, never a figure of the day.
6. **Step 0 reads two freeze lines**: F1 MM1-v3.2's land `4e386f75` (every declared model's forecasts) and **F1R the registration commit**
   (subtree `deb6726f`; its push froze 'MM1-v3.2 without its gemmLnc term', the rules and the scorer), then F2 the kit, S1 the sealed-forecast
   check, D0 and G1: "STEP0-E218 arm A: 6 of 6 as stated".
7. **Step 2 runs the registration's five checks in their `--check` form** (points_e218, forecast_e218 with its cache in RB_OUT, rules_e218 with
   `--work` in RB_OUT, plan_e218, desk/kernel_e218) and the frozen scorer's `--forecasts` directly: E218's scorer prints and writes nothing in that
   mode (E218.md 10), so E215's print helper is not needed; P1W reads the print in RB_OUT.
8. **Step 6n's judgement is E218.md 4's**: every registered point the repeated scan finds run is labelled 'ran before' and leaves every rule,
   whatever the date; each file's date against the freeze line is REPORTED beside it; the two points the registration dropped (D1) are REPORTED.

## The round's lessons, and where each is met

1. **A real-path desk test**, stand-ins for every device tool, et-who, the lock, the sampler and the host, inside W/nodev.sh, through the smoke,
   the stop path and at least two points, one of them G: `desk/realpath_e218.sh` (RA1: s01, the stop-path test, t01, y06b, y08a; **RA1G: the
   third tie, s03 in its place, g08 and g04 on rgm211's real host with rgm136's real ELF**; RA3 a host hung past its TERM; RA13 the STOP file).
2. **Every host-output parser fed real committed bytes from aifoundry3 card 0**: E215 arm A's whole session and E213 arm A's
   (`desk/realbytes_e218.py`, RB-E215A, RB-E215AR, RB-E213A, RB-E213AR), with E211's and E207's beside them.
3. **No SIGKILL anywhere**: a plain `timeout 10` on every device process; a host alive past its TERM is HUNG, reported and left (the runner
   test's C6 and HG, the real path's RA3); the sampler is stopped by SIGTERM only; the quick set's kill scan reads no kill call in the kit's code.
   One thing is not the kit's code and is said here, as E215's kit said it: the k6 runbook library the steps source bounds the DESK'S own ssh and
   rsync calls with `rb_run.py`, which ends a call past its bound (or on a login link) with TERM and then KILL on aifoundry2's own process group - a
   process on the desk, never one on a box and never a device process (the session runs detached on the box; step 7's one config read runs on
   the box under its own `timeout 10`).
4. **Step 7's config read only once the rest has opened**: `rb/s09_reads_e218.sh` reads the 6n report's age (at most 30 minutes) and THE REST
   RULE on the box first, no card command, and refuses (10) while either fails (the runbook test's R7); R7f a threshold read at 70 C stops the day
   (16).
5. **THE ONE-LAB RULE in the step table**, with undesk and uncollect on every stop path: CARD-LANE-BRIEF.md section 2, rows 0-2 inside the desk
   span, rows 11-12 inside the collect span, row E on every path; the dry listing prints the same notes.
6. **Step 2 never rewriting a registered file in LAB**: every registration check step 2 runs is its `--check` form (rebuilt in memory and
   compared, scratch in RB_OUT), the scorer's self-tests write into RB_OUT, its forecasts print writes nothing, the history check refuses any change
   to a registered file, and **step 2 reads at its end that no file under E218's folder, tools/matmul/mm1 or the seal note's folder is newer than
   its start marker and that E218's paths are clean again** (the runbook test's P1W and P1X: a rewrite with the same bytes is seen).
7. **The sealed-forecast check at step 0**, reading `W/out/orch/sealed-e218.txt` and `tools/claims-v3/sealed-e218/e218-freeze-lines.md`:
   `rb/s00_step0_e218.sh` S1 (the runbook test's S0: no record, a registered seal, an unregistered one); a later seal is a comment line in the
   record and a NEW note (`e218-freeze-lines-2.md`), which step 0 never reads.
8. **dmcmd_audit_v2 GO**: `preflight_e218.sh` on the session's files, no WRITE allowed (`logs/dmcmd-audit-e218.txt`), read again by step 2, by
   step 6 on the box and by the runner before anything opens.
9. **The collection's scrub tested on records that carry a home path**: RB-SCRUB rebuilds E215 arm A's, E213 arm A's, E211's and E207's
   committed sessions into the box's own bytes (the home in them) and scrubs them back to the committed bytes; step 8 ends with THE SCRUB CHECK on
   the dry pass's own records before any card time (runbook test D and DS); RB-HOLDERS masks another login's et-who lines.
10. **The G block last**: the registered order, checked by the common module's self-check (the G block after the third tie, s03 first, nothing
    after), the runner test's OR, LN and LN2, and the real path's RA1G.
11. **The card lane named exactly `card-e218`**: the registration's scanner subtracts `W/out/card-e218*`; the runbook test's NR puts a record of
    f01's token in a stand-in `card-e218` folder and reads it subtracted; CARD-LANE-BRIEF.md names the lane.

## 1. The kit

- **The runner** ([`run_e218.py`](run_e218.py), [`session_e218.sh`](session_e218.sh), [`e218_common.py`](e218_common.py),
  [`e218_ident.py`](e218_ident.py), [`ident_e218.py`](ident_e218.py)): one session, E215 arm A's runner with the changes above. **THE TWO
  FAMILIES BY THE POINT'S LOOP** (points-e218.json's "loop" field, never the arm token): 'rgm136 gemmL' and 'rgm136 gemmLnc'. **THE IDENTITY GATE
  PER PROCESS** (before every process `ident_e218.gate(family, elf)`: its `.text` always the pin `61315bf6...`, and the whole ELF `aace138c...` or
  the loadable identity `649d4079...`; the words recorded with the process; a GATE FAILED at a run starts no process and stops the session; at s03
  it drops the G block). **THE WALK CHECK** on every rgm211-host process (walk mn). **THE KERNEL STOPS** (a 'rgm136 gemmLnc' run with a check of C
  wrong, a tensor error, the walk check failed, a launch timeout (K1 or rc 124), a launch not ok or an exit not 0 stops the session). The opening
  smoke s01 against **R0's absolute band, 200-4,000 cycles an op** (the counter's mean, the median over counted launches), then the stop-path test,
  then the registered sequence. No run after 60 card-minutes, cap 70. The die gate min(60, the session's rest die + 4) C, at most 300 s. Before
  anything opens: the host name (aifoundry3), ET_DEVICES unset, build/e218rgm's record today's BUILT by build_e218.sh on this box (both gates'
  lines), rgm136's ELF through THE KERNEL GATE again and rgm211's tree through THE TREE GATE, both hosts at the sha256 the build recorded, the
  reader at its pin `16037641...`, the three tiles at their sha256, the harness (HARNESS OK) and the preflight (dmcmd_audit_v2 GO). Then the card's
  lock (`flock -n`, held to the end), the holders (counts only), THE FIRST CARD COMMAND `ettelem config` through
  [`ettelem_guard_e218.sh`](ettelem_guard_e218.sh) under a plain `timeout 10` (the start config TDP 0 W / 65 C / 600 MHz and the card's identity;
  the card time counts from it), ONE sampler (10 Hz) whose every line feeds THE STOP LINES as it arrives, THE IDENTITY READ, the smoke and then the
  stop-path test, the registered order, the closing config, "session end", MANIFEST.sha256 last. Nothing is set. Every start first reads the
  operator's STOP file; never two samplers at once.
- **No SIGKILL anywhere** (the orchestrator's standing ruling): every device process is under a plain `timeout 10`; the runner waits for it with a
  bound and, past `timeout`'s TERM by HANG_GRACE_S (4 s), writes "<time> HUNG: ..." in the session log, touches the stop file, starts nothing
  further, sends no further card command (no closing config read), closes the session and LEAVES the process (exit 8). et-who, the harness check
  and the preflight are waited on with a bound and left past it. The sampler is stopped by SIGTERM only. The build runs under a plain `timeout`.
- **The build** ([`build_e218.sh`](build_e218.sh), [`check_e218.py`](check_e218.py)): E136's rgm136 unchanged into **build/e218rgm/rgm136** and
  E211's rgm211 into **build/e218rgm/rgm211** (new folders of ours) on aifoundry3 only (any other box refused before anything is built); rgm136's
  ELF through THE KERNEL GATE (`check_e218.py --kernel rgm136`) and rgm211's through THE TREE GATE (`--kernel rgm211`); the hosts by their
  behaviour: twelve refusals, **each run inside a bubblewrap sandbox with no device node and each required to end before the device stage**;
  ET_DEVICES is not a gate on aifoundry3 (its one card); build/e218rgm/BUILD-e218.json.
- **The doubles** ([`fake_card_e218.py`](fake_card_e218.py)): E215 arm A's config, et-who, toy sampler and host, the host double in two forms
  (`--as rgm136`; `--as rgm211` with the walk fields), driven by MM1-v3.2's frozen forecasts; modes for every failure the tests need (a new config
  mode `thr70`, a threshold of 70 C).
- **The reducer** ([`reduce_e218.py`](reduce_e218.py)): each run by E206's readings, written in the frozen scorer's form (`{"experiment": "E218",
  "arms": {"A": {"smoke": {"runs"}, "points": {pid: {"runs"}}, "ties": {"runs"}}}}`; on rgm211-host runs the walk and the gate words; a process the
  gate refused kept as a run with its gate words and no check, so R0 reads it; s03 a smoke RUN at its place). **The collection**
  ([`collect_e218.py`](collect_e218.py)): COPY-BACK EXACT, the data directory `docs/reports/data/<day>-e218-blind-matmul-aifoundry3/` (or a gate
  stop's record), THE SCRUB of every form of the box's home and our login, and of another login's et-who holder lines, the reducer, step 6n's
  report, judgement and labels, SHA256SUMS; and `scrub-check`, the scrub on a private copy (step 8). **The harness** ([`check_e218.py`](check_e218.py),
  `harness-e218.json`, 43 files) and **the preflight** ([`preflight_e218.sh`](preflight_e218.sh)).
- **Step 6n** ([`desk/neverrun_card_e218.py`](desk/neverrun_card_e218.py)): the registration's scanner (`desk/neverrun_e218.py`, at its pinned
  sha256 `f9744c78...`, unchanged) over the lab at HEAD, the round's lane folders and MM1-v3.2's measured points, then THE JUDGEMENT (section 4,
  item 10) and the scorer's labels (`{"A": {"ran_before_points": [...]}}`).
- **The runbook** ([`rb/`](rb/)), from aifoundry2 through k6's drivers, unchanged: **step 0** (`s00_step0_e218.sh`); the window; step 2 (outside
  the kit's list); the look (k6's); the sync; the build; **step 6n**; **step 7, only once the rest has opened and within 30 minutes of 6n**; the dry
  pass **and the scrub check**; the session; the wait; the copy-back; the data directory; the scorer after the data commit (with step 6n's
  labels). **No post and no release** (waived). [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) is the card lane's brief, with THE ONE-LAB RULE and THE
  QUIET HOLD in its step table; [`DATA-README-FORM-e218.md`](DATA-README-FORM-e218.md) is the data README's form.

## 2. Card-minutes and the cap (registered: plan-e218.json)

48.0 card-minutes planned (107 runs at 26.60 s a run, E215 arm A's pace on this card, and the 2 smoke processes and the stop-path test 0.53 min);
no run starts once the card time passes 60 minutes; at 70 the session ends after the run in progress. A started run is cut only by a stop. The
registered subset if cut: the opening smoke, tie 1, pass 1 and tie 2: every Gt, Y and F point once, the G block not reached (42 runs, about 19.2
card-minutes). E218_BUDGET_S is the cap plus 5 minutes (4,500 s); the registered last start G + 1:30 binds the launch.

## 3. The order on the box

The card lane's full table, with the queue, the booking, THE ONE-LAB RULE, THE QUIET HOLD and the end of every path, is
[`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) section 2. The kit's steps (every step takes `A` and refuses a window written for another arm or
another runbook):

| step | file | what |
|---|---|---|
| 0 | `E218_SEALED=W/out/orch/sealed-e218.txt rb/s00_step0_e218.sh A` | read only, at the desk: S0 GitHub main (REPORTED); F1 MM1-v3.2's land `4e386f75` an ancestor of GitHub main; F1R the registration commit (subtree `deb6726f`) an ancestor; F2 the kit commit; S1 THE SEALED-FORECAST CHECK; S2 the note's commits (REPORTED); D0 no datum (folder-level glob); G1 the clone clean |
| 1 | `rb/s02_window_e218.sh A <day> <last start> <last end>` | today only; the window (G = the booking) in RB_OUT |
| 2 | `rb/s03_desk_e218.sh A` (outside the kit's list) | the window; the pull under the lab-git lock; the registration (subtree `deb6726f`) and the kit found by content, ancestors of HEAD, and MM1-v3.2's land `4e386f75`; the paths clean; HISTORY OK; both lists at their pins; the harness; the three self-checks; the registration's five checks; the scorer's two self-tests byte-identical and its forecasts print; the preflight; the desk tests' logs; nothing written; no datum in any ref (`:(glob)docs/reports/data/*e218*-aifoundry3/**`), gate stops and seal notes REPORTED |
| 4 | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | k6's look, unchanged (it writes the box-login file the scrub reads) |
| 5 | `rb/s07_sync_e218.sh A` | the rsync into the box's tree (`~/aifoundry`); HARNESS OK on the box |
| 6 | `rb/s08_build_e218.sh A start`, then `wait` | the detached build of both trees, NO-THIRD-BUILD, the record (rgm136 KERNEL OK, rgm211's tree KERNEL OK), the harness, the preflight and both self-checks on the box |
| 6n | `E218_ROUND_OUT=<the round's OUT> rb/s06n_neverrun_e218.sh A` | THE NEVER-RUN SEARCH, REPEATED, and its judgement; its NEVER-RUN-E218 line in RB_OUT |
| 7 | `rb/s09_reads_e218.sh A` | 6n's report under 30 minutes old, then THE REST RULE on the box, no card command; then k6's step 7 (TDP 0 W / 65 C / 600 MHz, et-who clean) |
| 8 | `rb/s10_dry_e218.sh A start`, then `wait` | the runner on the box with its doubles, no device (s01, the stop-path test, t01, y06b, y08a); then THE SCRUB CHECK on the dry pass's own records |
| 9 | `rb/s11_session_e218.sh A` | the last start, the cap before the last end, today's 6n report, the guard (k6's), THE REST RULE, THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and build, then `session_e218.sh` detached |
| 10 | `rb/s20_wait_e218.sh A` | the T0 the runbook launched; HUNG, K1, CRASHED and a gate stop are 16; ended (runner rc 0) 0; running 17 |
| 11 | `rb/s22_collect_e218.sh A` | one read-only copy back, COPY-BACK EXACT, the box's home in every form |
| 12 | `rb/s23_data_e218.sh A` | the data directory (or a gate stop's record), the scrub, the reducer, step 6n's report, judgement and labels, SHA256SUMS, the desk-path gate, the history check |
| 13 | `rb/s24_score_e218.sh A` | after the data commit only: the labels checked, then score_e218.py (registered, unchanged) on the committed data-e218.json with `--labels` |

## 4. The readings stated here before any datum (where E218.md leaves a choice to the kit)

1. **THE DIE LINE'S "HOTTEST SENSOR" IS A LATCH** (E218.md 6, E213's and E215 arm A's lines): the line trips on the shires' mean
   (`minshire[0]`) at or above 70 C, or on the latch (`minshire[2]`) only when it has risen during the session above the lowest value it read since
   the session's first sample and reads at or above 70 C (`e218_common.Stops`).
2. **The board line**: strictly above 70 W on 3 samples in a row that carry a board reading (a sample with none neither counts nor breaks the
   row). A trip touches the host's `--stop-file` at once (the host ends at its next launch boundary), never a kill; nothing further starts. The
   67.0 W planning line: no point's planning peak reaches it (the self-check reads plan-e218.json).
3. **The smoke, then the stop-path test; s03 in its place**: a rest read (30 s; the rest die: the median of the shires' mean over it; the die
   gate is formed from it), then one process of s01 ('rgm136 gemmL', `gemmL2x2x2` fp32), **E206's form, `--seconds 2 --budget 3.5`**, gated first;
   it must read rc 0, counted launches, its check of C (approx for fp32), **the counter's mean inside R0's absolute band, 200-4,000 cycles an op**,
   the board at least 2 W over the rest, and the host on card 0; any failure is the smoke gate (no run). Then the stop-path test (both lines trip a
   stand-in file in process; the start refused). **s03** ('rgm136 gemmLnc', `gemmLnc2x2x2` fp32, rgm211's host with rgm136's ELF) is the sequence's
   own entry at place 84 (after the third tie), read as **a run's frame around a smoke process**: the card-time rule and the window, the die gate (as
   a run's: at most 300 s), the holders, a 10 s rest whose last 5 s are the board's rest for the rise, then the smoke process and its checks, then
   a 4 s tail. **s03's own stop path**: a failure that is the family's alone (a GATE FAILED, a check of C wrong or missing, the walk check failed, a
   tensor error, a launch not ok, an exit not 0 but 124, the counter's mean outside 200-4,000, the board's rise short on a live sampler, or its not
   starting by the die gate) drops the G block - g01-g12 never start, NO DATA - and the session closes as usual (the G block is last, so nothing
   else is lost); a failure that is the session's (K1, HUNG, rc 124, the host not shown on card 0, the sampler not live after it) or any stop
   raised during it stops the session; the runs before it stand.
4. **THE IDENTITY GATE PER PROCESS BY THE POINT'S LOOP**: `ident_e218.FAMILY_KERNEL` maps both families to rgm136's ELF; the gate reads the
   process's `--kernel`: its `.text` always the pin, and either the whole ELF the pin or the loadable identity the pin (aifoundry3's gcc writes
   "(g1b306039a) 15.1.0" into `.comment`, a section the card never loads). An ELF whose `.text` is rgm211's is named so in the refusal.
5. **THE TREE GATE** (the build, and the runner's box check before anything opens): rgm211's ELF in build/e218rgm/rgm211 at kernel-e218.json's
   `rgm211_host` pins, the whole ELF or the loadable identity; it is never handed to a host as `--kernel` (no E218 process runs it).
6. **THE WALK CHECK**: 'rgm136 gemmLnc' walk mn, the tag on none; on every launch walk_ok true, and the check line's walk_launches_bad 0.
   'rgm136 gemmL' (rgm136's host) prints no walk.
7. **THE KERNEL STOPS** apply to the 'rgm136 gemmLnc' runs; an 'rgm136 gemmL' process keeps E206's rules (a TERM'd run flagged and the session
   going on; two failed processes in a row stop it).
8. **The start config** (read, nothing set): TDP 0 W, threshold 65 C, minion 600 MHz; anything else is 16 at step 7 and a gate stop in the
   session. **ET_DEVICES** is unset on every device process (an inherited value dropped, a table setting it refused; the guard refuses it set).
9. **The rest rule** (before step 7's read and step 9's launch): every session-log form of ours on the box, fix-e202's activity floor (build/e218
   and build/e218rgm excluded: E218's own builds and dry passes are no card session), energy.sh's folders and the model session's
   `~/claude/work/ee-*/` folders; at least 40 minutes since the latest (E215 arm A's ended 12:58:41 PST Thu 19 Nov 2026).
10. **Step 6n's judgement** (E218.md 4: "a registered point the repeated scan finds run is labelled 'ran before' and leaves every rule"): every
    registered point (52) whose literal verdict by its family's reading (F the token on any card; G and Gt the token on aifoundry3 card 0; Y the
    shape at its mask on aifoundry3 card 0) is not "never run" is labelled, **whatever the date**; every file the scanner's own rules find again for
    it is dated - a lab file by the commit that added it, a lane file by its modification time - against the freeze line (`4e386f75`'s committer
    time) and REPORTED beside the label; the dropped g07t and y03a are REPORTED. The labels are checked against points-e218.json before they are
    written and again at step 13 (LABELS-OK); the scorer takes them with `--labels`.
11. **Step 0's sealed check**: a seal is "registered" when its sha256 appears in `tools/claims-v3/sealed-e218/e218-freeze-lines.md` at the lab
    clone's HEAD; the record's non-comment lines must read `E218 <sha256> ...`; an unreadable line is NOT AS STATED; a comment line is never read.
12. **The scrub**: every form of the box's home step 11 reads (`$HOME`, the user database's home, the home's physical path), the longest first,
    becomes "~"; our box login becomes "<login>"; another login's et-who holder line keeps its node, pid and time, its login becomes
    "<another-login>" and its command is dropped; then no file may hold a `/home/` path, any of those homes, the login, or a holder line naming any
    login but "<login>" or "<another-login>". Step 8 runs the same scrub on the dry pass's own records before the session (SCRUB-CHECK).
13. **Datum checks are folder-level**: a datum is a commit on a `docs/reports/data` folder named `*e218*-aifoundry3` (git's glob magic), so a file
    whose name merely holds "e218" is not one (the runbook test's GS).

## 5. Found while kitting (REPORTED; for the verifier and the land lane)

- **Step 2's checks read a file outside `tools/`**: MM1-v3.2's layout module (`tools/matmul/mm1/v3.2/layout_v32.py`) loads E215's
  `tools/matmul/mm1/v3.2-terms/layout/controls-e215/v01_map.py` at import, which reads the mesh map `workloads/nocbench/analyze.py` from the lab;
  forecast_e218 and rules_e218 (through run_v32) import it. E215's step 2 did not list that path. The kit's step 2 now lists it, and E213 arm B's
  data folder (`docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1`, whose scores run_v32 reads), among E218's paths read clean (and
  check_history_e218.py's run paths); the runbook test's sparse scratch includes the mesh map (its first pass, without it, read forecast_e218 and
  rules_e218 failing at import - a desk-test gap, not a kit gap). v01_map.py writes its own `work/` file only when run as a script, never on import.
- **The registration's D1 and the drop's consequences** (the orchestrator's answer 1): g07 is scored without its twin, y03b alone; the kit's
  order, doubles and tests carry 52 points and never name g07t or y03a as points (the common module's self-check reads both absent).
- **The seal slot** (the orchestrator's answer 2): no `W/out/orch/sealed-e218.txt` existed at the kit; step 0 reads "sealed 0 of 0" until one is
  registered; the card lane books only after the orchestrator's `orch-hold-e218-seal`, if any, is released.
- **The look at aifoundry3 was NOT RUN** (section 8): the box's present build of E215 (build/e215rgm) is not E218's; E218 builds its own folder
  (build/e218rgm) on the card day, two starts a Pacific day at most.

## 6. Files

The kit: `run_e218.py`, `session_e218.sh`, `e218_common.py`, `e218_ident.py`, `ident_e218.py`, `ettelem_guard_e218.sh`, `build_e218.sh`,
`check_e218.py`, `harness-e218.json`, `preflight_e218.sh`, `fake_card_e218.py`, `reduce_e218.py`, `collect_e218.py`, `desk/neverrun_card_e218.py`;
the desk tests: `selftest_run_e218.py`, `desk/realpath_e218.py`, `desk/realpath_e218.sh`, `desk/realbytes_e218.py`, `desk/desktest_build_e218.sh`,
`rb/selftest_rb_e218.sh`; the runbook: `rb/rb_e218.sh`, `rb/s00_step0_e218.sh`, `rb/s02_window_e218.sh`, `rb/s03_desk_e218.sh` (step 2: outside
the kit's list, which it pins), `rb/s06n_neverrun_e218.sh`, `rb/s07_sync_e218.sh`, `rb/s08_build_e218.sh`, `rb/s09_reads_e218.sh`,
`rb/s10_dry_e218.sh`, `rb/s11_session_e218.sh`, `rb/s20_wait_e218.sh`, `rb/s22_collect_e218.sh`, `rb/s23_data_e218.sh`, `rb/s24_score_e218.sh`,
`rb/rest_rule_e218.sh`, `rb/check_history_e218.py`, `rb/list_steps_e218.sh`; the documents: this file, `CARD-LANE-BRIEF.md`,
`DATA-README-FORM-e218.md`; the logs under `logs/`; and `SHA256SUMS-e218-kit` (every kit file but itself and step 2; its own sha256 is step 2's
KITPIN). Nothing outside E218's folder.

## 7. Device commands

The session's only device commands are READs (dmcmd_audit_v2 GO on the session's files, no WRITE allowed): `ettelem config` and `ettelem sample
--seconds N --every-ms 100` through the guard (aifoundry3 with ET_DEVICES unset; anything else refused, exit 97; `sample --reset-ms`, the
statistics reset, refused), and the hosts' own runtime (rgm136's and rgm211's), each under a plain `timeout 10`. Every runtime creation also sends
the ops node's abort to every submission queue of every card the device layer enumerates (harmless on a card held alone; aifoundry3 has one card).
No set, no reset, no statistics reset, no governor, TDP, threshold, clock or voltage change, no PMIC command, no PCIe recovery, no driver reload,
no power cycle, no firmware change: none is in the kit.

## 8. What the desk cannot show

- The card itself: its meter, its clock, its temperatures, a launch that does not finish on silicon; every number here is the doubles'.
- The hosts' device path (the runtime's own opening of a card) past the refusals: the doubles and stand-ins stand in for it; the real-path test
  runs everything else.
- aifoundry3's own build of build/e218rgm (its gcc's `.comment` form is read by the loadable identity, as E213 and E215 arm A's builds there read):
  the build's own run is step 6 on the card day.
- The box's present state (its boot, et-who, the reader's sha256 on the box): the look was NOT RUN; steps 4, 5 and 7 read them on the day.
- aifoundry3's own disk for step 6n (NOT SEARCHED, as registered).
- The model session's sealed forecasts: none was posted for E218 when this kit was written; step 0 reads them on the day.

## 9. Labels

Every figure here is **registered** (E218.md), a **desk check of code** (the tests above, on the doubles and stand-ins), or a **desk read** of
committed records (the real-bytes test, step 6n's scan). Nothing here is measured, blind, held out or post hoc.

## Compute

kit-e218's runs (Thu 19 Nov 2026, PST), on aifoundry2's CPU through the round's slots (`W/slot.sh`, nice 10), one slot job at a time, single-threaded (OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, MKL_NUM_THREADS and NUMEXPR_NUM_THREADS 1), builds at -j2; `/usr/bin/python3` 3.12.3 (numpy and scipy only through the registration's own checks, MM1-v3.2's modules and the never-run scanner's data loader). The development runs: step 6n's tool on the round's folders (21:14:40-21:14:51), a runner-test subset of 5 cases (to 21:26), the real-path test (to 21:31:18), the real-bytes test (to 21:34:24), the build test (to 21:35:49), the runbook test twice (21:49:06-21:53:11, 29 of 31: its sparse scratch lacked workloads/nocbench/analyze.py, section 5; 21:53:21-22:12:15, 31 of 31), the runner test's first full pass (22:12:32-22:36:37, 71 of 72: CT's E215 calibration, --rule-s 8.5, fell after E218's third start, since E218's opening smoke is one process, not three; set to 4.5 s), each log in the lane's folder. The final runs, each its own slot job and one at a time, the quiet-desk flag absent, all but two also inside `W/nodev.sh` (the dry listing and step 6n's tool ran in the slot alone: neither runs a host, the runner or a stand-in session, and the dry listing's stand-in ssh was called 0 times): the runbook test (22:37:03-22:55:48), the real-bytes test (22:55:48-22:56:01), the build test (22:56:01-22:56:09), the real-path test (22:56:09-22:57:53), the dry listing (22:57:53), step 6n's tool on the round's folders (22:57:53-22:58:05), the quick set (22:58:05-23:00:16), the runner test (23:00:16-23:24:18). One scratch path, in the build test's log, is masked as `<scratch>` (that log's first line says so); no other log held one. No card, no simulator, no box.

SPDX-License-Identifier: Apache-2.0
