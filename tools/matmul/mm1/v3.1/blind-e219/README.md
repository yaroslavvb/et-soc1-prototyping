# blind-e219: the lab's BLIND test of its frozen matmul models on E219, declared and frozen before any E219 datum

E219 is the model session's fifth matmul sweep (1119-mmsweep5; proposal #14 on the coordination Discussion, named E219 in #14.1): E136's rgm136 unchanged over 206 arms and an anchor in five sessions on aifoundry1 (card 1 S1-S3 at 600 MHz, card 0 S1-S2 at low power), mostly the host's own block, stream and TenB arms (gemmc and gemmh with R ladders and shared C, the packed walk gemm, mm16 and mm128, tenb) with gemmL gap cells and 1x1x1 controls. This folder holds the lab's declaration of how it will score its frozen models on E219, MM1's domain stated first, and the forecasts frozen at nominal conditions, all made at the desk on aifoundry2 before any E219 session ran. Nothing here is a measurement.

**Label: BLIND.** BLIND: MM1-v3.1 (2c971828), MM1-v3 (b1493082), MM1-v2 (3ca4b717), the contention term F1 (#1.29.1, landed 595fcb59), verify-lay's controls (#1.29.1.1) and the gemmLnc term (#1.29, landed aaeaa495) frozen and unchanged; this declaration and the nominal forecasts hashed and frozen (FROZEN.txt, posted by the orchestrator) before any E219 datum exists. A session whose first datum precedes the freeze post is UNREAD for it.

**MM1's domain first** (DOMAIN-e219.md, domain-e219.csv): 139 of E219's 314 cases are in domain and forecast: rgm136's gemmL loop (the 1x1x1 controls, the gap cells, the anchor) and run_gemm's c-arms that the frozen models' table holds (gemmc1, gemmc4s, gemmc8s, gemmc16, gemmc16s and the gemmc16r<R> ladder); 175 are OUT OF DOMAIN (gemmc at other B, R or shared C, gemmh, gemm packed by k, mm16, mm128, tenb): no frozen MM1 has a form for them, so none is forecast; the scores report them apart as the model's domain limit.

## The order of hashes and times (Pacific, Thu 19 Nov 2026; logs/progress.txt)

- Thu 19 Nov 2026 18:36:38 PST step 00c MM1-v3.2 check: NOT_ON_MAIN (tools/matmul/mm1/v3.2 is not in GitHub main's tree at Thu 19 Nov 2026 18:36:38 PST (LAB HEAD 2b25bd4a); W/out/q230-anchor-lines-v32.txt absent)
- Thu 19 Nov 2026 18:36:51 PST step 00c MM1-v3.2 checked (rc 0): NOT ON MAIN (GitHub main = LAB HEAD 2b25bd4a at 18:36:38: no tools/matmul/mm1/v3.2, no W/out/q230-anchor-lines-v32.txt); main moved 1c446c93 -> 2b25bd4a by one E217 data commit only, tools/matmul, e215 rules and kinds unchanged (git diff empty); e219-releases.txt 2 post lines, no E219 claim (claim-aifoundry1.txt = E217 a1c0-S3)
- Thu 19 Nov 2026 18:37:24 PST step 01 DECLARED (rc 0): DECLARED-blind-e219.md d629bd14aff6fe4d214931fc6bad6b684ab910cd42bb5afdc07b8f8f62330495, DECLARED-blind-e219.json 670caa8c2f29a5d1d95591df0cba3ab80047d0f4b5dc27b8f2568c1da480f479 (written 18:37:19 PST; a first write at 18:36:51 was rewritten at 18:37:19 for one wording fix in the R-ladder form, before any hash was logged or posted); every step-0/1 file and script in logs/step1-sha256.txt (sha256 3ebd6e637165b499ac40c186d4c1edc8cd4b01bb9d4b6a8db5e64db2e72aeddd); no E219 datum exists (e219-releases.txt: the proposal and the naming only; claim-aifoundry1.txt = E217 a1c0-S3; no quiet-desk flag)
- Thu 19 Nov 2026 18:37:50 PST step 02 FORECAST (rc 0): nominal forecasts made 18:37:29-18:37:34 PST in one slot job (fc-nominal.json 1c6172047d5aafa9f07f1e3bb4277cc1d896a0acd7ad1108469e70365ecdaed1; 314 cases: 139 in domain x 9 models (MM1-v3.1, MM1-v3, MM1-v2, +contention, +both, the four controls; energy FORECAST 139/139 each), 175 OUT OF DOMAIN listed NOT FORECAST; checks before any output: F1 re-made its 94 frozen E215 rows (factor diff 4.0e-10), the controls re-made v02_e215_controls.csv's N3, N1+N2, G1, G1+N1 columns (worst 5.0e-5 cycles); F1 and the layout-blind F1 factor 1 on every E219 case, the count controls 0.995-1.008 on the 6 subset cases); forecasts-nominal-e219.csv 5433f8c4e88642bad32909a491eb47321a854fad7f2785a188d4ce8d072a3a67, forecasts-nominal-e219.json d605db13b6342a283cb5aacb9179c406d529846c3bfc8e152fbf3aef9bd04899 (written 18:37:34 PST; 1,426 CSV rows); step-2 files in logs/step2-sha256.txt (sha256 17699cfed6f3bdf89e1a92549502eccf0014fda303f747ebaa27078addd43cd0); no E219 datum exists
- Thu 19 Nov 2026 18:37:57 PST step 03 FROZEN.txt written (rc 0) at 18:37:50 PST: 73a2dd754b70d18a4a7803cd782b1179984d36185c762058d94219ad0fc69f1e FROZEN.txt; the freeze line = DECLARED-blind-e219.md d629bd14..., DECLARED-blind-e219.json 670caa8c..., forecasts-nominal-e219.csv 5433f8c4..., forecasts-nominal-e219.json d605db13...; for the orchestrator to post on the Discussion (#14); e219-releases.txt: the proposal and the naming only, no E219 claim at the freeze (claim-aifoundry1.txt = E217 a1c0-S3, 18:25-19:47); MM1-v3.2 NOT on main at the declaration; step 4 (counts) NOT NEEDED: E219 designs no tile
- Thu 19 Nov 2026 18:38:51 PST recheck (after the freeze, rc 0): each base model's nominal forecasts re-made in a process of its own (MM1-v3.1, MM1-v3, MM1-v2) and the composed forms re-derived from the frozen MM1-v3.1 fields: 3,753 fields compared, 0 differences; every one of the 175 out-of-domain cases raises KeyError in all three base models (work/recheck/recheck.json 06992b9e77790141f76531822604b5ac9891ddf5e58db6e3a87412b968ce88b6)

## The freeze line (FROZEN.txt)

FROZEN.txt names the lane's own paths: here `work/step1/` is `inputs/step1/`, `work/step2/` is `inputs/step2/`; every file keeps its bytes. The scripts under `scripts/` carry the box's paths replaced (<W>, <LAB>, <SCRATCH>, ~), so their sha256 differ from the as-run hashes in FROZEN.txt and logs/step1-sha256.txt / step2-sha256.txt; the declaration, the forecasts and the inputs keep their bytes.

```
decl-e219 (round Q232): the lab's BLIND test of its frozen matmul models on E219 (#14, 1119-mmsweep5), DECLARED and its nominal forecasts FROZEN at Thu 19 Nov 2026 18:37:50 PST, before any E219 datum exists.
MM1's domain first: 139 of E219's 314 cases are IN DOMAIN (rgm136's gemmL loop: the 1x1x1 controls, the gap cells and the anchor, 44 cases; run_gemm's c-arms in the models' table: gemmc1, gemmc4s, gemmc8s, gemmc16, gemmc16s, 22 cases, and the gemmc16r<R> ladder, 73 cases) and forecast; 175 are OUT OF DOMAIN (gemmc at other B, R or shared C 121, gemmh 32, gemm packed by k 10, mm16 and mm128 6, tenb 6): no frozen MM1 has a form for them, so no forecast; the scores report them apart.
Models frozen and unchanged: MM1-v3.1 2c971828, MM1-v3 b1493082, MM1-v2 3ca4b717, 'v3.1 + contention' F1 (#1.29.1), verify-lay's controls N1+N2, G1, G1+N1 and the layout-blind F1 (#1.29.1.1), 'v3.1 + both' (= F1 here); 'v3.1 + gemmLnc' NOT APPLICABLE (E219 runs no gemmLnc arm). MM1-v3.2: NOT_ON_MAIN at the declaration (work/v32-status.json).
Scope: 392 runs (arm + anchor) in 314 cases over E219's five sessions (aifoundry1 card 1 S1-S3 at 600 MHz, card 0 S1-S2 low power), from the kit copy out/orch/e219-src (SRC-SHA256SUMS.txt 247456da...); E219 designs no tile: no counts are made.
sha256 (the freeze line):
d629bd14aff6fe4d214931fc6bad6b684ab910cd42bb5afdc07b8f8f62330495  DECLARED-blind-e219.md
670caa8c2f29a5d1d95591df0cba3ab80047d0f4b5dc27b8f2568c1da480f479  DECLARED-blind-e219.json
5433f8c4e88642bad32909a491eb47321a854fad7f2785a188d4ce8d072a3a67  forecasts-nominal-e219.csv
d605db13b6342a283cb5aacb9179c406d529846c3bfc8e152fbf3aef9bd04899  forecasts-nominal-e219.json
supporting (the makers and their records):
46d30dea607d7710eb1a2bf128d17115f96d8babac435e4167be38889fad5878  scripts/s02b_nominal.py
4a745f7b70edb7594e201a9ee37c08f6d5c23188ecbce155f631074894bb1ad9  scripts/s02w_walk.py
b8b9a4072caa006a2f11d4fe6f006496a161020201307735a8471652775b2b2d  scripts/s02c_write.py
1c6172047d5aafa9f07f1e3bb4277cc1d896a0acd7ad1108469e70365ecdaed1  work/step2/fc-nominal.json
9c13958d026c8a6f9e5fabfc34c580377dab9efa24ae8095b1dc47eb5e09020d  work/step2/walk-feats-e219.json
3ebd6e637165b499ac40c186d4c1edc8cd4b01bb9d4b6a8db5e64db2e72aeddd  logs/step1-sha256.txt
17699cfed6f3bdf89e1a92549502eccf0014fda303f747ebaa27078addd43cd0  logs/step2-sha256.txt
Times (Pacific): declared 18:37:19 (hash logged 18:37:24); nominal forecasts made 18:37:29-18:37:34, files written 18:37:34 (hash logged 18:37:35); this file Thu 19 Nov 2026 18:37:50 PST.
State at the freeze: out/orch/e219-releases.txt holds 2 post lines (the last: '#14.1 2026-11-19 18:15:03 PST: the lab n...') and no E219 claim; 1 claim files in out/orch (claim-aifoundry1.txt ; the claim file names the session it holds); no E219 session has run, so no E219 datum exists.
Label rule (the declaration's section g): BLIND for a session whose first datum comes after this freeze is posted; a session whose first datum precedes the post is UNREAD for it (POST-READ if a lab lane read its data first).
```

## What is declared (DECLARED-blind-e219.md; the JSON is the machine form)

- **The runs:** 392 runs ({'anchor': 36, 'arm': 356}) in 314 cases, by id from the kit's schedules; classes CTRL (the gemmL 1x1x1 controls, apart: the tie to E217), GAP, ANCHOR, CTAB, C16R in domain, the OUT classes apart; configuration twins apart.
- **The quantities:** wall cycles (T1), the counter mean (T2), seconds a pass (T3), J over idle given t (E1) and with t forecast (E2), J at rest given t (E3) and with t forecast (E4), per card, format, kind and class.
- **The models:** MM1-v3.1; MM1-v3; MM1-v2; v3.1+contention; v3.1+gemmLnc; v3.1+both; controls (see the declaration for each one's call and form).
- **The forecast procedure:** each frozen predictor unchanged at each run's measured clock, minion volts and die at start, read from the data's start-of-run records only (MM1-v3 README section 5's form, as unread-e214 and decl-e217 did); a second footing, the nominal forecasts here, scored beside.
- **The comparisons:** exact sign tests per case: MM1-v3.1 vs MM1-v3 and vs MM1-v2 (H1-H5); the contention term and each of verify-lay's controls vs MM1-v3.1 on the 6 subset-mask cases (TOO FEW by construction, stated before the data); the switch route NOT APPLICABLE (no operand-pattern arm).
- **The pass rule:** part A (MM1-v3.1 within E215's bands on 90% of each card's in-domain no-twin cases, every rule), decided by the scoring lane's script, hashed before its first read; part S NOT APPLICABLE.
- **E219 designs no tile:** every tile file it names is one of the lab's kinds byte for byte, so no switch count is made (no step 4).

## The nominal forecasts (forecasts-nominal-e219.csv / .json)

- Conditions: {"aifoundry1 card 0": {"V": null, "f": 800.0, "t0_c": 55.0}, "aifoundry1 card 1": {"V": 0.517, "f": 600.0, "t0_c": 60.0}}.
- 139 in-domain cases x 9 models: MM1-v3.1, MM1-v3, MM1-v2, v3.1+contention, v3.1+both, ctrl N1+N2, ctrl G1, ctrl G1+N1, ctrl F1-layout-blind; 175 out-of-domain cases listed NOT FORECAST (one row each in the CSV).
- Energy: {"MM1-v2": {"FORECAST": 139}, "MM1-v3": {"FORECAST": 139}, "MM1-v3.1": {"FORECAST": 139}, "ctrl F1-layout-blind": {"FORECAST": 139}, "ctrl G1": {"FORECAST": 139}, "ctrl G1+N1": {"FORECAST": 139}, "ctrl N1+N2": {"FORECAST": 139}, "v3.1+both": {"FORECAST": 139}, "v3.1+contention": {"FORECAST": 139}}.
- Checks before any output: the contention term re-made its 94 frozen E215 rows (factor difference 4.0e-10); verify-lay's controls re-made its E215 columns (worst 5.0e-05 cycles, the CSV's rounding).
- Factor ranges on the subset masks: {"ctrl F1-layout-blind": [1.0, 1.0], "ctrl G1": [1.0058, 1.0074], "ctrl G1+N1": [0.9952, 0.9958], "ctrl N1+N2": [0.9961, 1.0083], "v3.1+contention": [1.0, 1.0]}.
- Recheck after the freeze (inputs/recheck/recheck.json): 3753 fields, differences {'MM1-v3.1': 0, 'MM1-v3': 0, 'MM1-v2': 0}, composed 0: pass True.

## Files

- `DECLARED-blind-e219.md`, `.json`: the declaration (section 0 the domain, a the runs, b the quantities, the models, the forecast procedure, c the metric, d the comparisons, e reported beside, f the pass rule, g the label rule, h the nominal footing, i the earlier reads, the out-of-domain cases, the inputs by sha256).
- `FROZEN.txt`: the freeze line as written for the Discussion.
- `forecasts-nominal-e219.*`: the frozen nominal forecasts.
- `DOMAIN-e219.md`, `domain-e219.csv`: the domain table (made from the declaration and the run list after the freeze; not in the freeze line).
- `inputs/`: the step files the forecasts were made from (the run list, the models' records, the twin keys, the bands, the walk features, the MM1-v3.2 check) and the recheck.
- `logs/`: the progress log and the step hash lists. `scripts/`: every script as run (box paths replaced).

Python: /usr/bin/python3 3.12.3 (-I -B), numpy 1.26.4, every numerical job single-threaded inside slot.sh. No card, no simulator, no ssh, no commit by this lane. SPDX-License-Identifier: Apache-2.0
