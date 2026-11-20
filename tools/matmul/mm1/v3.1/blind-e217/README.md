# blind-e217: the lab's BLIND test of its frozen matmul models on E217, declared and frozen before any E217 datum

E217 is the model session's fourth matmul sweep (1119-mmsweep4; proposal #13 on the coordination Discussion, named E217 in #13.1): E136's rgm136 unchanged, 331 arms and an anchor in seven sessions on aifoundry1 (card 1 S1-S4 at 600 MHz, card 0 S1-S3 at low power), including 1x1x1 cells at 12 new core-group masks a card and 24 operand-pattern tiles of 2,048 bytes. This folder holds the lab's declaration of how it will score its own frozen models on E217, the forecasts frozen at nominal conditions, and the switch counts of E217's 21 new tile kinds, all made at the desk on aifoundry2 before any E217 session ran. Nothing here is a measurement.

**Label: BLIND.** BLIND: MM1-v3.1 (2c971828), MM1-v3 (b1493082), MM1-v2 (3ca4b717), the contention term F1 (#1.29.1), verify-lay's controls (#1.29.1.1) and the gemmLnc term (#1.29) frozen and unchanged, this declaration and the nominal forecasts hashed and frozen (FROZEN.txt, posted by the orchestrator) before any E217 datum exists. A session whose first datum precedes the freeze post is UNREAD for it.

## The order of hashes and times (Pacific, Thu 19 Nov 2026; logs/progress.txt)

- Thu 19 Nov 2026 11:36:23 PST step 01 DECLARED (rc 0): DECLARED-blind-e217.md 099806dc1a5cb6c53ed7ea0645d5e2b3ae55e0d7734872a467019222da324405, DECLARED-blind-e217.json 633d725620d06295a144312956579fabc54462f109ea3a29e8026d992bdd4eb7 (written 11:35:59 PST); every step-1 file and script in logs/step1-sha256.txt (sha256 111937947f50bfcde24770d4c9351c3061d738eaea46bce52556c4d735b2ac47); no E217 datum exists (e217-releases.txt: the proposal and the naming only; no claim file; no quiet-desk flag)
- Thu 19 Nov 2026 11:37:24 PST step 02 FORECAST (rc 0): nominal forecasts made 11:36:27-11:37:07 PST in one slot job (fc-nominal.json 2842d09e88cec63ed1d6de5d4cbdf8310d162f4d0132e7ae5a0cc215d1dc1b0f; 486 cases x 9 models; checks before any output: F1 re-made its 94 frozen E215 rows (factor diff 4.0e-10), the controls re-made v02_e215_controls.csv's N3, N1+N2, G1, G1+N1 columns (worst 5.0e-5 cycles, 4-dp rounding); energy FORECAST v3.1 451 / v3 451 / v2 433, NOT FORECAST the 35 group-S cases (no count yet) and v2's 18 C cases); forecasts-nominal-e217.csv 4725efa361c16059bae8a5182a5455718ca1d053633293474668983370cdb3e6, forecasts-nominal-e217.json 611ca08d27c81f0972e5d2b1f23ac24d0455a602cfe87a665963d83af1fdc97c (written 11:37:13 PST); step-2 files in logs/step2-sha256.txt (sha256 e45e688ec492cab21b6593642df8f129d90bf41e83c4d87066e79da51bdc53e7); no E217 datum exists
- Thu 19 Nov 2026 11:37:53 PST step 03 FROZEN.txt written (rc 0): 32311daf2e0ace10d4efdce2be7a3248fb82b2ab852c0acc45fa6c6f37bd42a8 FROZEN.txt; the freeze line = DECLARED-blind-e217.md 099806dc..., DECLARED-blind-e217.json 633d7256..., forecasts-nominal-e217.csv 4725efa3..., forecasts-nominal-e217.json 611ca08d...; for the orchestrator to post on the Discussion (#13); e217-releases.txt: no claim at the freeze
- Thu 19 Nov 2026 11:54:52 PST counts-e217 s06b re-counts vs committed v3.1 rows: VERDICT: MATCH  rc=0
- Thu 19 Nov 2026 12:11:48 PST counts-e217 s07 new fp32 counts at GEMM states (10 kinds, S1 and S2, jobs 1) (slot job from Thu 19 Nov 2026 11:54:52 PST) rc=0
- Thu 19 Nov 2026 12:21:27 PST counts-e217 s08 new fp16/int8 counts at the launch points (11 tiles, jobs 1) (slot job from Thu 19 Nov 2026 12:11:48 PST) rc=0
- Thu 19 Nov 2026 12:22:02 PST step 04 COUNTS made (rc 0): counts-e217 by the RTL bench in 9 slot jobs, 41.42 slot-minutes, 11:38:15-12:21:27 PST; re-count MATCH 1971/1971 leaves bit-equal (11:54:52); new-fp32-S1.json dc8fcfcb52607b4c25da0c1f08907f383ccfd7e1ee97f1515cc5a421e33f57b7 (ended 12:03:22), new-fp32-S2.json 1c7bea3ba0887980a56117c409fda5accc92f45f33becf7fa428cca67e84cc37 (ended 12:11:48), new-launch.json 934eccaf6879a0020be3766b3d05e63c838116fd7d3096e231761d4d8fa0fbb1 (ended 12:21:27); tables counts-fp32-gemm-states.json 0169d260348ae8b0ae8a540f1c702ff2e931577215d5d60ba887447cc13893c2, counts-fp16-int8-launch.json 6509e20d4fe21c942fdb89d7feaa0479e3b7efac847a0561405dfae9cd65f1f0 (12:21:27); merge check: 26 new (format, kind, KB) cells return a count, 107 committed cells unchanged, problems 0; every check_mismatch 0; no E217 measurement read
- Thu 19 Nov 2026 12:22:02 PST step 04c group S nominal energy with counts-e217 (MM1-v3.1, own process) (slot job from Thu 19 Nov 2026 12:22:02 PST; load 5.67) rc=0
- Thu 19 Nov 2026 12:22:07 PST step 04c group S nominal energy with counts-e217 (MM1-v3, own process) (slot job from Thu 19 Nov 2026 12:22:07 PST; load 5.78) rc=0
- Thu 19 Nov 2026 12:22:08 PST step 04c merge (the composed forms; the files) (slot job from Thu 19 Nov 2026 12:22:07 PST; load 5.78) rc=0
- Thu 19 Nov 2026 12:22:24 PST step 04c group S nominal energy with counts-e217 (rc 0): fc-counts-v31.json 05131274e15e0a3f16081d19722a1170a0df134bda4a2ae77bbfd5e3760c87ec (MM1-v3.1 + 31 rows; the 8-case bit-for-bit check of the lab's kinds held), fc-counts-v3.json c7eb86ac5759191d6fb776bae9e836d20db46a8edd5870699270ec50bf6e9e3f (MM1-v3 + 3e8991d0's 39 and counts-e217's 31 rows), each in its own process; forecasts-nominal-e217-counts.csv 305e23efa918fedba666fb4f4996f09dd1d2dee8ab996c6f8a79fe9b49efc78c, .json 590c0be2ebb30bd07fd89b6d22bd182eb5415134807ca8afde06d67952065353 (12:22:08 PST): 35 of 35 group-S cases FORECAST; the declared gate with the frozen literal and the count-implied gate REPORTED beside (count valid share: gt125 0.125, gt25 0.25, gt875 0.875, h_gt25 0.2258 against declared g_op 0.8125, 0.625, 0.125, 0.75)
- Thu 19 Nov 2026 12:22:24 PST step 04 COUNTS-FROZEN.txt written (rc 0): 4867c1d0be500da2f2d2a7a8fd757a1b893b92d802616b2195f10a34bcc89e01 COUNTS-FROZEN.txt; for the orchestrator to post on #13; e217-releases.txt: 2 post lines, no claim
- Thu 19 Nov 2026 12:25:45 PST counts-e217 s06b and s09b re-run for their labels only (12:26 PST; they read counts-e214's 'counts-e214'/'E214' wording): the same VERDICT MATCH and the same merge summary (26 new cells, 107 unchanged, problems 0); recount-check.json now 6d3449e05c0b060e..., merge-check.json b331cf477ed9a529...; neither file is in COUNTS-FROZEN.txt's freeze line; rc=0

## The freeze line (FROZEN.txt)

FROZEN.txt and COUNTS-FROZEN.txt name the lane's own paths: here `work/step1/` is `inputs/step1/`, `work/step2/` is `inputs/step2/`, `work/step4/` is `inputs/step4/`, `cnt/counts/` is `counts-e217/` and `cnt/work/counts/` is `counts-e217/raw/`; every file keeps its bytes.

```
decl-e217 (round Q228): the lab's BLIND test of its frozen matmul models on E217 (#13, 1119-mmsweep4), DECLARED and its nominal forecasts FROZEN at Thu 19 Nov 2026 11:37:53 PST, before any E217 datum exists.
Models frozen and unchanged: MM1-v3.1 2c971828, MM1-v3 b1493082, MM1-v2 3ca4b717, 'v3.1 + contention' F1 (#1.29.1), verify-lay's controls N1+N2, G1, G1+N1 and the layout-blind F1 (#1.29.1.1), 'v3.1 + both' (= F1 here); 'v3.1 + gemmLnc' NOT APPLICABLE (E217 runs no gemmLnc arm).
Scope: 599 runs (544 arm + 55 anchor) in 486 cases over E217's seven sessions (aifoundry1 card 1 S1-S4 at 600 MHz, card 0 S1-S3 low power), from the kit copy out/orch/e217-src (SRC-SHA256SUMS.txt 854bd075...).
sha256 (the freeze line):
099806dc1a5cb6c53ed7ea0645d5e2b3ae55e0d7734872a467019222da324405  DECLARED-blind-e217.md
633d725620d06295a144312956579fabc54462f109ea3a29e8026d992bdd4eb7  DECLARED-blind-e217.json
4725efa361c16059bae8a5182a5455718ca1d053633293474668983370cdb3e6  forecasts-nominal-e217.csv
611ca08d27c81f0972e5d2b1f23ac24d0455a602cfe87a665963d83af1fdc97c  forecasts-nominal-e217.json
supporting (the makers and their records):
0a13366ace4d819e22aac98d1055e1a4a08bfb7085f2c5cdab25879cc7e00f0b  scripts/s02b_nominal.py
023231764a69015a4dee3000521a3264ef5227a3261282c0952a0b0efcb140bc  scripts/s02w_walk.py
c4a1273acd59590f555e911a5743e21fa723e22628fa5de8e55afcaedb780cfe  scripts/s02c_write.py
2842d09e88cec63ed1d6de5d4cbdf8310d162f4d0132e7ae5a0cc215d1dc1b0f  work/step2/fc-nominal.json
6c65696dfe40bbdc69097ea5f4b05b980ee09d270f69dfdae029b102fac2bba0  work/step2/walk-feats-e217.json
111937947f50bfcde24770d4c9351c3061d738eaea46bce52556c4d735b2ac47  logs/step1-sha256.txt
e45e688ec492cab21b6593642df8f129d90bf41e83c4d87066e79da51bdc53e7  logs/step2-sha256.txt
Times (Pacific): declared 11:35:59 (hash logged 11:36:23); nominal forecasts made 11:36:27-11:37:07, files written 11:37:13 (hash logged 11:37:24); this file Thu 19 Nov 2026 11:37:53 PST.
State at the freeze: out/orch/e217-releases.txt holds 2 post lines (the last: '#13.1 2026-11-19 11:14:42 PST: the lab n...'), 0 claim files in out/orch; no E217 session has run, so no E217 datum exists.
Label rule (the declaration's section g): BLIND for a session whose first datum comes after this freeze is posted; a session whose first datum precedes the post is UNREAD for it (POST-READ if a lab lane read its data first).
Still to come (step 4): counts-e217, the switch counts of E217's 21 new tile kinds from the tile files alone (RTL bench, Verilator 5.042), then COUNTS-FROZEN.txt; group S's switch-route energy takes COUNTS-FROZEN.txt's post time by the same rule.
```

## The counts freeze line (COUNTS-FROZEN.txt)

```
decl-e217 (round Q228) step 4: counts-e217, the switch counts of E217's 21 new tile kinds, FROZEN at Thu 19 Nov 2026 12:22:24 PST, made from the kit's tile files alone (no E217 measurement read).
Bench: rtl-sim/fma_toggle_v2 at GitHub main 8bde0182, Verilator 5.042 (-j 2, make -j 1), one bench process, inside slot.sh + nodev.sh; counts-e214's scripts and rules.
Re-count first: VERDICT: MATCH  (two committed MM1-v3.1 rows of 3e8991d0 in each footing; cnt/counts/recount-check.json).
each count (sha256, file, the time its bench run ended):
dc8fcfcb52607b4c25da0c1f08907f383ccfd7e1ee97f1515cc5a421e33f57b7  cnt/work/counts/new-fp32-S1.json  (fp32 at S1, 10 kinds x 4 points; ended Thu 19 Nov 2026 12:03:22 PST)
1c7bea3ba0887980a56117c409fda5accc92f45f33becf7fa428cca67e84cc37  cnt/work/counts/new-fp32-S2.json  (fp32 at S2, 10 kinds x 4 points; ended Thu 19 Nov 2026 12:11:48 PST)
934eccaf6879a0020be3766b3d05e63c838116fd7d3096e231761d4d8fa0fbb1  cnt/work/counts/new-launch.json  (fp16 5 and int8 6 tiles x 3 launch points; rc 0, Thu 19 Nov 2026 12:21:27 PST)
the tables (the models' row form) and their sums:
0169d260348ae8b0ae8a540f1c702ff2e931577215d5d60ba887447cc13893c2  cnt/counts/counts-fp32-gemm-states.json
6509e20d4fe21c942fdb89d7feaa0479e3b7efac847a0561405dfae9cd65f1f0  cnt/counts/counts-fp16-int8-launch.json
bc569673fa05893bfc0df45e2fa9f980aeda35cf1d9b8953b4c7cb733af27416  cnt/counts/counts-e217.csv
133a8cd6841e02862f95a6509e9f1217fd122c8e1a7b35a2520401309348f742  cnt/counts/counts-e217-tiles.csv
group S's nominal energy with the counts (the declaration's section h):
305e23efa918fedba666fb4f4996f09dd1d2dee8ab996c6f8a79fe9b49efc78c  forecasts-nominal-e217-counts.csv
590c0be2ebb30bd07fd89b6d22bd182eb5415134807ca8afde06d67952065353  forecasts-nominal-e217-counts.json
the makers: 56309408f537c1b5b462cf578906889e0f345405b546b28619509b8dbf636364 scripts/s04c_nominal_counts.py
The freeze before it: FROZEN.txt 32311daf2e0ace10d4efdce2be7a3248fb82b2ab852c0acc45fa6c6f37bd42a8 (declaration 099806dc... / 633d7256..., nominal forecasts 4725efa3... / 611ca08d..., 11:37:53 PST).
State at this freeze: out/orch/e217-releases.txt holds 2 post lines (the last: '#13.1 2026-11-19 11:14:42 PST: the lab names it E217 (regist...').
Label (the declaration's section g): group S's switch-route energy is BLIND for a session whose first datum comes after this file is posted; UNREAD for one whose first datum precedes the post if no lab lane had read its data first; else POST-READ (REPORTED).
```

## What is declared (DECLARED-blind-e217.md; the JSON is the machine form)

- **The runs:** 599 runs ({'anchor': 55, 'arm': 544}) in 486 cases, by id from the kit's schedules; the 1x1x1 cells (X1), the new core-group masks (MG), the other subset masks and the full chip apart; group S (the 21 new tile kinds), group C (the sparse50 pools) and the lab's kinds apart; configuration twins apart.
- **The quantities:** wall cycles (T1), the counter mean (T2), seconds (T3), J over idle given t (E1) and with t forecast (E2), J at rest given t (E3) and with t forecast (E4), per card, format and kind.
- **The models:** MM1-v3.1; MM1-v3; MM1-v2; v3.1+contention; v3.1+gemmLnc; v3.1+both; controls (see the declaration for each one's call and form).
- **The forecast procedure:** each frozen predictor unchanged at each run's measured clock, minion volts and die at start, read from the data's start-of-run records only (MM1-v3 README section 5's form, as unread-e214 did); a second footing, the nominal forecasts here, scored beside.
- **The comparisons:** exact sign tests per case (MM1-v3.1 vs MM1-v3, vs MM1-v2; the contention term and each of verify-lay's controls vs MM1-v3.1 on the subset-mask cases; the switch route with the counts vs the null on group S).
- **The pass rule:** part A (MM1-v3.1 within E215's bands on 90% of each card's no-twin cases, every rule) and part S (the switch test P1-P4), decided by the scoring lane's script, hashed before its first read.

## The nominal forecasts (forecasts-nominal-e217.csv / .json)

- Conditions: {"aifoundry1 card 0": {"V": null, "f": 800.0, "t0_c": 55.0}, "aifoundry1 card 1": {"V": 0.517, "f": 600.0, "t0_c": 60.0}}.
- 486 cases x 9 models: MM1-v3.1, MM1-v3, MM1-v2, v3.1+contention, v3.1+both, ctrl N1+N2, ctrl G1, ctrl G1+N1, ctrl F1-layout-blind.
- Energy: {"MM1-v2": {"FORECAST": 433, "NOT FORECAST": 53}, "MM1-v3": {"FORECAST": 451, "NOT FORECAST": 35}, "MM1-v3.1": {"FORECAST": 451, "NOT FORECAST": 35}, "v3.1+contention": {"FORECAST": 451, "NOT FORECAST": 35}} (group S's 35 cases have no energy at the first freeze: no count yet).
- Checks before any output: the contention term re-made its 94 frozen E215 rows (factor difference 4.0e-10); verify-lay's controls re-made its E215 columns (worst 5.0e-05 cycles, the CSV's rounding).
- Factor ranges on the subset masks: {"ctrl F1-layout-blind": [0.9372, 1.0293], "ctrl G1": [0.9907, 1.0294], "ctrl G1+N1": [0.9617, 1.0375], "ctrl N1+N2": [0.9815, 1.0199], "v3.1+contention": [0.9703, 1.0139]}.
- Group S with counts-e217 (forecasts-nominal-e217-counts.*): 35 cases, energy {"FORECAST": 35}; the declared gate for the four zero-row tiles beside the frozen code's literal (REPORTED); the count's valid share beside each declared share: {"fp16|pattern:h_gt25": {"count_valid_share": {"launch": 0.2258168452707702}, "declared_g_op": 0.75}, "fp32|pattern:gt125": {"count_valid_share": {"S1": 0.125, "S2": 0.125}, "declared_g_op": 0.8125}, "fp32|pattern:gt25": {"count_valid_share": {"S1": 0.25, "S2": 0.25}, "declared_g_op": 0.625}, "fp32|pattern:gt875": {"count_valid_share": {"S1": 0.875, "S2": 0.875}, "declared_g_op": 0.125}}.

## The counts (counts-e217/)

Made exactly as counts-e214 made E214's (its scripts, under scripts/cnt/ here): the RTL bench rtl-sim/fma_toggle_v2 built with Verilator 5.042 (Verilator -j 2, make -j 1), single-threaded, one bench process, inside slot.sh and nodev.sh; the functional check first; the net maps trained on this binary; two committed MM1-v3.1 rows re-counted first and matched; then fp32 at the GEMM accumulator states S1 and S2 (count_e210.py) and fp16 and int8 at the harness launch points (run_kinds.py).
- Re-count check: pass True (VERDICT: MATCH (every rule quantity within 0.999-1.001, every check 0 or as committed, same tiles, depths and points)).

| fmt | kind | state | fin edges lo / hi a MAC | valid share | points |
|---|---|---|---:|---:|---:|
| fp32 | pattern:gt125 | S1 | 5,810 / 6,519 | 0.125 | 4 |
| fp32 | pattern:gt25 | S1 | 6,374 / 7,168 | 0.250 | 4 |
| fp32 | pattern:gt875 | S1 | 7,906 / 8,436 | 0.875 | 4 |
| fp32 | pattern:rt16 | S1 | 9,760 / 11,116 | 1.000 | 4 |
| fp32 | pattern:rt32 | S1 | 8,829 / 9,652 | 1.000 | 4 |
| fp32 | pattern:rt32b | S1 | 8,744 / 9,519 | 1.000 | 4 |
| fp32 | pattern:rt64 | S1 | 8,619 / 9,323 | 1.000 | 4 |
| fp32 | pattern:sg_kk | S1 | 8,241 / 8,728 | 1.000 | 4 |
| fp32 | pattern:sgm1 | S1 | 19,394 / 26,258 | 1.000 | 4 |
| fp32 | pattern:th_top | S1 | 85,216 / 129,706 | 1.000 | 4 |
| fp32 | pattern:gt125 | S2 | 5,849 / 6,580 | 0.125 | 4 |
| fp32 | pattern:gt25 | S2 | 6,483 / 7,338 | 0.250 | 4 |
| fp32 | pattern:gt875 | S2 | 7,905 / 8,434 | 0.875 | 4 |
| fp32 | pattern:rt16 | S2 | 9,863 / 11,277 | 1.000 | 4 |
| fp32 | pattern:rt32 | S2 | 8,841 / 9,672 | 1.000 | 4 |
| fp32 | pattern:rt32b | S2 | 8,752 / 9,531 | 1.000 | 4 |
| fp32 | pattern:rt64 | S2 | 8,641 / 9,357 | 1.000 | 4 |
| fp32 | pattern:sg_kk | S2 | 8,234 / 8,719 | 1.000 | 4 |
| fp32 | pattern:sgm1 | S2 | 19,053 / 25,722 | 1.000 | 4 |
| fp32 | pattern:th_top | S2 | 85,037 / 129,425 | 1.000 | 4 |
| fp16 | pattern:h_gt25 | launch | 3,035 / 3,348 | 0.226 | 3 |
| fp16 | pattern:h_rt32 | launch | 4,487 / 4,940 | 1.000 | 3 |
| fp16 | pattern:h_rt64 | launch | 4,315 / 4,671 | 1.000 | 3 |
| fp16 | pattern:h_sg | launch | 9,045 / 12,104 | 1.000 | 3 |
| fp16 | pattern:h_th_in | launch | 30,912 / 46,471 | 1.000 | 3 |
| int8 | pattern:i8_t06 | launch | 522 / 575 | 1.000 | 3 |
| int8 | pattern:i8_t1 | launch | 525 / 579 | 1.000 | 3 |
| int8 | pattern:i8_t2 | launch | 529 / 586 | 1.000 | 3 |
| int8 | pattern:i8_t3 | launch | 524 / 577 | 1.000 | 3 |
| int8 | pattern:i8_t46 | launch | 2,635 / 3,895 | 1.000 | 3 |
| int8 | pattern:i8_t5 | launch | 527 / 583 | 1.000 | 3 |

## Files

- `DECLARED-blind-e217.md`, `.json`: the declaration (section a the runs, b the quantities, the models, the forecast procedure, c the metric, d the comparisons, e the switch arms, f the pass rule, g the label rule, h the nominal footing, i the earlier reads, the inputs by sha256).
- `FROZEN.txt`, `COUNTS-FROZEN.txt`: the two freeze lines as written for the Discussion.
- `forecasts-nominal-e217.*`, `forecasts-nominal-e217-counts.*`: the frozen nominal forecasts.
- `counts-e217/`: the counts in the committed tables' form (`counts-fp32-gemm-states.json`, `counts-fp16-int8-launch.json`, CSVs), the raw bench outputs (`raw/`), the scope, the re-count rule and check, the merge check, the tile zero shares, SOURCES.json.
- `inputs/`: the step files the forecasts were made from (the run list, the models' records, the twin keys, the bands, the walk features, the two models' group-S runs with the counts).
- `inputs/recheck/recheck.json`: after the freeze, each base model re-made its nominal forecasts in a process of its own and the composed forms were re-derived: 12,753 fields, 0 differences.
- `logs/`: the progress log and the step hash lists. `scripts/`: every script as run (box paths replaced), `scripts/cnt/` the counting scripts.

Python: /usr/bin/python3 3.12.3 (-I -B), numpy 1.26.4, every numerical job single-threaded inside slot.sh. No card, no simulator, no commit by this lane. SPDX-License-Identifier: Apache-2.0
