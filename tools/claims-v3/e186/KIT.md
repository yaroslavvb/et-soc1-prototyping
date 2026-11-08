# E186's run kit: ten A B B A trains on aifoundry3 card 0 at 600 MHz (the fp16 swap H16 first), E182's host-only change built into its own directory, the session's float scale read from the float trains' own anchors, an exact copy-back against the session's manifest, and the scorer for every registered rule with note M1's reader after it (Q158; kitted, not run)

*Sun 8 Nov 2026 (week 45), PST, on the Intel, desk only (Q158, lane `kit-e186`): no card was claimed, no device command was sent, no lab
box was reached, nothing was posted. New files only, all under `tools/claims-v3/e186/`. The registration [`E186.md`](E186.md) (`a41408d9`,
git 07:15:08 PST), its dated note M1 ([`E186.md.dated-note-M1.md`](E186.md.dated-note-M1.md), `3adb8bfe`) and the merged list
(`tools/claims-v3/m12/`, `80d53792`) stay as committed, with every file their hash lists name (10, 5 and 24 OK after this commit). This is
E186.md section 12, step 4: the kit, ported from E182's kit (`tools/claims-v3/e182/`: KIT.md with its dated notes 1-4, the runbook as its
note 4 runs it, the card lane's brief with its notes 1-2). No E186 datum exists. **Nothing here changes a rule, a forecast, a threshold, a
statistic, a registered power figure, the plan, a cap or a stop.** Where E186.md leaves a reading to the kit, the reading is stated below
before any datum (section 4).*

## Results first

- **The box kit, E182's form, for aifoundry3 card 0.** The ten trains 18610-18619 run in E186.md's rank order (H16, S23, Q63-sign,
  Q63-swap, B15-B7, B23-B15, Q3-sign, Q3-swap, A15-A7, A23-A15), each between its format's zeros and random anchor and the two reversed
  (int8 trains with int8.zeros and int8.full, fp32 with fp32.zeros and fp32.randn, the fp16 train with fp16.zeros and fp16.randn), its
  64 (int8) or 76 (float) processes alternating from the registered first orientation, 13 launches a process after the calibration
  launch, every launch through Q139(k)'s C-logging wrapper, E171's live stops (65 W, 70 C on `minshire[0]`) and in-run watcher. FULL is
  the ten trains and no kinds pass (cap 100 card-minutes); PASSES, the trains' registered fallback, is five kinds passes 18620-18624 of
  the fallback's 15 kinds (cap 40); before either, the stop-path test 18602 and the smoke 18601 (the tie, E78's six anchors, four of
  the session's kinds, then two H16 processes), gated as E182's smoke with its train part.
- **The train host is E182's** host-only change (`tools/claims-v3/e182/patch_host_e182.py`, unchanged), built on the box by
  [`build_host_e186.sh`](build_host_e186.sh) into `build/e186host/` from the same nine pinned inputs (E182's `check_inputs_e182.py`,
  unchanged): its patched source's sha256 is the one E182 registered and ran. The patch is type-blind, so **the fp16 train runs the same
  host**: [`desktest_host_e186.sh`](desktest_host_e186.sh) builds it against the check of C's mock runtime and runs H16 in both
  orientations, S23, B15-B7, Q63-sign and Q3-swap: **DESKTEST-HOST-E186 31 of 31 PASS** ([`logs/desktest-host-e186.txt`](logs/desktest-host-e186.txt)).
- **A limit of the check of C, found here (D8, D9):** in six of the ten trains - the two float swaps (H16, S23) and the four int8 trains,
  whose two kinds share one product (Q3 and Q63, swap and sign) - the two kinds' C are equal word for word (a x b = b x a, and the
  products are exact), so a C record re-paired to the other kind's tiles still reads PASS. E186-C checks those launches' arithmetic, not
  which tile set each ran; their pairing rests on the host's own record (`train_kind`, `train_values`, the C record's fnv), which the
  smoke's train gate reads against the schedule on H16 and the trains' reduction requires on every process. E182's int8 and fp32 swaps
  had the same property. On a ladder train the re-paired launch reads not PASS (D7: ROUNDING, which the registered rule never counts).
  No rule changes.
- **The session's float scale in FULL** (E186.md section 4.2) is read from the float trains' own anchor runs:
  [`reduce_e186.py anchors`](reduce_e186.py) makes each float train's four anchor runs one E78 pass and runs E78's reduction, unchanged,
  over them together on E182's registered footing, and `score_e178.session_scale` reads s from fp32.randn and fp16.randn. **On E182's
  committed fp32 trains (T5, T6) the route keeps both passes and reads s = 1.01360 from fp32.randn, beside E182's own s = 1.00947 read
  from its kinds passes** (post hoc, a check of code; [`logs/selftest-score-e186.txt`](logs/selftest-score-e186.txt) A1). Fail closed: an
  exception, or no float anchor used, is "s not read".
- **The scorer** ([`score_e186.py`](score_e186.py)) reads every rule of E186.md section 5 with `e186_stats.py`'s words and
  `forecast_e186.lines_at`'s lines, both imported unchanged, and writes `scored-e186.json` in E182's form, which note M1's reader reads
  after it. **SELFTEST-SCORE-E186 16 of 16 PASS**: on E182's committed data (the scale route; E182's `reduce_train` through E186's import,
  equal to the last bit; the trains' measured rate from their own records, 1.0003-1.0016 of the candidates' rates); and on synthetic
  sessions in the box's layout that run end to end through E78's reduction, E182's train reduction, the scorer and note M1's reader: M12's
  world, M10's, the fp16-scaled arm's, doubled noise, a short train, a C FAIL, no anchors (fail closed), the fallback's levels, the
  C-session list, the smoke's H16 gate, the exact copy-back, and the 15 kinds' images.
- **The exact copy-back** (new in E186; verify-k4's fault 2 on E184's step 11): the session's last act on the box is
  `build/e186/T<T0>/MANIFEST.sha256`, the sha256 of every file of its own directory and of every block directory it ran; step 11 copies
  exactly those by name and [`copyback_e186.py`](copyback_e186.py) reads every line back: **COPY-BACK EXACT**, or DIFFERS, EXTRA or
  NO-MANIFEST and the step stops before any reduction.
- **The runbook** ([`rb/`](rb/)): E182's note-4 steps ported, with the window rule (a window written that day, for E186; every box step
  reads its last start or its last end), step 2's pull under the lab-git lock, every list pinned at its count and its own bytes, step 6's
  detached build under its 500 s bound (a 90 s stand-in build runs past one read's 60 s, waited on; a cut check read is no reading; a lost
  job is a build's failure), the history check in steps 2 and 11, and step 11's exact copy-back and note M1's reader through its gate.
  **SELFTEST-RB-E186 19 of 19 PASS**
  ([`logs/selftest-rb-e186.txt`](logs/selftest-rb-e186.txt)); the dry listing, both paths, 19 steps, 0 failing, no call
  ([`logs/dry-listing-e186.txt`](logs/dry-listing-e186.txt)); **DRY-INTEL-E186 PASS** ([`logs/dry-intel-e186.txt`](logs/dry-intel-e186.txt));
  **SELFTEST-STOPS-E186T 8 of 8 PASS** ([`logs/selftest-stops-e186t.txt`](logs/selftest-stops-e186t.txt)).
- **The history check** (new here: verify-d2b's faults 1-3 on the day-2 kits, Q158b, which E185's kit note 3 answers with its day-2
  check, `1e74546a`, git 08:37:53 PST): [`rb/check_history_e186.py`](rb/check_history_e186.py) is that check in E186's form. The kit's own
  list is pinned at its count only (it lists step 2), so a kit file (E186's scorer, its brief) rewritten together with its line would
  pass step 2. Step 2, and step 11 before any scoring, now refuse any change but an addition since E186's registration (`a41408d9`) on
  E186's paths (E186's, M12's, E182's, the k6/v3.1 runbook's and the workload's directories and every file outside them that a list E186
  reads or the harness names), any added file that shadows a module, and anything uncommitted there; note M1's reader runs only through
  its gate (its list at its count and own bytes, every entry OK, its files unchanged, nothing written beside its two outputs).
  **SELFTEST-HISTORY-E186 10 of 10 PASS** on a sparse local clone of the lab's own history
  ([`logs/selftest-history-e186.txt`](logs/selftest-history-e186.txt)); its T1 re-makes the fault (after a scorer edit with its line
  rewritten, the kit's list reads as before at its count; the check refuses it). T1's baseline is the kit's list as it stood when the
  test ran (71 entries, before this check's three files joined it; the list is made last, over every log).
- **Device commands: `dmcmd_audit.py` GO, 32 send sites, 0 disallowed, every one READ** but E153's one reviewed exception (`lib.sh:154`,
  the forwarded `--reset-ms` E186 never passes: without it the audit reads NO-GO exactly there); E186's desk files send nothing; the
  runbook's steps with k6's look and reads and the guard: GO, 11 sites, every one READ (section 6). No set, no reset, no firmware query of
  any kind.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sun 8 Nov 2026 at about 08:12 PST. Public rows read: H07, H08, H09, H24, H27, H28.
   The row ids are opaque pointers into a private inventory. Pieces newer than it are cited by commit: E182's kit (`41865c18`, notes 1-4
   `6c158cd2`, `22da6a7b`, `e0d31903`, `6b2d2ae6`) and data (`0f6a8c45`); E185's kit note 1 (`ad2ed873`, the exact copy-back's form);
   E184's step 11 v4 (`8092c27a`) and its verifier's faults (Q157 verify-k4); E186's registration (`a41408d9`), note M1 (`3adb8bfe`) and
   merged list (`80d53792`).
2. **Used** (each unchanged, called, sourced or imported by path; sha256 in [`SHA256SUMS-e186-kit`](SHA256SUMS-e186-kit) or the lists
   step 2 pins):
   - **E182's kit** (the form of every box and desk file here, H27's descendant): its patch and build inputs' check, its train reduction
     (`reduce_train`), its sync-list reader, its stand-in cmakes, its fake card's model of a train's board readings. *Check against the
     same operation:* E182 ran this form on aifoundry3 on 8 Nov 2026 (98.1 card-minutes, every command a READ, C 8,820 of 8,820 PASS);
     its train reduction, called through E186's import on E182's committed T1 and T5 blocks, gives `trains-e182.json`'s estimates to the
     last bit.
   - **E78's card code and reduction** (H07) and the C-logging host and kernel E182 ran (H08, H09: the check of C, accum.c and the mock
     runtime), through `make_harness_e186.py`, which refuses unless every value equals E182's harness.
   - **`score_e178.session_scale`** (pool 8's predictor route, H24): the session's float scale. *Check:* on E182's committed fp32 trains'
     anchors it reads s = 1.01360 against E182's 1.00947 from its kinds passes (0.4% apart; post hoc).
   - **`ccsessions_p8.py`** (Q142(k6)), imported unchanged with E186's layout; **the k6 runbook's v3 drivers** (`rb_common.sh`, its look
     and reads; v3.1's `rb_run.py` and `nopath_q142s.py`), sourced unchanged; **Q136(w)'s `dmcmd_audit.py` and E128's guard** (H28).
   - **E185's exact copy-back** (`collect_e185_v2.sh`, its manifest and its check), its form only; **E185's day-2 check**
     (`rb/check_day2_v1.py`, kit note 3, `1e74546a`), its tree checks and its M1 gate in E186's form, with **verify-d2b's** faults 1-4
     and nits 5, 6, 8 and 9 (section 1). *Check against the same operation:* its T1 re-makes verify-d2b's H2d on E186's own list.
   - **E186's registration** (`a41408d9`): `plan-e186.json`, `forecast-e186.json` (`lines_at`), `e186_stats.py`, `power-e186.json`, each
     checked against the registration's hash list first (`e186_common.check_frozen`); the merged list (`kinds-m12-e186.json`, M12's
     tiles) against M12's list for E186.
3. **Not used:** card 1 and every other card; E184's and E185's kits' code beyond the copy-back's form and the day-2 check's; the PVT sampler; E182's seven
   reduction arms (E186 registers none); anything of the october-forecast-model but note M1's committed reader.
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this kit.
5. **Readiness:** this block is the kit's. A verifier checks it against INVENTORY.md and the cited commits.

## 1. Kit v5's lessons and the faults the last kits' verifiers found, item by item

| lesson or fault | here |
|---|---|
| one copy of each C log | `collect_e186.sh` copies each listed session's C log once, gzipped, to `ccheck/`, and the session directories without it |
| s02 before s03, and the window written that day | step 2 and every E186 step that starts something on the box or copies from it call `e186_window`: RB_OUT's `window.env` written today (Pacific), naming today, written for E186 (W1-W3); the wait reads the T0 the runbook launched today |
| the window's last start and last end read (verify-k4 fault 3) | the sync, the build, the dry pass and the launch read the last start; the launch reads the plan's budget before the last end; the collection's copies start at least 600 s before it (C4) |
| the pull under the lab-git lock (verify-k4 fault 6) | step 2's pull runs under `lockf -k -t 600 $RB_GITLOCK`; without RB_GITLOCK it refuses (G) |
| every list pinned at its count and its bytes (critic-q155, verify-d2) | step 2 pins eleven lists by count and own sha256 (E186's registration 10; M12's 37, 24, 1, 9; E182's 32, 79, 50, 49, 89, 19) and the kit's own at its count, 74 (P1-P4); note M1's list (5) and any later M-note's are read and REPORTED, never a gate |
| a file changed and committed with its list line, past a count-only pin; a committed change to the brief unseen (verify-d2b faults 2, 3) | the history check in step 2 (H1) and in step 11 before any scoring (C): no change but an addition since `a41408d9` on E186's paths (T1, T2, T6), no added file that shadows a module or shares a module name (T3, T4), nothing uncommitted (T5), HEAD descending from it (T9) |
| note M1's reader behind a gate weaker than step 2's pin (verify-d2b fault 1) | step 11 runs it only through `check_history_e186.py m1`: its list at 5 and its own bytes, every entry OK, its files and list unchanged since the registration, then note M1's own run line bounded at 50 s, and nothing written beside its two outputs (T7, T8); the gate's refusal and the reader's are recorded, never a stop; a reader that wrote anything else stops step 11 (16) before the data commit |
| the brief named actions for some step-2 stops only (verify-d2b fault 4) | the brief: anything but 0 from step 2 is no box step that day, whatever it names (status, ancestry, history, a list, the harness, a log), with one exception: a pull whose output shows the upstream did not answer (step 2 again once it answers; a diverged or detached clone is no exception); a 13 or 11 is k6's (run the step again; approve first); every step-2 pull is under the lab-git lock (G) |
| "wait while it says 17 or 14" also caught a 14 that is no cut call (verify-d2b nit 5) | section 3 and the brief: step 6's `wait` while it says 17, or 14 with "no reading"; any other 14 names what to read |
| "never a gate" holds for committed M1 changes only (verify-d2b nit 6) | the same here: an uncommitted change to note M1's files stops step 2 (its paths-clean read); a committed one is reported (T7) |
| datelines ahead of the clock (verify-d2b nit 8) | this kit quotes git's times for every commit it names; its own commit's time is git's |
| scans without the lab scanner's private table (verify-d2b nit 9) | the same here: this machine holds no private table, so the scan read the fixed list only (a records line) |
| an exact copy-back (verify-k4 fault 2) | the session's manifest and COPY-BACK EXACT before any reduction (C, C3) |
| never merge into an earlier copy (verify-k4 fault 4) | step 11 refuses a used `build/e186-raw/` or output (C2); the session refuses a box that already holds an E186 block directory |
| the box build under a bound that covers it (E182 notes 2-4) | step 6 is E182 v5's: one detached job under `timeout -k 15 500`, each check in its own 60 s read, the re-run rule, a cut call no reading |
| never beside a session of ours | k6's `ours_live` in steps 6, 8 and 9 (O) |
| the scale read fail-closed (critic-q156's kit nit) | section 4 |
| the readers' interpreter pinned | every desk command names `/usr/bin/python3` (3.9, numpy for the scale) |
| the commit message scanned | this commit's subject and body went through the public-text scan with the files |

## 2. Card-minutes and the caps (registered; unchanged)

| plan (`E186_PLAN`) | sequence | expected | cap (the budget rule) | the day's post says |
|---|---|---|---|---|
| **FULL** (default) | the stop-path test, the smoke, then 18610-18619 in rank order, no kinds pass | **about 93 (94 with the reserve)**; 89-99 at E182's measured block times | **100** (6,000 s from E186_T0, 60 s reserve) | `for 2 h` |
| PASSES (the fallback) | the stop-path test, the smoke's kinds items, 18620-18624 | about 28 | 40 (2,400 s) | `for 1 h` |

The queue projects a train at its plan estimate plus 30 s (or the longest train measured, if longer) and a kinds pass at
`plan-e186.json`'s 304.5 s plus 30 s (335 s, the same rule; E182's 640 s was a 70-run pass) until one ends, then the longest measured.
A piece in flight is never cut; nothing is skipped ahead. At E182's longest measured times the queue stops before A23-A15 (E186.md
section 7), and E186-GA then reads A15-A7 alone.

## 3. The order on aifoundry3, and the box steps

E186 runs alone on aifoundry3 card 0, after day 2 (E185, then E183 after E185's step 14), never while another session of ours runs on the
box; `et-who` clean; an idle login does not block (D1, the owner's ruling of 1 Nov 2026). The day's one post follows the one-post rule.
Run from the lab clone, each step with this day's `RB_OUT` (outside the repo), the one `RB_LOCK` and, for step 2, `RB_GITLOCK`. The k6
drivers bound every remote call: a 15 s hard-killed probe, then 60 s for a read, 600 s for a copy. A printed login link stops the step (11)
and appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`.

| KIT.md box step | file | what |
|---|---|---|
| 1, the window | [`rb/s02_window_e186.sh`](rb/s02_window_e186.sh) `<day> <last start> <last end>` | FIRST; today's day only |
| 2, the desk check | [`rb/s03_desk_e186.sh`](rb/s03_desk_e186.sh) | the window; the pull under the lab-git lock; ancestry; the paths clean; the history check; the lists at their pins; the harness rebuilt; the items, images, orders and trains; HARNESS OK 71; NOTE1 FILES OK 10; the plan and forecast re-made; the desk tests' logs; note M1 reported |
| 4, the look, FIRST | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` | k6's, unchanged |
| 3, the post, after the look | (the card lane's) | `using aifoundry3 for 2 h, until ~HH:MM PST [doc](...)` |
| 5, the sync | [`rb/s07_a3_sync_e186.sh`](rb/s07_a3_sync_e186.sh) | every file of `harness-e186.json` but what the box builds |
| 6, the build and the box's checks | [`rb/s08_a3_build_e186.sh`](rb/s08_a3_build_e186.sh) `start`, then `wait` while it says 17, or 14 with "no reading" (or `--no-trains`) | the detached build job, then NOTE1 FILES OK 10, HARNESS OK 78, the preflight GO and the verify, each its own 60 s read |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | k6's, unchanged |
| 8, the dry pass | [`rb/s10_a3_dry_e186.sh`](rb/s10_a3_dry_e186.sh) `start`, then `wait` (or `--no-trains`) | 18610 (fp16), 18611, 18612, 18620, the smoke, the start gate's 8 |
| 9, the session | [`rb/s11_a3_session_e186.sh`](rb/s11_a3_session_e186.sh) `FULL yes` (or `PASSES no`) | launches `session_e186.sh` detached: the check, the preflight, the stop-path test, the smoke and its two gates, the first heat, the queue, the manifest last |
| 10, the wait | [`rb/s20_wait_e186.sh`](rb/s20_wait_e186.sh), while it says 17 | the T0 the runbook launched; the manifest written |
| 11, the release, then the collection | [`rb/s22_collect_e186.sh`](rb/s22_collect_e186.sh) | the copies by name, COPY-BACK EXACT, the history check, `collect_e186.sh` (the check of C, the trains, the anchors, the fallback's passes, the scorer), the C-session gate, the desk-path gate, the login scrub, note M1's reader through its gate |

The fallback, as it runs: step 6 names it after two builds that did not read TRAIN-HOST-BUILT -> step 6 `--no-trains` (HARNESS OK 75) ->
step 7 -> step 8 `start --no-trains`, `wait --no-trains` -> step 9 `PASSES no` -> steps 10 and 11. Inside FULL, a failed train gate of the
smoke turns the queue to PASSES. Every train rule then reads NOT SCORED (E186.md section 7). The output is
`build/e186-out/<day>-e186-one-number-r3-aifoundry3/`, the data directory `docs/reports/data/<day>-e186-one-number-r3-aifoundry3/`. The
card lane's brief is [`KIT-BRIEF.md`](KIT-BRIEF.md).

## 4. The scorer's readings, stated here before any datum (where E186.md leaves a choice)

- **The measured rate** (E186.md section 4.2, "from its own launch records"): a train's `rate_per_s` from `reduce_e186.py trains`, over
  the processes with 13 launches, the mean of the work of launches 0-12 (iters x minions, from their own records) over the time from
  launch 0's start to launch 12's end; the candidates' rate when none. On E182's six committed trains it reads 1.0003 (int8) and 1.0016
  (fp32) of the candidates' rates.
- **The scale in FULL** (section 4.2): the float trains' anchor runs (H16's fp16 and the five fp32 trains'), one E78 pass a train, E78's
  reduction together on E182's footing (`--leak 0.20563713796102187 --no-refit`, dips removed once), then `score_e178.session_scale`. In
  PASSES, the kinds passes' reduction, as E182.
- **s not read** (section 4.2's fail-closed clause): an exception in the scale's reading, or a reading that used no float anchor (the
  predictor's own "1 if none" is never taken as a reading). Then the four ladder trains (B15-B7, B23-B15, A15-A7, A23-A15) read NOT
  SCORED in every word built on a line (SIZE against M12, SIZE against M10, WHICH) and their z enters no joint word; E186-GB and E186-GA
  read NOT SCORED; their SIGN words stand. E186.md says that nothing else depends on s; E186-M's z for those four does (their M10 lines
  carry P10's offset times s), so the kit leaves them out of E186-M too, the one reading under which nothing scored uses an unread s.
  **A point for the verifier:** this reading is the kit's, stated before any datum; it changes no rule's words.
- **E186-M:** the session trains other than H16 whose SIZE words are scored; the joint words over all ten, and by family, are reported.
- **E186-TR-N:** the quads' residual sd pooled by family, int8 and float (fp16 with fp32), as `power_e186.py` pools them.
- **E186-LV** (the fallback only): the 15 kinds with two or more kept passes and every launch PASS, at the session's s and each kind's
  measured rate: M10's level P10 x s x q (int8 s = 1); M12's float level P10 x s x q plus its increment; M12's int8 level its flip part
  x q plus the rest, moved by the registered anchor D(int8.full, the session) - 7.16439 W; `random.Random(18660)`'s 2,000-draw bootstrap.
- **E186-C:** a launch's verdict is the check of C's for the same t_start_ms and t_end_ms; a train's anchors' launches count for it; a
  train with any launch not PASS is NOT SCORED. For the six trains whose two kinds give the same C (section "Results first"), PASS
  checks the arithmetic, not the pairing.
- **Reported, never a verdict:** E186.md section 5.4's list (each train's carry-over, halves, orientation means, anchors' levels, the
  minion rail, the process period; the joint Q's; gamma_B / gamma_A; each train's lines at s = 1 and at the candidates' rates).

## 5. Files, and what each builds on

| file | what | builds on |
|---|---|---|
| `e186_common.py` | the items (E78's and M12's 14 tiles), each kind's image against its words, the ten trains, the smoke, the fallback's orders, the frozen checks | `e182_common.py`; `plan-e186.json` |
| `run_e186.py`, `run_e186t.py` | the kinds runner (E78's unchanged, E171's stops and watcher) and the train runner | E182's two |
| `build_host_e186.sh` | E182's v2 build into `build/e186host/` | `build_host_e182_v2.sh` |
| `block_e186.sh`, `queue_e186.sh`, `session_e186.sh` | one block (a train, a fallback pass, the smoke, the stop-path test), the plan's budget, the session with its manifest | E182's three |
| `check_e186.py`, `preflight_e186.sh`, `smoke_gate_e186.py` | the harness check (and the train host), the device-command preflight, the smoke gate (kinds and train parts) | E182's three |
| `harness-e186.json`, `make_harness_e186.py` | the sha256 of everything the box runs or reads (E182's called files and the build inputs among them) | E182's |
| `reduce_e186.py` | the trains (E182's `reduce_train`), the float trains' anchors (E78's reduction), the fallback's passes | `reduce_e182.py` |
| `ccsessions_e186.py`, `collect_e186.sh`, `score_e186.py`, `copyback_e186.py` | the C-session rule, the collection, every rule, the exact copy-back | E182's; E185's copy-back |
| `fake_card_e186.py`, `selftest_score_e186.py` | synthetic sessions in the box's layout (anchors as E78 runs) and the scorer's self-test | E182's |
| `desktest_host_e186.sh`, `.py` | the train host against the mock runtime, the fp16 train first | E182's |
| `selftest_stops_e186t.py`, `dry_intel_e186.sh` | the train runner's stops, live; the Intel dry pass | E182's |
| `rb/` | steps 1, 2, 5, 6, 8, 9, 10, 11, the dry listing, the desk test | E182's note-4 runbook (k6's drivers) |
| `rb/check_history_e186.py`, `rb/selftest_history_e186.sh` | the history check and note M1's reader gate; its desk test on the lab's own history | E185's `check_day2_v1.py` |
| `KIT-BRIEF.md` | the card lane's brief for the day | E182's brief and its notes 1-2 |
| `logs/` | every check below | |
| `SHA256SUMS-e186-kit` | the kit's files, its logs and the unchanged files it calls (74) | |

## 6. The checks, and what they ran

| check | result | log |
|---|---|---|
| the train host against the mock runtime (H16 both orientations, S23, B15-B7, Q63-sign, Q3-swap; refusals; a plain run; the tampers) | **DESKTEST-HOST-E186 31 of 31 PASS** | `logs/desktest-host-e186.txt` |
| the scorer, the reductions and the copy-back (E182's committed data; synthetic sessions end to end through the scorer and note M1's reader) | **SELFTEST-SCORE-E186 16 of 16 PASS** | `logs/selftest-score-e186.txt` |
| the train runner's stops, live | **SELFTEST-STOPS-E186T 8 of 8 PASS** | `logs/selftest-stops-e186t.txt` |
| the Intel dry pass (every train, every fallback pass, the smoke, the refusals, the queue's rules, the session's gates and manifest) | **DRY-INTEL-E186 PASS** | `logs/dry-intel-e186.txt` |
| the runbook's desk test, fake ssh and rsync, a stand-in box | **SELFTEST-RB-E186 19 of 19 PASS** | `logs/selftest-rb-e186.txt` |
| the history check and note M1's gate, on a sparse local clone of the lab's history (T0-T9) | **SELFTEST-HISTORY-E186 10 of 10 PASS** | `logs/selftest-history-e186.txt` |
| the dry listing, both paths | 19 steps, 0 failing, no call, the look before the post | `logs/dry-listing-e186.txt` |
| the harness check | HARNESS OK 71 (desk); the harness rebuilt CHECK PASS; NOTE1 FILES OK 10; the items 0 problems; every list E186 reads OK | `logs/harness-check-e186.txt` |
| `dmcmd_audit`, the session's files | GO, 32 sites, 0 disallowed, every one READ but the excepted `lib.sh:154` | `logs/dmcmd-audit-e186.txt` |
| `dmcmd_audit` without the exception | NO-GO exactly at `lib.sh:154` | `logs/dmcmd-audit-noexcept-e186.txt` |
| `dmcmd_audit`, the desk files | GO, 0 sites | `logs/dmcmd-audit-desk-e186.txt` |
| `dmcmd_audit`, the runbook with k6's look and reads and the guard | GO, 11 sites, every one READ | `logs/dmcmd-audit-rb-e186.txt` |

## 7. What the desk cannot show (for the verifier and the readiness critic)

1. **The train host's first compile on the box** is step 6 there (`build/e186host/`). E182's build of the same source on the same box read
   TRAIN-HOST-BUILT in 3 s on 8 Nov (00:13:48-00:13:51 PST; post hoc, E182's data `logs/e182-build-attempts.txt`), so the job's 500 s
   bound covers it with a wide margin; if E186's fails twice, the fallback runs to its end.
2. **The fp16 train's first launches on the card** are the smoke's two H16 processes; its train gate checks their schedule, tiles, rates
   and C records before any train runs.
3. **The scale from the trains' anchors** has run on E182's real anchors (T5, T6) and on synthetic sessions, never on an fp16 train's
   real anchors: the first is the session's H16.
4. **The collector** (`collect_e186.sh`) has run once at the desk on a synthetic raw tree in a scratch copy of the lab tree: its train
   and anchor reductions, then the scorer, which refused (4) at the C-session gate by design, the synthetic blocks holding no C log. The
   scorer and the reductions have run end to end on synthetic sessions (the scorer's self-test), and the runbook's step 11 on a staged
   session (its copies and COPY-BACK EXACT, stopped by design at the C gate). None has run on a card's raw tree.
5. **The swap trains' pairing** rests on the host's record (section "Results first").
6. The october-forecast-model: note M1's reader runs after the score; v4 covers none of the session's trains. A later note (M2) may add a
   later version's forecasts only before the first datum, with its own reader; step 2 reports its list and never gates on it.
7. Card time waits on his go (`KIT-BRIEF.md`).

## 8. Labels

Every figure quoted from E186.md, its note M1, the merged list and E182's kit (the plan, the caps, the stops, the trains, the pins) is
**registered**. The checks on E182's committed data (the scale route, the rate, the train reduction) are **post hoc** checks of code,
deciding nothing. The desk tests' results are checks of code at the desk, not measurements: nothing here is **blind** or **held out**, and
no E186 datum exists.

## Compute

On the Intel through the round's local slot (`slot.sh`), one job at a time, at nice 10: the harness and audits (seconds); the host desk
test (about 30 s: one compile against the mock runtime and ten runs); the scorer's self-test (about 40 s); the stops test (seconds); the
Intel dry pass (about 3 minutes); the runbook's desk test and dry listing (a few minutes); the history check's desk test (about 20 s,
on a sparse local clone of the lab clone in the scratch, never pushed). No bench job, mini, lab box or card was used.
The desk tests wrote only under the round's scratch.

SPDX-License-Identifier: Apache-2.0
