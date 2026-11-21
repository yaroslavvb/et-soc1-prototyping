# E222's run kit: the MM1-v3.3 candidates' blind day on aifoundry3 card 0 from aifoundry2, in E218's kit form with E220's newer parts - one runner, the opening smoke s01 and the stop-path test, the two families both on rgm136's ELF, the G block last with its own smoke s03 in its place, every process gated by its family's ELF and under a plain `timeout 10` sized so that no frozen GEMM's check of C is cut off, never killed; the never-run search repeated right before the first card command by session records on this card, family R exempt by its name and read RAN by a positive control; the scrub checked on the dry pass's records before the session (Q236; kitted, not run)

*Fri 20 Nov 2026 (week 47), from 14:20 PST, on aifoundry2, desk only (Q236, lane `kit-e222`). No card was claimed or opened: aifoundry2 has a
card, so every desk test that runs a built host, the runner, a stand-in session or a stand-in reader ran inside the round's slots and its sandbox
(`W/slot.sh bash W/nodev.sh`: no /dev/et*, an empty /run/lock), single-threaded, one slot job at a time, every committed log from a run that
started and ended with the quiet-desk flag absent (two earlier runs did not: section 5). No device command was sent, no simulator was run,
nothing was posted. **One read-only look at aifoundry3** (15:05:22 PST, `book.sh show` read just before: aifoundry1 and aifoundry2 booked
by E220's card lanes, aifoundry3 free; one bounded ssh call, reads only: section 5). **New files only, all under `tools/claims-v3/e222/`**,
on top of E222's registration ([`E222.md`](E222.md): reg-e222's local commit `d8659859` on GitHub main
`2f0ab9cd`, applied here with `git am`, the same hash; its `tools/claims-v3/e222` subtree `f8e6ec56...`; `SHA256SUMS-e222-registration`
`de67150b...`, 30 entries), which this kit changes in no byte. **No E222 datum exists. Nothing here adds or re-chooses a point or changes a
forecast, a band, a rule, a threshold, the order, the card time, the cap, a stop or the scorer.** Where E222.md leaves a reading to the kit, the
reading is stated in section 4 before any datum. E218's landed kit (`5582edfc`, which ran E218 FULL on this card at 03:11-03:56 PST today, 107 of
107 runs, data `b445b0f5`) is the authority every behaviour below is checked against; the kit is its code, renamed for E222, with the changes this
file names, and E220's kit (`2f0ab9cd`, GitHub main when this lane cloned it) supplies the judgement of step 6n's form, the no-kill audit, the
timeout sizing and the scorer check.*

**His words** (Mon 16 Nov 2026, received at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul and "FME" the
tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and
number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other
operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation."

**The orchestrator's answer the kit follows** (`W/out/orch/e222-answers.txt`, item 1, 14:21 PST Fri 20 Nov 2026): reg-e222's never-run report
read family R's four points "never run" only because the exemption returns True; **every later never-run judgement - the kit's step 6n at the
booking included - prints R's four as "RAN (exempt by family name: same-card repeats, REPORTED only)" and the 66 others as never ran**, and a
positive control of the scanner (the exemption lifted, all four must read RAN from E218's committed data folder on this card) shows the scan sees
this card's sessions. Step 6n's judgement does both (section 4, item 10); the kit's runbook test reads it on a stand-in lab with and without
E218's data folder.

## Results first (desk checks of code and desk reads of committed records; nothing is measured on a card)

| desk test (each run for real, its log under `logs/`) | what it shows | result |
|---|---|---|
| **the runner** (`selftest_run_e222.py`: the doubles, the real runner, the real sandboxing) | every registered behaviour of the session on the doubles: the smoke s01 against R0's band and the stop-path test (G1, R1-R7X), the start config gate (C1-C9, RTC), the holders and the identity read (H1-H7, S2, RT, RT2), the sampler (S1-S4, DF), every stop line (B1, BN, D1-D3), the die gate and the card-time rule (DG, CT), **HUNG and K1, never killed** (C6, HG, K0, K1), the operator's STOP (OP, SF, SS, SSG, S0), the identity gate per process and THE KERNEL STOPS (GS, GRY, GR, CW, TE, WR, TL, WG), **s03's own stop path** (LG3, LW3, LC3 drop the G block; LK3, LT3, LD3 stop the session), **the order, the G block last** (OR: 121 entries; LN, LN2), the reducer and the frozen scorer on the runner's output end to end (E2-ok, E2-W), the dry-only refusals (RF) | SELFTEST-RUN-E222 72 of 72 PASS |
| **the real path** (`desk/realpath_e222.sh`: the real build, the real runner, the real guard; stand-ins only for the card's tools, et-who, the lock, the sampler and the host's device; inside W/nodev.sh under the hostname aifoundry3) | RA1 the whole real path through s01, the stop-path test and three runs (t01, wn07t, wp04b); **RA1G the G block on the real path** (the third tie, s03 at place 99, wn01 and wn05 on rgm211's real host with rgm136's real ELF); RA3 a host hung past its TERM, never killed; RA6/RA6T a changed .text refused by the kernel gate and by the tree gate; RA2, RA4, RA5, RA7-RA12 the refusals and stops before and during a run (the lock held, a device process of ours, the reader off its pin, ET_DEVICES, another login, card 1, the sampler dying, a build record without its builder); RA13 the STOP file; RA14 the identity gate per process on real ELFs; RA15 the walk check on a G run; RA16 s03's own stop path on the real path | REALPATH-E222 19 of 19 PASS |
| **the real bytes** (`desk/realbytes_e222.py`: every host-output parser fed committed bytes from this card) | **RB-E218A/RB-E218AR** (E218's whole session on aifoundry3 card 0 through the parsers and the reducer; s03 at its place 84), RB-E215A/RB-E215AR (E215 arm A), RB-E213A/RB-E213AR (E213 arm A), RB-E211/R, RB-E207/R, RB-SPLICE, RB-CFG, RB-ID, RB-SIM, RB-SMOKE, **RB-SCRUB** (committed sessions rebuilt with the box's home in them and scrubbed back to the committed bytes), RB-HOLDERS | REALBYTES-E222 17 of 17 PASS |
| **the build** (`desk/desktest_build_e222.sh`: this desk's real toolchain) | the real build under aifoundry3's hostname: rgm136 KERNEL OK, rgm211's tree KERNEL OK, the hosts' twelve refusals before the device stage; a changed source refused; aifoundry3's `.comment` form by the loadable identity; a changed byte refused; the wrong kernel each way; another box refused; the runner's box check; the guard | DESKTEST-BUILD-E222 9 of 9 PASS |
| **the runbook** (`rb/selftest_rb_e222.sh`: a fake ssh and rsync, a stand-in aifoundry3 booted 2026-11-17 16:46:07, the real build) | the dry listing; the window rule; the lab-git lock; step 2 at every pin, **P1W/P1X: step 2 writes nothing in the lab and sees a rewrite with the same bytes**; the history check; the datum check (DA, GS); **S0, step 0's eight lines with the posted freeze line and the sealed-forecast check**; **OB, the stand-in box booted after the firmware read**; the look; the sync; NO-THIRD-BUILD; the real build; **NR, step 6n's judgement** (R's four RAN by name, the labels by session records, `card-e222` never opened) and **NRP, THE POSITIVE CONTROL failing without E218's data folder (16)**; **R7, step 7 only with a fresh report and once the rest has opened**, R7f a 70 C threshold refused; **D/DS, the scrub check before the session**; HG, SD, LS, NS, step 9's refusals; LA, step 9 launching the real session_e222.sh (stopping at its box check); W10, step 10's readings; C/C2, the collection and a gate stop's record; CD, the data directory and the frozen scorer with step 6n's labels; Z, nothing left running | SELFTEST-RB-E222 33 of 33 PASS |
| **the dry listing** (`rb/list_steps_e222.sh A`) | every step of the day in order, nothing run, no box call | dry listing: 15 steps listed, 0 exited non-zero, 0 box calls |
| **the preflight** (`preflight_e222.sh`) | dmcmd_audit_v2 on the session's files, no WRITE allowed | dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none) |
| **step 6n's tool on the round's real folders** (`desk/neverrun_card_e222.py run`) | the registration's scanner over the lab at HEAD, the round's lane folders and MM1-v3.2's measured points, then THE JUDGEMENT (session records on this card; R exempt by name, printed RAN) and THE POSITIVE CONTROL (R's exemption lifted: 4 of 4 must read RAN) | NEVER-RUN-E222 arm A: 66 of 66 registered non-R points never ran on aifoundry3 card 0 by session records (dated note 1's reading; scan d796c6d50809, 106928 files, lab d8659859b925); ran before, labelled: none; family R: ry01a RAN, ry01b RAN, rg01 RAN, rg01t RAN (exempt by family name: same-card repeats, REPORTED only); the positive control (R's exemption lifted, the same scan): 4 of 4 RAN; the literal reading (REPORTED, not a label): 47 of 70 never ran |
| **the no-kill audit** (`desk/nokill_e222.py`) | every line of the kit and k6's runbook library that could send SIGKILL, classed by its target | NOKILL-E222: 0 lines that could send SIGKILL toward a device process (want 0); 12 lines that send SIGKILL to the desk's own call tree only (k6's rb_run.py kill_tree(), TERM then KILL past a call's bound or on a login link: the desk's ssh, rsync, git or desk Python on aifoundry2, where E222 runs no device process); 4 lines state the rule; read: 175 files under tools/claims-v3/e222 (the kit and the registration) and the q141k runbook folder (k6's library and rb_run.py) |
| **the timeout sizing** (`desk/timeout_e222.py --check`) | every E222 process class S under the plain timeout 10, from committed bytes of this card and the frozen forecasts | TIMEOUT-E222 CHECK PASS (every E222 process class S under the plain timeout 10 s; the class-S bound 9.6 s per process, E220's form 10.2 s REPORTED; the longest frozen GEMM 0.063219 s) |
| **the quick set** (`logs/checks-e222.txt`) | the registration's list and its four checks in their `--check` form, the scorer's two self-tests byte-identical (in a scratch folder), the kit's self-checks, the harness re-made (CHECK PASS) and HARNESS OK, the sized timeout, the no-kill audit, the preflight, nothing written, every kit file parsed in memory, no bytecode | QUICK-SET-E222 PASS: 0 not as stated (2026-11-20 16:35:57 PST) |
| **the read-only look at aifoundry3** (`book.sh show` just before; one bounded ssh call, reads only) | the box the kit rests on: its boot, its reader, its tools, E218's session end, its holders | 15:05:22 PST: booted 2026-11-17 16:46:07; the reader at the pin 16037641...; Python 3.12.3; et-who, cmake, the toolchain and bwrap present; no build/e222*; E218's session end 03:56:36 PST; 0 holders |

## What E222 changes against E218's kit, and why (each before any datum)

1. **E222's registration**: 70 points (T 32, L3b 10, Y3 10, G3 7, G3t 7, R 4), its order (plan-e222.json > order > runs: 122 entries), its
   frozen forecasts (forecast-e222.csv, MM1-v3.2's rows drive the doubles), its card-time rule (no run after **70** card-minutes) and cap
   (**80**), its plan's words (the common module's self-check reads them). E218's registration forms the module read (points-e218.json's
   `sequence_blocks`, its `smoke` and `tie` lists) are not E222's: the kit reads E222's plan for the order and **E218's registered points-e218.json
   for the tie t01 and the smokes s01, s03 alone** (E222.md 3 names them E218's), at its registered sha256 `9a5f252f...`, each checked against
   points-e222.json's extra rows (token, format).
2. **The order and the G block.** s01; t01; pass 1 (55: every non-gemmLnc point once); t01; pass 2 (40: the L3b, Y3, T-L3, T-Y2 and R-Y points,
   pass 1's order reversed); t01; then **the G block LAST**: s03 at the kit's place 99 (`099-G-smoke-s03`; the registered place 100, kept as
   `reg_n`), every gemmLnc point once by PP32 ascending (wn01 wn05 wn04 wn03 wn02 wn06 wn07 k01 k02 k03 k04 rg01 k06 k05 k07: G-pass1), then the G3
   points again in reverse (k07 k05 k06 k04 k03 k02 k01: G-pass2): 120 runs and 2 smoke processes (section 4, item 14).
3. **The families are E218's two**, unchanged: 'rgm136 gemmL' (rgm136's host and ELF: T-L3, T-Y2, T-G2t, L3b, Y3, G3t, R-Y, R-Gt, the tie and
   s01) and 'rgm136 gemmLnc' (rgm211's host with rgm136's ELF, walk mn: R's rg01, T-G2 wn01-wn07, G3 k01-k07, and s03). Every point is fp32 random
   (one tile, `kinds/tiles/fp32/randn.bin`).
4. **Step 0 reads E222's freeze lines**: F0 THE POSTED FREEZE LINE (the round's record `W/out/orch/q236-frozen-posts.txt` names FROZEN.txt
   `172ed079` and the three forecast files; each at HEAD has the posted sha256; FROZEN.txt's bytes read when `E222_FROZEN` names it), F1
   MM1-v3.2's land `4e386f75`, **F1C the three candidates' lands** (`badf08fa`, `911651ee`, `2a509f5a`: the code the forecasts read in place),
   F1R the registration commit (subtree `f8e6ec56`), F2 the kit, S1 the sealed-forecast check, D0, G1: "STEP0-E222 arm A: 8 of 8 as stated".
5. **Step 2 never runs the scorer's `--selftest-*` modes** (score_e222.py's `main()` writes `selftest-standins.json` and `selftest-real.json`
   into its own folder, registered files): `rb/scorer_check_e222.py` (E220's form) imports the frozen scorer unchanged and calls its two
   functions with output paths in RB_OUT, then compares each with the committed file byte for byte. The registration's checks are its four
   `--check` forms (forecast_e222 by one combined candidate call, rules_e222 with `--work` in RB_OUT, plan_e222, desk/kernel_e222), each run with
   `TMPDIR` in RB_OUT (models_e222's candidate staging folder is a `tempfile` folder). E222's scorer has no `--forecasts` print. Step 2 also reads
   the sized timeout (`desk/timeout_e222.py --check`) and the no-kill audit (`desk/nokill_e222.py`), and its no-write read covers E218's and
   E220's folders and E220's dated notes beside E222's and MM1's (the scorer reads E220's frozen scorer and inputs at their pins; the scanner
   E220's note 1).
6. **Step 6n's judgement is E220's dated note 1's** (the registration's reading, built into E222's scanner): a point counts as RUN on aifoundry3
   card 0 only by a session record on that card; **family R is exempt by its family name only, printed RAN, and checked by THE POSITIVE CONTROL**
   (16, no card command, if it fails); the labels in the frozen scorer's form `{"ran_before_points": {"A": [...]}}` (score_e220.read_a's).
7. **Step 13 calls the frozen scorer in its registered form** (`score_e222.py --a <data> --a-tag A [--labels <file>] --out <dir>`) and leaves the
   cross-card rule to the scores lane (CX reads "PENDING E220 DATA" here; E222.md 7: CX is scored only once E220's data are committed and
   verified).
8. **The plain timeout 10, sized** (`desk/timeout_e222.py`, E220's tool for E222's one card): every E222 process is class S (MM1-v3.2's frozen
   seconds a GEMM at most 0.063 s, wn04t), and the bound one process can reach - its own pre and post (at most 1.188 s on this card's committed
   processes, E218's g11 at KB 48, E222's deepest K) plus the budget and one launch - is 9.6 s, under the plain timeout 10: no frozen GEMM's check
   of C is cut off (E218's R0 lesson, f04's run 77, a 1.31 s GEMM). E220's own form, which adds the largest pre, launch and post of different
   processes, reads 10.2 s on this card and is REPORTED beside (section 4, item 15). The runner's `timeout 10` is unchanged.
9. **The stand-in box boots after the firmware read** (the lesson of E213 arm B's day): the runbook test's stand-in aifoundry3 reports the real
   box's boot, 2026-11-17 16:46:07 (this lane's look), after E82's firmware read of 31 Oct 2026; its case OB reads the look FREE with no identity
   line (k6's identity-by-continuity rule is aifoundry1's alone; no step of E222's gates on the boot).

## The round's lessons, and where each is met

1. **A real-path desk test**, stand-ins for every device tool, et-who, the lock, the sampler and the host, inside W/nodev.sh, through the smoke,
   the stop path and at least two points, one of them G: `desk/realpath_e222.sh` (RA1: s01, the stop-path test, t01, wn07t, wp04b; **RA1G: the
   third tie, s03 in its place, wn01 and wn05 on rgm211's real host with rgm136's real ELF**; RA3 a host hung past its TERM; RA13 the STOP file).
2. **Stand-in boots after the firmware read**: the runbook test's stand-in aifoundry3 boots at the real box's 2026-11-17 16:46:07 (after E82's
   read); case OB.
3. **Every host-output parser fed real committed bytes from aifoundry3 card 0 (E218, E215 arm A, E213 arm A)**: `desk/realbytes_e222.py`
   (RB-E218A, RB-E218AR: E218's whole session through the parsers and the reducer, equal to its committed data-e218.json, s03 at its place 84;
   RB-E215A, RB-E215AR, RB-E213A, RB-E213AR), with E211's and E207's beside them; E218's session also in RB-SMOKE and RB-SCRUB.
4. **No SIGKILL toward any device process**: a plain `timeout 10` on every device process; a host alive past its TERM is HUNG, reported and left
   (the runner test's C6 and HG, the real path's RA3); the sampler is stopped by SIGTERM only; **`desk/nokill_e222.py` (E220's widened audit)
   classes every line that could send SIGKILL by its target: 0 toward a device process**, 12 (three in each of the q141k runbook folder's four
   versions of k6's runner `rb_run.py`, all in its `kill_tree()`) toward the desk's own call tree only (TERM, then KILL, to the desk's own
   ssh, rsync, git or desk Python past a call's bound or on a login link: a process on aifoundry2, never one on a box and never a device
   process).
5. **The plain timeout 10 sized so that no frozen GEMM's check of C is cut off**: `desk/timeout_e222.py` (lesson 8 above; its log
   `logs/timeouts-e222.txt`), read by step 2.
6. **Step 7's config read only once the rest has opened**: `rb/s09_reads_e222.sh` reads the 6n report's age (at most 30 minutes) and THE REST
   RULE on the box first, no card command, and refuses (10) while either fails (the runbook test's R7); R7f a threshold read at 70 C stops the day
   (16).
7. **THE ONE-LAB RULE in the step table**, with undesk and uncollect on every stop path: CARD-LANE-BRIEF.md section 2, rows 0-2 inside the desk
   span, rows 11-12 inside the collect span, row E on every path; the dry listing prints the same notes.
8. **Step 2 never rewriting a registered file in LAB**: its registration checks are their `--check` forms (rebuilt in memory and compared, scratch
   in RB_OUT), the scorer's self-tests write into RB_OUT only (`rb/scorer_check_e222.py`), the history check refuses any change to a registered
   file, and **step 2 reads at its end that no file under E222's folder, tools/matmul/mm1, E218's and E220's folders, E220's notes or the seal
   note's folder is newer than its start marker and that E222's paths are clean again** (the runbook test's P1W and P1X: a rewrite with the same
   bytes, of forecast-e222.csv and of MM1-v3.2's constants, is seen).
9. **The sealed-forecast check at step 0** (`W/out/orch/sealed-e222.txt` and `tools/claims-v3/sealed-e222/e222-freeze-lines.md`):
   `rb/s00_step0_e222.sh` S1 (the runbook test's S0 b, c: a registered seal, an unregistered one); a later seal is a comment line in the record
   and a NEW note (`e222-freeze-lines-2.md`), which step 0 never reads.
10. **dmcmd_audit_v2 GO**: `preflight_e222.sh` on the session's files, no WRITE allowed (`logs/dmcmd-audit-e222.txt`), read again by step 2, by
    step 6 on the box and by the runner before anything opens.
11. **The collection's scrub tested on records that carry a home path**: RB-SCRUB rebuilds E218's, E215 arm A's, E213 arm A's, E211's and E207's
    committed sessions into the box's own bytes (the home in them) and scrubs them back to the committed bytes; step 8 ends with THE SCRUB CHECK
    on the dry pass's own records before any card time (runbook test D and DS); RB-HOLDERS masks another login's et-who lines.
12. **The G block last**: the registered order, checked by the common module's self-check (the G block after the third tie, s03 first, every
    gemmLnc point there and only there, nothing after), the runner test's OR, LN and LN2, and the real path's RA1G.
13. **Family R's exemption from the never-run judgement by family name only**: step 6n's tool reads R by the registration's `exempt` reading
    and refuses (14) a report in which R is not exactly the four exempt by name or any other point reads `exempt`; R's four are never labels
    (check-labels refuses one), printed RAN and checked by THE POSITIVE CONTROL; the runbook test's NR (4 of 4 RAN; k01, q01a, q01b labelled by
    session records; wn01's desk copy not) and NRP (the control failing without E218's data folder: 16).
14. **The card lane named exactly `card-e222`**: the registration's scanner never opens a lane or data folder whose name holds `e222`; the
    runbook test's NR puts a record of b01's token in a stand-in `card-e222` folder and reads it never opened; CARD-LANE-BRIEF.md names the lane.

## 1. The kit

- **The runner** ([`run_e222.py`](run_e222.py), [`session_e222.sh`](session_e222.sh), [`e222_common.py`](e222_common.py),
  [`e222_ident.py`](e222_ident.py), [`ident_e222.py`](ident_e222.py)): one session, E218's runner with E222's registration read by the common
  module. **THE TWO FAMILIES BY THE POINT'S LOOP** (points-e222.json's "loop" field, never the arm token): 'rgm136 gemmL' and 'rgm136 gemmLnc'.
  **THE IDENTITY GATE PER PROCESS** (before every process `ident_e222.gate(family, elf)`: its `.text` always the pin `61315bf6...`, and the whole
  ELF `aace138c...` or the loadable identity `649d4079...`; the words recorded with the process; a GATE FAILED at a run starts no process and stops
  the session; at s03 it drops the G block). **THE WALK CHECK** on every rgm211-host process (walk mn). **THE KERNEL STOPS** (a 'rgm136 gemmLnc'
  run with a check of C wrong, a tensor error, the walk check failed, a launch timeout (K1 or rc 124), a launch not ok or an exit not 0 stops the
  session). The opening smoke s01 against **R0's absolute band, 200-4,000 cycles an op** (the counter's mean, the median over counted launches),
  then the stop-path test, then the registered sequence. No run after 70 card-minutes, cap 80. The die gate min(60, the session's rest die + 4)
  C, at most 300 s. Before anything opens: the host name (aifoundry3), ET_DEVICES unset, build/e222rgm's record today's BUILT by build_e222.sh on
  this box (both gates' lines), rgm136's ELF through THE KERNEL GATE again and rgm211's tree through THE TREE GATE, both hosts at the sha256 the
  build recorded, the reader at its pin `16037641...` (this lane's look read the box's reader at it), the tile at its sha256, the harness (HARNESS
  OK) and the preflight (dmcmd_audit_v2 GO). Then the card's lock (`flock -n`, held to the end), the holders (counts only), THE FIRST CARD COMMAND
  `ettelem config` through [`ettelem_guard_e222.sh`](ettelem_guard_e222.sh) under a plain `timeout 10` (the start config TDP 0 W / 65 C / 600 MHz
  and the card's identity; the card time counts from it), ONE sampler (10 Hz) whose every line feeds THE STOP LINES as it arrives, THE IDENTITY
  READ, the smoke and then the stop-path test, the registered order, the closing config, "session end", MANIFEST.sha256 last. Nothing is set.
  Every start first reads the operator's STOP file; never two samplers at once.
- **No SIGKILL toward a device process** (the orchestrator's standing ruling): every device process is under a plain `timeout 10`; the runner
  waits for it with a bound and, past `timeout`'s TERM by HANG_GRACE_S (4 s), writes "<time> HUNG: ..." in the session log, touches the stop file,
  starts nothing further, sends no further card command (no closing config read), closes the session and LEAVES the process (exit 8). et-who,
  the harness check and the preflight are waited on with a bound and left past it. The sampler is stopped by SIGTERM only. The build runs under a
  plain `timeout`.
- **The build** ([`build_e222.sh`](build_e222.sh), [`check_e222.py`](check_e222.py)): E136's rgm136 unchanged into **build/e222rgm/rgm136** and
  E211's rgm211 into **build/e222rgm/rgm211** (new folders of ours) on aifoundry3 only (any other box refused before anything is built); rgm136's
  ELF through THE KERNEL GATE (`check_e222.py --kernel rgm136`) and rgm211's through THE TREE GATE (`--kernel rgm211`); the hosts by their
  behaviour: twelve refusals, **each run inside a bubblewrap sandbox with no device node and each required to end before the device stage**;
  ET_DEVICES is not a gate on aifoundry3 (its one card); build/e222rgm/BUILD-e222.json.
- **The doubles** ([`fake_card_e222.py`](fake_card_e222.py)): E218's config, et-who, toy sampler and host, the host double in two forms (`--as
  rgm136`; `--as rgm211` with the walk fields), driven by MM1-v3.2's frozen forecasts (forecast-e222.csv; the smokes keep the toy 900 / 800 cycles
  an op and 20 W, as in E218's kit); modes for every failure the tests need.
- **The reducer** ([`reduce_e222.py`](reduce_e222.py)): E218's, each run by E206's readings, written in the frozen scorer's form (`{"experiment":
  "E222", "arms": {"A": {"smoke": {"runs"}, "points": {pid: {"runs"}}, "ties": {"runs"}}}}`, which score_e220.read_a reads; on rgm211-host runs
  the walk and the gate words; a process the gate refused kept as a run with its gate words and no check, so R0 reads it; s03 a smoke RUN at its
  place). **The collection** ([`collect_e222.py`](collect_e222.py)): COPY-BACK EXACT, the data directory
  `docs/reports/data/<day>-e222-blind-matmul-aifoundry3/` (or a gate stop's record), THE SCRUB of every form of the box's home and our login, and
  of another login's et-who holder lines, the reducer, step 6n's report, judgement and labels, SHA256SUMS; and `scrub-check`, the scrub on a private
  copy (step 8). **The harness** ([`check_e222.py`](check_e222.py), `harness-e222.json`, 41 files: the box files, E222's plan, points, kernel
  record and forecast CSV, E218's points-e218.json, E206's gate files, the device-command checker and its table, the tile manifest and tile, the
  two builds' twenty sources) and **the preflight** ([`preflight_e222.sh`](preflight_e222.sh)).
- **Step 6n** ([`desk/neverrun_card_e222.py`](desk/neverrun_card_e222.py)): the registration's scanner (`desk/neverrun_e222.py`, at its registered
  sha256 `e3c0b391...`, unchanged; its `scan` and its `report`) over the lab at HEAD, the round's lane folders and MM1-v3.2's measured points,
  then THE JUDGEMENT and THE POSITIVE CONTROL (section 4, item 10) and the scorer's labels (`{"ran_before_points": {"A": [...]}}`).
- **The desk checks the card lane reads**: [`desk/timeout_e222.py`](desk/timeout_e222.py) (the sizing, `desk/timeouts-e222.json`),
  [`desk/nokill_e222.py`](desk/nokill_e222.py) (the audit), [`rb/scorer_check_e222.py`](rb/scorer_check_e222.py) (the scorer's self-tests in RB_OUT).
- **The runbook** ([`rb/`](rb/)), from aifoundry2 through k6's drivers, unchanged: **step 0** (`s00_step0_e222.sh`); the window; step 2 (outside
  the kit's list); the look (k6's); the sync; the build; **step 6n**; **step 7, only once the rest has opened and within 30 minutes of 6n**; the dry
  pass **and the scrub check**; the session; the wait; the copy-back; the data directory; the scorer after the data commit (with step 6n's
  labels). **No post and no release** (waived). [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) is the card lane's brief, with THE ONE-LAB RULE and THE
  QUIET HOLD in its step table; [`DATA-README-FORM-e222.md`](DATA-README-FORM-e222.md) is the data README's form.

## 2. Card-minutes and the cap (registered: plan-e222.json)

50.7 card-minutes planned (120 runs and 2 smoke processes at 25.35 s a run, E218's pace on this card); no run starts once the card time passes
70 minutes; at 80 the session ends after the run in progress. A started run is cut only by a stop. The registered subset if cut: the opening smoke,
tie 1, pass 1 and tie 2: every non-gemmLnc point once, the G block not reached (57 runs, about 24.1 card-minutes). E222_BUDGET_S is the cap plus 5
minutes (5,100 s); the registered last start G + 1:30 binds the launch.

## 3. The order on the box

The card lane's full table, with the queue, the booking, THE ONE-LAB RULE, THE QUIET HOLD and the end of every path, is
[`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) section 2. The kit's steps (every step takes `A` and refuses a window written for another arm or
another runbook):

| step | file | what |
|---|---|---|
| 0 | `E222_SEALED=W/out/orch/sealed-e222.txt E222_FROZEN_POSTS=W/out/orch/q236-frozen-posts.txt E222_FROZEN=W/out/reg-e222/FROZEN.txt rb/s00_step0_e222.sh A` | read only, at the desk: S0 GitHub main (REPORTED); F0 the posted freeze line; F1 MM1-v3.2's land `4e386f75` and F1C the candidates' lands ancestors of GitHub main; F1R the registration commit (subtree `f8e6ec56`) an ancestor; F2 the kit commit; S1 THE SEALED-FORECAST CHECK; S2 the note's commits (REPORTED); D0 no datum (folder-level glob); G1 the clone clean |
| 1 | `rb/s02_window_e222.sh A <day> <last start> <last end>` | today only; the window (G = the booking) in RB_OUT |
| 2 | `rb/s03_desk_e222.sh A` (outside the kit's list) | the window; the pull under the lab-git lock; the registration (subtree `f8e6ec56`) and the kit found by content, ancestors of HEAD, and MM1-v3.2's land and the candidates' lands; the paths clean; HISTORY OK; both lists at their pins; the harness; the three self-checks; the registration's four checks; the scorer's two self-tests in RB_OUT, byte-identical; the sized timeout; the no-kill audit; the preflight; the desk tests' logs; nothing written; no datum in any ref (`:(glob)docs/reports/data/*e222*-aifoundry3/**`), gate stops and seal notes REPORTED |
| 4 | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | k6's look, unchanged (it writes the box-login file the scrub reads) |
| 5 | `rb/s07_sync_e222.sh A` | the rsync into the box's tree (`~/aifoundry`); HARNESS OK on the box |
| 6 | `rb/s08_build_e222.sh A start`, then `wait` | the detached build of both trees, NO-THIRD-BUILD, the record (rgm136 KERNEL OK, rgm211's tree KERNEL OK), the harness, the preflight and both self-checks on the box |
| 6n | `E222_ROUND_OUT=<the round's OUT> rb/s06n_neverrun_e222.sh A` | THE NEVER-RUN SEARCH, REPEATED, its judgement (session records on this card; family R exempt by name, printed RAN) and THE POSITIVE CONTROL (16 if it fails); its NEVER-RUN-E222 line in RB_OUT |
| 7 | `rb/s09_reads_e222.sh A` | 6n's report under 30 minutes old, then THE REST RULE on the box, no card command; then k6's step 7 (TDP 0 W / 65 C / 600 MHz, et-who clean) |
| 8 | `rb/s10_dry_e222.sh A start`, then `wait` | the runner on the box with its doubles, no device (s01, the stop-path test, t01, wn07t, wp04b); then THE SCRUB CHECK on the dry pass's own records |
| 9 | `rb/s11_session_e222.sh A` | the last start, the cap before the last end, today's 6n report, the guard (k6's), THE REST RULE, THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and build, then `session_e222.sh` detached |
| 10 | `rb/s20_wait_e222.sh A` | the T0 the runbook launched; HUNG, K1, CRASHED and a gate stop are 16; ended (runner rc 0) 0; running 17 |
| 11 | `rb/s22_collect_e222.sh A` | one read-only copy back, COPY-BACK EXACT, the box's home in every form |
| 12 | `rb/s23_data_e222.sh A` | the data directory (or a gate stop's record), the scrub, the reducer, step 6n's report, judgement and labels, SHA256SUMS, the desk-path gate, the history check |
| 13 | `rb/s24_score_e222.sh A` | after the data commit only: the labels checked, then `score_e222.py --a <data-e222.json> --a-tag A --labels <labels-e222.json> --out RB_OUT/scores-A` (registered, unchanged); CX PENDING E220 DATA (the scores lane's) |

## 4. The readings stated here before any datum (where E222.md leaves a choice to the kit)

1. **THE DIE LINE'S "HOTTEST SENSOR" IS A LATCH** (E222.md 6, E218's line): the line trips on the shires' mean (`minshire[0]`) at or above 70 C,
   or on the latch (`minshire[2]`) only when it has risen during the session above the lowest value it read since the session's first sample and
   reads at or above 70 C (`e222_common.Stops`).
2. **The board line**: strictly above 70 W on 3 samples in a row that carry a board reading (a sample with none neither counts nor breaks the
   row). A trip touches the host's `--stop-file` at once (the host ends at its next launch boundary), never a kill; nothing further starts. The
   67.0 W drop line: no point's planning peak reaches it (the self-check reads plan-e222.json: the highest PP32 55.54 W at k07).
3. **The smoke, then the stop-path test; s03 in its place** (E218's form, E222.md 3 naming E218's smokes): a rest read (30 s; the rest die: the
   median of the shires' mean over it; the die gate is formed from it), then one process of s01 ('rgm136 gemmL', `gemmL2x2x2` fp32), **E206's
   form, `--seconds 2 --budget 3.5`**, gated first; it must read rc 0, counted launches, its check of C (approx for fp32), **the counter's mean
   inside R0's absolute band, 200-4,000 cycles an op**, the board at least 2 W over the rest, and the host on card 0; any failure is the smoke gate
   (no run). Then the stop-path test (both lines trip a stand-in file in process; the start refused). **s03** ('rgm136 gemmLnc', `gemmLnc2x2x2`
   fp32, rgm211's host with rgm136's ELF) is the sequence's own entry at the kit's place 99 (after the third tie), read as **a run's frame around a
   smoke process**: the card-time rule and the window, the die gate (as a run's: at most 300 s), the holders, a 10 s rest whose last 5 s are the
   board's rest for the rise, then the smoke process and its checks, then a 4 s tail. **s03's own stop path** (E218.md 3's, E213's Amendment A1
   form; E222.md names E218's smoke and E218's kit as the form, and its frozen scorer's reader, score_e220.read_a, reads a failed s03 as the G
   block's NO DATA and not an R0 failure while no gemmLnc point ran): a failure that is the family's alone (a GATE FAILED, a check of C wrong or
   missing, the walk check failed, a tensor error, a launch not ok, an exit not 0 but 124, the counter's mean outside 200-4,000, the board's rise
   short on a live sampler, or its not starting by the die gate) drops the G block - rg01, wn01-wn07 and k01-k07 never start, NO DATA - and the
   session closes as usual (the G block is last, so nothing else is lost); a failure that is the session's (K1, HUNG, rc 124, the host not shown on
   card 0, the sampler not live after it) or any stop raised during it stops the session; the runs before it stand.
4. **THE IDENTITY GATE PER PROCESS BY THE POINT'S LOOP**: `ident_e222.FAMILY_KERNEL` maps both families to rgm136's ELF; the gate reads the
   process's `--kernel`: its `.text` always the pin, and either the whole ELF the pin or the loadable identity the pin (aifoundry3's gcc writes
   "(g1b306039a) 15.1.0" into `.comment`, a section the card never loads). An ELF whose `.text` is rgm211's is named so in the refusal.
5. **THE TREE GATE** (the build, and the runner's box check before anything opens): rgm211's ELF in build/e222rgm/rgm211 at kernel-e222.json's
   `rgm211_host` pins, the whole ELF or the loadable identity; it is never handed to a host as `--kernel` (no E222 process runs it).
6. **THE WALK CHECK**: 'rgm136 gemmLnc' walk mn, the tag on none; on every launch walk_ok true, and the check line's walk_launches_bad 0.
   'rgm136 gemmL' (rgm136's host) prints no walk.
7. **THE KERNEL STOPS** apply to the 'rgm136 gemmLnc' runs; an 'rgm136 gemmL' process keeps E206's rules (a TERM'd run flagged and the session
   going on; two failed processes in a row stop it).
8. **The start config** (read, nothing set): TDP 0 W, threshold 65 C, minion 600 MHz; anything else is 16 at step 7 and a gate stop in the
   session. **ET_DEVICES** is unset on every device process (an inherited value dropped, a table setting it refused; the guard refuses it set).
9. **The rest rule** (before step 7's read and step 9's launch): every session-log form of ours on the box, fix-e202's activity floor (build/e222
   and build/e222rgm excluded: E222's own builds and dry passes are no card session), energy.sh's folders and the model session's
   `~/claude/work/ee-*/` folders; at least 40 minutes since the latest (E218's ended 03:56:36 PST Fri 20 Nov 2026).
10. **Step 6n's judgement** (E222.md 4: "a point found run then is labelled 'ran before' and leaves every rule, said", by the registration's
    reading, E220's dated note 1: session records on this card only): every registered point outside family R whose verdict the registration's
    report reads not never run - a session record on aifoundry3 card 0 names it (a committed data folder naming the card, a session's own file in
    a lane folder naming the card, never a dry pass), or an MM1-v3.2 measured point holds it there, by its family's reading (token; Y3 token and
    masks) - is labelled, **whatever the date**; desk copies in folders naming no card never count, the literal reading REPORTED beside. **Family R
    (ry01a, ry01b, rg01, rg01t) is exempt by its family name only** (the report's `exempt` reading; the tool refuses, 14, a report in which R is
    not exactly those four or another point reads `exempt`): never a label (check-labels refuses one), printed "RAN (exempt by family name:
    same-card repeats, REPORTED only)" (the orchestrator's answer 1). **THE POSITIVE CONTROL** (the same answer): R's exemption lifted, each R point
    read by the registered scanner's own Never class on the same scan (the R-Y pair by configuration, rg01 and rg01t by token) must read RAN (E218
    ran them here); if not, the scan cannot see this card's sessions: "POSITIVE CONTROL FAILED", the tool's 15 (which k6's runner reports
    as 14: step 6n reads the tool's printed line), step 6n's 16, no card command that day, the orchestrator told. The labels are checked
    against points-e222.json before they are written and again at step 13 (LABELS-OK); the scorer takes them with `--labels`.
11. **Step 0's sealed check**: a seal is "registered" when its sha256 appears in `tools/claims-v3/sealed-e222/e222-freeze-lines.md` at the lab
    clone's HEAD; the record's non-comment lines must read `E222 <sha256> ...`; an unreadable line is NOT AS STATED; a comment line is never read.
12. **The scrub**: every form of the box's home step 11 reads (`$HOME`, the user database's home, the home's physical path), the longest first,
    becomes "~"; our box login becomes "<login>"; another login's et-who holder line keeps its node, pid and time, its login becomes
    "<another-login>" and its command is dropped; then no file may hold a `/home/` path, any of those homes, the login, or a holder line naming any
    login but "<login>" or "<another-login>". Step 8 runs the same scrub on the dry pass's own records before the session (SCRUB-CHECK).
13. **Datum checks are folder-level**: a datum is a commit on a `docs/reports/data` folder named `*e222*-aifoundry3` (git's glob magic), so a file
    whose name merely holds "e222" is not one (the runbook test's GS).
14. **The kit's places**: the kit's sequence is the registered order without its first entry (the opening smoke s01, the runner's own), numbered
    1..121 (the registered place less one; the registered place kept as `reg_n` and checked by the self-check); the registered blocks keep their
    order, renamed for the run folders (`G block` -> `G-pass1`, `G block reversed (G3 only)` -> `G-pass2`, s03's `smoke` -> `G-smoke`).
15. **The timeout's bound is read per process**: a process's length is its own pre (to the first launch), its own device phase (at most the 7.5 s
    budget and one launch) and its own post (the check of C and the closing), so the class-S bound adds the largest pre + post of ONE committed
    process on this card (1.188 s, E218's g11 at KB 48) to the budget and the largest launch wall (each rounded up, 0.1 s more): 9.6 s, under the
    plain timeout 10 (`desk/timeout_e222.py`). E220's tool adds the largest pre and the largest post of different processes (E218's g11t 0.882 s,
    E215 arm A's a046 0.713 s): 10.2 s on this card, REPORTED beside, never the rule. E222's shapes sit inside the committed ranges that drive pre
    and post: the deepest K is KB 48 (wn01, wn01t), at which E218's g11 and g11t ran 7.4-7.7 s; the longest committed process that exited 0 on
    this card ran 7.83 s (E218's y07b); every E222 GEMM is at most 0.063 s, where E218's f04 (cut at 10.1 s) was 1.31 s.

## 5. Found while kitting (REPORTED; for the verifier and the land lane)

- **The read-only look at aifoundry3** (15:05:22 PST Fri 20 Nov 2026; `book.sh show` just before: aifoundry1 `card-e220a`, aifoundry2
  `card-e220b`, aifoundry3 free; no claim file for it; one `timeout 60 ssh -o BatchMode=yes aifoundry3 bash -s` call with a read-only script):
  booted 2026-11-17 16:46:07 (after E82's firmware read: no rule of E222's reads the boot); the reader `build/ettelem/ettelem` at the pin
  `16037641...`; Python 3.12.3; et-who, cmake, /opt/et's toolchain and bwrap present; the card's lock file present; no `build/e222*` yet;
  E218's session ended 03:56:36 PST (`session end (T0 1795173084)`); et-who 0 holder lines; 319 GB free.
- **E222.md's words the port had to keep straight**: five quotations the rename had attributed to E222.md were E218.md's - four in the kit's
  code (the family smoke's note in `e222_common.py`, the measured side's form in `reduce_e222.py`, s03's entry in `run_e222.py`, the second freeze
  line in `rb/s00_step0_e222.sh`) and one in E218's KIT text this file replaces: each now quotes E222.md's own words or names E218.md (the lane's
  check: every quotation of E222.md in the kit's files found in E222.md, 14 of 14 once this file was written). The runner's own words "(its own
  stop path, E222.md 3)" are a reference, read as section 4 item 3 states: E222.md 3 names s03 E218's smoke, and its stop path is E218.md 3's.
- **Step 0's F0 and the round's record of the post**: F0 first dropped every line of `q236-frozen-posts.txt` that begins with `#` as a comment,
  but the record's post lines begin with the post's own id (`#1.30.1.2.1.1.1 2026-11-20 13:51:12 PST: ...`, as every round's record of its
  freeze posts does): on the real record F0 would have read no post line and stopped the day. Found by reading the real record against the code
  before the final runbook test; a comment is now `#` and a blank (or nothing), a post line is read (the runbook test's S0 a-j, on a stand-in
  record of the same form).
- **Step 6n and k6's exit codes**: k6's runner (`rb_run.py` v3.1, unchanged) reports every non-zero exit of a desk call as 14, so step 6n
  first read the judgement tool's own 15 in vain and stopped with 14 ("run this step again") where a failed POSITIVE CONTROL must stop the day
  with 16; the final runbook test's NRP case caught it (15:59 PST). Step 6n now reads the tool's printed "POSITIVE CONTROL FAILED: ..." line,
  which the tool prints only when the control fails, on any non-zero exit; the runbook test ran again on the corrected bytes.
- **The tie and the smokes are E218's records**: points-e222.json holds no host arguments for t01, s01 and s03 (only their tokens, E222.md 3:
  "E218's"); the kit reads them from E218's registered points-e218.json at its sha256 and checks their tokens and formats against E222's extra
  rows (the self-check); the harness syncs points-e218.json to the box.
- **The scorer writes registered files in its self-test modes**: `score_e222.py --selftest-standins` and `--selftest-real` write
  `selftest-standins.json` and `selftest-real.json` into E222's folder. Step 2 never runs those modes (`rb/scorer_check_e222.py`, E220's form).
- **The scorer's labels' form** is score_e220.read_a's (`{"ran_before_points": {"A": [...]}}`), not E218's scorer's (`{"A":
  {"ran_before_points": [...]}}`): step 6n's tool writes it and checks it.
- **The cross-card rule** is not step 13's: E222.md 7 scores CX only once E220's data are committed and verified (a verify lane's HOLDS); the
  scores lane passes `--e220-a`, `--e220-b` and `--e220-verified`.
- **The seal slot** (E222.md 0): no `W/out/orch/sealed-e222.txt` existed when this kit was written; step 0 reads "sealed 0 of 0" until one is
  registered (the record absent: none posted); reg-e222's result asks that the seal slot (`tools/claims-v3/sealed-e222/` and
  `W/out/orch/sealed-e222.txt`) be registered before `card-e222` books, which is the orchestrator's to do (no hold on aifoundry3 stood at 15:05
  PST).
- **Two incidents of this lane's own (THE QUIET DESK)**: the lane read `quiet-desk-aifoundry2` before each desk run's start only, and twice a
  flag was raised while a run of the runner or the stand-ins was under way, inside `W/slot.sh bash W/nodev.sh` (one slot job, nice 10,
  single-threaded): (1) a development run of the runner test (started 14:51 PST, before any flag) went on after `card-e220b` raised the flag at
  14:55:42 PST for E220 arm B's session on aifoundry2's card, to 15:16:43 PST (21 minutes; the 1-minute load read 0.37-0.60); (2) the first final
  runbook test (started 15:43:21 PST, before any flag) went on after the orchestrator raised it at 15:53:25 PST for the model session's E221 S3
  on aifoundry2 card 0, to 16:00:41 PST (7 minutes). Since then every desk test runs under the lane's guard, which reads the flag every 2 s and
  stops the test (SIGTERM to its own process group and to each of its descendants, never SIGKILL; no device node in the sandbox) the moment
  the flag appears (its own test: a stand-in flag mid-run stops a 30 s job in 4 s, a descendant in its own session too); a test
  stopped so is run again once the flag is gone, and the committed logs come from runs that started and ended with the flag absent (the lane's
  finals record names each). The lanes behind both sessions may weigh the two windows.

## 6. Files

The kit: `run_e222.py`, `session_e222.sh`, `e222_common.py`, `e222_ident.py`, `ident_e222.py`, `ettelem_guard_e222.sh`, `build_e222.sh`,
`check_e222.py`, `harness-e222.json`, `preflight_e222.sh`, `fake_card_e222.py`, `reduce_e222.py`, `collect_e222.py`, `desk/neverrun_card_e222.py`,
`desk/timeout_e222.py` and `desk/timeouts-e222.json`, `desk/nokill_e222.py`, `rb/scorer_check_e222.py`; the desk tests: `selftest_run_e222.py`,
`desk/realpath_e222.py`, `desk/realpath_e222.sh`, `desk/realbytes_e222.py`, `desk/desktest_build_e222.sh`, `rb/selftest_rb_e222.sh`; the runbook:
`rb/rb_e222.sh`, `rb/s00_step0_e222.sh`, `rb/s02_window_e222.sh`, `rb/s03_desk_e222.sh` (step 2: outside the kit's list, which it pins),
`rb/s06n_neverrun_e222.sh`, `rb/s07_sync_e222.sh`, `rb/s08_build_e222.sh`, `rb/s09_reads_e222.sh`, `rb/s10_dry_e222.sh`, `rb/s11_session_e222.sh`,
`rb/s20_wait_e222.sh`, `rb/s22_collect_e222.sh`, `rb/s23_data_e222.sh`, `rb/s24_score_e222.sh`, `rb/rest_rule_e222.sh`, `rb/check_history_e222.py`,
`rb/list_steps_e222.sh`; the documents: this file, `CARD-LANE-BRIEF.md`, `DATA-README-FORM-e222.md`; the logs under `logs/`; and
`SHA256SUMS-e222-kit` (every kit file but itself and step 2; its own sha256 is step 2's KITPIN): 56 new files in all (44 of code and
documents, 11 logs and the list). Nothing outside E222's folder.

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
- aifoundry3's own build of build/e222rgm (its gcc's `.comment` form is read by the loadable identity, as E213, E215 arm A's and E218's builds
  there read): the build's own run is step 6 on the card day.
- The box's state on the card day (et-who, a later session's end): the look read it once at 15:05:22 PST; steps 4, 5 and 7 read it on the day.
- aifoundry3's own disk for step 6n (NOT SEARCHED, as registered).
- The model session's sealed forecasts: none was posted for E222 when this kit was written; step 0 reads them on the day.

## 9. Labels

Every figure here is **registered** (E222.md), a **desk check of code** (the tests above, on the doubles and stand-ins), or a **desk read** of
committed records (the real-bytes test, the timeout sizing, step 6n's scan) or of the box (the look). Nothing here is measured, blind, held out or
post hoc.

## Compute

Desk only, on aifoundry2 (/usr/bin/python3 3.12.3, single-threaded, each final test its own job in the round's slots at nice 10, one at a time, those that run a built host, the runner or a stand-in inside W/nodev.sh, the quiet-desk flag absent): the real-bytes test 0.3 min, the build test 0.1 min, the real-path test 1.8 min, the dry listing 0.0 min, step 6n's tool on the round's folders 0.3 min, the no-kill audit 0.0 min, the timeout sizing check 0.0 min, the quick set 2.0 min, the runbook test 17.3 min, the runner test 25.7 min; 47 minutes in all. One read-only ssh call to aifoundry3 (under a second). No card time, no simulator, no device command.

SPDX-License-Identifier: Apache-2.0
