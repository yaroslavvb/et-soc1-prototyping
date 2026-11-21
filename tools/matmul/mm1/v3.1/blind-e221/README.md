# blind-e221: the lab's BLIND test of its frozen matmul models on E221, declared and frozen before any E221 datum

E221 is the model session's sixth matmul sweep (1120-mmsweep6; proposal #15 on the coordination Discussion, named E221 in #15.2): E136's rgm136 unchanged over 345 gemmL arms and an anchor in nine sessions (aifoundry1 card 1 S1-S3 at 600 MHz, aifoundry1 card 0 S1-S3 at low power, aifoundry2 card 0 S1-S3 under its governor): the core-group masks, the 1x1x1 cells at new masks, KB = 1, deep K, the held walks, the int8 L2 point, the MB = 3 ladders, NB = 1 and the BW shapes. This folder holds the lab's declaration of how it will score its frozen models on E221, MM1's domain stated first, and the forecasts frozen at nominal conditions, all made at the desk on aifoundry2 before any E221 run ran. Nothing here is a measurement.

**Label:** BLIND (sessions whose first datum follows the freeze post); UNREAD (any whose first datum precedes it).

**MM1's domain first** (DOMAIN-e221.md, domain-e221.csv): EVERY E221 case is IN MM1's domain: all 345 arms and the anchor are rgm136's cooperative gemmL<MB>x<NB>x<KB> loop (no gemmLnc, no block, stream or TenB arm); NO case is OUT OF DOMAIN, so none is left unforecast.

## The order of hashes and times (Pacific, Fri 20 Nov 2026; logs/progress.txt)

- Fri 20 Nov 2026 06:13:38 PST probe p02 (a code test of s02b_nominal.py, before the declaration): first try 06:11:55 rc 1 (KeyError: an E220 check configuration absent from posimb's frozen cache; the script now makes it by the maker's own branch, as h01_freeze.main does, and drops it after the check); second try 06:12:13-06:12:50 rc 0: checks pass (F1 94 E215 rows, factor diff 4.0e-10; controls worst 5.0e-05 cycles; posimb re-made its 306 frozen E220 rows exactly (100 in scope); L3S re-made its 306 frozen E220 rows exactly); 733 cases x 12 models, energy FORECAST 733/733 each; only summary lines printed (checks, counts, the factor ranges over the subset cases); its output (in the scratchpad) deleted unread
- Fri 20 Nov 2026 06:15:58 PST step 01 DECLARED (rc 0): DECLARED-blind-e221.md 9cd8256bbc9a40b2850094bf936c02d2efd8fe65b886e95b92774dd1d5bc9f1b, DECLARED-blind-e221.json b483f46cdcc0138d912e445a01fadb84a113cce0967f80e2b3f0ebe1f08c8ec4 (written 06:15:39 PST, once); every step-0/1 file and script in logs/step1-sha256.txt (sha256 deb15fa9340303c32e4f9fc101c0e20caf51592b475687564423118c3c17de6f); no E221 datum read (e221-releases.txt: #15, #15.1, #15.2, #15.2.1; no claim file; S1's stopped start has no run)
- Fri 20 Nov 2026 06:17:11 PST step 02 FORECAST (rc 0): nominal forecasts made 06:16:27-06:17:04 PST in one slot job (fc-nominal.json a80943cb770dc7f5681671fdeadecea4c571270a0a6674ae1a6911ab8895756c; 733 cases x 12 models (MM1-v3.2, MM1-v3.1, MM1-v3, MM1-v2, +contention, +both, the four controls; REPORTED posimb and L3S), energy FORECAST 733/733 each; checks before any output: F1 94 E215 rows (factor diff 4.0e-10), controls worst 5.0e-05 cycles, posimb's 306 and L3S's 306 frozen E220 rows re-made exactly); forecasts-nominal-e221.csv e3361847c4d1600b1b3deeaac3a42131b26f7bcb6434450bd8094c4965cbe59a, forecasts-nominal-e221.json f787561175410898cca55f223652307ed5799062f18165b02f88285e3cf30831 (written 06:17:05 PST; 8,796 CSV rows); step-2 files in logs/step2-sha256.txt (sha256 49e4de9a690e5a727426fcd0ff9ca1450a27ba347fe0b636f19bee15bafccf9d); no E221 datum read
- Fri 20 Nov 2026 06:17:46 PST step 03 FROZEN.txt written (rc 0) at 06:17:38 PST: 2df06f06b7d4c16caca6ceb56cff8d6c47abcb6fec6e6671ce72c700378b299b FROZEN.txt; the freeze line = DECLARED-blind-e221.md 9cd8256b..., DECLARED-blind-e221.json b483f46c..., forecasts-nominal-e221.csv e3361847..., forecasts-nominal-e221.json f7875611...; for the orchestrator to post on the Discussion (#15); e221-releases.txt: 4 post lines (#15.1 the only CLAIM: S1's stopped start, no run); no claim file; step 4 (counts) NOT NEEDED: E221 designs no tile; the five frozen files made read-only (444)
- Fri 20 Nov 2026 06:19:47 PST recheck (after the freeze, rc 0, 06:18:13-06:19:39): each base model's nominal forecasts re-made in a process of its own (MM1-v3.2, MM1-v3.1, MM1-v3, MM1-v2, and MM1-v3.2+L3S with its maker's module) and the composed forms re-derived from the frozen base fields (F1, both, the four controls on MM1-v3.1; posimb on MM1-v3.2): 30786 {'MM1-v3.2': 0, 'MM1-v3.1': 0, 'MM1-v3': 0, 'MM1-v2': 0, 'MM1-v3.2+L3S': 0} 0 True (work/recheck/recheck.json 16dd26418f8ccf16)

## The freeze line (FROZEN.txt)

FROZEN.txt names the lane's own paths: here `work/step1/` is `inputs/step1/`, `work/step2/` is `inputs/step2/`; every file keeps its bytes. The scripts under `scripts/` carry the box's paths replaced (<W>, <LAB>, <SCRATCH>, ~), so their sha256 differ from the as-run hashes in FROZEN.txt and logs/step1-sha256.txt / step2-sha256.txt; the declaration, the forecasts and the inputs keep their bytes.

```
decl-e221 (round Q235): the lab's BLIND test of its frozen matmul models on E221 (#15, 1120-mmsweep6), DECLARED and its nominal forecasts FROZEN at Fri 20 Nov 2026 06:17:38 PST, before any E221 datum it could read (no E221 run has run).
MM1's domain first: all 733 of E221's cases (811 runs: 740 arm + 71 anchor, over 345 gemmL arms and the anchor in nine sessions) are IN DOMAIN: every arm is rgm136's cooperative gemmL loop, and every declared model has a form for every case (probe p01: 733/733 in MM1-v3.2, MM1-v3.1, MM1-v3 and MM1-v2); OUT OF DOMAIN: none. Classes: the core-group masks 392, the 1x1x1 cells at new masks 79, KB = 1 72, the int8 L2 point 54, MB = 3 ladders 47, deep K 30, the held walks 23, BW 18, NB = 1 15, the anchor 3; 461 cases at shire subsets (65 masks).
Models frozen and unchanged: MM1-v3.2 (4e386f75, the lab's newest: the pass rule's model), MM1-v3.1 2c971828, MM1-v3 b1493082, MM1-v2, 'v3.1 + contention' F1 (#1.29.1), verify-lay's controls N1+N2, G1, G1+N1 and the layout-blind F1 (#1.29.1.1), 'v3.1 + both' (= F1 here); REPORTED: the MM1-v3.3 candidates 'MM1-v3.2 + posimb' (layout2, FROZEN 81d04c97, 05:39:48) at the subset masks and 'MM1-v3.2 + L3S' (l3-edge, FROZEN e8216cbb, 05:57:20; its post line in out/orch/q234-frozen-posts.txt: 1) at the full chip, by their own frozen makers; NOT APPLICABLE (no gemmLnc arm): 'v3.1 + gemmLnc' and 'MM1-v3.2 + gemmLnc term AF4' (lnc-form, FROZEN 5373973f).
Cards: aifoundry1 card 1 at 600 MHz; aifoundry1 card 0 low power and aifoundry2 card 0 under their governors (nominal 800 MHz). Kit copy out/orch/e221-src (SRC-SHA256SUMS.txt 5680112f...); E221 designs no tile: no counts are made.
sha256 (the freeze line):
9cd8256bbc9a40b2850094bf936c02d2efd8fe65b886e95b92774dd1d5bc9f1b  DECLARED-blind-e221.md
b483f46cdcc0138d912e445a01fadb84a113cce0967f80e2b3f0ebe1f08c8ec4  DECLARED-blind-e221.json
e3361847c4d1600b1b3deeaac3a42131b26f7bcb6434450bd8094c4965cbe59a  forecasts-nominal-e221.csv
f787561175410898cca55f223652307ed5799062f18165b02f88285e3cf30831  forecasts-nominal-e221.json
supporting (the makers and their records):
b43030186fe153b96634e642f75ca73b75a62332ac3b2bfd01cc2443042e75d0  scripts/s02b_nominal.py
0a8571ccfbcc8a9fd3418b0a18ca4b1a5508820f30a020f8b29ef476e463357f  scripts/s02w_walk.py
342138469cba6ed5ed6bd835214d7ebd883a61c8e07eb30b3ee3502233b8476a  scripts/s02f_cands.py
84bc47b8f7021c9e9a89f8b1ade1140df3b34da79f9ddbab3f58ab2033eb910c  scripts/s02c_write.py
a80943cb770dc7f5681671fdeadecea4c571270a0a6674ae1a6911ab8895756c  work/step2/fc-nominal.json
b316da119b61c2ec2ab275e9528d843ae6bfad146e29edc36f0ddac6949be7b8  work/step2/walk-feats-e221.json
848db0174a64edd81265ff2bfc8261585b93861b9b9437a27d02e95980e599b2  work/step2/cand-feats-e221.json
deb15fa9340303c32e4f9fc101c0e20caf51592b475687564423118c3c17de6f  logs/step1-sha256.txt
49e4de9a690e5a727426fcd0ff9ca1450a27ba347fe0b636f19bee15bafccf9d  logs/step2-sha256.txt
Times (Pacific): declared 06:15:39 (hash logged 06:15:58); nominal forecasts made 06:16:27-06:17:04, files written 06:17:05 (hash logged 06:17:11); this file Fri 20 Nov 2026 06:17:38 PST.
State at the freeze: out/orch/e221-releases.txt holds 4 post lines (the last: '#15.2.1 2026-11-20 05:55:48 PST: the model sessi...'), 1 of them a CLAIM (#15.1, S1 on aifoundry1 card 1, whose start at 05:53:56 was stopped at 05:55:27 with no run run: #15.2.1, kept apart, not scored); 0 claim files in out/orch (none).
Label rule (the declaration's section g): BLIND for a session whose first datum (first card command) comes after this freeze is posted; a session whose first datum precedes the post is UNREAD for it (POST-READ if a lab lane read its data first). S1, claimed again whole after the post, is labelled by its own first card command.
```

## What is declared (DECLARED-blind-e221.md; the JSON is the machine form)

- **The runs:** 811 runs in 733 cases, by id from the kit's schedules; every case in domain; classes MASK, CELL1, KB1, L2I8, MQ3, DK, HLD, BW, NB1, ANCHOR; FULL and SUB; configuration twins apart.
- **The quantities:** wall cycles (T1), the counter mean (T2), seconds a pass (T3), J over idle given t (E1) and with t forecast (E2), J at rest given t (E3) and with t forecast (E4), per card, format, kind and class.
- **The models:** MM1-v3.2, MM1-v3.1, MM1-v3, MM1-v2, v3.1+contention, v3.1+both, ctrl N1+N2, ctrl G1, ctrl G1+N1, ctrl F1-layout-blind, MM1-v3.2+posimb, MM1-v3.2+L3S (the last two REPORTED: the MM1-v3.3 candidates by their own frozen makers); NOT APPLICABLE: v3.1+gemmLnc, MM1-v3.2+AF4.
- **The forecast procedure:** each frozen predictor unchanged at each run's measured clock, minion volts and die at start, read from the data's start-of-run records only; a second footing, the nominal forecasts here, scored beside.
- **The comparisons:** exact sign tests per case: MM1-v3.2 vs MM1-v3.1, MM1-v3.1 vs MM1-v3 and vs MM1-v2 (H1-H5); the contention term and each of verify-lay's controls vs MM1-v3.1 on the subset-mask cases (H1, H2); the candidates vs MM1-v3.2 REPORTED; the switch route NOT APPLICABLE (no operand-pattern arm).
- **The pass rule:** part A (MM1-v3.2 within E215's bands on 90% of each card's no-twin cases, every rule), decided by the scoring lane's script, hashed before its first read; MM1-v3.1 by the same rules REPORTED; part S NOT APPLICABLE.
- **E221 designs no tile:** every tile file it names is one of the lab's kinds byte for byte, so no switch count is made (no step 4).

## The nominal forecasts (forecasts-nominal-e221.csv / .json)

- Conditions: {"aifoundry1 card 0": {"V": null, "f": 800.0, "t0_c": 55.0}, "aifoundry1 card 1": {"V": 0.517, "f": 600.0, "t0_c": 60.0}, "aifoundry2 card 0": {"V": null, "f": 800.0, "t0_c": 55.0}}.
- 733 cases x 12 models: MM1-v3.2, MM1-v3.1, MM1-v3, MM1-v2, v3.1+contention, v3.1+both, ctrl N1+N2, ctrl G1, ctrl G1+N1, ctrl F1-layout-blind, MM1-v3.2+posimb, MM1-v3.2+L3S.
- Energy: every model FORECAST on every case ({"FORECAST": 733} for MM1-v3.2).
- Checks before any output: the contention term re-made its 94 frozen E215 rows (factor difference 4.0e-10); verify-lay's controls re-made its E215 columns (worst 5.0e-05 cycles); posimb re-made its 306 frozen E220 rows (worst g_wall difference 0.0); L3S its 306 (worst relative wall-cycle difference 0.0).
- Recheck after the freeze (inputs/recheck/recheck.json): 30786 fields, differences {'MM1-v3.2': 0, 'MM1-v3.1': 0, 'MM1-v3': 0, 'MM1-v2': 0, 'MM1-v3.2+L3S': 0}, composed 0: pass True.

## Files

- `DECLARED-blind-e221.md`, `.json`: the declaration (section 0 the domain, a the runs, b the quantities, the models, the forecast procedure, c the metric, d the comparisons, e reported beside, f the pass rule, g the label rule, h the nominal footing, i the earlier reads, the inputs by sha256).
- `FROZEN.txt`: the freeze line as written for the Discussion.
- `forecasts-nominal-e221.*`: the frozen nominal forecasts.
- `DOMAIN-e221.md`, `domain-e221.csv`: the domain table (made from the declaration and the run list after the freeze; not in the freeze line).
- `inputs/`: the step files the forecasts were made from (the run list, the domain probe, the models' records, the twin keys, the bands, the walk features, the candidates' features) and the recheck.
- `logs/`: the progress log and the step hash lists. `scripts/`: every script as run (box paths replaced).

Python: /usr/bin/python3 3.12.3 (-I -B), numpy, every numerical job single-threaded inside slot.sh. No card, no simulator, no ssh, no commit by this lane. SPDX-License-Identifier: Apache-2.0
