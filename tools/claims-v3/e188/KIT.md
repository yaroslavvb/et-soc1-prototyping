# E188's run kit: seven fp32 A B B A trains and two same-session kinds passes on aifoundry3 card 0 at 600 MHz, E182's host-only change built into its own directory and read from the built host's BEHAVIOUR (never grepped from its bytes), E183's rest rule over every session-log form of ours, the scorer for every rule, and october-forecast-model's reader behind a gate after the data commit (Q165; kitted, not run)

*Thu 12 Nov 2026 (week 46), PST, on the Intel, desk only (Q165, lane `kit-e188`): no card was claimed, no device command was sent, no lab
box was reached, nothing was posted, no Modal, no mordast. New files only, all under `tools/claims-v3/e188/`. The registration
[`E188.md`](E188.md) (`878b6f63`, git 12:53:42 PST) and every file its list names stay as committed (`SHA256SUMS-e188-registration`, 20 of 20
OK after this commit). This is E188.md section 13, step 3: the kit, ported from E186's kit (`tools/claims-v3/e186/`: KIT.md with its dated notes
1-4, the runbook as its note 4 runs it, KIT-BRIEF.md with its notes 1-4; run on aifoundry3 on Mon 9 Nov 2026, 98.2 card-minutes, every command
a READ), with E183's kit note 4's two lessons (`tools/claims-v3/e183/KIT.md.dated-note-4.md`, `24b9b99e`). No E188 datum exists. **Nothing here
changes a rule, a forecast, a threshold, a statistic, a registered power figure, the plan, a cap or a stop.** Where E188.md leaves a reading
to the kit, the reading is stated below before any datum (section 4).*

## Results first (desk checks of code; nothing is measured)

| check | result | log |
|---|---|---|
| **the train change's check on real builds**: the patched host (37ca98ad...), the C-logging host (Q139(k)'s patch alone) and E78's committed host, each built by g++-13 at -O2 and -O3 and by clang++ at -O1 and -O2 against the recording mock | **DESKTEST-TRAIN-CHECK-E188 PASS (50 of 50)**: the new check passes all four patched builds and fails all eight of the two negative controls ("unknown option --values-b"); no run of it reached a device call; the refusal a check must not use ("a train needs --launches") reaches the device layer, the runtime and the kernel load first on every patched build | [`logs/desktest-train-check-e188.txt`](logs/desktest-train-check-e188.txt) |
| the train host against the mock runtime (B05 both orientations, PAIR, AALL, B22; the refusals; a plain run; a re-paired launch on every train) | **DESKTEST-HOST-E188 29 of 29 PASS** | [`logs/desktest-host-e188.txt`](logs/desktest-host-e188.txt) |
| the scorer, the reductions, the pairing check and the copy-back (E186's committed data; synthetic sessions end to end through E78's reduction, E182's train reduction and the scorer) | **SELFTEST-SCORE-E188 20 of 20 PASS** | [`logs/selftest-score-e188.txt`](logs/selftest-score-e188.txt) |
| october-forecast-model's reader (v8 and v9) and its gate after the data commit, on synthetic sessions and a scratch repository | **SELFTEST-ARM-E188 14 of 14 PASS** | [`logs/selftest-arm-e188.txt`](logs/selftest-arm-e188.txt) |
| the rest rule on committed session logs of E182, E184, E185 and E186 at their box paths, E183's form as its kit note 4 writes it and E188's own; dry and no-device blocks; a cut session; the kits' markers; a shared day | **SELFTEST-REST-E188 PASS (20 of 20)** | [`logs/selftest-rest-e188.txt`](logs/selftest-rest-e188.txt) |
| the train runner's stops, live | **SELFTEST-STOPS-E188T 8 of 8 PASS** | [`logs/selftest-stops-e188t.txt`](logs/selftest-stops-e188t.txt) |
| the Intel dry pass (every train, every kinds pass of both families, the smoke, the refusals, the negative control's host, the queue's rules, the session's gates and manifest) with a REAL g++-13 -O2 train host | **DRY-INTEL-E188 PASS** | [`logs/dry-intel-e188.txt`](logs/dry-intel-e188.txt) |
| the runbook's desk test, fake ssh and rsync, a stand-in box whose cmake builds the host with g++-13 -O2 | **SELFTEST-RB-E188 21 of 21 PASS** | [`logs/selftest-rb-e188.txt`](logs/selftest-rb-e188.txt) |
| the dry listing, both paths | 19 steps, 0 exiting non-zero, 0 box calls (stand-in ssh, rsync and scp), rc 0 | [`logs/dry-listing-e188.txt`](logs/dry-listing-e188.txt) |
| `dmcmd_audit`, the session's files (`preflight_e188.sh`) | GO, 32 send sites, 0 disallowed, every one READ but E153's reviewed exception; without the exception NO-GO exactly at tools/claims-v3/lib.sh:154 | [`logs/dmcmd-audit-e188.txt`](logs/dmcmd-audit-e188.txt) |
| `dmcmd_audit`, the runbook with k6's look and reads and the guard | GO, 11 send sites, 0 disallowed, every one READ | [`logs/dmcmd-audit-rb-e188.txt`](logs/dmcmd-audit-rb-e188.txt) |
| `dmcmd_audit`, the desk files | GO, 0 send sites | [`logs/dmcmd-audit-desk-e188.txt`](logs/dmcmd-audit-desk-e188.txt) |
| the harness and the items | harness-e188.json re-made CHECK PASS (77 files); the items, images, orders and trains 0 problems; HARNESS OK 72 at the desk; NOTE1 FILES OK 10 | [`logs/harness-check-e188.txt`](logs/harness-check-e188.txt) |

- **The box kit, E186's form, for aifoundry3 card 0.** FULL (E188.md section 6): the stop-path test 18802, the smoke 18801 (the tie, E78's
  six anchors, E188's six new tiles at 2 s each, then two processes of B05's train, SFFS then FSSF: the train the kit names, the session's
  first), the first heat, **the kinds pass 18820, the seven trains 18810-18816 (B05, PAIR, B19, AALL, B10, B22, B04), then the kinds pass
  18821 only if its projected end fits** the cap less the reserve and the deadline. Each train between fp32.zeros and fp32.randn and the two
  reversed (E78 runs), 76 processes alternating from the registered first orientation, 13 launches a process after the calibration launch,
  every launch through Q139(k)'s C-logging wrapper, E171's live stops (65 W, 70 C on `minshire[0]`) and in-run watcher. A kinds pass is
  E178's form: the tie; three segments, each E78's six anchors then the eight kinds; the tie: 44 runs and two burn-ins. PASSES, the trains'
  registered fallback, is the five kinds passes 18830-18834 of the fifteen kinds (35 runs each). Every order is recomputed by rule and
  refused unless it equals `plan-e188.json` run for run.
- **THE TRAIN CHANGE IS READ FROM THE BUILT HOST'S BEHAVIOUR** (E183's kit note 4's lesson, binding here): [`train_check_e188.sh`](train_check_e188.sh)
  runs the host with every option of both patches (`--values-b`, `--abba`, `--launches`, `--c-log`, `--c-poison`) and an empty `--kernel`
  (rc 1 at "cannot read kernel ", nothing written, no device call: main.cpp 1093-1154 before Session's constructor at 1161), and each value
  option alone (rc 2, "<option> needs a value"). A host without E182's patch refuses `--values-b` in its options loop. **No string is grepped
  from any binary anywhere in this kit**: E186's build and block greps are replaced by this check (the build's last step, every block that
  runs the train host, the session before any device opens) and by every binary's sha256 against `harness-e188.json` (`check_e188.py`, in
  every block and at the session's start). On this Mac's desk, E186's greps all found their strings in the four patched builds, and missed
  `file:` in the C-logging host built by clang -O2 (reported in the desk test's log): the grep's verdict depends on the compiler, the
  behaviour's does not.
- **THE REST RULE over every session-log form of ours** ([`rb/rest_rule_e188.sh`](rb/rest_rule_e188.sh)): E183's kit note 4's rule, line for line
  but its words, sent by step 9 to the box after k6's guard and before the launch: no E188 launch within 40 minutes of the end of our last
  real session on aifoundry3, read from `build/e*/session.log`, `session-*.log`, `T*/session.log` and `T*/session-*.log` (E182's, E183's
  `session-t<T0>.log`, E184's `session-<arm>-t<T0>.log`, E185's, E186's and E188's `T<T0>/session.log`), dry and no-device blocks skipped by
  the kits' own markers only. On a shared day it makes E188 wait 40 minutes after E183's end.
- **The scorer** ([`score_e188.py`](score_e188.py)) reads every rule of E188.md section 5 with `e188_stats.py`'s and `e186_stats.py`'s words and
  `forecast_e188.lines_at`'s lines, imported unchanged: the same calls `power_e188.py` simulated (size_band, which, zscore, joint,
  models_word, held_part, mean_of, flat_q, per_bit, repeat). E188-SCHED (E186-PAIR's gate, renamed) is its pairing check
  ([`pairing_e188.py`](pairing_e188.py)) over every train block; E188-C its check of C; the kinds passes' contrasts are reported only.
- **october-forecast-model's reader** ([`arm_read_e188.py`](arm_read_e188.py)) reads v8 and v9 from the registered `ofm-e188.json` (pinned) as
  REPORTED arms, per item only (no summary), each item with its frozen label; **its gate** ([`rb/check_arms_e188.py`](rb/check_arms_e188.py))
  runs it only after E188's data commit, on the committed scored file, with the reader at the kit list's sha256, and writes its outputs only
  outside the repo: the tier keeps a reported arm's readings private (the private Horace Hub quotes their printed lines; public records name
  the arms by their committed files only). This departs from E186's form (its notes M1 and M2 wrote beside the data), on the tier of Thu 12
  Nov 2026.
- **The runbook** ([`rb/`](rb/)): E186's steps ported, each in the kits' form (k6's drivers, unchanged: the 15 s hard-killed probe, the read,
  copy, wait and launch bounds, the login-link stop with its line in `RB_LOCK`, exit codes 0/10/11/12/13/14/15/16/17), with the window
  written that day for E188, step 2's pull under the lab-git lock, every list pinned at its count and its own bytes (E188's kit list among
  them; lists found by "SHA256SUMS" anywhere in a name, an unknown one reported, never a gate), the history check in steps 2 and 11, step 5
  never beside a session or job of ours, step 6's detached build read by its behaviour, step 9's rest rule, step 11's exact copy-back.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md as E188.md section 1 read it (Thu 12 Nov 2026, about 12:35 PST): public rows H07, H08, H09,
   H24, H27, H28 (opaque pointers into a private inventory). Pieces newer than it are cited by commit: E186's kit (`523002be`, notes 1-4
   `88750359`, `565523d3` and their lists) and data (`b880ed63`, `c7786e5d`); E183's kit note 4 (`24b9b99e`); E182's kit (`41865c18` and notes
   1-4) and data (`0f6a8c45`); E188's registration (`878b6f63`).
2. **Used** (each unchanged, called, sourced or imported by path; sha256 in [`SHA256SUMS-e188-kit`](SHA256SUMS-e188-kit) or the lists step 2
   pins):
   - **E186's kit** (the form of every box and desk file here): its runners, block, queue, session, check, preflight, smoke gate, harness
     maker, reduction, C-session rule, pairing check, copy-back, collector, fake card, scorer's self-test, stops test, dry pass and runbook,
     each ported with E188's names. *Check against the same operation:* E186 ran this form on aifoundry3 on 9 Nov 2026; on E186's committed
     data E188's import of E182's `reduce_train` gives `trains-e186.json` to the last bit, the scale route reads E186's own s, the pairing
     check pairs every launch record E186-PAIR paired, and E186's committed SIZE and WHICH words are re-made by the same functions (the
     scorer's self-test, A1-A6).
   - **E183's kit note 4**: its train-change check's form (`train_check_e183.sh`), its desk test's form, its rest rule (`rb/rest_rule_e183.sh`,
     ported with its words changed only) and its desk cases.
   - **E182's host-only change** (`patch_host_e182.py`, `check_inputs_e182.py`, the build inputs' pins), its train reduction and statistics,
     its stand-in cmake's form; **E78's card code and reduction**; **Q139(k)'s check of C** (ccheck.py, the wrapper, the mock runtime);
     **`score_e178.session_scale`** (the scale route); **`ccsessions_p8.py`**; **k6's runbook drivers** (`rb_common.sh`, its look and reads;
     v3.1's `rb_run.py`); **Q136(w)'s `dmcmd_audit.py`** and **E128's guard**.
   - **E188's registration** (`878b6f63`): `plan-e188.json`, `kinds-e188.json`, `forecast-e188.json` (`lines_at`), `e188_stats.py`,
     `power-e188.json` (E186-GB's and E186-GA's references), `ofm-e188.json`, each checked against the registration's list first
     (`e188_common.check_frozen`).
3. **Not used:** card 1 and every other card; int8 and fp16 (none of E188's kinds); E186's notes M1 and M2 readers and gates (E188's arms
   have their own); anything of the october-forecast-model but `ofm-e188.json`'s registered figures; anything of mordast or the private tier.
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this kit.
5. **Readiness:** this block is the kit's. A verifier checks it against INVENTORY.md and the cited commits.

## 1. The two binding lessons, and the last kits' faults, item by item

| lesson or fault | here |
|---|---|
| **no check of a compiled binary by a string grep** (E183's two builds on Thu 12 Nov 2026; critic-q163's finding 2) | `train_check_e188.sh` (the build's last step, every train block's preflight, the session before any device); the other binaries by their sha256 (`check_e188.py`); desk test on 12 real builds with two negative controls; the dry pass and the runbook's test build with g++-13 -O2 and read the behaviour |
| **the rest rule reads every session-log form of ours** (E185's step 10 v2 never read E186's form; E183 had none until its kit note 4) | `rb/rest_rule_e188.sh` in step 9; desk cases for E184's, E185's, E186's, E182's, E183's (note 4's form) and E188's forms, a shared day, dry markers, a cut session (`rb/selftest_rest_e188.sh`); through the runbook (`rb/selftest_rb_e188.sh` RS) |
| the critic's "a train needs --launches" refusal is NOT safe (it comes after the device layer) | not used anywhere; the desk test shows it reaching `createPcieDeviceLayer`, `IRuntime::create` and `loadCode` first on every patched build |
| one copy of each C log; s02 before s03; the window written that day; its last start and last end read | E186's, kept |
| the pull under the lab-git lock | step 2's `e188_pull` (RB_GITLOCK required) |
| every list pinned at its count and its bytes, found by "SHA256SUMS" anywhere in a name | step 2: E188's registration 20; M12's 37, 24, 1, 9; E182's 32, 79, 50, 49, 89, 19; E186's registration 10; E186's data 376 and 6; the scale route's 209, 16, 9, 68, 10, 160; the kit's own list at its count and bytes (step 2 is outside it); any other list in E188's directory reported |
| a file changed and committed with its list line | the history check (`rb/check_history_e188.py`) in steps 2 and 11: no change but an addition since `878b6f63` on E188's paths (E188's, E186's, M12's, E182's, the runbook's and the workload's directories, and every file a list or the harness names), no shadowing addition, nothing uncommitted |
| step 5 beside a session of ours (E186's kit note 1) | step 5 reads `ours_live` and `jobs_live` first and refuses (10) |
| the pairing check over every train block (E186's kit note 1) | E188-SCHED in the scorer itself |
| an exact copy-back; never merge into an earlier copy | E186's: the session's manifest last, COPY-BACK EXACT before any reduction, a used output refused |
| the box build under a bound that covers it; the re-run rule; a cut call no reading | E182's v5 / E186's step 6, unchanged but for the behavioural check |
| a reported arm's reader behind a gate | `rb/check_arms_e188.py`, after the data commit only, its outputs outside the repo |
| the readers' interpreter pinned; the commit message scanned | every desk command names `/usr/bin/python3`; the commit's subject and body went through the public-text scan with the files |

## 2. Card-minutes and the caps (registered; unchanged)

| plan (`E188_PLAN`) | sequence | expected | cap (the budget rule) | the day's post says |
|---|---|---|---|---|
| **FULL** (default) | the stop-path test, the smoke, the first heat, 18820, 18810-18816, 18821 if it fits | **about 82.4 card-minutes** at E182's registered piece times; 91.3-92.8 at E186's measured block times | **100** (6,000 s from E188_T0, 60 s reserve) | `for 2 h` |
| PASSES (the fallback) | the stop-path test, the smoke's kinds items, 18830-18834 | about 27.6 | 40 (2,400 s) | `for 1 h` |

The queue projects a train at its plan estimate plus 30 s (608 s), or the longest train measured if longer, and a kinds pass at its plan's
estimate plus 30 s (FULL's 378.6 s read as 379, 409 s; the fallback's 304.5 s read as 305, 335 s) until one of its kind ends, then the longest
measured. A piece in flight is never cut; nothing is skipped ahead; 18821, last, starts only if it fits.

## 3. The order on aifoundry3, and the box steps

E188 runs alone on aifoundry3 card 0, after E183 on any shared day, never while another session of ours runs on the box; `et-who` clean; an
idle login does not block (D1, the owner's ruling of 1 Nov 2026). The day's one post follows the one-post rule. Run from the lab clone, each
step with this day's `RB_OUT` (outside the repo), the one `RB_LOCK` and, for step 2, `RB_GITLOCK`. The card lane's brief is
[`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md).

| KIT.md box step | file | what |
|---|---|---|
| 1, the window | [`rb/s02_window_e188.sh`](rb/s02_window_e188.sh) `<day> <last start> <last end>` | FIRST; today's day only |
| 2, the desk check | [`rb/s03_desk_e188.sh`](rb/s03_desk_e188.sh) | the window; the pull under the lab-git lock; ancestry; the paths clean; the history check; every list at its pins; the harness rebuilt; the items, images, orders and trains; HARNESS OK 72; NOTE1 FILES OK 10; the plan and forecast re-made; the statistics' self-check; the desk tests' logs; E188 data in any ref reported |
| 4, the look, FIRST | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` | k6's, unchanged |
| 3, the post, after the look | (the card lane's) | `using aifoundry3 for 2 h, until ~HH:MM PST [doc](...)` |
| 5, the sync | [`rb/s07_a3_sync_e188.sh`](rb/s07_a3_sync_e188.sh) | the box read first (never beside a session or job of ours), then every file of `harness-e188.json` but what the box builds |
| 6, the build and the box's checks | [`rb/s08_a3_build_e188.sh`](rb/s08_a3_build_e188.sh) `start`, then `wait` while it says 17, or 14 with "no reading" (or `--no-trains`) | the detached build job (its last step the behavioural check), then NOTE1 FILES OK 10, HARNESS OK 79, TRAIN-CHANGE OK, the preflight GO and the verify, each its own 60 s read |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | k6's, unchanged |
| 8, the dry pass | [`rb/s10_a3_dry_e188.sh`](rb/s10_a3_dry_e188.sh) `start`, then `wait` (or `--no-trains`) | 18810, 18811, 18820, the smoke, the start gate's 8 (the fallback: 18830, the smoke without trains, the gate) |
| 9, the session | [`rb/s11_a3_session_e188.sh`](rb/s11_a3_session_e188.sh) `FULL yes` (or `PASSES no`) | the guard, THE REST RULE, the dry pass and (with trains) the build of today, then `session_e188.sh` detached: the check, the train host's behaviour, the preflight, the stop-path test, the smoke and its two gates, the first heat, the queue, the manifest last |
| 10, the wait | [`rb/s20_wait_e188.sh`](rb/s20_wait_e188.sh), while it says 17 | the T0 the runbook launched; the manifest written |
| 11, the release, then the collection | [`rb/s22_collect_e188.sh`](rb/s22_collect_e188.sh) | the copies by name and the day's step-6 record, COPY-BACK EXACT, the history check, `collect_e188.sh` (the check of C, the trains, the anchors, the kinds passes, the scorer with E188-SCHED), the C-session gate, the desk-path gate, the login scrub |
| after the data commit | [`rb/check_arms_e188.py`](rb/check_arms_e188.py) | october-forecast-model's reader through its gate, its outputs outside the repo |

The fallback, as it runs: step 6 names it after two builds that did not read TRAIN-HOST-BUILT -> step 6 `--no-trains` (HARNESS OK 76) ->
step 7 -> step 8 `start --no-trains`, `wait --no-trains` -> step 9 `PASSES no` -> steps 10 and 11. Inside FULL, a failed train gate of the
smoke turns the queue to PASSES. Every train rule then reads NOT SCORED and E188-LV is the reading. The output is
`build/e188-out/<day>-e188-one-number-r4-aifoundry3/`, the data directory `docs/reports/data/<day>-e188-one-number-r4-aifoundry3/`.

## 4. The scorer's readings, stated here before any datum (where E188.md leaves a choice)

- **The scale s** (section 4.2's order): the trains' own anchor runs (`reduce_e188.py anchors`: every train block's a0 and a1 as one E78 pass,
  E78's reduction together on E182's footing, `--leak 0.20563713796102187 --no-refit`, dips removed once) through `score_e178.session_scale`;
  if they give none, the session's kinds passes' reduction the same way; if neither, s = 1 and every word built on a line carries "s unread
  (1 used)". "Gives none" is an exception in the reading or a reading that used no float anchor. E188 does not fail closed on s (section 4.2).
- **The measured rate:** a train's `rate_per_s` from `reduce_e188.py trains` (its own launch records, E186's rule) over forecast-e188.json's
  `rate_fp32_per_s`; ratio 1 when none. On E186's committed fp32 trains it reads 1.0016-1.0017 of that rate (the self-test's A3).
- **A train scored:** C all PASS (E188-C), paired (E188-SCHED), 8 units or more; else NOT SCORED in every word.
- **E188-GB1** over the five one-bit B trains when all five are scored; with fewer, over those scored if at least three (section 5.3's words);
  **E188-BPOS** over the same, at least three; **E188-GA23** from AALL over 23 bits; their REPEAT references are `power-e188.json`'s
  `e186_gb` and `e186_ga` (E186-GB's and E186-GA's measured intervals as the registration froze them).
- **E188-M** over every scored train, PAIR included, at the chi-square point for n scored trains; the joint words over the six trains other
  than PAIR are reported.
- **E188-TR-N:** the quads' residual sd pooled over the scored trains against 0.03804 W.
- **E188-LV** (the fallback only, no train scored, two or more kept fallback passes): the fifteen kinds with two or more kept passes and every
  launch PASS, M10's level P10 x s x q and M12's P10 x s x q + (M12_w - P10_w); `random.Random(18860)`'s 2,000-draw bootstrap. In FULL its
  arithmetic over the eight kinds is reported only.
- **The kinds passes (FULL's, reported only):** a kind's per-segment contrast D(kind) - D(fp32.ones) over the kept segments of the kept passes,
  the mean with t(0.975, n - 1); the tie: its mean over a pass's two runs less fp32.ones' and less the pi x pi tile's means over the pass; BALL
  - AALL beside E182's T5 interval; T5's halves across sessions beside M10's BALL offset plus 23 x E188-GB1.

## 5. Files, and what each builds on

| file | what | builds on |
|---|---|---|
| `e188_common.py` | the items (E78's and the 13 committed tiles), each kind's words against its image, the trains, the smoke, both families of kinds pass, the frozen checks | `e186_common.py`; `plan-e188.json`, `kinds-e188.json` |
| `run_e188.py`, `run_e188t.py` | the kinds runner (E78's unchanged, E171's stops and watcher) and the train runner | E186's two |
| `train_check_e188.sh` | the train change read from the host's behaviour | E183's `train_check_e183.sh` |
| `build_host_e188.sh` | E186's build into `build/e188host/`, its last step the behavioural check | `build_host_e186.sh` |
| `block_e188.sh`, `queue_e188.sh`, `session_e188.sh` | one block (a train, a kinds pass of either family, the smoke, the stop-path test), the plan's budget, the session with its manifest | E186's three |
| `check_e188.py`, `preflight_e188.sh`, `smoke_gate_e188.py` | the harness check (and the train host), the device-command preflight, the smoke gate (kinds and train parts) | E186's three |
| `harness-e188.json`, `make_harness_e188.py` | the sha256 of everything the box runs or reads (77) | E186's |
| `reduce_e188.py` | the trains (E182's `reduce_train`), the trains' anchors (E78's reduction), the kinds passes of one family | `reduce_e186.py` |
| `ccsessions_e188.py`, `collect_e188.sh`, `score_e188.py`, `pairing_e188.py`, `copyback_e188.py` | the C-session rule, the collection, every rule, E188-SCHED, the exact copy-back | E186's |
| `arm_read_e188.py`, `rb/check_arms_e188.py`, `selftest_arm_e188.py` | october-forecast-model's reader, its gate, their self-test | E186's note M2 reader and gates |
| `fake_card_e188.py`, `selftest_score_e188.py` | synthetic sessions in the box's layout and the scorer's self-test | E186's |
| `desk/mock_rt_e188.cpp`, `desk/desktest_train_check_e188.sh` | the check of C's mock with a device record; the train change's desk test on 12 real builds | ccheck's mock; E183's desk test |
| `desktest_host_e188.sh`, `.py` | the train host against the mock runtime | E186's |
| `selftest_stops_e188t.py`, `dry_intel_e188.sh` | the train runner's stops, live; the Intel dry pass | E186's |
| `rb/` | steps 1, 2, 5, 6, 8, 9, 10, 11, the rest rule, the history check, the dry listing, the desk tests, the stand-in cmake, the closure trace | E186's runbook, E183's note 4 |
| `CARD-LANE-BRIEF.md` | the card lane's brief for the day | E186's KIT-BRIEF and E183's brief notes |
| `logs/` | every check below | |
| `SHA256SUMS-e188-kit` | the kit's files (step 2 aside), its logs and the unchanged files it calls (106) | |

## 6. The checks, and what they ran

The table in "Results first". Every one ran on the Intel through the round's slot, one job at a time, at nice 10; none reached a box or a card.
Step 2 for real on this commit, check_day2_v2, E183's step 2 v5 and E183's anchor lines 1-6 are the land's checks (the lane's result).

## 7. Device commands

`dmcmd_audit.py` on the session's file set: GO, 32 send sites, 0 disallowed, every one a READ but E153's one reviewed exception
(`lib.sh:154`, the forwarded `--reset-ms` E188 never passes); without the exception, NO-GO exactly at `lib.sh:154`. E188's new box file `train_check_e188.sh` sends nothing: its runs stop before any device call (the desk
test's device record is empty on every build). The runbook with k6's look and reads and the guard (GO, 11 send sites, 0 disallowed, every one READ); the desk files (GO, 0 send sites). No
set, no reset, no statistics reset, no firmware query of any kind; nothing near card 0's 75 W alarm.

## 8. What the desk cannot show (for the verifier and the readiness critic)

1. **The train host's first compile on the box** is step 6 there (`build/e188host/`). E186's build of the same source on the same box read
   TRAIN-HOST-BUILT on 9 Nov; the behavioural check then reads the box's own GCC binary (its compiler line is in the build's configure log,
   copied by step 11). The desk built with Homebrew GCC 13.2 and Apple clang 21; the box's GCC is the box's.
2. **The libraries' load-time behaviour** is read from the open source (E183's kit note 4's reading, et-platform `836a4ab`), not from the
   box's `/opt/et`.
3. **The scale from the trains' anchors** has run on E186's committed fp32 trains and on synthetic sessions, not on an E188 session.
4. **The collector** has run on synthetic sessions through its reductions and the scorer, and the runbook's step 11 on a staged session
   (its copies and COPY-BACK EXACT, stopped by design at the C gate). None has run on a card's raw tree of E188.
5. **The arms' gate** has run on a scratch repository; its first real run is after E188's data commit.
6. Card time waits on his go, after E183's on any shared day (`CARD-LANE-BRIEF.md`).

## 9. Labels

Every figure quoted from E188.md, its registration files, E186's and E182's kits (the plan, the caps, the stops, the trains, the pins) is
**registered**. The checks on E186's committed data are **post hoc** checks of code, deciding nothing. The desk tests' results are **desk
checks of code**, not measurements: nothing here is **blind** or **held out**, and no E188 datum exists. october-forecast-model's arms are
**reported** arms.

## Compute

On the Intel through the round's local slot (`slot.sh`), one job at a time, at nice 10: twelve host builds for the train check's desk test (a
few minutes), the host desk test, the scorer's and the reader's self-tests (synthetic sessions), the stops test, the rest rule's test, the dry
pass (two host builds) and the runbook's desk test (a scratch repository of the files step 2 reads, a stand-in box, about ten g++-13 builds).
No bench job, mini, lab box or card was used. The desk tests wrote only under the round's scratch.

SPDX-License-Identifier: Apache-2.0
