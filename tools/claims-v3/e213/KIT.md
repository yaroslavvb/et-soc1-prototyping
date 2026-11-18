# E213's run kit: MM1-v3's blind matmul day on two cards from aifoundry2 - arm A on aifoundry3 card 0 in E207's and E211's kit form, arm B on aifoundry1 card 1 in E206 arm B's form: one runner per arm with one sampler and the stop lines live, the two kernels built on each box through their gates, THE IDENTITY GATE PER PROCESS by the point's loop (four families), THE WALK CHECK and THE KERNEL STOPS, the smoke and then the stop-path test, every run under a plain `timeout 10` and never killed; the never-run search repeated right before the first card command and judged against each arm's freeze line; the scrub checked on the dry pass's own records before the session (Q216; kitted, not run)

*Tue 17 Nov 2026 (week 47) from 21:27 PST to Wed 18 Nov 2026 00:05 PST (the desk tests' final runs), on aifoundry2, desk only (Q216, lane
`kit-e213`); **amended by Q216's lane `fix-e213` on Wed 18 Nov 2026 from 01:26 PST, before any datum and before the land** (the kit notes below;
its desk tests' final runs 03:10:01-03:59:29 PST Wed 18 Nov 2026). No card was claimed or opened: aifoundry2 has a card, so every
desk test that runs a built host, the runner, a stand-in session or a stand-in reader ran inside the round's slots and its sandbox (no /dev/et*,
an empty /run/lock), single-threaded. No device command was sent, nothing was posted. Two boxes were reached, each once, only while no lane booked
them (`book.sh show` read first): **one read-only look at aifoundry1 and aifoundry3 at 21:39:38 PST** (the trees, Python 3.12.3, the riscv gcc
in /opt/et/bin, g++ 13.3.0, cmake 3.28.3, bwrap, flock and timeout present; the readers at E206's pins, aifoundry3 `16037641...` and aifoundry1
`8008f96f...`; aifoundry1's /opt/et/lib/libdeviceLayer.a carries the string ET_DEVICES, aifoundry3's does not; et-who: no holder on either;
both up 4:53). Nothing was written on either box and no device was opened there. New files only, all under `tools/claims-v3/e213/`, on top of
E213's registration with its Amendment A1 ([`E213.md`](E213.md), fix-e213's, a local commit at GitHub main `ee0356d9`: its `tools/claims-v3/e213`
subtree `75778ad3...`, `SHA256SUMS-e213-registration` `96e5d168...`, 27 entries), which this kit changes in no byte. **No E213 datum exists.
Nothing here changes a forecast, a band, a rule, a threshold, the order, the card time, the cap, a stop or the scorer.** Where E213.md leaves a
reading to the kit, the reading is stated in section 4 before any datum. E211's landed kit (`2b7f261f`, which ran E211 FULL on aifoundry3) and
E206's (`906699ea`, whose arm B ran FULL on aifoundry1 card 1) are the authorities every behaviour below is checked against.*

**His words** (Mon 16 Nov 2026, received at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul and "FME" the
tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and
number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other
operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation."

## Kit notes by fix-e213 (Wed 18 Nov 2026, before any datum): verify-e213's findings and what the kit does about each

verify-e213 read the registration and this kit as HOLDS WITH FIXES (01:24 PST); the orchestrator's answer 5 (00:15 PST) asked for a smoke process
for rgm211's own gemmL family "with its identity gate and its own stop path". Every desk test below was run again on the amended kit.

| finding | what changed |
|---|---|
| 1 (medium): the family 'rgm211 gemmL' has no smoke process; a085 at run 74 was its first card process | **s04** (E213.md A1 clause 1): gemmL2x2x2 fp32 random on rgm211's host and ELF, last in arm A's smoke (`e213_common.ARMS`, `points-e213.json`), gated and read like s01-s03, with **its own stop path** (`e213_common.FAMILY_SMOKE`, `a1_session_level`; `run_e213.drop_family`): a failure for its family alone (a GATE FAILED, a check of C wrong or missing, the walk check failed, a tensor error, a launch not ok, an exit not 0 but 124, the counter's mean outside 200-4,000, the board's rise short on a live sampler) drops the family - a074, a078, a081 and a085 are "not started" (NO DATA, no card time; queue.json `families_dropped`) - and the session goes on; K1, a HUNG host, a launch timeout (rc 124), the host not shown on the arm's card, the sampler not live after s04, or any stop raised during s04 stop the session as at s01-s03. The reducer copies the drop into its arm's queue; the frozen scorer's R0 reads a dropped family as a drop (E213.md A1 clause 2). Tests: the runner's G1, K4, GF4, WF4, CF4, KF4, TF4, SF4; the real path's RA1 and RA16; the scorer's stand-in days Q and R. |
| 2 (medium): another login's et-who holder line reached the committed record verbatim | **The scrub** (`collect_e213.py`, the data collection and `scrub-check` alike): after the home and our login, every et-who holder line of another login (a first field `/dev/et*` or `lock:<name>`, its second field the login: the form the runner's holder rule reads) keeps its node, pid and time, its login becomes `<another-login>` and its command is dropped; a holder line still naming any login but `<login>` or `<another-login>` (one in a file the scrub does not rewrite, for one) is refused: SCRUB-CHECK LEFT or SCRUB FAILED. Test: the real-bytes test's RB-HOLDERS (on a committed card-1 et-who record with made-up logins); RB-SCRUB still scrubs three committed sessions back to their committed bytes exactly. |
| 3 (medium-low): E213.md's Builds on block | E213.md section 9 (A1 clause 3): the registration's, not the kit's. |
| 4 (low): "no ref holds a docs/reports/data/*e213* path" | E213.md's header (A1 clause 4); every datum check in this kit was already folder-level (section 4, item 14). |
| 5 (low): the brief said QUEUE CANCELLED means SKIPPED | [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) section 1 and row B now follow Q216's card-lane text: keep waiting while QUEUE BUSY or QUEUE CANCELLED (no booking, no ssh call to that box while a claim stands), at most until 20:29:00 PST Wed 18 Nov 2026, then SKIPPED. |
| 6 (low): the scorer's docstring gave E1's t_op as t_gemm / ops | the registration's (A1 clause 5): the docstring corrected, the code unchanged. |
| 7 (low): the die latch may be live after the boxes' reboot | nothing changes (A1 clause 7): the latch line is read as section 4 item 1 says, and the readiness lane reads minshire[2] at rest on both cards. |
| 8 (low): a failed rgm211 build on arm B costs arm B's whole day | the brief's row 6 says so (A1 clause 6): `build_e213.sh` fails the whole build (RGM-BUILD-FAILED) if rgm211's host does not build or gate on aifoundry1, so no session of arm B that day, not k37-k40 alone. |

**Found and fixed while fixing** (none of them verify-e213's): (1) the real path's RA11 stopped its stand-in sampler at a launch count meant for three
smoke processes, so it died inside s04: moved past arm A's four (36, as RB7's on arm B); (2) a sampler dying inside s04 would have read as the
family's failure (its board rise unreadable): the sampler is the session's, so `e213_common.a1_session_level` stops the session then (the runner's
case SF4); (3) the common module's self-check compared s04 with rules-e213.json, a desk file the box never receives, so step 6's self-check on the
box would have failed: it compares with it only where it is (the desk's step 2, beside the scorer that pins it) and checks s04 against
points-e213.json everywhere (the runbook test's BA runs it on the stand-in box).

## Results first (desk checks of code and desk reads of committed records; nothing is measured on a card)

| check | result | log |
|---|---|---|
| **the runner on the doubles** (`selftest_run_e213.py`): both arms; the short path with the card's identity gate and read; the smoke and THEN the stop-path test; every config gate, holder, sampler fault and stop line of E206's and E211's per arm; THE FOUR FAMILIES (K4); the identity gate refusing the smoke (GS), a run (GR) and **the new family's first scored run (G211)**, each through the reducer and the frozen scorer (R0 FAIL); the walk check failing in the smoke (WS) and on **a085, the new family** (WR); **AMENDMENT A1's FAMILY SMOKE s04** (fix-e213): its gate (GF4), its walk (WF4) and its check of C (CF4) failing drop the family and the session goes on (GF4, WF4 through the reducer and the frozen scorer: R0 PASS, the drop flagged, a074 a078 a081 a085 NO DATA), and K1 (KF4), a launch timeout (TF4) or the sampler dying inside s04 (SF4) stop the session; THE KERNEL STOPS (CW, TL, TE, TEB); HUNG with nothing killed (C6, HG, DF); the STOP file and SIGTERM; a crash; the card-time rule; **each arm's whole registered order** (OR: 105 runs; ORB: 85), every argv and gate the registered; **END TO END**, both arms in one data file through the frozen scorer, the pooled rules among them (E2) | **SELFTEST-RUN-E213 86 of 86 PASS (03:33:21-03:59:29 PST Wed 18 Nov 2026, 1,568 s; both arms, every case one session of its own)** | [`logs/selftest-run-e213.txt`](logs/selftest-run-e213.txt) |
| **the REAL path** (`desk/realpath_e213.py`, `desk/realpath_e213.sh`): run_e213.py WITHOUT --dry under each arm's hostname (a private UTS namespace) and a private PID namespace, stand-ins for the reader behind the REAL guard, et-who, the two hosts, the lock and the nodes; **the two REAL kernel ELFs from the REAL build_e213.sh**, so the identity gate per process reads real ELFs: arm A RA0-RA15 (the build, the whole path, the four families (RA1K), the lock, a host hung past its TERM left to end by itself, the reader's pin, a changed .text, ET_DEVICES three ways, other logins, the other card three ways, runtime lines, the sampler, the build record, the STOP file, **RA14: rgm136's real ELF over rgm211's refused by the new family's gate at a085, and the walk alone cannot tell**, RA15 the walk check; **RA16 (fix-e213): s04's own stop path on the real path, the walk failing at s04 on its real gate (the family dropped, the session going on) and K1 at s04 (the session stopped)**); arm B RB0-RB11 (the build stopping at the ET_DEVICES gate on this desk's device layer, the whole path at ET_DEVICES=1 with card 1's identity, gemmLnc (RB1K), card 0 three ways, ET_DEVICES missing, card 0's holders, the sampler, runtime lines of both cards, **RB9: arm B requires rgm136's WHOLE ELF**, a host hung past its TERM, the identity gate per process) | **REALPATH-E213 31 of 31 PASS (arm A 18 of 18, arm B 13 of 13) (03:29:47-03:33:21 PST Wed 18 Nov 2026, 214 s)** | [`logs/realpath-e213.txt`](logs/realpath-e213.txt) |
| **the parsers on real committed bytes** (`desk/realbytes_e213.py`): **E207's and E211's committed outputs on aifoundry3** (both hosts; E211's walk fields read by family) and **E206 arm B's and E212's on aifoundry1 card 1** (card 1's runtime lines dropped and counted), each through host_records with its own command line, and E207's, E211's and E206 arm B's runs through reduce_run against their committed data files field for field; runtime lines spliced at every byte offset; the config line; the card's identity forms per arm; rgm211's host's real simulator bytes by E213's family, **the new family's own case N** among them; the smoke's reading; **THE COLLECTION'S SCRUB ON REAL RECORDS THAT CARRY THE BOX'S HOME** (E211's, E207's and E206 arm B's sessions turned back into the box's own bytes through their manifests, scrubbed back to the committed bytes exactly; three forms of the home; a home not given refused); **RB-HOLDERS (fix-e213): another login's et-who holder lines on a committed card-1 record masked at the collection, our own lines byte-identical, a holder line the scrub cannot rewrite refused** | **REALBYTES-E213 14 of 14 PASS (03:29:14-03:29:32 PST Wed 18 Nov 2026, 18 s)** | [`logs/realbytes-e213.txt`](logs/realbytes-e213.txt) |
| **the build on this desk's real toolchain** (`desk/desktest_build_e213.sh`; riscv gcc "() 15.1.0", g++ 13.3.0, cmake 3.28.3): both kernels through their gates on each arm's box (arm B rgm136 at its whole ELF), the hosts' twelve refusals in the build's sandbox (arm B with ET_DEVICES=1), **arm B's ET_DEVICES gate refusing this desk's stock device layer**, changed sources, aifoundry3's `.comment` form (identity OK, --whole FAILED), a changed `.rodata` or `.text` byte, the wrong kernel each way and **all four families both ways**, another box, the runner's box check on each arm, the guard on both boxes | **DESKTEST-BUILD-E213 11 of 11 PASS (03:29:32-03:29:47 PST Wed 18 Nov 2026, 15 s)** | [`logs/desktest-build-e213.txt`](logs/desktest-build-e213.txt) |
| **the runbook** (`rb/selftest_rb_e213.sh`: a fake ssh and rsync, stand-in aifoundry3 and aifoundry1 boxes, the real builds): the dry listings; the window rule per arm; the lab-git lock; step 2 at every pin; the history check and a shadow; an arm's datum refusing step 2 for that arm only; a gate stop reported; **E175's tile named *e213* is no datum**; **STEP 0** (no record, a registered seal, an unregistered seal NOT AS STATED, arm B with GitHub main before the registration NOT AS STATED, an arm's datum); the look on each box; ours_live; the sync per arm; a login link; a hang; NO-THIRD-BUILD; **the real build on aifoundry3 and the ET_DEVICES gate on aifoundry1**; **step 6n on stand-in lane folders** (a pre-freeze record labelled, a post-freeze record REPORTED, E213's own lanes subtracted); step 7 refusing without a fresh 6n report and before the rest, then each arm's read; **the dry pass and THE SCRUB CHECK per arm, and the scrub check refusing another home's path before the session**; THE HUNG MARKER; the same-day rule; the last start; the real session stopping at its box check; step 10's readings; the copy-back, a byte changed after the manifest; **each arm's data directory with step 6n's labels and the frozen scorer on it** | **SELFTEST-RB-E213 30 of 30 PASS (03:10:01-03:27:17 PST Wed 18 Nov 2026, 1,036 s; none to a lab box)** | [`logs/selftest-rb-e213.txt`](logs/selftest-rb-e213.txt) |
| the dry listings, every step of each arm with stand-ins | **arm A: dry listing: 15 steps listed, 0 exited non-zero, 0 box calls**; **arm B: dry listing: 15 steps listed, 0 exited non-zero, 0 box calls** | [`logs/dry-listing-e213-A.txt`](logs/dry-listing-e213-A.txt), [`logs/dry-listing-e213-B.txt`](logs/dry-listing-e213-B.txt) |
| **the registration's checks and the kit's self-checks, as step 2 runs them** (`/usr/bin/python3` 3.12.3, single-threaded): points candidates, points, forecast_e213b, rules, plan and desk/kernel --check; the scorer's stand-in self-test, real-bytes self-test and forecasts print byte-identical to the committed files; e213_common, e213_ident and ident_e213 --check; the harness re-made and HARNESS OK; the preflight; the registration's list and subtree; every kit file parsed; the kill scan (the history check needs the kit committed: step 2 runs it, and the runbook test's P1 reads HISTORY OK on the stand-in kit commit) | **QUICK-SET-E213 PASS: 0 not as stated (03:27:17-03:28:57 PST Wed 18 Nov 2026, 100 s): the scorer's three self-checks byte-identical, the registration's list 27 of 27 and its subtree 75778ad3, 23 shell files and 13 Python files parse, 0 kill calls** | [`logs/checks-e213.txt`](logs/checks-e213.txt) |
| **dmcmd_audit_v2** on the session's files (`preflight_e213.sh`) | **dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)** | [`logs/dmcmd-audit-e213.txt`](logs/dmcmd-audit-e213.txt) |
| **step 6n's tool on the round's real folders** (03:28:58-03:29:14 PST Wed 18 Nov 2026: fix-e213's clone at its HEAD as the lab, the round's OUT as the lanes; the registration's scanner unchanged) | arm A: **87 of 87** scored points never ran on any card; arm B: **40 of 40** never ran on aifoundry1 card 1; 70,552 files read; nothing labelled, nothing REPORTED; the labels LABELS-OK (a desk read; the card lanes repeat it at step 6n) | [`logs/neverrun-desk-e213.txt`](logs/neverrun-desk-e213.txt) |

## The orchestrator's answers (Tue 17 Nov 2026 21:27 PST; answer 5 Wed 18 Nov 2026 00:15 PST), and where the kit meets each

1. **The stop lines, confirmed as registered** (arm A: the 65 W planning line, the board stop 70 W on 3 samples, the die stop 70 C; arm B: 65
   W, 72 W on 3 samples, 80 C; ET_DEVICES=1 and nothing on card 0; no set of any kind, reads only, never a reset, never kill a device process):
   `e213_common.ARMS` and `Stops` carry them per arm; the self-check reads them against plan-e213.json's words; the runner's tests B1, B1B, D1,
   D1B, D2, D3, D3B, D3C and BN read them live; every device command is a READ (dmcmd_audit_v2 GO), and no path of the kit sends a SIGKILL.
2. **The sealed forecasts**: step 0 (`rb/s00_step0_e213.sh`, line S1) reads the round's record `W/out/orch/sealed-e213.txt` and the note
   `tools/claims-v3/sealed-e213/e213-freeze-lines.md` at the lab clone's HEAD: every sealed sha256 the record lists must be registered in the
   note, else NOT AS STATED and no box step that day; the brief's step B never books over the orchestrator's `orch-hold-e213-seal`. The runbook
   test's case S0 covers no record, a registered seal and an unregistered one.
3. **rgm211's gemmL family (a074, a078, a081, a085): KEPT.** The kit gates every process by its ELF's `.text` and loadable identity through the
   point's LOOP (`ident_e213.FAMILY_KERNEL`: 'rgm211 gemmL' is its own family, pinned to rgm211's ELF, never read from the arm token, which it
   shares with rgm136's gemmL); the host's walk tag is checked per family (E211's tag on every hart for 'rgm211 gemmLn'; none for 'rgm211 gemmL'
   and 'rgm136 gemmLnc'); and **a wrong ELF is refused for that family** on the doubles (G211: through the reducer and the frozen scorer, R0
   FAIL), on the real path with the REAL ELFs (RA14: rgm136's real ELF copied over rgm211's, a085's gate GATE FAILED, no process; and in process
   all four families both ways), in the build's desk test (B6b: 'rgm211 gemmL' on rgm136's real ELF FAILED) and on rgm211's host's real
   simulator bytes (RB-SIM case N read OK as 'rgm211 gemmL'). **The walk alone cannot tell the two ELFs apart for an mn family** (RA14 shows it):
   only the identity gate refuses there, and it runs before every process.
4. **Arm B's freeze line is the registration commit's push**: step 0's F1 line requires it to be an ancestor of GitHub main for arm B (found by
   content: the commit that added E213.md, its subtree `75778ad3...`), read in the lab clone or, when GitHub main's commit is not there yet, in a
   temporary bare repository that borrows the clone's objects (never a fetch into the lab clone); step 6n dates arm B's hits against that commit's
   committer time; the brief's step B makes it a booking condition. The runbook test's case S0 (d) shows F1 NOT AS STATED with GitHub main before
   the registration.
5. **(Wed 18 Nov 2026 00:15 PST) A smoke point for rgm211's own gemmL family: YES** - s04, added by E213.md's Amendment A1 (fix-e213) before
   the land, with its identity gate and its own stop path: the kit notes above.

## The round's lessons, and where each is met

1. **A real-path desk test per arm**, stand-ins for every device tool, et-who, the lock, the sampler and the host, inside W/nodev.sh, through the
   smoke, the stop path and at least two points: `desk/realpath_e213.sh A|B` (RA1: t01, a039, a005; RB1: t02, k03, k18; both through the smoke,
   the stop-path test and three runs; RA13 the STOP file; RA3 and RB10 a host hung past its TERM).
2. **Every host-output parser fed real committed bytes**: E207 and E211 on aifoundry3, E206 arm B and E212 on card 1 (`desk/realbytes_e213.py`).
3. **No SIGKILL anywhere**: a plain `timeout 10` on every device process; a host alive past its TERM is HUNG, reported and left (C6, HG, DF, RA3,
   RB10); the sampler is stopped by SIGTERM only; the one kill in the path is k6's bounded runner's, of the desk's own ssh or rsync.
4. **Step 7's config read only once the rest has opened**: `rb/s09_reads_e213.sh` reads the 6n report's age and THE REST RULE on the box first,
   no card command, and refuses (10) while either fails (runbook test R7: the stand-in reader called 0 times in three refusals, then once).
5. **THE ONE-LAB RULE in the step table**, with undesk and uncollect on every stop path: CARD-LANE-BRIEF.md section 2, rows 0-2 inside the desk
   span, rows 11-12 inside the collect span, row E on every path.
6. **The sealed-forecast check at step 0**, reading `W/out/orch/sealed-e213.txt` and `tools/claims-v3/sealed-e213/`: `rb/s00_step0_e213.sh` S1.
7. **dmcmd_audit_v2 GO**: `preflight_e213.sh` (11 send sites, every one a READ, no WRITE allowed), run by step 2, the build's checks, the runner's
   box check and this log.
8. **The collection's scrub tested on records that carry a home path** (E209's lesson): RB-SCRUB on three committed sessions rebuilt as the box
   wrote them; and the runbook's step 8 now ends with THE SCRUB CHECK on the dry pass's own records, before any card time (runbook test D, DB,
   DS).
9. **The gemmL family's identity** (the orchestrator's answer 3): above; and its own smoke s04 (answer 5, E213.md A1).
10. **No other login's name in a committed record** (fix-e213, verify-e213's finding 2): the collection masks another login's et-who holder lines
    and refuses one it cannot mask (RB-HOLDERS).

## 1. The kit

- **The runner** ([`run_e213.py`](run_e213.py), [`session_e213.sh`](session_e213.sh), [`e213_common.py`](e213_common.py),
  [`e213_ident.py`](e213_ident.py), [`ident_e213.py`](ident_e213.py)): one session per arm, E211's runner (arm A's form) with E206's arm B
  (ET_DEVICES=1, card 1's lock `/run/lock/etsoc-shire1.lock`, the config read's card-1 identity gate with minion_mv below 510, the other card's
  runtime line an identity stop, nothing on card 0). **THE FOUR FAMILIES BY THE POINT'S LOOP**: 'rgm136 gemmL' (rgm136's host and ELF; both arms),
  'rgm136 gemmLnc' (rgm211's host, rgm136's ELF; arm A, and arm B's k37-k40 and s14), 'rgm211 gemmLn' (rgm211's host and ELF; arm A) and **'rgm211
  gemmL'** (rgm211's host and ELF, walk mn; a074, a078, a081, a085). **THE IDENTITY GATE PER PROCESS** (`gate_of`: before every process
  `ident_e213.gate(family, elf, whole=(arm B))`; the words recorded with the process; a GATE FAILED starts no process and stops the session; in
  `--dry` the gate reads the ELF's path, and the real gate on real ELFs is the real-path test's). **THE WALK CHECK** on every rgm211-host process.
  **THE KERNEL STOPS** (an rgm211-host process with a check of C wrong, a tensor error, the walk check failed, a launch timeout (K1 or rc 124), a
  launch not ok or an exit not 0 stops the session). The smoke (arm A s01-s04 - s04, 'rgm211 gemmL', by E213.md A1 with **its own stop path**: a failure for its family alone drops a074, a078,
  a081 and a085 and the session goes on; K1, HUNG, a launch timeout or the host off the arm's card stop it - and arm B s11-s14) against **R0's absolute band, 200-4,000 cycles an op**
  (the counter's mean, the median over counted launches). The order per arm (arm A 105 runs, arm B 85). The card-time rule and the cap per arm
  (arm A no run after 60 card-minutes, cap 70; arm B 42 and 48). The die gate per arm. Before anything opens: the host name (the arm's box), the
  device environment (arm A ET_DEVICES unset; arm B ET_DEVICES=1), build/e213rgm's record today's BUILT by build_e213.sh on this box for this arm
  (arm B: its ET_DEVICES reading), both kernels through THE KERNEL GATE again (arm B rgm136 `--whole`), both hosts at the sha256 the build
  recorded, the reader at its arm's pin, the eight tiles at their manifest's sha256, the harness (HARNESS OK) and the preflight (dmcmd_audit_v2
  GO). Then the card's lock (`flock -n`, held to the end), the holders (counts only), THE FIRST CARD COMMAND `ettelem config` through
  [`ettelem_guard_e213.sh`](ettelem_guard_e213.sh) under a plain `timeout 10` (the start config and the card's identity gate; the card time counts
  from it), ONE sampler (10 Hz) whose every line feeds THE STOP LINES as it arrives, THE IDENTITY READ, the smoke and then the stop-path test, the
  registered order, the closing config, "session end", MANIFEST.sha256 last. Nothing is set. Every start first reads the operator's STOP file;
  never two samplers at once.
- **No SIGKILL anywhere** (the orchestrator's standing ruling; AGENT.md "never kill -9"): every device process is under a plain `timeout 10`; the
  runner waits for it with a bound and, past `timeout`'s TERM by HANG_GRACE_S (4 s), writes "<time> HUNG: ..." in the session log, touches the stop
  file, starts nothing further, sends no further card command (no closing config read), closes the session and LEAVES the process (exit 8).
  et-who, the harness check and the preflight are waited on with a bound and left past it. The sampler is stopped by SIGTERM only. The build runs
  under a plain `timeout`.
- **The build** ([`build_e213.sh`](build_e213.sh), [`check_e213.py`](check_e213.py)): E136's rgm136 unchanged into **build/e213rgm/rgm136** and
  E211's rgm211 into **build/e213rgm/rgm211** (new folders of ours) on the arm's box; each kernel through THE KERNEL GATE (`check_e213.py --kernel
  rgm136|rgm211`, `--whole` for rgm136 on arm B); the hosts by their behaviour: twelve refusals, **each run inside a bubblewrap sandbox with no
  device node and each required to end before the device stage** (on arm B with ET_DEVICES=1); **on aifoundry1 THE ET_DEVICES GATE** (both hosts,
  the device layer and both CMakeCaches; E206's); build/e213rgm/BUILD-e213.json with its arm.
- **The doubles** ([`fake_card_e213.py`](fake_card_e213.py)): E206's config, et-who, toy sampler and host per arm, the host double in two forms
  (`--as rgm136`; `--as rgm211` with the walk fields, the tag written only when a gemmLn arm runs an ELF from rgm211's build folder), driven by the
  arm's frozen forecast (arm A MM1-v3's `mm1_v3_e213.csv`; arm B `forecast-e213b-v3.csv`); modes for every failure the tests need.
- **The reducer** ([`reduce_e213.py`](reduce_e213.py)): each run by E206's readings, written in the frozen scorer's form
  (`{"experiment": "E213", "arms": {"A" | "B": {"smoke": {"runs"}, "points": {pid: {"runs"}}, "ties": {"runs"}}}}`; on rgm211-host runs the walk
  and the gate words; a process the gate refused kept as a run with its gate words and no check, so R0 reads it). **The collection**
  ([`collect_e213.py`](collect_e213.py)): COPY-BACK EXACT, the data directory (or a gate stop's record), THE SCRUB of every form of the box's home
  and our login, and of another login's et-who holder lines (`<another-login>`, the command dropped; one it cannot mask refused: fix-e213),
  the reducer, step 6n's report, judgement and labels, SHA256SUMS; and `scrub-check`, the scrub on a private copy (step 8). **The harness**
  ([`check_e213.py`](check_e213.py), `harness-e213.json`, 48 files) and **the preflight** ([`preflight_e213.sh`](preflight_e213.sh)).
- **Step 6n** ([`desk/neverrun_card_e213.py`](desk/neverrun_card_e213.py)): the registration's scanner (`desk/neverrun_e213.py`, at its pinned
  sha256, unchanged) over the lab at HEAD and the round's lane folders, then THE JUDGEMENT per arm (section 4, item 12) and the scorer's labels.
- **The runbook** ([`rb/`](rb/)), from aifoundry2 through k6's drivers, unchanged: **step 0** (`s00_step0_e213.sh`, new: the freeze line, the
  kit, the sealed-forecast check, no datum of the arm, the clone clean); the window; step 2 (the pull under the lab-git lock, both lists pinned by
  count and bytes, the history check, the harness, the registration's checks and the scorer's self-checks, the preflight, the desk tests' logs;
  outside the kit's list); the look (k6's); the sync; the build; **step 6n**; **step 7, only once the rest has opened and within 30 minutes of
  6n**; the dry pass **and the scrub check**; the session; the wait; the copy-back; the data directory; the scorer after the data commit (with step
  6n's labels). **No post and no release** (waived). [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) is the card lanes' brief, with THE ONE-LAB RULE and
  THE QUIET HOLD in its step table; [`DATA-README-FORM-e213.md`](DATA-README-FORM-e213.md) is the data README's form.

## 2. Card-minutes and the cap (registered; arm A's smoke minutes by E213.md A1)

Arm A: 46.3 card-minutes planned (105 runs at 25.96 s a run, E207's measured rate on this card, and the smoke's four processes and the stop-path
test 0.89 min: E207's 0.67 for three, x 4/3; 46.1 before A1);
no run starts once the card time passes 60 minutes; at 70 the session ends after the run in progress. Arm B: 32.5 card-minutes planned (85 runs
at 22.22 s a run, E206 arm B's on card 1, and 1.0 min); no run after 42; the session ends at 48. A started run is cut only by a stop. The
registered subset if cut: the smoke, tie 1, pass 1 and tie 2 (arm A 92 runs, about 40.7 card-minutes; arm B 43). E213_BUDGET_S is the cap plus 5 minutes (4,500 s and
3,180 s); the registered last start G + 1:30 binds the launch.

## 3. The order on the box

The card lanes' full table, with the queue, the booking, THE ONE-LAB RULE, THE QUIET HOLD and the end of every path, is
[`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) section 2. The kit's steps (`<arm>` A or B; each step refuses a window written for the other arm):

| step | file | what |
|---|---|---|
| 0 | `E213_SEALED=W/out/orch/sealed-e213.txt rb/s00_step0_e213.sh <arm>` | read only, at the desk: S0 GitHub main; F1 the arm's freeze line an ancestor of GitHub main; F2 the kit commit; S1 THE SEALED-FORECAST CHECK; S2 the note's commits; D0 no datum of the arm (folder-level glob); G1 the clone clean |
| 1 | `rb/s02_window_e213.sh <arm> <day> <last start> <last end>` | today only; the window (G = the booking) in the arm's own RB_OUT |
| 2 | `rb/s03_desk_e213.sh <arm>` (outside the kit's list) | the window; the pull under the lab-git lock; the registration (subtree `75778ad3`) and the kit found by content, ancestors of HEAD, and arm A's freeze line `b1493082`; the paths clean; HISTORY OK; both lists at their pins; the harness; the three self-checks; the registration's checks and the scorer's three self-checks byte-identical; the preflight; the desk tests' logs; no datum of this arm in any ref (`:(glob)docs/reports/data/*e213*-<suffix>/**`), the other arm's and gate stops REPORTED |
| 4 | `../q141k-runbook/k6/s05_look_k6.sh <box>` | k6's, unchanged; our login recorded for the scrub |
| 5 | `rb/s07_sync_e213.sh <arm>` | the rsync into the box's tree (aifoundry3 `~/aifoundry`, aifoundry1 `~/nekko`); HARNESS OK on the box |
| 6 | `rb/s08_build_e213.sh <arm> start`, then `wait` | the detached build of both kernels, NO-THIRD-BUILD, the record (both KERNEL OK; arm B the whole ELF and ET_DEVICES), the harness, the preflight and both self-checks on the box |
| 6n | `E213_ROUND_OUT=<the round's OUT> rb/s06n_neverrun_e213.sh <arm>` | THE NEVER-RUN SEARCH, REPEATED, and its judgement; its NEVER-RUN-E213 line in RB_OUT |
| 7 | `rb/s09_reads_e213.sh <arm>` | 6n's report under 30 minutes old, then THE REST RULE on the box, no card command; then arm A k6's step 7 (TDP 0 W / 65 C / 600 MHz, et-who clean), arm B the card-1 read (TDP 65 W / 65 C / 600 MHz, minion_mv below 510, /dev/et1_mgmt and ID 1 alone, card 0 clean) |
| 8 | `rb/s10_dry_e213.sh <arm> start`, then `wait` | the runner on the box with its doubles, no device; then THE SCRUB CHECK on the dry pass's own records |
| 9 | `rb/s11_session_e213.sh <arm>` | the last start, the cap before the last end, today's 6n report, k6's guard, THE REST RULE, THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and build, then `session_e213.sh` detached |
| 10 | `rb/s20_wait_e213.sh <arm>` | the T0 the runbook launched; HUNG, K1, CRASHED and a gate stop are 16; ended (runner rc 0) 0; running 17 |
| 11 | `rb/s22_collect_e213.sh <arm>` | one read-only copy back, COPY-BACK EXACT, the box's home in every form |
| 12 | `rb/s23_data_e213.sh <arm>` | the data directory `docs/reports/data/<day>-e213-blind-matmul-<aifoundry3 / aifoundry1-c1>/` (or a gate stop's record), the scrub, the reducer, step 6n's report, judgement and labels, SHA256SUMS, the desk-path gate, the history check |
| 13 | `rb/s24_score_e213.sh <arm>` | after the data commit only: the labels checked, then score_e213.py (registered, unchanged) on the committed data-e213.json with `--labels` |

## 4. The readings stated here before any datum (where E213.md leaves a choice to the kit)

1. **THE DIE LINE'S "HOTTEST SENSOR" IS A LATCH** (E206.md amendment A1 item 1, which plan-e213.json adopts): each arm's line trips on the
   shires' mean (`minshire[0]`) at or above its stop (arm A 70 C, arm B 80 C), or on the latch (`minshire[2]`) only when it has risen during the
   session above the lowest value it read since the session's first sample and reads at or above the stop. On aifoundry3 card 0 the latch read
   87 C in every committed sample of E206 arm A; on card 1 E206 arm B's latch read 66 C at its highest (E213.md 6; the doubles read 87 C and 66 C). `e213_common.Stops`, E206's line for
   line.
2. **The board line**: strictly above the arm's watts (70 W, 72 W) on 3 samples in a row that carry a board reading (a sample with none neither
   counts nor breaks the row: E206.md A1 item 2). A trip touches the host's `--stop-file` at once (the host ends at its next launch boundary, about
   0.5 s), never a kill; nothing further starts. The 65 W planning line: no point's planning peak passes it (the self-check reads plan-e213.json).
3. **The smoke, then the stop-path test**: a rest read (the rest die: the median of the shires' mean over it; the die gate is formed from it),
   then one process of each smoke point (arm A s01 'rgm136 gemmL', s02 'rgm211 gemmLn', s03 'rgm136 gemmLnc', s04 'rgm211 gemmL'; arm B s11-s13 'rgm136 gemmL' in
   fp32, fp16 and int8, s14 'rgm136 gemmLnc'), **E206's form, `--seconds 2 --budget 3.5`**, each gated by its family first; each must read rc 0,
   counted launches, its check of C as the type gives it (approx for fp32 and fp16, exact for int8), the walk where its family has one, **the
   counter's mean (the median over counted launches) inside R0's absolute band, 200-4,000 cycles an op** (E213.md 7; the reducer hands the scorer
   the same number: RB-SMOKE), the board at least 2 W over the rest, and the host on the arm's card. Then the stop-path test (both lines trip a
   stand-in file in process; the start refused). **The family 'rgm211 gemmL' has its own smoke, s04** (E213.md A1, fix-e213; the orchestrator's
   answer 5), the last of arm A's, with its own stop path: a failure that is the family's alone (a GATE FAILED, a check of C wrong or missing, the
   walk check failed, a tensor error, a launch not ok, an exit not 0 but 124, the counter's mean outside 200-4,000, the board's rise short on a
   live sampler) drops the family - its runs never start, NO DATA - and the session goes on to the stop-path test and the runs; a failure that is
   the session's (K1, HUNG, rc 124, the host not shown on the arm's card, the sampler not live after s04) or any stop raised during s04 is the
   smoke gate, as at s01-s03. Every other smoke failure
   is the smoke gate (no run).
4. **THE IDENTITY GATE PER PROCESS BY THE POINT'S LOOP**: `ident_e213.FAMILY_KERNEL` maps each family to its ELF (rgm136 for 'rgm136 gemmL' and
   'rgm136 gemmLnc'; rgm211 for 'rgm211 gemmLn' and 'rgm211 gemmL'); the gate reads the process's `--kernel`: its `.text` always the pin, and
   either the whole ELF the pin or the loadable identity the pin (arm A; aifoundry3's gcc writes "(g1b306039a) 15.1.0" into `.comment`, a section
   the card never loads); **arm B requires the whole ELF** (E213.md 2; E206 arm B's committed build on aifoundry1 read rgm136's whole ELF
   `aace138c...`). The family is read from points-e213.json's "loop" field, never from the arm token (rgm211's gemmL spells its arm as rgm136's).
5. **THE WALK CHECK by family**: 'rgm211 gemmLn' walk nm, the tag on every hart (E211's); 'rgm136 gemmLnc' and 'rgm211 gemmL' walk mn, the tag on
   none; on every launch walk_ok true, and the check line's walk_launches_bad 0. 'rgm136 gemmL' (rgm136's host) prints no walk.
6. **THE KERNEL STOPS** apply to the three rgm211-host families; an 'rgm136 gemmL' process keeps E206's rules (a TERM'd run flagged and the session
   going on; two failed processes in a row stop it).
7. **The die gate**: arm A min(60, the session's rest die + 4) C, arm B min(63, rest + 3) C, waited at most 300 s, else that run is NO DATA.
8. **The start config** (read, nothing set): arm A TDP 0 W, threshold 65 C, minion 600 MHz; arm B TDP 65 W, 65 C, 600 MHz and minion_mv below 510
   (card 0 reads 519), PCIe target /dev/et1_mgmt and physical device ID 1 alone.
9. **ET_DEVICES**: on aifoundry3 unset (its one card; an inherited value dropped, a table setting it refused); on aifoundry1 `ET_DEVICES=1` on every
   device process (the guard refuses anything else), and a runtime line naming card 0 on any host is an identity stop.
10. **The rest rule** (before step 7's read and step 9's launch): every session-log form of ours on the box, fix-e202's activity floor, energy.sh's
    folders and the model session's `~/claude/work/ee-*/` folders; at least 40 minutes since the latest. On aifoundry1 it covers either card (one
    login, one tree).
11. **Step 0's sealed check**: a seal is "registered" when its sha256 appears in `tools/claims-v3/sealed-e213/e213-freeze-lines.md` at the lab
    clone's HEAD; the record's non-comment lines must read `E213 <sha256> ...`; an unreadable line is NOT AS STATED.
12. **Step 6n's judgement** (E213.md 4: "a record dated before its freeze line"): every file holding a scored point's token, found again by the
    scanner's own rules, is dated - a lab file by the commit that added it (its committer time), a lane file by its modification time - against the
    arm's freeze line (arm A `b1493082`'s committer time; arm B the registration commit's). A point with any counted file dated before it, a file
    that cannot be dated, or MM1-v3's measured points is labelled 'ran before' (the conservative side); a point whose every file is dated after it
    is REPORTED and kept. The scan is shape-level, so a token's label covers every scored point of the arm with that token. The labels are checked
    against points-e213.json before they are written and again at step 13 (LABELS-OK); the scorer takes them with `--labels`.
13. **The scrub**: every form of the box's home step 11 reads (`$HOME`, the user database's home, the home's physical path), the longest first,
    becomes "~"; our box login becomes "<login>"; another login's et-who holder line keeps its node, pid and time, its login becomes
    "<another-login>" and its command is dropped (fix-e213); then no file may hold a `/home/` path, any of those homes, the login, or a holder line
    naming any login but "<login>" or "<another-login>". Step 8 runs the same scrub
    on the dry pass's own records before the session (SCRUB-CHECK).
14. **Datum checks are folder-level**: an arm's datum is a commit on a `docs/reports/data` folder named `*e213*-<aifoundry3 / aifoundry1-c1>`
    (git's glob magic: `:(glob)docs/reports/data/*e213*-<suffix>/**`), so a file whose name merely holds "e213" is not one (section 5).

## 5. Found while kitting (REPORTED; for the verifier and the land lane)

- **E175's design tile names "e213"** (`docs/reports/data/2026-11-05-q143g-e175-design/candidates/tiles/fp16/fp16.e5c92_ar_k_t7_0e213f.bin`,
  commit `b3f5e83c7`): a plain pathspec `docs/reports/data/*e213*` matches it (fnmatch's `*` crosses `/`), so a datum check written that way
  reads one E213 "datum" before any exists. E213.md's sentence that no ref holds "a docs/reports/data/*e213* path" is true of folders and false
  of that file. The kit's checks (step 0's D0, step 2) use the folder-level glob; **the land lane's own check must too**
  (`:(glob)docs/reports/data/*e213*/**`). The runbook test's case GS commits a file of that form beside a gate stop's record: no datum, step 2 goes on.
- **The new family had no smoke process** (as kitted): 'rgm211 gemmL' first met a card in a scored run (a085, pass 1, run 074 on arm A's order).
  **Answered by fix-e213**: E213.md's Amendment A1 adds s04 with its own stop path (the kit notes above; section 4, item 3).
- **This desk's device layer carries no ET_DEVICES**, so arm B's build can pass only on aifoundry1 (whose device layer carries it: the look at
  21:39:38 PST; E206 arm B's committed build record) - the desk shows the gate refusing (B2, RB0, the runbook's BB), never passing.
- **All three boxes booted at about 16:46 PST Tue 17 Nov 2026** (aifoundry1 16:46:32, aifoundry3 16:46:07, aifoundry2 16:46:04, by `uptime -s`
  and the look): REPORTED for the readiness lane (a card's state after a boot is the readiness lane's to read: the config read at step 7 is the
  gate).

## 6. Files

The kit: `run_e213.py`, `session_e213.sh`, `e213_common.py`, `e213_ident.py`, `ident_e213.py`, `ettelem_guard_e213.sh`, `build_e213.sh`,
`check_e213.py`, `harness-e213.json`, `preflight_e213.sh`, `fake_card_e213.py`, `reduce_e213.py`, `collect_e213.py`, `desk/neverrun_card_e213.py`;
the desk tests: `selftest_run_e213.py`, `desk/realpath_e213.py`, `desk/realpath_e213.sh`, `desk/realbytes_e213.py`, `desk/desktest_build_e213.sh`,
`rb/selftest_rb_e213.sh`; the runbook: `rb/rb_e213.sh`, `rb/s00_step0_e213.sh`, `rb/s02_window_e213.sh`, `rb/s03_desk_e213.sh` (step 2: outside
the kit's list, which it pins), `rb/s06n_neverrun_e213.sh`, `rb/s07_sync_e213.sh`, `rb/s08_build_e213.sh`, `rb/s09_reads_e213.sh`,
`rb/s10_dry_e213.sh`, `rb/s11_session_e213.sh`, `rb/s20_wait_e213.sh`, `rb/s22_collect_e213.sh`, `rb/s23_data_e213.sh`, `rb/s24_score_e213.sh`,
`rb/rest_rule_e213.sh`, `rb/check_history_e213.py`, `rb/list_steps_e213.sh`; the documents: this file, `CARD-LANE-BRIEF.md`,
`DATA-README-FORM-e213.md`; the logs under `logs/`; and `SHA256SUMS-e213-kit` (49 entries: every kit file but itself and step 2; its own
sha256 is step 2's KITPIN).

## 7. Device commands

The session's only device commands are READs (dmcmd_audit_v2 GO on the session's files: 11 send sites, every one a READ, no WRITE allowed):
`ettelem config` and `ettelem sample --seconds N --every-ms 100` through the arm's guard (aifoundry3 with ET_DEVICES unset, aifoundry1 with
ET_DEVICES=1; anything else refused, exit 97), and the hosts' own runtime (rgm136's and rgm211's), each under a plain `timeout 10`. Every runtime
creation also sends the ops node's abort to every submission queue of every card the device layer enumerates (harmless on a card held alone; on
aifoundry1 ET_DEVICES=1 keeps it off card 0). No set, no reset, no statistics reset, no governor, TDP, threshold, clock or voltage change, no PMIC
command, no PCIe recovery, no driver reload, no power cycle, no firmware change: none is in the kit.

## 8. What the desk cannot show

- The cards themselves: their meters, their clocks, their temperatures, a launch that does not finish on silicon; every number here is the
  doubles'.
- The hosts' device path (the runtime's own opening of a card) past the refusals: the doubles and stand-ins stand in for it; the real-path test
  runs everything else.
- arm B's build passing the ET_DEVICES gate (only aifoundry1's device layer carries it) and aifoundry1's gcc writing the whole ELF the pin names
  (E206 arm B's committed build did); the build's own run on each box is step 6 on the card day.
- aifoundry3's and aifoundry1's own disks for step 6n (NOT SEARCHED, as registered).
- The model session's sealed forecasts: none was posted when this kit was written; step 0 reads them on the day.

## 9. Labels

Every figure here is **registered** (E213.md), a **desk check of code** (the tests above, on the doubles and stand-ins), or a **desk read** of
committed records (the real-bytes test, step 6n's scan). Nothing here is measured, blind, held out or post hoc.

## Compute

fix-e213's runs (Wed 18 Nov 2026): the registration's generators and checks three times between 01:41 and 02:17 PST (rules_e213 about a minute
each time); subsets of the runner's, the real-bytes and the real-path tests while fixing; two full passes of every desk test that found the last
two defects (02:05-02:12, stopped by the lane when the real path's RA11 read a sampler death inside s04, its launch count fixed for three smoke
processes; 02:19-03:08, whose runbook case BA found the common module's self-check reading rules-e213.json, a desk file, on the box); then every
desk test once more in its final form 03:10:01-03:59:29 PST Wed 18 Nov 2026 (one slot job at a time); no card time, no lab box. Before them, kit-e213's: aifoundry2's CPU through the round's slots (`W/slot.sh`, nice 10), one slot job at a time, single-threaded (OMP_NUM_THREADS, OPENBLAS_NUM_THREADS,
MKL_NUM_THREADS and NUMEXPR_NUM_THREADS 1), builds at -j2; `/usr/bin/python3` 3.12.3. The final runs, each its own slot job and one at a time: the runner 1,481 s (23:38:49 PST Tue - 00:03:30 PST Wed), the runbook 979 s (23:20:15-23:36:34), the real path 196 s, the checks 94 s (00:03:46-00:05:20 Wed), the real bytes 17 s, the build 15 s, step 6n 16 s, the dry listings 1 s: about 47 minutes of one slot. The development runs before them took about as long again (a full runner pass 22:31-22:56, a runbook pass 22:59-23:15, the real path twice, subsets). No card time; no CPU on a lab box (the two looks at 21:39:38 PST read files only).

SPDX-License-Identifier: Apache-2.0
