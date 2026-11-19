# E215's run kit: MM1-v3.1's blind matmul day on two cards from aifoundry2 - arm A on aifoundry3 card 0 in E213 arm A's kit form, arm B on aifoundry1 card 1 in E213 arm B's form as its Amendments A2 (fwgate's identity gate on the box's present boot) and A3 (every gemmLnc point last) left it: one runner per arm, the opening smoke and the stop-path test, every family but rgm136's gemmL with its own family smoke and stop path, the gemmLnc block last with its smoke in its place, every process gated by its family's ELF, every run under a plain `timeout 10` and never killed; the never-run search repeated right before the first card command and judged by each point's own reading; the scrub checked on the dry pass's records before the session (Q224; kitted, not run)

*Thu 19 Nov 2026 (week 47), from 00:06 PST, on aifoundry2, desk only (Q224, lane `kit-e215`). No card was claimed or opened: aifoundry2 has a
card, so every desk test that runs a built host, the runner, a stand-in session or a stand-in reader ran inside the round's slots and its sandbox
(`W/slot.sh bash W/nodev.sh`: no /dev/et*, an empty /run/lock), single-threaded, one slot job at a time. No device command was sent, no simulator
was run, nothing was posted. Two boxes were reached, each once, only while no lane booked them and no claim stood: **one read-only look at
aifoundry3 and aifoundry1 at 00:52:27 PST** (`logs/look-boxes.txt`: both booted 16:46 PST Tue 17 Nov 2026; the readers at the kit's pins,
aifoundry3 `16037641...`, aifoundry1 `8008f96f...`; aifoundry1's device layer carries ET_DEVICES, aifoundry3's does not; E213's builds still on
both, aifoundry1's rgm136 and rgm211 at their WHOLE-ELF pins `aace138c...` and `00402801...`, aifoundry3's by the loadable identity; fwgate.py on
aifoundry1 at its pin `4d529a57...`; et-who: no holder on either; no device process of ours). Nothing was written on either box and no device was
opened there. **New files only, all under `tools/claims-v3/e215/`** (and, by fix-e215 below, one dated note on E215.md's text beside it,
under `tools/claims-v3/e215-notes/`), on top of E215's registration ([`E215.md`](E215.md), reg-e215's, a local
commit at GitHub main `2c971828`: its `tools/claims-v3/e215` subtree `e89e512f...`, `SHA256SUMS-e215-registration` `99439f8f...`, 35 entries),
which this kit changes in no byte. **No E215 datum exists. Nothing here changes a point, a forecast, a band, a rule, a threshold, the order, the
card time, the cap, a stop or the scorer.** Where E215.md leaves a reading to the kit, the reading is stated in section 4 before any datum. E213's
landed kit (`6efdb002`, which ran E213 arm A FULL on aifoundry3, data `c69a12aa`) and its Amendments A2 and A3 (`tools/claims-v3/e213-a2/`,
`e213-a3/`, landed `8b675547`, under which E213 arm B ran on aifoundry1 card 1 to its registered board stop at run 079, data `b0c727c5`) are the
authorities every behaviour below is checked against; the kit is their code, renamed for E215, with the changes this file names.*

**His words** (Mon 16 Nov 2026, received at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul and "FME" the
tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and
number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other
operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation."

## fix-e215: verify-e215's findings answered before the land (dated Thu 19 Nov 2026 (week 47), before any E215 datum)

*Round Q224's lane `fix-e215`, from 04:45 PST, on aifoundry2, desk only, in a fresh scratch clone of GitHub main `2c971828` with reg-e215's and
kit-e215's land patches applied (the registration as a local commit, unchanged; the kit's files untracked on it, as kit-e215 tested and committed
them). verify-e215 (04:44 PST) read the registration and the kit as HOLDS WITH FIXES: one medium finding in the kit, three low findings and a nit
in the registration's text, and four infos. **Nothing here changes a point, a forecast, a band, a rule, a threshold, the order, the card time, the
cap, a stop or the scorer, and the registration changes in no byte.** No card, box, simulator or device command; nothing posted.*

- **Finding 1 (medium), answered in the kit: step 2 rewrote a registered file in the lab clone.** `rb/s03_desk_e215.sh` ran
  `score_e215.py --forecasts`, whose main() prints the forecasts and also writes them over the registered `forecasts-e215.txt` (the same bytes
  today, so git status stayed clean), and then compared the print with the file the same call had just rewritten: E213's lesson broken, and the
  comparison vacuous. Now:
  - **`rb/forecasts_print_e215.py`** (new, standard library): it loads the registered scorer unchanged, by its path, and calls the scorer's own
    `forecasts_print()`, which checks the scorer's pinned inputs (exit 4 if a byte changed) and prints; it writes nothing (no file, no bytecode).
    Its print equals the scorer's own `--forecasts` print and the committed file byte for byte, and a changed pinned file gives exit 4 (fix-e215's
    test of the helper, in a copy).
  - **Step 2** runs it into RB_OUT, reads the committed bytes into RB_OUT (`git show HEAD:tools/claims-v3/e215/forecasts-e215.txt`) and requires
    the print equal to those bytes (`forecasts-committed`) and to the file in the lab clone (`forecasts`).
  - **Step 2 reads that its checks wrote nothing:** a marker in RB_OUT right after the pull; at the end, no file under `tools/claims-v3/e215`,
    `tools/matmul/mm1/v3.1/out/e215` (arm A's frozen forecasts) or `tools/claims-v3/sealed-e215` (when it exists) newer than the marker
    (`wrote-in-lab`: a rewrite with the same bytes, which git status cannot see, is seen here), and E215's paths clean again, untracked files
    included (`status-after`). Either is a 16.
  - **The runbook test** gains **P1W** (P1 and P1B wrote nothing in the scratch repository's work tree, and each arm's print equals the committed
    bytes) and **P1X** (a stand-in print that runs the scorer's own `--forecasts` mode: step 2 refuses arm A naming `wrote-in-lab` and
    forecasts-e215.txt, whose bytes stay the same): SELFTEST-RB-E215 33 of 33 PASS.
  - `SHA256SUMS-e215-kit` (now 62 entries: the helper added) and step 2's KITPIN made again (kit-e215's commit form); the runbook test, the
    dry listings and the quick set re-run, their logs replacing kit-e215's.
- **Findings 2-4 (low) and the nit (5), answered by one dated note outside E215's registered folder:**
  [`../e215-notes/E215.md.dated-note-1.md`](../e215-notes/E215.md.dated-note-1.md), with its re-derivation `metric_e215_note1.py`: arm B's post
  hoc T1-T3 read TOO FEW (their P(PASS) 0, not the printed 0.687 / 0.396 / 0.201); "arm A's on no card" holds for arm A's literal and L points,
  family S standing by its own reading; the bands' basis (forecast / measured - 1) and the rules' metric (|measured / forecast - 1|) named, the
  bands standing; arm B's freeze line for step 6n is the registration commit's committer time (section 4 item 12). The registration's subtree
  `e89e512f...` and its list `99439f8f...` stay as verify-e215 checked them.
- **Info, for the readiness lane's go lines:** arm B's step 4 will make the second firmware read on aifoundry1's present boot (section 5, its first
  item): fwgate allows it (E213 arm B's read on this boot ended EQUAL) and the owner's rulings allow reads; the go lines name it, or aifoundry1 is
  rebooted first. **Info, no change:** the head-to-head against MM1-v3 is nearly powerless (2-8%) and H4/H5 are TOO FEW by construction, as E215.md
  states before the data.
- **Not re-run by fix-e215** (none of the files they run changed): the runner test (95 of 95), the real-path test (34 of 34), the real-bytes test
  (19 of 19), the build test (11 of 11) and the A2 form's test (39 of 39); their logs stand as kit-e215 committed them, and verify-e215 re-ran
  each of them.

## Results first (desk checks of code and desk reads of committed records; nothing is measured on a card)

| check | result | log |
|---|---|---|
| **the runner on the doubles** (`selftest_run_e215.py`): both arms; the short path with the card's identity gate and read; THE OPENING SMOKE and THEN the stop-path test; every config gate, holder, sampler fault and stop line of E213's per arm; THE FOUR FAMILIES (K4, K4B: every entry of rgm211's host in pass 1 and the gemmLnc block's smoke and pass 1); the identity gate refusing the session's smoke (GS), a run (GR) and 'rgm211 gemmL''s run (G211), through the reducer and the frozen scorer (R0 FAIL); THE FAMILY SMOKES' OWN STOP PATHS: s04 (GF4, WF4, CF4 drop the family and the session goes on, through the reducer and the frozen scorer: R0 PASS, the drop flagged, a027 NO DATA; KF4, TF4, SF4 stop the session), s02 (GF2, WS) and arm B's s15 (WSB: rgm211's ELF's first process on card 1, b009-b012 dropped); THE GEMMLNC BLOCK with its smoke in its place (LN, LNB; its gate refused (LG3, LGB, on the whole order: every other point scored, R0 PASS, the drop flagged), its walk (LW3), K1 at it (LK3: the session stops), its die gate (LD3: never started, its family dropped)); THE KERNEL STOPS (CW, TL, TE, TEB); HUNG with nothing killed (C6, HG, HGB, DF); the STOP file and SIGTERM; a crash; the card-time rule; **each arm's whole registered order** (OR: 119 runs and s03; ORB: 71 and s14), every argv and gate the registered; **END TO END**, both arms in one data file through the frozen scorer, both groups and the pooled rules (E2) | **SELFTEST-RUN-E215 95 of 95 PASS** | logs/selftest-run-e215.txt |
| **the REAL path** (`desk/realpath_e215.py`, `desk/realpath_e215.sh`): run_e215.py WITHOUT --dry under each arm's hostname and a private PID namespace, stand-ins for the reader behind the REAL guard, et-who, the two hosts, the lock and the nodes; **the two REAL kernel ELFs from the REAL build_e215.sh**: arm A RA0-RA17 (the build; the whole path; the four families with the gemmLnc smoke in its place (RA1K); the lock; a host hung past its TERM left to end by itself; the reader's pin; a changed .text; ET_DEVICES three ways; other logins; the other card three ways; runtime lines; the sampler; the build record; the STOP file; RA14 rgm136's real ELF over rgm211's refused by a027's gate; RA15 the walk; RA16 s04's own stop path; **RA17 the gemmLnc block on the real path, its smoke good and its walk dropping the family**); arm B RB0-RB13 (the build stopping at the ET_DEVICES gate on this desk's device layer; the whole path at ET_DEVICES=1 with card 1's identity and **s15 on rgm211's real ELF at its whole ELF**; **RB1K b009-b012 on rgm211's real ELF and s14, b013 on rgm136's**, each at its whole ELF; card 0 three ways; ET_DEVICES missing; card 0's holders; the sampler; runtime lines of both cards; RB9 rgm136's whole ELF; a host hung past its TERM; RB11 the gate per process; **RB12 rgm211 at its whole ELF on arm B** (an identity-equal variant refused by the box check; rgm136's ELF over rgm211's refused by b011's gate); **RB13 the gemmLnc block**) | **REALPATH-E215 34 of 34 PASS (REALPATH-E215 arm A: 19 of 19 PASS; REALPATH-E215 arm B: 15 of 15 PASS)** | logs/realpath-e215.txt |
| **the parsers on real committed bytes** (`desk/realbytes_e215.py`): **E213 arm A's committed outputs on aifoundry3** (all four families, the walk read by each run's own family) and its runs through the reducer field for field; **E213 arm B's and E214's on card 1** (runtime lines dropped and counted), E213 arm B's runs through the reducer; and, as E213's kit read them, E207's and E211's on aifoundry3 and E206 arm B's and E212's on card 1; runtime lines spliced at every byte offset; the config line; the card's identity forms per arm; rgm211's host's real simulator bytes by family; the smoke's reading on 17 committed smoke processes; **THE COLLECTION'S SCRUB ON REAL RECORDS THAT CARRY THE BOX'S HOME** (E213 arm A's, E213 arm B's, E211's, E207's and E206 arm B's sessions turned back into the box's own bytes and scrubbed back to the committed bytes exactly; three forms of the home; a home not given refused); another login's et-who holder lines masked | **REALBYTES-E215 19 of 19 PASS** | logs/realbytes-e215.txt |
| **the build on this desk's real toolchain** (`desk/desktest_build_e215.sh`; riscv gcc "() 15.1.0", g++ 13.3.0, cmake 3.28.3): both kernels through their gates on each arm's box (**arm B both at the whole ELF**), the hosts' twelve refusals in the build's sandbox, **arm B's ET_DEVICES gate refusing this desk's stock device layer**, changed sources, aifoundry3's `.comment` form (identity OK, **--whole FAILED for rgm136 and for rgm211**), a changed `.rodata` or `.text` byte, the wrong kernel each way and all four families both ways, another box, the runner's box check on each arm, the guard on both boxes | **DESKTEST-BUILD-E215 11 of 11 PASS** | logs/desktest-build-e215.txt |
| **the runbook** (`rb/selftest_rb_e215.sh`: a fake ssh and rsync, stand-in aifoundry3 and aifoundry1 boxes, the real builds): the dry listings; the window rule per arm; the lab-git lock; step 2 at every pin (P1B with arm B's choice check, about ten minutes); **fix-e215's P1W: P1 and P1B wrote nothing in the scratch's work tree, each arm's forecasts print equal to the committed bytes; P1X: a rewrite of forecasts-e215.txt with the same bytes refused by step 2 (`wrote-in-lab`)**; the history check and a shadow; an arm's datum refusing step 2 for that arm only; a gate stop reported; E175's tile named *e215* is no datum; **STEP 0** (no record, a registered seal, an unregistered seal NOT AS STATED, arm B with GitHub main before the registration NOT AS STATED, an arm's datum); the look on each box; **OB: a stand-in aifoundry1 booted after E82's firmware read stopping k6's look** (why arm B's step 4 is the A2 form's); ours_live; the sync per arm; a login link; a hang; NO-THIRD-BUILD; the real build on aifoundry3 and the ET_DEVICES gate on aifoundry1; **step 6n on stand-in lane folders** (a043's token dated before arm A's freeze line labelled with a044 and their cases; b014's after arm B's REPORTED; E215's own card lanes subtracted); step 7 refusing without a fresh 6n report and before the rest, then each arm's read; the dry pass and THE SCRUB CHECK per arm, and the scrub check refusing another home's path before the session; THE HUNG MARKER; the same-day rule; the last start; the real session stopping at its box check; step 10's readings; the copy-back, a byte changed after the manifest; each arm's data directory with step 6n's labels and the frozen scorer on it (re-run by fix-e215, 05:03-05:49 PST, 2,795 s) | **SELFTEST-RB-E215 33 of 33 PASS** | logs/selftest-rb-e215.txt |
| **arm B's A2 form** (`a2/desk/selftest_a2_e215.sh`, E213's A2 desk test renamed: fwgate's stand-ins, stand-in boxes BOOTED AFTER E82's firmware read but in the continuity case): NEEDS-READ then EQUAL (the stand-in CLI once, both locks held, the record, the attempt log, the copy, the scrub), CONTINUITY the same day, the guard and the launch, DIFFERENT, UNREADABLE, a cut-off SENT, a busy lock, a busy et-who, a missing lock file (each 16, never a second read), both cards held for the whole wait (17, nothing read), the guard with no EQUAL of this boot, a stale EQUAL of an earlier boot or day, THE REST RULE before the read, the pins on the box (fwgate.py changed) and at the desk (the helper changed), arm A refused, step 12's addition (fwgate/ and the evidence, or the evidence left out and said), the evidence of the one call and its failing (never a gate) | **SELFTEST-A2-E215 39 of 39 PASS** | a2/logs/selftest-a2-e215.txt |
| the dry listings, every step of each arm with stand-ins (arm B's steps 4, 9 and 12 through the A2 form's files) | **arm A: dry listing: 15 steps listed, 0 exited non-zero, 0 box calls; arm B: dry listing: 15 steps listed, 0 exited non-zero, 0 box calls; the A2 form's own listing: dry listing (A2, arm B): 15 steps listed, 0 exited non-zero, 0 box calls** | logs/dry-listing-e215-A.txt, logs/dry-listing-e215-B.txt, a2/logs/dry-listing-a2-B.txt |
| **the registration's checks and the kit's self-checks, as step 2 runs them** (`/usr/bin/python3` 3.12.3, single-threaded): the registration's list (35 entries) and subtree; points candidates and --check, forecast_e215, rules, plan, desk/kernel --check; the scorer's stand-in self-test and real-bytes self-test byte-identical to the committed files, **its forecasts print through rb/forecasts_print_e215.py byte-identical to the committed bytes, and nothing written in the clone by it (fix-e215)**; e215_common, e215_ident, ident_e215 --check; the harness re-made and HARNESS OK; the preflight; the A2 form's pins; every kit file parsed; the kill scan (desk/choose_e215b --check ran in the runbook test's P1B step-2 run; re-run by fix-e215) | **QUICK-SET-E215 PASS: 0 not as stated (2026-11-19 05:53:45 PST)** | logs/checks-e215.txt |
| **dmcmd_audit_v2** on the session's files (`preflight_e215.sh`) and on the A2 form's fwgate files | **dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none); the A2 form: dmcmd_audit: GO (1 send site(s), 0 disallowed; allow-list: none)** | logs/dmcmd-audit-e215.txt, a2/logs/dmcmd-audit-a2.txt |
| **step 6n's tool on the round's real folders** (the scratch clone at its HEAD as the lab, the round's OUT as the lanes; the registration's scanner unchanged; `34d0852f` in arm B's line is the registration as the scratch clone's local commit: on the day step 6n names the landed registration commit, found by content) | **NEVER-RUN-E215 arm A: 60 of 60 scored points never ran on any card (scan f3653773587b, 81285 files); ran before the freeze line (MM1-v3.1's land 2c971828), labelled: none; ran after it (REPORTED, kept): none; NEVER-RUN-E215 arm B: 30 of 30 scored points never ran on aifoundry1 card 1 (scan 32e8e6f676ed, 81285 files); ran before the freeze line (the registration commit 34d0852f), labelled: none; ran after it (REPORTED, kept): none; scan: 81285 files read, 442 distinct tokens, 0 over 400 MB, 0 unreadable, 0 git dirs not read; 2026-11-19 01:17:30 PST - 2026-11-19 01:17:41 PST; scan-e215.json f3653773587bf7d1ca8a4d5f2c3b73108d80209df4c9ce7945fd7a6d3bc8517c** | logs/neverrun-desk-e215.txt |
| the read-only look at the two boxes (00:52:27 PST, no lane booking either, no claim) | **aifoundry3 and aifoundry1 booted 16:46 PST Tue 17 Nov 2026; the readers at the pins; aifoundry1's E213 builds at the whole-ELF pins (rgm136 aace138c..., rgm211 00402801...); fwgate.py at its pin; et-who no holder; nothing written** | logs/look-boxes.txt |

## What E215 changes against E213's kit, and why (each before any datum)

| change | where | why |
|---|---|---|
| **The gemmLnc family's smoke runs inside the sequence, right before its block** (arm A s03 at place 112, arm B s14 at place 70): a run's start rules (the card-time rule and the window, the die gate, the holders), a run's 10 s at rest whose last 5 s are the board's rest for the rise and the reducer's p_rest, one 2 s smoke process gated by its family, the smoke's checks, a 4 s tail; its files a smoke's (`smoke/<id>/smoke.json` with `sequence_n` and `sequence_block`), so the reducer hands the frozen scorer a smoke RUN (block "smoke", n its place) | `run_e215.Session.lnc_smoke`; `e215_common.is_lnc_smoke`, `LNC_SMOKE_BLOCK`; `reduce_e215.reduce_arm` | E215.md 3: "The gemmLnc family's smoke runs right before the gemmLnc block (E213's lesson: E213 arm B's opening gemmLnc smoke read about 66 W of its 72 W stop)"; the scorer reads a smoke RUN by its block "smoke" |
| **Every smoke but the session's gate has its family's own stop path** (arm A s02 'rgm211 gemmLn', s04 'rgm211 gemmL', s03 'rgm136 gemmLnc'; arm B s15 'rgm211 gemmLn', s14 'rgm136 gemmLnc'); the session's gate is s01 and s11-s13 (`SESSION_SMOKE`, the frozen scorer's own); a gemmLnc smoke that cannot start (the die gate's 300 s) drops its family too | `e215_common.FAMILY_SMOKE`, `SESSION_SMOKE`; the runner's `smoke` and `lnc_smoke` | E215.md 3: "s01 and s11-s13 are the session's gate ...; every other smoke is its family's own, with its own stop path (E213's Amendment A1 form)"; never a family past a smoke that did not pass |
| **Arm B gates rgm211 at its WHOLE ELF too** (the build, the box check and the gate per process) | `build_e215.sh` (`W=` for both kernels), `run_e215.box_check`, `ident_e215.gate(..., whole=True)` on arm B | E215.md 2: rgm211's ELF runs on card 1 for the first time (b009-b012, s15); E213 arm B's real build on aifoundry1 read rgm211's whole ELF `00402801...` the pin (b0c727c5 `session/kernel-rgm211.txt`; the look of 00:52:27 read the same ELF there) |
| **E215.md 2's contingency decided: KEEP arm B's rgm211 gemmLn points, no amendment** | the build's desk test B2 and B4, the real path's RB1, RB1K and RB12, the runner's K4B and WSB | the kit builds rgm211's ELF with this desk's toolchain (riscv gcc "() 15.1.0", aifoundry1's string) at the whole-ELF pin and gates every process of 'rgm211 gemmLn' on arm B by E211's identity in its desk tests, refusing a wrong or changed ELF (RB12) |
| **Arm B's steps 4, 9 and 12 are E213's Amendment A2's files, renamed** (`a2/`: fwgate's look and one read on NEEDS-READ at step 4, fwgate's guard at step 9, the read's folder and the evidence of the one call into the data at step 12) | `a2/rb/s05_look_e215_a2.sh`, `a2/rb/s11_session_e215_a2.sh`, `a2/rb/s23_data_e215_a2.sh`, `a2/fwgate_e215a2.py`, `a2/data_e215a2.py`, `a2/rb/rb_e215_a2.sh` (the pins: fwgate.py `4d529a57...`, its six records, the helper `c8080292...`) | E215.md 6: "A2's firmware gate on aifoundry1 (E213's Amendment A2, as arm B ran it on Wed 18 Nov 2026)"; k6's continuity identity stops every boot of aifoundry1 after E82's read (E213's card-e213b stopped there) |
| **No order override** (E213's A3 ran `run_e213_a3.py` to reorder arm B) | the runner reads `points-e215.json` > `order` > `sequence` | E215's registered order already puts every gemmLnc point last (A3's form registered as the order itself) |
| **Step 6n judges each point by its own reading**: literal (the shape token: arm A any card, arm B counted for card 1), post hoc L (the configuration: the token's files that name the point's mask), post hoc S (the kind: GEMM run records naming its tiles or generator outside MM1-v3.1's data); MM1-v3.1's own measured points are 'ran before' by construction; labels: a literal point's covers its token's scored P/C/R points and their cases, an L point's itself and its case, an S point's itself only (never its case, which is its random reference's) | `desk/neverrun_card_e215.py` (rewritten; E213's form) | E215.md 4's three readings; the scorer removes every point of a labelled case, so an S point's case must never be labelled |
| **Step 2 checks E215's registration** (35 entries `99439f8f...`; `points_e215.py candidates --check` and `--check`, `forecast_e215.py`, `rules_e215.py`, `plan_e215.py`, `desk/kernel_e215.py`, and on arm B `desk/choose_e215b.py --check`, about ten minutes) and never rewrites a registered file: each registration check its `--check`, the scorer's self-tests into RB_OUT, **the scorer's forecasts print through `rb/forecasts_print_e215.py` (print only), compared with the committed bytes; at its end, no registered file newer than its start marker and E215's paths clean again (fix-e215)** | `rb/s03_desk_e215.sh`, `rb/forecasts_print_e215.py` | the registration's checks; E213's lesson (step 2 never rewrites a registered file in LAB); verify-e215's finding 1 (the scorer's own `--forecasts` mode writes over the registered file) |
| **The tiles**: seventeen, family S's among them (E212's pattern tiles, E207's real:blind4 two-file pools and blind3 tile; the e37 generator reads the randn tile), each at the registration's `tile_sha256`, its manifest's line (`kinds/kinds.json`, `kinds/blind3/SHA256SUMS`, `kinds/blind4/SHA256SUMS`, `e212/proposal/src/SRC-SHA256SUMS`) and its bytes | `e215_common.TILES`, `TILE_MANIFESTS`, `manifest_sha`; the harness | E215.md 2 (the data) |
| **The doubles' toy figures**: MM1-v3.1's frozen forecasts (arm A by each point's source token from MM1-v3.1's land CSV; arm B by id; the references and ties from `forecast-e215-refs.csv`) | `e215_common.forecast_rows`, `double_of` | the forecasts E215 tests |
| **The real bytes of the lab's latest days**: E213 arm A's committed outputs on aifoundry3 (all four families), E213 arm B's on card 1 and E214's four card-1 sessions, through every reader, the reducer, the smoke reading and the scrub | `desk/realbytes_e215.py` (RB-E213A, RB-E213AR, RB-E213B, RB-E213BR, RB-E214; RB-SMOKE and RB-SCRUB widened) | the round's lesson: every host-output parser fed real committed bytes (E213 arm A on aifoundry3; E213 arm B and E214 on card 1) |

## The round's lessons (E207-E213), and where each is met

1. **A real-path desk test per arm**, stand-ins for every device tool, et-who, the lock, the sampler and the host, inside W/nodev.sh, through the
   smoke, the stop path and at least two points: `desk/realpath_e215.sh` (RA1: t01, a051, a023; RB1: t02, b011, b014; both through the opening
   smoke, the stop-path test and three runs; RA17 and RB13 the gemmLnc block with its smoke in its place on the real path; RA13 the STOP file; RA3
   and RB10 a host hung past its TERM).
2. **Stand-in boxes booted after the firmware read**: the A2 form's desk test (`a2/desk/selftest_a2_e215.sh`) boots its stand-in aifoundry1 at
   2026-11-17 16:46:32 PST (aifoundry1's boot now), after E82's read, and before it only in its continuity case; the kit's own runbook test drives
   arm B's steps 4, 9 and 12 through the A2 form's files in the dry listing.
3. **Every host-output parser fed real committed bytes**: E213 arm A on aifoundry3, E213 arm B and E214 on card 1 (and E207, E211, E206 arm B,
   E212 as E213's kit read them): `desk/realbytes_e215.py`.
4. **No SIGKILL anywhere**: a plain `timeout 10` on every device process; a host alive past its TERM is HUNG, reported and left (C6, HG, HGB, RA3,
   RB10); the sampler is stopped by SIGTERM only; the quick set's kill scan reads 0 kill calls in the kit's code. One thing is not the kit's
   code and is said here: the k6 runbook library the steps source, unchanged since E190's form, bounds the DESK'S own ssh and rsync calls with
   `rb_run.py`, which ends a call past its bound (or on a login link) with TERM and then KILL on aifoundry2's own process group - a process on the
   desk, never one on a box and never a device process (`rb/rb_e215.sh`'s header; E213's kit ran the same library).
5. **Step 7's config read only once the rest has opened**: `rb/s09_reads_e215.sh` reads the 6n report's age and THE REST RULE on the box first,
   no card command, and refuses (10) while either fails (runbook test R7/R7B). On arm B the A2 form's step 4 applies THE REST RULE before its one
   firmware read (the A2 test's RS).
6. **THE ONE-LAB RULE in the step table**, with undesk and uncollect on every stop path, **and the two arms' desk spans kept apart**:
   CARD-LANE-BRIEF.md section 2, rows 0-2 inside the desk span (the other E215 lane's span among those `onelab.sh desk` waits for), rows 11-12
   inside the collect span, row E on every path.
7. **Step 2 never rewriting a registered file in LAB**: every registration check step 2 runs is its `--check` form (rebuilt in memory and
   compared), the scorer's self-tests write into RB_OUT, the scorer's forecasts print runs through `rb/forecasts_print_e215.py`, which prints and
   writes nothing, and is compared with the committed bytes (fix-e215: kit-e215's step 2 ran the scorer's own `--forecasts` mode, which writes
   over the registered `forecasts-e215.txt`, verify-e215's finding 1), the history check refuses any change to a registered file, and **step 2
   reads at its end that no file under E215's registered folders is newer than its start marker and that E215's paths are clean again** (a
   rewrite with the same bytes is seen); the runbook test's P1W and P1X show both.
8. **The sealed-forecast check at step 0**, reading `W/out/orch/sealed-e215.txt` and `tools/claims-v3/sealed-e215/`: `rb/s00_step0_e215.sh` S1;
   **a later seal is a comment line** in the record and a NEW note (`e215-freeze-lines-2.md`), which step 0 never reads (the runbook test's S0).
9. **dmcmd_audit_v2 GO**: `preflight_e215.sh` (the session's files, no WRITE allowed) and the A2 form's fwgate files (`a2/logs/dmcmd-audit-a2.txt`).
10. **The collection's scrub tested on records that carry a home path**: RB-SCRUB rebuilds E213 arm A's, E213 arm B's, E211's, E207's and E206 arm
    B's committed sessions into the box's own bytes (the home in them) and scrubs them back to the committed bytes; the runbook's step 8 ends with
    THE SCRUB CHECK on the dry pass's own records before any card time (runbook test D, DB, DS); RB-HOLDERS masks another login's et-who lines.
11. **Every gemmLnc point runs LAST in its arm** (rgm136's gemmLnc drew about 1.7x MM1-v3's W over idle on card 1 and tripped E213 arm B's 72 W x3
    stop): the registered order, checked by the common module's self-check (the gemmLnc block after the third tie, its smoke first, nothing
    after), the runner's OR/ORB and the real path's RA17/RB13.

## 1. The kit

- **The runner** ([`run_e215.py`](run_e215.py), [`session_e215.sh`](session_e215.sh), [`e215_common.py`](e215_common.py),
  [`e215_ident.py`](e215_ident.py), [`ident_e215.py`](ident_e215.py)): one session per arm, E213's runner with the changes above. **THE FOUR
  FAMILIES BY THE POINT'S LOOP**: 'rgm136 gemmL' (rgm136's host and ELF; both arms), 'rgm136 gemmLnc' (rgm211's host, rgm136's ELF; arm A a024,
  a026, a031, a032 and s03; arm B b013 and s14), 'rgm211 gemmLn' (rgm211's host and ELF; arm A a021, a022, a023, a025 and s02; arm B b009-b012 and
  s15) and 'rgm211 gemmL' (rgm211's host and ELF, walk mn; arm A a027 and s04). **THE IDENTITY GATE PER PROCESS** (`gate_of`: before every process
  `ident_e215.gate(family, elf, whole=(arm B))`; the words recorded with the process; a GATE FAILED at a run starts no process and stops the
  session; at a family smoke it drops the family; in `--dry` the gate reads the ELF's path, and the real gate on real ELFs is the real-path test's).
  **THE WALK CHECK** on every rgm211-host process. **THE KERNEL STOPS** (an rgm211-host run with a check of C wrong, a tensor error, the walk check
  failed, a launch timeout (K1 or rc 124), a launch not ok or an exit not 0 stops the session). The opening smoke (arm A s01 s02 s04; arm B s11
  s12 s13 s15) against **R0's absolute band, 200-4,000 cycles an op** (the counter's mean, the median over counted launches), then the stop-path
  test, then the registered sequence (arm A 119 runs and s03; arm B 71 and s14). The card-time rule and the cap per arm (arm A no run after 60
  card-minutes, cap 70; arm B 42 and 48). The die gate per arm. Before anything opens: the host name (the arm's box), the device environment
  (arm A ET_DEVICES unset; arm B ET_DEVICES=1), build/e215rgm's record today's BUILT by build_e215.sh on this box for this arm (arm B: its
  ET_DEVICES reading), both kernels through THE KERNEL GATE again (arm B both `--whole`), both hosts at the sha256 the build recorded, the reader
  at its arm's pin, the seventeen tiles at their sha256, the harness (HARNESS OK) and the preflight (dmcmd_audit_v2 GO). Then the card's lock
  (`flock -n`, held to the end), the holders (counts only), THE FIRST CARD COMMAND `ettelem config` through
  [`ettelem_guard_e215.sh`](ettelem_guard_e215.sh) under a plain `timeout 10` (the start config and the card's identity gate; the card time counts
  from it), ONE sampler (10 Hz) whose every line feeds THE STOP LINES as it arrives, THE IDENTITY READ, the smoke and then the stop-path test, the
  registered order, the closing config, "session end", MANIFEST.sha256 last. Nothing is set. Every start first reads the operator's STOP file;
  never two samplers at once.
- **No SIGKILL anywhere** (the orchestrator's standing ruling; AGENT.md "never kill -9"): every device process is under a plain `timeout 10`; the
  runner waits for it with a bound and, past `timeout`'s TERM by HANG_GRACE_S (4 s), writes "<time> HUNG: ..." in the session log, touches the stop
  file, starts nothing further, sends no further card command (no closing config read), closes the session and LEAVES the process (exit 8).
  et-who, the harness check and the preflight are waited on with a bound and left past it. The sampler is stopped by SIGTERM only. The build runs
  under a plain `timeout`.
- **The build** ([`build_e215.sh`](build_e215.sh), [`check_e215.py`](check_e215.py)): E136's rgm136 unchanged into **build/e215rgm/rgm136** and
  E211's rgm211 into **build/e215rgm/rgm211** (new folders of ours) on the arm's box; each kernel through THE KERNEL GATE (`check_e215.py --kernel
  rgm136|rgm211`, `--whole` for both on arm B); the hosts by their behaviour: twelve refusals, **each run inside a bubblewrap sandbox with no
  device node and each required to end before the device stage** (on arm B with ET_DEVICES=1); **on aifoundry1 THE ET_DEVICES GATE** (both hosts,
  the device layer and both CMakeCaches); build/e215rgm/BUILD-e215.json with its arm.
- **The doubles** ([`fake_card_e215.py`](fake_card_e215.py)): E213's config, et-who, toy sampler and host per arm, the host double in two forms
  (`--as rgm136`; `--as rgm211` with the walk fields, the tag written only when a gemmLn arm runs an ELF from rgm211's build folder), driven by
  MM1-v3.1's frozen forecasts; modes for every failure the tests need.
- **The reducer** ([`reduce_e215.py`](reduce_e215.py)): each run by E206's readings, written in the frozen scorer's form
  (`{"experiment": "E215", "arms": {"A" | "B": {"smoke": {"runs"}, "points": {pid: {"runs"}}, "ties": {"runs"}}}}`, the references among the
  points; on rgm211-host runs the walk and the gate words; a process the gate refused kept as a run with its gate words and no check, so R0 reads
  it; the gemmLnc smoke a smoke RUN at its place). **The collection** ([`collect_e215.py`](collect_e215.py)): COPY-BACK EXACT, the data directory
  (or a gate stop's record), THE SCRUB of every form of the box's home and our login, and of another login's et-who holder lines
  (`<another-login>`, the command dropped; one it cannot mask refused), the reducer, step 6n's report, judgement and labels, SHA256SUMS; and
  `scrub-check`, the scrub on a private copy (step 8). **The harness** ([`check_e215.py`](check_e215.py), `harness-e215.json`) and **the
  preflight** ([`preflight_e215.sh`](preflight_e215.sh)).
- **Step 6n** ([`desk/neverrun_card_e215.py`](desk/neverrun_card_e215.py)): the registration's scanner (`desk/neverrun_e215.py`, at its pinned
  sha256 `9e68b001...`, unchanged) over the lab at HEAD and the round's lane folders, then THE JUDGEMENT per arm (section 4, item 12) and the
  scorer's labels.
- **The runbook** ([`rb/`](rb/)), from aifoundry2 through k6's drivers, unchanged: **step 0** (`s00_step0_e215.sh`: the freeze line, the kit, the
  sealed-forecast check, no datum of the arm, the clone clean); the window; step 2 (outside the kit's list); the look (arm A k6's; **arm B the A2
  form's**, `a2/rb/s05_look_e215_a2.sh`); the sync; the build; **step 6n**; **step 7, only once the rest has opened and within 30 minutes of
  6n**; the dry pass **and the scrub check**; the session (arm A `rb/s11_session_e215.sh`; **arm B `a2/rb/s11_session_e215_a2.sh`**, fwgate's
  guard); the wait; the copy-back; the data directory (arm A `rb/s23_data_e215.sh`; **arm B `a2/rb/s23_data_e215_a2.sh`**, with `fwgate/`); the
  scorer after the data commit (with step 6n's labels). **No post and no release** (waived). [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) is the card
  lanes' brief, with THE ONE-LAB RULE and THE QUIET HOLD in its step table; [`DATA-README-FORM-e215.md`](DATA-README-FORM-e215.md) is the data
  README's form.

## 2. Card-minutes and the cap (registered: plan-e215.json)

Arm A: 49.4 card-minutes planned (119 runs at 24.47 s a run, E213 arm A's pace on this card, and the four smoke processes and the stop-path test
0.89 min); no run starts once the card time passes 60 minutes; at 70 the session ends after the run in progress. Arm B: 28.0 card-minutes planned
(71 runs at 22.59 s a run, E213 arm B's pace on card 1, and the five smoke processes and the stop-path test 1.25 min); no run after 42; the session
ends at 48. A started run is cut only by a stop. The registered subset if cut: the opening smoke, tie 1, pass 1 and tie 2, every point once but
the gemmLnc block (arm A 82 runs, about 34.1 card-minutes; arm B 43, about 17.2). E215_BUDGET_S is the cap plus 5 minutes (4,500 s and 3,180 s);
the registered last start G + 1:30 binds the launch.

## 3. The order on the box

The card lanes' full table, with the queue, the booking, THE ONE-LAB RULE, THE QUIET HOLD and the end of every path, is
[`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) section 2. The kit's steps (`<arm>` A or B; each step refuses a window written for the other arm):

| step | file | what |
|---|---|---|
| 0 | `E215_SEALED=W/out/orch/sealed-e215.txt rb/s00_step0_e215.sh <arm>` | read only, at the desk: S0 GitHub main; F1 the arm's freeze line an ancestor of GitHub main (arm A `2c971828`; arm B the registration commit, subtree `e89e512f`); F2 the kit commit; S1 THE SEALED-FORECAST CHECK; S2 the note's commits; D0 no datum of the arm (folder-level glob); G1 the clone clean |
| 1 | `rb/s02_window_e215.sh <arm> <day> <last start> <last end>` | today only; the window (G = the booking) in the arm's own RB_OUT |
| 2 | `rb/s03_desk_e215.sh <arm>` (outside the kit's list) | the window; the pull under the lab-git lock; the registration (subtree `e89e512f`) and the kit found by content, ancestors of HEAD, and arm A's freeze line `2c971828`; the paths clean; HISTORY OK; both lists at their pins; the harness; the three self-checks; the registration's checks (arm B also `choose_e215b --check`) and the scorer's three self-checks byte-identical; the preflight; the desk tests' logs; no datum of this arm in any ref (`:(glob)docs/reports/data/*e215*-<suffix>/**`), the other arm's and gate stops REPORTED |
| 4 | arm A `../q141k-runbook/k6/s05_look_k6.sh aifoundry3`; **arm B `a2/rb/s05_look_e215_a2.sh B`** | arm A k6's, unchanged; arm B the A2 form (k6's holder rule with `--wait`, fwgate's look, one read on NEEDS-READ after the rest and both cards free, the folder copied back and its scrub checked, the evidence) |
| 5 | `rb/s07_sync_e215.sh <arm>` | the rsync into the box's tree (aifoundry3 `~/aifoundry`, aifoundry1 `~/nekko`); HARNESS OK on the box |
| 6 | `rb/s08_build_e215.sh <arm> start`, then `wait` | the detached build of both kernels, NO-THIRD-BUILD, the record (both KERNEL OK; arm B both at the whole ELF and ET_DEVICES), the harness, the preflight and both self-checks on the box |
| 6n | `E215_ROUND_OUT=<the round's OUT> rb/s06n_neverrun_e215.sh <arm>` | THE NEVER-RUN SEARCH, REPEATED, and its judgement; its NEVER-RUN-E215 line in RB_OUT |
| 7 | `rb/s09_reads_e215.sh <arm>` | 6n's report under 30 minutes old, then THE REST RULE on the box, no card command; then arm A k6's step 7 (TDP 0 W / 65 C / 600 MHz, et-who clean), arm B the card-1 read (TDP 65 W / 65 C / 600 MHz, minion_mv below 510, /dev/et1_mgmt and ID 1 alone, card 0 clean) |
| 8 | `rb/s10_dry_e215.sh <arm> start`, then `wait` | the runner on the box with its doubles, no device; then THE SCRUB CHECK on the dry pass's own records |
| 9 | arm A `rb/s11_session_e215.sh A`; **arm B `a2/rb/s11_session_e215_a2.sh B`** | the last start, the cap before the last end, today's 6n report, the guard (arm A k6's; arm B the A2 form's pins on the box and fwgate's guard), THE REST RULE, THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and build, then `session_e215.sh` detached |
| 10 | `rb/s20_wait_e215.sh <arm>` | the T0 the runbook launched; HUNG, K1, CRASHED and a gate stop are 16; ended (runner rc 0) 0; running 17 |
| 11 | `rb/s22_collect_e215.sh <arm>` | one read-only copy back, COPY-BACK EXACT, the box's home in every form |
| 12 | arm A `rb/s23_data_e215.sh A`; **arm B `a2/rb/s23_data_e215_a2.sh B`** | the data directory `docs/reports/data/<day>-e215-blind-matmul-<aifoundry3 / aifoundry1-c1>/` (or a gate stop's record), the scrub, the reducer, step 6n's report, judgement and labels, SHA256SUMS, the desk-path gate, the history check; arm B then `fwgate/` and the evidence, SHA256SUMS again |
| 13 | `rb/s24_score_e215.sh <arm>` | after the data commit only: the labels checked, then score_e215.py (registered, unchanged) on the committed data-e215.json with `--labels` |

## 4. The readings stated here before any datum (where E215.md leaves a choice to the kit)

1. **THE DIE LINE'S "HOTTEST SENSOR" IS A LATCH** (E206.md amendment A1 item 1, which plan-e215.json adopts): each arm's line trips on the
   shires' mean (`minshire[0]`) at or above its stop (arm A 70 C, arm B 80 C), or on the latch (`minshire[2]`) only when it has risen during the
   session above the lowest value it read since the session's first sample and reads at or above the stop (`e215_common.Stops`, E206's line for
   line). The doubles read 87 C (arm A) and 66 C (arm B).
2. **The board line**: strictly above the arm's watts (70 W, 72 W) on 3 samples in a row that carry a board reading (a sample with none neither
   counts nor breaks the row: E206.md A1 item 2). A trip touches the host's `--stop-file` at once (the host ends at its next launch boundary, about
   0.5 s), never a kill; nothing further starts. The 65 W planning line: no point's planning peak passes it (the self-check reads plan-e215.json).
3. **The smoke, then the stop-path test; the gemmLnc smoke in its place**: a rest read (30 s; the rest die: the median of the shires' mean over it;
   the die gate is formed from it), then one process of each OPENING smoke point (arm A s01 'rgm136 gemmL', s02 'rgm211 gemmLn', s04 'rgm211
   gemmL'; arm B s11-s13 'rgm136 gemmL' in fp32, fp16 and int8, s15 'rgm211 gemmLn'), **E206's form, `--seconds 2 --budget 3.5`**, each gated by
   its family first; each must read rc 0, counted launches, its check of C as the type gives it (approx for fp32 and fp16, exact for int8), the walk
   where its family has one, **the counter's mean (the median over counted launches) inside R0's absolute band, 200-4,000 cycles an op** (E215.md
   7; the reducer hands the scorer the same number: RB-SMOKE), the board at least 2 W over the rest, and the host on the arm's card. Then the
   stop-path test (both lines trip a stand-in file in process; the start refused). **The gemmLnc smoke** (arm A s03, arm B s14) is the sequence's
   own entry at its place (after the third tie): the kit reads E215.md 3's "its smoke, its points ..." as **a run's frame around a smoke process**
   - the card-time rule and the window, the die gate (as a run's: at most 300 s), the holders, a 10 s rest whose last 5 s are the board's rest for
   the rise (the opening rest is about an hour back on a warmer card) and the reducer's p_rest, then the smoke process and its checks, then a 4 s
   tail; about 0.3 card-minutes, inside the plan's smoke allowance. **The family smokes' own stop path** (E213's Amendment A1 form): a failure
   that is the family's alone (a GATE FAILED, a check of C wrong or missing, the walk check failed, a tensor error, a launch not ok, an exit not 0
   but 124, the counter's mean outside 200-4,000, the board's rise short on a live sampler; for the gemmLnc smoke also its not starting by the die
   gate) drops the family - its runs never start, NO DATA - and the session goes on; a failure that is the session's (K1, HUNG, rc 124, the host
   not shown on the arm's card, the sampler not live after it) or any stop raised during it stops the session (in the opening smoke a gate stop).
   s01 and s11-s13: any failure is the smoke gate (no run).
4. **THE IDENTITY GATE PER PROCESS BY THE POINT'S LOOP**: `ident_e215.FAMILY_KERNEL` maps each family to its ELF (rgm136 for 'rgm136 gemmL' and
   'rgm136 gemmLnc'; rgm211 for 'rgm211 gemmLn' and 'rgm211 gemmL'); the gate reads the process's `--kernel`: its `.text` always the pin, and
   either the whole ELF the pin or the loadable identity the pin (arm A; aifoundry3's gcc writes "(g1b306039a) 15.1.0" into `.comment`, a section
   the card never loads); **arm B requires the whole ELF for BOTH kernels** (E213 arm B's builds on aifoundry1 read both whole ELFs the pins). The
   family is read from points-e215.json's "loop" field, never from the arm token (rgm211's gemmL spells its arm as rgm136's).
5. **THE WALK CHECK by family**: 'rgm211 gemmLn' walk nm, the tag on every hart (E211's); 'rgm136 gemmLnc' and 'rgm211 gemmL' walk mn, the tag on
   none; on every launch walk_ok true, and the check line's walk_launches_bad 0. 'rgm136 gemmL' (rgm136's host) prints no walk.
6. **THE KERNEL STOPS** apply to the three rgm211-host families' runs; an 'rgm136 gemmL' process keeps E206's rules (a TERM'd run flagged and the
   session going on; two failed processes in a row stop it).
7. **The die gate**: arm A min(60, the session's rest die + 4) C, arm B min(63, rest + 3) C, waited at most 300 s, else that run is NO DATA (and a
   gemmLnc smoke that cannot start drops its family).
8. **The start config** (read, nothing set): arm A TDP 0 W, threshold 65 C, minion 600 MHz; arm B TDP 65 W, 65 C, 600 MHz and minion_mv below 510
   (card 0 reads 519), PCIe target /dev/et1_mgmt and physical device ID 1 alone.
9. **ET_DEVICES**: on aifoundry3 unset (its one card; an inherited value dropped, a table setting it refused); on aifoundry1 `ET_DEVICES=1` on every
   device process (the guard refuses anything else) but the A2 form's one firmware read (the stock CLI does not honour it: `--both-nodes-ok`), and
   a runtime line naming card 0 on any host is an identity stop.
10. **The rest rule** (before step 7's read, the A2 form's read and step 9's launch): every session-log form of ours on the box, fix-e202's activity
    floor, energy.sh's folders and the model session's `~/claude/work/ee-*/` folders; at least 40 minutes since the latest. On aifoundry1 it
    covers either card (one login, one tree).
11. **Step 0's sealed check**: a seal is "registered" when its sha256 appears in `tools/claims-v3/sealed-e215/e215-freeze-lines.md` at the lab
    clone's HEAD; the record's non-comment lines must read `E215 <sha256> ...`; an unreadable line is NOT AS STATED; a comment line is never read
    (a later seal's line, E213's lesson).
12. **Step 6n's judgement** (E215.md 4: "a record dated before its freeze line"): every file that makes a scored point's verdict false under the
    point's own reading (above), found again by the scanner's own rules, is dated - a lab file by the commit that added it (its committer time), a
    lane file by its modification time - against the arm's freeze line (arm A `2c971828`'s committer time; arm B the registration commit's, which is
    what E215.md section 4's "this registration's push" names here: the two differ only by the land lane's push delay, and arm B cannot book before
    the push, so no arm B run can fall between them; fix-e215's dated note, section 4). A point
    with any counted file dated before it, with no file found again, with a file that cannot be dated, or held by MM1-v3.1's measured points is
    labelled 'ran before' (the conservative side); a point whose every file is dated after it is REPORTED and kept. The labels are checked against
    points-e215.json before they are written and again at step 13 (LABELS-OK); the scorer takes them with `--labels`.
13. **The scrub**: every form of the box's home step 11 reads (`$HOME`, the user database's home, the home's physical path), the longest first,
    becomes "~"; our box login becomes "<login>"; another login's et-who holder line keeps its node, pid and time, its login becomes
    "<another-login>" and its command is dropped; then no file may hold a `/home/` path, any of those homes, the login, or a holder line naming any
    login but "<login>" or "<another-login>". Step 8 runs the same scrub on the dry pass's own records before the session (SCRUB-CHECK). The A2
    form's step 4 runs it on the firmware read's folder before the session.
14. **Datum checks are folder-level**: an arm's datum is a commit on a `docs/reports/data` folder named `*e215*-<aifoundry3 / aifoundry1-c1>`
    (git's glob magic: `:(glob)docs/reports/data/*e215*-<suffix>/**`), so a file whose name merely holds "e215" is not one (E175's design tile
    `...0e215f.bin`: the runbook test's GS).

## 5. Found while kitting (REPORTED; for the verifier and the land lane)

- **aifoundry1's present boot is E213 arm B's** (booted 16:46:32 PST Tue 17 Nov 2026; the look of 00:52:27 read it): fwgate's look counts the
  committed records and the EQUAL reads of TODAY on this boot only, so arm B's step 4 will read NEEDS-READ and make this boot's SECOND firmware read
  (fwgate allows it: the first, E213 arm B's at 15:13:25 PST Wed 18 Nov 2026, ended EQUAL; fwgate and the A2 form's helper refuse a later read only
  after a read that did not end EQUAL). Its evidence (read only, never a gate) will then read fwgate's ledger with two calls of this boot, both EQUAL
  ("NOT one EQUAL call on this boot: read the lines"): expected; the data README says so and the data verifier reads both lines. A reboot before arm
  B's day makes it the boot's first read again. For the readiness lane's go lines.
- **The gemmLnc smoke's frame is the kit's reading** (section 4 item 3): a run's start rules, a 10 s rest and a 4 s tail around the 2 s smoke
  process, about 0.3 card-minutes, inside the plan's smoke allowance; a gemmLnc smoke that cannot start drops its family (no family runs past a
  smoke that did not pass) - the frozen scorer then sees neither the smoke nor the family's runs (NO DATA, no flag): the README must say why
  (queue.json's `families_dropped`).
- **The box's dry pass (step 8) runs the short sequence** (the opening smoke, the stop-path test, three runs), as E213's did: the gemmLnc smoke's
  place in the sequence is exercised at the desk (the runner's LN, LNB, LG3, LGB, LW3, LK3, LD3, OR, ORB, E2; the real path's RA17, RB13), not on
  the box before the session.
- **Step 2 on arm B takes about ten minutes more than on arm A** (`desk/choose_e215b.py --check`); the two arms' desk spans are kept apart, so a
  lane waiting for the other's span waits that long (CARD-LANE-BRIEF.md 2). The runbook test leaves the choice check out of every step-2 run but
  P1B (`E215_DESK_NO_CHOOSE`, read with `RB_DESKTEST=1` only).
- **The frozen scorer's verdicts are per group** (registered P/C/R and post hoc L/S, in `arms.<arm>.verdicts.<group>` and `pooled.<group>`):
  step 13's printed words and the README name the group of every verdict.
- **The queue chains**: queue_state.py holds `e215a` (aifoundry3) and `e215b` (aifoundry1) with E215's lanes; the dry listing names the last
  chains queued before E215 (`e213a`, `e213b2`); the readiness lane's go lines set the call.
- **The card lanes must be named exactly `card-e215a` and `card-e215b`**: the registration's never-run scanner subtracts those two lane folders
  (and data folders holding `-e215-`).
- **This desk's device layer carries no ET_DEVICES**, so arm B's build passes only on aifoundry1 (whose device layer carries it: the look of
  00:52:27; E213 arm B's committed build) - the desk shows the gate refusing (B2, RB0), never passing.
- **The doubles' smoke counter** reads 800 cycles an op for every smoke (no forecast prices a smoke); E213's committed smoke processes read 755-819
  on aifoundry3 and card 1 (RB-SMOKE), inside R0's 200-4,000.

## 6. Files

The kit: `run_e215.py`, `session_e215.sh`, `e215_common.py`, `e215_ident.py`, `ident_e215.py`, `ettelem_guard_e215.sh`, `build_e215.sh`,
`check_e215.py`, `harness-e215.json`, `preflight_e215.sh`, `fake_card_e215.py`, `reduce_e215.py`, `collect_e215.py`, `desk/neverrun_card_e215.py`;
arm B's A2 form: `a2/fwgate_e215a2.py`, `a2/data_e215a2.py`, `a2/rb/rb_e215_a2.sh`, `a2/rb/s05_look_e215_a2.sh`, `a2/rb/s11_session_e215_a2.sh`,
`a2/rb/s23_data_e215_a2.sh`, `a2/rb/list_steps_e215_a2.sh`; the desk tests: `selftest_run_e215.py`, `desk/realpath_e215.py`,
`desk/realpath_e215.sh`, `desk/realbytes_e215.py`, `desk/desktest_build_e215.sh`, `rb/selftest_rb_e215.sh`, `a2/desk/selftest_a2_e215.sh`; the
runbook: `rb/rb_e215.sh`, `rb/s00_step0_e215.sh`, `rb/s02_window_e215.sh`, `rb/s03_desk_e215.sh` (step 2: outside the kit's list, which it pins),
`rb/s06n_neverrun_e215.sh`, `rb/s07_sync_e215.sh`, `rb/s08_build_e215.sh`, `rb/s09_reads_e215.sh`, `rb/s10_dry_e215.sh`, `rb/s11_session_e215.sh`,
`rb/s20_wait_e215.sh`, `rb/s22_collect_e215.sh`, `rb/s23_data_e215.sh`, `rb/s24_score_e215.sh`, `rb/rest_rule_e215.sh`, `rb/check_history_e215.py`,
`rb/list_steps_e215.sh`, `rb/forecasts_print_e215.py` (step 2's print-only forecasts print, fix-e215); the documents: this file,
`CARD-LANE-BRIEF.md`, `DATA-README-FORM-e215.md`; the logs under `logs/` and `a2/logs/`; and `SHA256SUMS-e215-kit` (every kit file but itself and
step 2; its own sha256 is step 2's KITPIN). Beside the kit, outside E215's folder and in no list of it: fix-e215's dated note on E215.md's text,
`tools/claims-v3/e215-notes/E215.md.dated-note-1.md`, and its re-derivation, `tools/claims-v3/e215-notes/metric_e215_note1.py`.

## 7. Device commands

The session's only device commands are READs (dmcmd_audit_v2 GO on the session's files, no WRITE allowed): `ettelem config` and `ettelem sample
--seconds N --every-ms 100` through the arm's guard (aifoundry3 with ET_DEVICES unset, aifoundry1 with ET_DEVICES=1; anything else refused, exit
97), and the hosts' own runtime (rgm136's and rgm211's), each under a plain `timeout 10`. On arm B, before the session and only on NEEDS-READ, the
A2 form's ONE firmware read (`fwgate.py read --both-nodes-ok`: `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`, a READ in the lab's table, under both
cards' locks; the owner's rulings of 15:07:01 and 15:09:49 PST Sun 15 Nov 2026). Every runtime creation also sends the ops node's abort to every
submission queue of every card the device layer enumerates (harmless on a card held alone; on aifoundry1 ET_DEVICES=1 keeps it off card 0). No
set, no reset, no statistics reset, no governor, TDP, threshold, clock or voltage change, no PMIC command, no PCIe recovery, no driver reload, no
power cycle, no firmware change: none is in the kit.

## 8. What the desk cannot show

- The cards themselves: their meters, their clocks, their temperatures, a launch that does not finish on silicon; every number here is the
  doubles'.
- The hosts' device path (the runtime's own opening of a card) past the refusals: the doubles and stand-ins stand in for it; the real-path test
  runs everything else.
- arm B's build passing the ET_DEVICES gate (only aifoundry1's device layer carries it) and aifoundry1's gcc writing the whole ELFs the pins name
  (E213 arm B's committed build did, and the look of 00:52:27 read them there); the build's own run on each box is step 6 on the card day.
- rgm211's ELF on card 1's silicon: never run there; the family smoke s15 and its own stop path are the card day's first test of it.
- fwgate's real read on aifoundry1 (the A2 form's desk test runs fwgate's own stand-ins): see section 5 on this boot.
- aifoundry3's and aifoundry1's own disks for step 6n (NOT SEARCHED, as registered).
- The model session's sealed forecasts: none was posted for E215 when this kit was written; step 0 reads them on the day.

## 9. Labels

Every figure here is **registered** (E215.md), a **desk check of code** (the tests above, on the doubles and stand-ins), or a **desk read** of
committed records (the real-bytes test, step 6n's scan, the look at the boxes). Nothing here is measured, blind, held out or post hoc.

## Compute

kit-e215's runs (Thu 19 Nov 2026), on aifoundry2's CPU through the round's slots (`W/slot.sh`, nice 10), one slot job at a time, single-threaded
(OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, MKL_NUM_THREADS and NUMEXPR_NUM_THREADS 1), builds at -j2; `/usr/bin/python3` 3.12.3 (numpy 1.26.4 and
scipy 1.11.4 only through the registration's own checks and the never-run scanner's MM1-v3.1 data loader). The development runs: four short dry
sessions (00:29-00:31), a runner-test subset of 18 cases (00:35-00:39), the runner test's whole development pass (00:39-01:13, 95 of 95 PASS,
`logs/dev-selftest-run-0035.txt` in the lane's folder). The final runs, each its own slot job and one at a time: the real-bytes test (01:11:34-01:11:57), the build test (01:12:03-01:12:18), the real-path test (01:12:26-01:16:37), the dry listings (01:17:23-01:17:25), step 6n's tool on the round's folders (01:17:30-01:17:51), the runbook test (a first pass from 01:18 stopped by me at 01:29 at its N case, whose sparse scratch lacked E207's and E206 arm B's data folders that rules_e215 reads; the final pass 01:29:26-02:12:39), the A2 form's test (02:13:37-02:14:41), the quick set (02:15:15-02:18:46, and again 02:50:17-02:53:46 once the kill scan's word list read a message's 'no kill -9' as the word it is), the runner test (02:19:03-02:50:00); every one inside `W/slot.sh` (nice 10), each built host, runner or stand-in also inside `W/nodev.sh`, the quiet-desk flag absent. No
card time; no CPU on a lab box (the one look at 00:52:27 read files only).

fix-e215's runs (Thu 19 Nov 2026), the same way (`W/slot.sh`, nice 10, one slot job at a time, single-threaded, `/usr/bin/python3` 3.12.3 with
`-I -B`; every runbook step, stand-in or listing also inside `W/nodev.sh`, the quiet-desk flag absent): the helper's test (about 04:59, a few
seconds of standard-library Python, single-threaded, outside a slot), the dry listings' development pass (05:02:41), the runbook test (05:03-05:49, 2,795 s), the final dry listings (05:50), the quick set (05:50:15-05:53:45) and the dated note's re-derivation (05:53:55, standard library, under a second). No card time; no
box reached; no CPU on a lab box.

SPDX-License-Identifier: Apache-2.0
