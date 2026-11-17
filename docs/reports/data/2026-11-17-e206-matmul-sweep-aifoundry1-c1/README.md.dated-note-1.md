# E206 arm B's data README, dated note 1 (Tue 17 Nov 2026): the frozen scorer's output, run on the data commit `79340bfa`, committed beside it - R0 PASS; C1 FAIL, S1 FAIL, S6 PASS; F1: S2 FAIL, S3 FAIL, S4 PASS; F2: S2 FAIL, S3 FAIL, S4 FAIL; MM1-v0 and MM1-v1 scored blind beside F1 and F2; the data verifier's own re-derivation gives the same words at every point

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `79340bfa`. Written on aifoundry2 from 02:14 PST on Tue 17 Nov 2026 (week 47) by the clock (built at 02:43:59 PST), desk only on aifoundry2 (no card, no call to another box, no device, no post), by Q201's lane `scores-e206b`, after this directory's data verifier `verify-e206bd` (01:47:58-02:12:57 PST: HOLDS WITH FIXES). The kit's step 13 ([`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e206/CARD-LANE-BRIEF.md), its table of steps: "the frozen scorer: RB_OUT/scores-e206-<arm>.json and .txt (R0, C1, S1-S4, S6 per model and arm; the summaries; the readings); read its words; a later lane commits them beside the data"; [`rb/s24_score_e206.sh`](../../../../tools/claims-v3/e206/rb/s24_score_e206.sh): "a later lane (scores-e206) commits it beside the data. The other arm reads NO DATA in this output (one arm a directory); the records lane may score both directories together.") runs the frozen scorer only after the data commit and leaves its output to a later commit; [`DATA-README-FORM-e206.md`](../../../../tools/claims-v3/e206/DATA-README-FORM-e206.md) says "The scorer runs after the data commit (step 13): its words are not in this README at the commit; a later lane adds them in a dated note beside it.", and README.md says "the frozen scorer (step 13, `score_e206.py`) runs on this directory only after it is committed, and a later lane commits its words beside it." This lane is that later lane for arm B (arm A's scores and dated note 1 are in [its own directory](../2026-11-16-e206-matmul-sweep-aifoundry3/README.md.dated-note-1.md)). This note commits the scorer's output byte for byte with its printed lines, sets the data verifier's figures beside the scorer's point by point, gives MM1-v0's and MM1-v1's blind scores on these points as the data verifier computed them (section 7), and answers the card lane's and the data verifier's findings in dated clauses (section 9). **No number, rule, verdict, forecast, band, threshold or gate reading changes, and nothing is scored again.** Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** ([`E206.md`](../../../../tools/claims-v3/e206/E206.md) with its amendment A1, and the kit, as committed), **measured** (the session's committed files), **desk check of code** (this lane's provenance check and re-runs, the verifier's re-derivation), **blind** (a forecast pushed to the public repository before the first card command, scored after the data), **REPORTED** (E206.md 7's summaries and readings, and every MM1 figure: beside the rules, deciding nothing), **post hoc** (desk readings after the data). The verdicts are the frozen scorer's own output on the committed data. Every joule below is against the card's own meter, whose absolute scale is one fixed gain for every board (README.md, "The meter's absolute scale").*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`scores-e206-B.json`](scores-e206-B.json) | the frozen scorer's output ([`score_e206.py`](../../../../tools/claims-v3/e206/score_e206.py), registered in `eb2f7ac2` as amended before any datum (A1), unchanged since), copied byte for byte from the card lane's RB_OUT: the gate R0, the rules C1, S1, S2, S3, S4 and S6 per model and arm with their counts and verdicts; every point's measured values, errors, given values and words; the summaries; the readings (a)-(h) | 360,318 | `9816de881798779b08b980285cc9bf5749836c5efa4efc2eb838c4d948dba465` |
| [`scores-e206-B.txt`](scores-e206-B.txt) | the scorer's printed lines, as the step copied them from the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 963 | `827c376579e8d7b00df22080a050b633bcc7eeba9a07eeb3b032127ad2efaefa` |
| `README.md.dated-note-1.md` | this note | | |

[`SHA256SUMS-note1`](SHA256SUMS-note1) pins these three and `README.md` and `SHA256SUMS` at their committed bytes. With `SHA256SUMS` (1,186 files, unchanged), every file here is pinned but `SHA256SUMS-note1` itself. The arm is named in the file names as step 13 named them (`scores-e206-<arm>`), and the scorer's output holds both arms (section 8).

## 2. When, where and on which commit the scorer ran

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder RB_OUT, and from the lab clone's own log of its HEAD (a desk check of code: this lane's provenance check, 49 checks, all OK):

- **Step 13** ([`rb/s24_score_e206.sh`](../../../../tools/claims-v3/e206/rb/s24_score_e206.sh) `B`, the kit's): Tue 17 Nov 2026 at **01:43:30 PST**, on aifoundry2, in the lab clone. The data commit **`79340bfa`** was made at 01:42:43 PST and pushed at 01:42:48 (the card lane's log); the card lane released its booking and the lab's commit hold at 01:42:55. At the step the clone's HEAD was `5d99fe17` (its own log of HEAD): another lane's data commit, for E208, made at 01:43:17 PST on top of `79340bfa`. It added files under E208's own data directory and one dated note beside E208's registration, and changed no file the scorer reads. HEAD has moved four times since (`3ca4b717`, `4e518735`, `3649245b`, `117885d9`); none of those commits touches the scorer's files or this directory.
- **Its gates**, the log's lines 97-100, at 01:43:30 PST, each with rc 0: the data directory committed (the last commit naming it: `79340bfa E206 arm B data: the matmul sweep on aifoundry1 card 1 at 600 MHz, RAN FULL - 229 of 229 runs, 84.81 card-minutes, reads only, before any score (Q201)`); the directory clean (no line); `SHA256SUMS` 1,186 of 1,186 entries OK; the history check: `HISTORY OK: HEAD descends from the registration eb2f7ac2f732 (subtree 114c094b); 46 additions and nothing else under tools/claims-v3/e206 since it; no shadowing addition under tools/ (sys.stdlib_module_names); E206's run paths clean`
- **The scorer**, the log's line 101 (its last of 101): `/usr/bin/python3 -I -B tools/claims-v3/e206/score_e206.py docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/data-e206.json --out RB_OUT/scores-e206-B.json`, rc 0 in 0.1 s. `scores-e206-B.json` was last written at 01:43:30.80612 PST, inside that call (after the previous call's capture closed at 01:43:30.65020, before this call's closed at 01:43:30.80619); the step then copied this call's capture, the scorer's printed lines, to `scores-e206-B.txt` (01:43:30.81906), and its own line reads "[s24_score_e206] scored arm B: RB_OUT/scores-e206-B.json and .txt (the scorer's printed words; a later lane commits them beside the data)".
- **Files beside the clone's tree at the step:** another lane (the MM1-v2 landing) had written 115 new files under `tools/matmul/mm1/v2/` at 01:43:10 PST, after the card lane's hold came off; they became that lane's commit `3ca4b717` (01:44:45 PST: 115 files, all added, all under `tools/matmul/mm1/v2/`). The card lane's step 13 counted them as "LAB status after: 115 lines". None is a file the scorer reads, and none lies on its import path.
- **No other run on data:** the log holds no earlier run of the scorer on data; its two self-tests (`--selftest-standins`, `--selftest-e190`) ran at step 3, at 00:00:56 PST, each with rc 0 (lines 23 and 24).
- **The frozen files:** `score_e206.py` at the data commit is E206.md 0's registered scorer (sha256 `65bd65fc79471c0f14b00e65476dd3b38070ca5ab113b11e93d7c677580ac1ac`); its `FORECAST_SHA256`, the sha256 of `forecast-e206.json` at the data commit and the output's own `forecast_sha256` are one value (`d8f3a8b1e3d22f515581aab1a9cc43ca30fbb6e1c61c96d7cc14bf32697bd888`), and the scorer refuses to run on any other forecast. The registration list's 25 files and the list, the forecast's 26 inputs (each at the sha256 the forecast records) and the kit list's 44 files and the list (the step's own scripts among them) are one git blob each at the registration `eb2f7ac2`, the kit `906699ea` (the kit list from there), the data commit, the step's HEAD `5d99fe17` and HEAD; both lists read OK in the lab clone. The scorer read `data-e206.json` at the data commit (sha256 `fe2b8e80feaa78be42270dacd7d21229e67adbd9876e0f7f24e1ce92971a3719`), the file the data verifier re-derived against.
- **Re-runs (desk checks of code):** at 02:22:59 PST this lane ran the frozen scorer once more, as step 13 ran it, in the lab clone's tree under an audit hook that lists every file a program opens (its output went to this lane's folder; the clone's HEAD and status were the same before and after). Both files came out byte for byte equal to RB_OUT. The scorer read 34 committed files and, besides them, only the standard library (it also looked for bytecode caches, which exist in neither tree): the kit's scorer, forecast module, frozen forecast, points and two desk files; E190's route and E136's, E119's and E83's modules, with E136's predictions and the desk files of E136, E146 and E190; the kinds and HPL surface modules with E101's predictions; ledgers v2 and v3 with v3's frozen file and the ledger estimate; 10 committed data files of earlier experiments; and this directory's `data-e206.json`. Each of those 34 files is one git blob at `79340bfa`, at `5d99fe17` and at HEAD. Then, at 02:23:36-02:23:37 PST, the frozen scorer ran twice more (plainly, and under the hook) in a tree holding only those 34 files as extracted from the data commit `79340bfa`, with no bytecode cache: both outputs were byte for byte equal to RB_OUT, the printed lines equal to the runbook's capture of the call, and no file outside that tree was opened but the standard library's and the run's own two outputs.

## 3. The rules' words and verdicts (registered rules; the frozen scorer's output)

The scorer's printed lines, as committed in `scores-e206-B.txt`:

```
R0 PASS 
C1.A NO DATA 0/0
S1.A NO DATA 0/0
S6.A NO DATA 0/0
S2.F1.A NO DATA 0/0
S3.F1.A NO DATA 0/0
S4.F1.A NO DATA 0/0
S2.F2.A NO DATA 0/0
S3.F2.A NO DATA 0/0
S4.F2.A NO DATA 0/0
C1.B FAIL 60/113
S1.B FAIL 66/113
S6.B PASS 113/113
S2.F1.B FAIL 17/113
S3.F1.B FAIL 49/113
S4.F1.B PASS 106/113
S2.F2.B FAIL 4/109
S3.F2.B FAIL 13/109
S4.F2.B FAIL 5/109
B.all cycles_per_op rms 0.180 bias -0.090 (n 113); cycles_per_op_P0 rms 0.178 bias -0.080 (n 113); t rms 0.160 bias -0.055 (n 113); cycles_gemm rms 0.160 bias -0.056 (n 113); F1.j_over_given rms 0.260 bias +0.201 (n 113); F1.j_over_forecast rms 0.225 bias +0.146 (n 113); F1.j_rest_given rms 0.067 bias +0.055 (n 113); F1.j_rest_forecast rms 0.143 bias +0.048 (n 113); F2.j_over_given rms 0.515 bias -0.174 (n 109); F2.j_over_forecast rms 0.513 bias -0.168 (n 109); F2.j_rest_given rms 0.147 bias -0.064 (n 109); F2.j_rest_forecast rms 0.214 bias -0.054 (n 109); P0.j_over_forecast rms 0.175 bias +0.070 (n 113)
```

| rule (E206.md 7) | what | registered threshold | the scorer, arm B | verify-e206bd's own scoring | points from a flip (desk arithmetic) | arm A (this output) |
|---|---|---|---|---|---|---|
| R0 | the ties: every check of C exact or approx (the smoke and every run: every point run, counted or not, and every tie run, A1); the smoke's cycles an op 50-250% of F1's point | one verdict; a FAIL labels every other verdict | **PASS** (232 checks, 0 wrong) | PASS (232 checks, 0 wrong) | - | (one verdict for the day) |
| C1 | cycles (the counter): the point's cycles an op inside F1's band | per point | **FAIL** 60 of 113 | FAIL 60 of 113 | 42 | NO DATA (0 scored) |
| S1 | seconds: the point's t_gemm inside F1's band | per point | **FAIL** 66 of 113 | FAIL 66 of 113 | 36 | NO DATA (0 scored) |
| S2 F1 | J over idle, given the measured seconds: \|measured / given - 1\|, F1 | <= 10% | **FAIL** 17 of 113 | FAIL 17 of 113 | 85 | NO DATA (0 scored) |
| S3 F1 | J with the card at rest, given the measured seconds and rest: \|measured / given - 1\|, F1 | <= 5% | **FAIL** 49 of 113 | FAIL 49 of 113 | 53 | NO DATA (0 scored) |
| S4 F1 | J over idle, the whole forecast (seconds forecast): the measured value inside F1's band | per point | **PASS** 106 of 113 | PASS 106 of 113 | 5 | NO DATA (0 scored) |
| S2 F2 | the same as S2, F2 (its four sparse50 points NOT PRICED, not scored) | <= 10% | **FAIL** 4 of 109 | FAIL 4 of 109 | 95 | NO DATA (0 scored) |
| S3 F2 | the same as S3, F2 | <= 5% | **FAIL** 13 of 109 | FAIL 13 of 109 | 86 | NO DATA (0 scored) |
| S4 F2 | the same as S4, F2's band | per point | **FAIL** 5 of 109 | FAIL 5 of 109 | 94 | NO DATA (0 scored) |
| S6 | the clock: every counted sample in 590-610 MHz (the lowest and the highest counted sample, A1) | per point | **PASS** 113 of 113 | PASS 113 of 113 | 12 | NO DATA (0 scored) |

A rule's verdict per model and arm (registered): PASS if at least 90% of its scored points pass, FAIL otherwise; TOO FEW under 10 scored points; NO DATA with none. A point with no run is NO DATA, never a failure; no run was set aside (the output's `set_aside` is empty).

- **R0 in detail** (measured): 232 checks of C - the smoke's 3, the 226 point runs' and the 3 tie runs' - 0 wrong (verify-e206bd: 121 approx and 111 exact); the smoke's cycles an op p001 1,120.107 (0.825 of F1's 1,357.99), p046 819.193 (0.819 of F1's 999.67), p021 787.470 (1.103 of F1's 713.85), each inside 50-250%.
- **Margins** (desk arithmetic of the counts; the column above): a verdict flips only when that many points change their word (90% of 113 scored points is 102 passes, of 109 it is 99). Every FAIL needs at least 36 more passing points (S1 36, C1 42); S4 F1 would flip if 5 of its passing points failed, S6 if 12 did.

## 4. The summaries (REPORTED): rms / mean of ln(measured / forecast), arm B

Each cell is rms / bias (the mean) of ln(measured / forecast) over the points, with the number of points; a negative bias means the model forecast more than the card measured. By format (the scorer's groups):

| quantity | all | fp32 | fp16 | int8 |
|---|---|---|---|---|
| cycles an op (the counter) against F1 | 0.180 / -0.090 (113) | 0.175 / -0.126 (50) | 0.161 / -0.135 (18) | 0.193 / -0.031 (45) |
| cycles an op against P0 | 0.178 / -0.080 (113) | 0.163 / -0.093 (50) | 0.128 / -0.070 (18) | 0.209 / -0.069 (45) |
| cycles a GEMM (the slowest minion) against F1 | 0.160 / -0.056 (113) | 0.149 / -0.096 (50) | 0.134 / -0.099 (18) | 0.181 / +0.006 (45) |
| seconds a GEMM against F1 | 0.160 / -0.055 (113) | 0.148 / -0.095 (50) | 0.133 / -0.098 (18) | 0.181 / +0.007 (45) |
| F1, J over idle, given the measured seconds | 0.260 / +0.201 (113) | 0.203 / +0.141 (50) | 0.229 / +0.214 (18) | 0.321 / +0.262 (45) |
| F1, J over idle, seconds forecast | 0.225 / +0.146 (113) | 0.145 / +0.046 (50) | 0.148 / +0.116 (18) | 0.309 / +0.269 (45) |
| F1, J with the card at rest, given | 0.067 / +0.055 (113) | 0.067 / +0.052 (50) | 0.082 / +0.075 (18) | 0.061 / +0.051 (45) |
| F1, J with the card at rest, forecast | 0.143 / +0.048 (113) | 0.100 / +0.001 (50) | 0.089 / +0.022 (18) | 0.193 / +0.111 (45) |
| F2, J over idle, given | 0.515 / -0.174 (109) | 0.498 / -0.218 (48) | 0.393 / -0.210 (18) | 0.574 / -0.110 (43) |
| F2, J over idle, forecast | 0.513 / -0.168 (109) | 0.496 / -0.212 (48) | 0.390 / -0.205 (18) | 0.573 / -0.104 (43) |
| F2, J with the card at rest, given | 0.147 / -0.064 (109) | 0.153 / -0.079 (48) | 0.143 / -0.074 (18) | 0.143 / -0.044 (43) |
| F2, J with the card at rest, forecast | 0.214 / -0.054 (109) | 0.200 / -0.094 (48) | 0.179 / -0.094 (18) | 0.240 / +0.009 (43) |
| P0, J over idle, forecast | 0.175 / +0.070 (113) | 0.140 / +0.027 (50) | 0.150 / +0.089 (18) | 0.215 / +0.111 (45) |

By regime, family and data kind (the four quantities the rules lean on most; every quantity of every group is in the JSON):

| group | points | cycles an op (F1) | seconds (F1) | F1 J over idle, given | F2 J over idle, given |
|---|---|---|---|---|---|
| all | 113 | 0.180 / -0.090 | 0.160 / -0.055 | 0.260 / +0.201 | 0.515 / -0.174 (109) |
| regime L2-resident | 12 | 0.242 / +0.165 | 0.245 / +0.169 | 0.168 / -0.033 | 0.592 / +0.517 (10) |
| regime L3-served | 30 | 0.184 / -0.136 | 0.122 / -0.034 | 0.296 / +0.268 | 0.329 / +0.289 (29) |
| regime all fresh | 18 | 0.202 / -0.173 | 0.199 / -0.170 | 0.228 / +0.155 | 0.900 / -0.859 (18) |
| regime mixed | 53 | 0.152 / -0.093 | 0.138 / -0.078 | 0.265 / +0.232 | 0.383 / -0.327 (52) |
| family anchor | 7 | 0.078 / -0.043 | 0.021 / +0.015 | 0.219 / +0.210 | 0.508 / -0.008 (7) |
| family extreme | 13 | 0.170 / -0.078 | 0.170 / -0.067 | 0.252 / +0.233 | 0.393 / -0.350 (13) |
| family kinds | 8 | 0.214 / +0.034 | 0.228 / +0.078 | 0.177 / +0.149 | 0.443 / +0.249 (4) |
| family kladder | 13 | 0.225 / -0.166 | 0.183 / -0.107 | 0.285 / +0.267 | 0.594 / -0.122 (13) |
| family square | 14 | 0.147 / -0.117 | 0.131 / -0.092 | 0.257 / +0.243 | 0.357 / -0.234 (14) |
| family star | 28 | 0.169 / -0.134 | 0.141 / -0.094 | 0.284 / +0.268 | 0.413 / -0.152 (28) |
| family subset | 16 | 0.205 / -0.018 | 0.171 / +0.017 | 0.331 / +0.205 | 0.337 / +0.021 (16) |
| family zeros | 14 | 0.180 / -0.090 | 0.168 / -0.073 | 0.125 / -0.044 | 0.898 / -0.470 (14) |
| kind random | 91 | 0.177 / -0.100 | 0.151 / -0.064 | 0.281 / +0.243 | 0.429 / -0.147 (91) |
| kind real | 4 | 0.225 / +0.012 | 0.231 / +0.068 | 0.199 / +0.174 | 0.443 / +0.249 (4) |
| kind sparse50 | 4 | 0.202 / +0.055 | 0.226 / +0.088 | 0.151 / +0.124 | not priced |
| kind zeros | 14 | 0.180 / -0.090 | 0.168 / -0.073 | 0.125 / -0.044 | 0.898 / -0.470 (14) |

verify-e206bd's own code gives the same 13 summaries over all points (`B.all`: 26 numbers, rms and bias; the largest difference 2.8e-17, desk check of code).

## 5. Point by point: the scorer's words, and verify-e206bd's beside them

Measured values (the scorer's, from the committed `data-e206.json`) beside F1's frozen points; the words are the scorer's per point and rule (C1, S1, S6; S2, S3, S4 for F1 and for F2; NOT PRICED: F2 has no price for the sparse50 kind). The last column sets verify-e206bd's re-derivation beside them: its own words for the same nine rules, and the largest relative difference of its measured values (cycles an op and a GEMM, seconds, J over idle and with the card at rest, the board W at work and at rest) from the scorer's.

| point | shape: M x N x K (shires) | format, kind | family; regime | cycles an op: measured / F1 | ms a GEMM: measured / F1 | mJ over idle: measured / F1 forecast | C1, S1, S6 | F1: S2, S3, S4 | F2: S2, S3, S4 | verify-e206bd |
|---|---|---|---|---|---|---|---|---|---|---|
| p001 | gemmL2x4x4: 2,048 x 2,048 x 2,048 | fp32, random | star; mixed | 1,120.3 / 1,358.0 | 3.828 / 4.635 | 79.04 / 74.02 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p002 | gemmL2x4x4: 2,048 x 2,048 x 8,192 | int8, random | star; mixed | 1,135.6 / 1,361.7 | 3.881 / 4.648 | 40.20 / 33.46 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p003 | gemmL2x4x4: 2,048 x 2,048 x 4,096 | fp16, random | star; mixed | 1,120.5 / 1,356.7 | 3.829 / 4.631 | 73.76 / 66.71 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p004 | gemmL1x4x4: 1,024 x 2,048 x 2,048 | fp32, random | star; L3-served | 831.7 / 1,041.8 | 1.555 / 1.778 | 40.37 / 35.88 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p005 | gemmL1x4x4: 1,024 x 2,048 x 8,192 | int8, random | star; L3-served | 866.2 / 1,084.4 | 1.657 / 1.851 | 19.12 / 13.80 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p006 | gemmL4x4x4: 4,096 x 2,048 x 2,048 | fp32, random | star; mixed | 1,120.5 / 1,358.0 | 7.658 / 9.271 | 158.1 / 148.0 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p007 | gemmL4x4x4: 4,096 x 2,048 x 8,192 | int8, random | star; mixed | 1,135.6 / 1,361.7 | 7.762 / 9.296 | 80.80 / 66.91 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p008 | gemmL8x4x4: 8,192 x 2,048 x 2,048 | fp32, random | star; mixed | 1,120.3 / 1,358.0 | 15.32 / 18.54 | 316.6 / 296.1 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p009 | gemmL8x4x4: 8,192 x 2,048 x 8,192 | int8, random | star; mixed | 1,135.6 / 1,361.7 | 15.52 / 18.59 | 160.5 / 133.8 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p010 | gemmL8x4x4: 8,192 x 2,048 x 4,096 | fp16, random | star; mixed | 1,120.4 / 1,356.7 | 15.31 / 18.52 | 296.6 / 266.8 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p011 | gemmL2x1x4: 2,048 x 512 x 2,048 | fp32, random | star; L3-served | 831.7 / 1,041.8 | 0.7776 / 0.8890 | 20.00 / 17.94 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p012 | gemmL2x1x4: 2,048 x 512 x 8,192 | int8, random | star; L3-served | 866.0 / 1,084.4 | 0.8286 / 0.9253 | 9.579 / 6.898 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p013 | gemmL2x2x4: 2,048 x 1,024 x 2,048 | fp32, random | star; L3-served | 831.8 / 1,041.8 | 1.556 / 1.778 | 39.93 / 35.88 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p014 | gemmL2x2x4: 2,048 x 1,024 x 8,192 | int8, random | star; L3-served | 866.2 / 1,084.4 | 1.657 / 1.851 | 19.12 / 13.80 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p015 | gemmL2x8x4: 2,048 x 4,096 x 2,048 | fp32, random | star; mixed | 1,372.6 / 1,358.6 | 9.381 / 9.274 | 164.9 / 148.1 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p016 | gemmL2x8x4: 2,048 x 4,096 x 8,192 | int8, random | star; mixed | 1,356.2 / 1,362.2 | 9.276 / 9.299 | 89.02 / 66.93 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p017 | gemmL2x16x4: 2,048 x 8,192 x 2,048 | fp32, random | star; mixed | 1,369.0 / 1,341.0 | 18.86 / 18.31 | 332.1 / 295.4 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p018 | gemmL2x16x4: 2,048 x 8,192 x 8,192 | int8, random | star; mixed | 1,364.5 / 1,346.8 | 18.78 / 18.39 | 178.5 / 132.6 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p019 | gemmL2x16x4: 2,048 x 8,192 x 4,096 | fp16, random | star; mixed | 1,370.5 / 1,339.7 | 18.87 / 18.29 | 313.8 / 265.9 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p020 | gemmL2x4x1: 2,048 x 2,048 x 512 | fp32, random | star; L3-served | 760.1 / 817.1 | 0.7320 / 0.6972 | 19.19 / 15.73 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p021 | gemmL2x4x1: 2,048 x 2,048 x 2,048 | int8, random | star; L3-served | 787.5 / 713.8 | 0.7567 / 0.6091 | 8.100 / 5.379 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p022 | gemmL2x4x2: 2,048 x 2,048 x 1,024 | fp32, random | star; L3-served | 819.2 / 1,000.9 | 1.546 / 1.708 | 39.96 / 35.07 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p023 | gemmL2x4x2: 2,048 x 2,048 x 4,096 | int8, random | star; L3-served | 854.0 / 1,017.0 | 1.644 / 1.736 | 18.71 / 13.24 | FAIL, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p024 | gemmL2x4x8: 2,048 x 2,048 x 4,096 | fp32, random | star; mixed | 1,433.1 / 1,446.1 | 9.796 / 9.872 | 167.0 / 149.9 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p025 | gemmL2x4x8: 2,048 x 2,048 x 16,384 | int8, random | star; mixed | 1,436.8 / 1,439.0 | 9.819 / 9.824 | 90.77 / 70.22 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p026 | gemmL2x4x16: 2,048 x 2,048 x 8,192 | fp32, random | star; all fresh | 1,521.6 / 1,886.5 | 20.80 / 25.76 | 336.5 / 322.1 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p027 | gemmL2x4x16: 2,048 x 2,048 x 32,768 | int8, random | star; all fresh | 1,529.7 / 1,825.3 | 20.91 / 24.92 | 185.5 / 173.7 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p028 | gemmL2x4x16: 2,048 x 2,048 x 16,384 | fp16, random | star; all fresh | 1,521.1 / 1,885.3 | 20.79 / 25.74 | 314.9 / 299.6 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p030 | gemmL1x1x1: 1,024 x 512 x 2,048 | int8, random | kladder; L2-resident | 388.0 / 275.9 | 0.04162 / 0.02943 | 0.6494 / 0.4479 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p032 | gemmL1x1x2: 1,024 x 512 x 1,024 | fp32, random | kladder; L3-served | 805.9 / 960.1 | 0.1920 / 0.2048 | 4.969 / 4.284 | FAIL, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p033 | gemmL1x1x2: 1,024 x 512 x 4,096 | int8, random | kladder; L3-served | 844.8 / 949.6 | 0.2038 / 0.2026 | 2.260 / 1.586 | FAIL, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p034 | gemmL1x1x4: 1,024 x 512 x 2,048 | fp32, random | kladder; L3-served | 831.7 / 1,041.8 | 0.3888 / 0.4445 | 9.923 / 8.969 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p035 | gemmL1x1x4: 1,024 x 512 x 8,192 | int8, random | kladder; L3-served | 866.0 / 1,084.4 | 0.4143 / 0.4627 | 4.804 / 3.449 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p036 | gemmL1x1x4: 1,024 x 512 x 4,096 | fp16, random | kladder; L3-served | 831.7 / 1,040.4 | 0.3889 / 0.4439 | 9.298 / 7.887 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p037 | gemmL1x1x8: 1,024 x 512 x 4,096 | fp32, random | kladder; L3-served | 831.1 / 1,041.8 | 0.7773 / 0.8890 | 19.90 / 17.94 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p038 | gemmL1x1x8: 1,024 x 512 x 16,384 | int8, random | kladder; L3-served | 866.3 / 1,084.4 | 0.8282 / 0.9253 | 9.431 / 6.898 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p039 | gemmL1x1x16: 1,024 x 512 x 8,192 | fp32, random | kladder; all fresh | 1,395.3 / 1,886.5 | 2.405 / 3.220 | 40.01 / 40.26 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p040 | gemmL1x1x16: 1,024 x 512 x 32,768 | int8, random | kladder; all fresh | 1,421.2 / 1,825.3 | 2.462 / 3.115 | 21.37 / 21.72 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p041 | gemmL1x1x32: 1,024 x 512 x 16,384 | fp32, random | kladder; all fresh | 1,573.8 / 1,886.5 | 5.382 / 6.439 | 84.46 / 80.53 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p042 | gemmL1x1x32: 1,024 x 512 x 65,536 | int8, random | kladder; all fresh | 1,544.2 / 1,825.3 | 5.275 / 6.230 | 48.09 / 43.43 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p043 | gemmL1x1x32: 1,024 x 512 x 32,768 | fp16, random | kladder; all fresh | 1,577.6 / 1,885.3 | 5.387 / 6.435 | 80.86 / 74.89 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p044 | gemmL1x2x2: 1,024 x 1,024 x 1,024 | fp32, random | square; L3-served | 819.3 / 1,000.9 | 0.3865 / 0.4271 | 9.988 / 8.768 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p045 | gemmL1x2x1: 1,024 x 1,024 x 1,024 | fp16, random | square; L3-served | 744.6 / 795.8 | 0.1797 / 0.1698 | 4.412 / 3.534 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p046 | gemmL2x4x2: 2,048 x 2,048 x 2,048 | fp16, random | square; L3-served | 819.2 / 999.7 | 1.546 / 1.706 | 37.16 / 31.00 | FAIL, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p047 | gemmL3x6x6: 3,072 x 3,072 x 3,072 | fp32, random | square; mixed | 1,149.8 / 1,370.3 | 13.26 / 15.79 | 266.7 / 250.2 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p048 | gemmL3x6x3: 3,072 x 3,072 x 3,072 | fp16, random | square; mixed | 1,116.4 / 1,369.0 | 6.438 / 7.885 | 125.8 / 112.9 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p049 | gemmL4x8x8: 4,096 x 4,096 x 4,096 | fp32, random | square; mixed | 1,416.7 / 1,419.7 | 38.74 / 38.77 | 662.8 / 597.3 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p050 | gemmL4x8x4: 4,096 x 4,096 x 4,096 | fp16, random | square; mixed | 1,372.6 / 1,357.3 | 18.77 / 18.53 | 310.8 / 266.9 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p051 | gemmL4x8x2: 4,096 x 4,096 x 4,096 | int8, random | square; mixed | 1,109.0 / 1,294.8 | 7.581 / 8.839 | 80.58 / 64.66 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p052 | gemmL6x12x12: 6,144 x 6,144 x 6,144 | fp32, random | square; mixed | 1,433.7 / 1,604.9 | 132.3 / 147.9 | 2,233 / 2,074 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p053 | gemmL6x12x6: 6,144 x 6,144 x 6,144 | fp16, random | square; mixed | 1,232.7 / 1,345.5 | 56.99 / 62.00 | 1,042 / 898.5 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p054 | gemmL6x12x3: 6,144 x 6,144 x 6,144 | int8, random | square; mixed | 1,128.5 / 1,351.9 | 26.03 / 31.15 | 279.6 / 224.4 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p055 | gemmL8x16x16: 8,192 x 8,192 x 8,192 | fp32, random | square; all fresh | 1,450.0 / 1,886.5 | 317.3 / 412.1 | 5,306 / 5,154 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p056 | gemmL8x16x8: 8,192 x 8,192 x 8,192 | fp16, random | square; mixed | 1,390.0 / 1,405.1 | 152.5 / 153.5 | 2,503 / 2,156 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p057 | gemmL8x16x4: 8,192 x 8,192 x 8,192 | int8, random | square; mixed | 1,364.9 / 1,346.8 | 75.15 / 73.55 | 723.9 / 530.2 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p058 | gemmL8x1x4: 8,192 x 512 x 2,048 | fp32, random | extreme; mixed | 1,406.5 / 1,323.4 | 4.859 / 4.517 | 81.53 / 73.69 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p059 | gemmL8x1x4: 8,192 x 512 x 8,192 | int8, random | extreme; mixed | 1,443.5 / 1,331.3 | 5.011 / 4.544 | 44.60 / 32.81 | FAIL, FAIL, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p060 | gemmL1x16x4: 1,024 x 8,192 x 2,048 | fp32, random | extreme; mixed | 1,368.8 / 1,323.4 | 9.450 / 9.034 | 165.8 / 147.4 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p061 | gemmL1x16x4: 1,024 x 8,192 x 8,192 | int8, random | extreme; mixed | 1,367.8 / 1,331.3 | 9.426 / 9.089 | 89.50 / 65.62 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p062 | gemmL1x15x4: 1,024 x 7,680 x 2,048 | fp32, random | extreme; mixed | 1,080.5 / 1,323.4 | 7.013 / 8.469 | 149.9 / 138.2 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p063 | gemmL1x15x4: 1,024 x 7,680 x 8,192 | int8, random | extreme; mixed | 1,092.2 / 1,331.3 | 7.092 / 8.521 | 75.65 / 61.52 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p064 | gemmL8x16x1: 8,192 x 8,192 x 512 | fp32, random | extreme; mixed | 1,140.7 / 1,100.9 | 15.93 / 15.03 | 322.3 / 256.6 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p065 | gemmL8x16x1: 8,192 x 8,192 x 2,048 | int8, random | extreme; mixed | 1,165.7 / 951.0 | 16.28 / 12.98 | 164.1 / 105.6 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p066 | gemmL8x1x16: 8,192 x 512 x 8,192 | fp32, random | extreme; all fresh | 1,395.6 / 1,886.5 | 19.25 / 25.76 | 317.7 / 322.1 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p067 | gemmL1x16x16: 1,024 x 8,192 x 8,192 | fp32, random | extreme; all fresh | 1,436.0 / 1,886.5 | 39.26 / 51.51 | 658.5 / 644.2 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p068 | gemmL3x5x7: 3,072 x 2,560 x 3,584 | fp32, random | extreme; mixed | 1,173.0 / 1,379.7 | 13.15 / 15.45 | 261.2 / 243.6 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p069 | gemmL3x5x7: 3,072 x 2,560 x 7,168 | fp16, random | extreme; mixed | 1,172.9 / 1,378.4 | 13.15 / 15.44 | 241.3 / 219.9 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p070 | gemmL3x5x7: 3,072 x 2,560 x 14,336 | int8, random | extreme; mixed | 1,179.4 / 1,380.7 | 13.23 / 15.46 | 134.5 / 111.1 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p073 | gemmc1: 1,024 x 512 x 2,048 | int8, random | anchor; L2-resident | 299.8 / 291.8 | 0.03220 / 0.03112 | 0.6391 / 0.4736 | PASS, FAIL, PASS | FAIL, FAIL, FAIL | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p074 | gemmc8s: 8,192 x 512 x 512 | fp32, random | anchor; L3-served | 753.7 / 856.9 | 0.7341 / 0.7313 | 19.67 / 15.93 | FAIL, PASS, PASS | FAIL, FAIL, FAIL | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p075 | gemmc8s: 8,192 x 512 x 1,024 | fp16, random | anchor; L3-served | 753.7 / 856.7 | 0.7341 / 0.7310 | 18.37 / 14.34 | FAIL, PASS, PASS | FAIL, FAIL, FAIL | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p076 | gemmc8s: 8,192 x 512 x 2,048 | int8, random | anchor; L3-served | 785.9 / 861.7 | 0.7656 / 0.7353 | 8.705 / 6.126 | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p077 | gemmc16s: 16,384 x 512 x 512 | fp32, random | anchor; all fresh | 1,410.1 / 1,406.4 | 2.409 / 2.400 | 39.41 / 34.27 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p078 | gemmc16s: 16,384 x 512 x 1,024 | fp16, random | anchor; all fresh | 1,410.0 / 1,406.6 | 2.409 / 2.401 | 37.37 / 32.08 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p079 | gemmc16s: 16,384 x 512 x 2,048 | int8, random | anchor; all fresh | 1,403.9 / 1,384.0 | 2.398 / 2.362 | 20.98 / 17.69 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p080 | gemmL1x1x1: 1,024 x 512 x 512 | fp32, zeros | zeros; L2-resident | 538.0 / 551.5 | 0.05759 / 0.05882 | 0.2548 / 0.2952 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p081 | gemmL1x1x1: 1,024 x 512 x 2,048 | int8, zeros | zeros; L2-resident | 388.0 / 275.9 | 0.04162 / 0.02943 | 0.1914 / 0.1457 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p082 | gemmL1x1x4: 1,024 x 512 x 2,048 | fp32, zeros | zeros; L3-served | 831.7 / 1,041.8 | 0.3889 / 0.4445 | 1.831 / 2.071 | FAIL, FAIL, PASS | PASS, PASS, PASS | PASS, PASS, PASS | same 9 of 9; 0 |
| p083 | gemmL1x1x4: 1,024 x 512 x 4,096 | fp16, zeros | zeros; L3-served | 831.7 / 1,040.4 | 0.3888 / 0.4439 | 1.857 / 1.946 | FAIL, FAIL, PASS | PASS, PASS, PASS | PASS, PASS, PASS | same 9 of 9; 0 |
| p084 | gemmL1x1x32: 1,024 x 512 x 16,384 | fp32, zeros | zeros; all fresh | 1,575.7 / 1,886.5 | 5.386 / 6.439 | 23.35 / 32.88 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p085 | gemmL1x1x32: 1,024 x 512 x 65,536 | int8, zeros | zeros; all fresh | 1,544.6 / 1,825.3 | 5.277 / 6.230 | 21.53 / 24.75 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p086 | gemmL2x4x4: 2,048 x 2,048 x 2,048 | fp32, zeros | zeros; mixed | 1,120.5 / 1,358.0 | 3.829 / 4.635 | 17.36 / 22.73 | FAIL, FAIL, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p087 | gemmL2x4x4: 2,048 x 2,048 x 4,096 | fp16, zeros | zeros; mixed | 1,120.6 / 1,356.7 | 3.829 / 4.631 | 17.90 / 20.93 | FAIL, FAIL, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p088 | gemmL2x4x4: 2,048 x 2,048 x 8,192 | int8, zeros | zeros; mixed | 1,135.5 / 1,361.7 | 3.881 / 4.648 | 16.16 / 16.95 | FAIL, FAIL, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p089 | gemmL8x16x16: 8,192 x 8,192 x 8,192 | fp32, zeros | zeros; all fresh | 1,450.0 / 1,886.5 | 317.3 / 412.1 | 1,391 / 2,104 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p090 | gemmL8x16x4: 8,192 x 8,192 x 8,192 | int8, zeros | zeros; mixed | 1,365.2 / 1,346.8 | 75.15 / 73.55 | 307.5 / 267.1 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p091 | gemmL8x16x1: 8,192 x 8,192 x 512 | fp32, zeros | zeros; mixed | 1,140.5 / 1,100.9 | 15.93 / 15.03 | 81.33 / 75.52 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p092 | gemmc1: 1,024 x 512 x 512 | fp32, zeros | zeros; L2-resident | 536.9 / 538.0 | 0.05747 / 0.05739 | 0.2359 / 0.2880 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p093 | gemmc16s: 16,384 x 512 x 512 | fp32, zeros | zeros; all fresh | 1,410.2 / 1,406.4 | 2.409 / 2.400 | 9.590 / 12.23 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p094 | gemmL4x8x4: 512 x 1,024 x 2,048 (1 shire, 0x1) | fp32, random | subset; L3-served | 1,217.2 / 1,041.8 | 16.64 / 14.22 | 11.15 / 8.969 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p095 | gemmL4x8x4: 512 x 1,024 x 8,192 (1 shire, 0x1) | int8, random | subset; L3-served | 1,259.5 / 1,084.4 | 17.21 / 14.81 | 7.230 / 3.449 | PASS, PASS, PASS | FAIL, PASS, FAIL | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p096 | gemmL4x8x4: 512 x 4,096 x 2,048 (4 shires, 0xf) | fp32, random | subset; mixed | 1,004.1 / 1,358.6 | 16.65 / 18.55 | 46.29 / 37.01 | FAIL, FAIL, PASS | FAIL, PASS, PASS | FAIL, PASS, PASS | same 9 of 9; 0 |
| p097 | gemmL4x8x4: 512 x 4,096 x 8,192 (4 shires, 0xf) | int8, random | subset; mixed | 1,036.6 / 1,362.2 | 17.20 / 18.60 | 25.80 / 16.73 | FAIL, FAIL, PASS | FAIL, PASS, FAIL | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p098 | gemmL4x8x4: 1,024 x 4,096 x 2,048 (8 shires, 0xff) | fp32, random | subset; mixed | 1,037.0 / 1,358.6 | 15.15 / 18.55 | 84.40 / 74.03 | FAIL, FAIL, PASS | FAIL, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p099 | gemmL4x8x4: 1,024 x 4,096 x 8,192 (8 shires, 0xff) | int8, random | subset; mixed | 1,073.5 / 1,362.2 | 15.80 / 18.60 | 48.27 / 33.47 | FAIL, FAIL, PASS | FAIL, PASS, FAIL | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p100 | gemmL4x8x4: 4,096 x 1,024 x 2,048 (8 shires, 0x11111111) | fp32, random | subset; mixed | 1,229.1 / 1,077.0 | 16.80 / 14.70 | 77.11 / 71.89 | PASS, PASS, PASS | PASS, PASS, PASS | PASS, PASS, PASS | same 9 of 9; 0 |
| p101 | gemmL4x8x4: 4,096 x 1,024 x 8,192 (8 shires, 0x11111111) | int8, random | subset; mixed | 1,223.5 / 1,115.2 | 16.72 / 15.23 | 42.48 / 28.24 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p102 | gemmL4x8x4: 2,048 x 4,096 x 2,048 (16 shires, 0xffff) | fp32, random | subset; mixed | 1,122.2 / 1,358.6 | 15.34 / 18.55 | 158.7 / 148.1 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p103 | gemmL4x8x4: 2,048 x 4,096 x 8,192 (16 shires, 0xffff) | int8, random | subset; mixed | 1,135.4 / 1,362.2 | 15.52 / 18.60 | 85.98 / 66.93 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p104 | gemmL4x8x4: 4,096 x 4,096 x 2,048 | fp32, random | subset; mixed | 1,371.3 / 1,358.6 | 18.75 / 18.55 | 332.2 / 296.1 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p105 | gemmL4x8x4: 4,096 x 4,096 x 8,192 | int8, random | subset; mixed | 1,358.0 / 1,362.2 | 18.56 / 18.60 | 178.4 / 133.9 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p106 | gemmL1x1x1: 128 x 128 x 512 (1 shire, 0x1) | fp32, random | subset; L2-resident | 538.8 / 551.5 | 0.05753 / 0.05882 | 0.04747 / 0.05119 | PASS, PASS, PASS | PASS, PASS, PASS | PASS, PASS, PASS | same 9 of 9; 0 |
| p107 | gemmL1x1x1: 128 x 128 x 2,048 (1 shire, 0x1) | int8, random | subset; L2-resident | 389.2 / 275.9 | 0.04155 / 0.02943 | 0.01299 / 0.01400 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p108 | gemmL1x1x1: 256 x 512 x 512 (8 shires, 0xff) | fp32, random | subset; L2-resident | 538.1 / 551.5 | 0.05754 / 0.05882 | 0.4416 / 0.4095 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p109 | gemmL1x1x1: 256 x 512 x 2,048 (8 shires, 0xff) | int8, random | subset; L2-resident | 388.0 / 275.9 | 0.04160 / 0.02943 | 0.1539 / 0.1120 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p111 | gemmL2x4x4: 2,048 x 2,048 x 2,048 | fp32, real | kinds; mixed | 1,120.5 / 1,358.0 | 3.829 / 4.635 | 76.83 / 73.75 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p113 | gemmL2x4x2: 2,048 x 2,048 x 2,048 | fp16, real | kinds; L3-served | 819.2 / 999.7 | 1.546 / 1.706 | 36.28 / 30.59 | FAIL, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p114 | gemmL1x1x1: 1,024 x 512 x 2,048 | int8, real | kinds; L2-resident | 388.0 / 275.9 | 0.04162 / 0.02943 | 0.5528 / 0.3851 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p115 | gemmL2x4x1: 2,048 x 2,048 x 2,048 | int8, real | kinds; L3-served | 787.5 / 713.8 | 0.7567 / 0.6091 | 6.999 / 4.714 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p116 | gemmL1x1x1: 1,024 x 512 x 512 | fp32, sparse50 | kinds; L2-resident | 538.0 / 551.5 | 0.05759 / 0.05882 | 0.8961 / 0.8116 | PASS, PASS, PASS | FAIL, PASS, PASS | NOT PRICED | same 9 of 9; 0 |
| p117 | gemmL2x4x4: 2,048 x 2,048 x 2,048 | fp32, sparse50 | kinds; mixed | 1,120.1 / 1,358.0 | 3.829 / 4.635 | 44.58 / 44.05 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | NOT PRICED | same 9 of 9; 0 |
| p118 | gemmL1x1x1: 1,024 x 512 x 2,048 | int8, sparse50 | kinds; L2-resident | 388.0 / 275.9 | 0.04162 / 0.02943 | 0.5417 / 0.3888 | PASS, PASS, PASS | PASS, PASS, PASS | NOT PRICED | same 9 of 9; 0 |
| p119 | gemmL2x4x1: 2,048 x 2,048 x 2,048 | int8, sparse50 | kinds; L3-served | 787.5 / 713.8 | 0.7567 / 0.6091 | 6.754 / 4.505 | PASS, PASS, PASS | FAIL, PASS, PASS | NOT PRICED | same 9 of 9; 0 |

Counts over the table: C1 60 PASS / 53 FAIL; S1 66 / 47; S6 113 / 0; F1 S2 17 / 96, S3 49 / 64, S4 106 / 7; F2 S2 4 / 105, S3 13 / 96, S4 5 / 104, and 4 NOT PRICED. Each count equals its rule's in section 3. verify-e206bd (desk check of code, its own code from the committed raw files, nothing imported from the kit): the same nine words at 113 of 113 points, 0 relative difference in every measured value, and its given values within 3.3e-16 of the scorer's.

## 6. The readings (REPORTED: registered before the data, never verdicts)

- **(a) Contention** (cycles an op against shires; F1 holds each subset at its own lines' time), measured / F1:

| shape, format | 1 shire | 4 | 8 | 8 (0x11111111) | 16 | 32 |
|---|---|---|---|---|---|---|
| gemmL4x8x4, fp32 | 1,217.2 / 1,041.8 (p094) | 1,004.1 / 1,358.6 (p096) | 1,037.0 / 1,358.6 (p098) | 1,229.1 / 1,077.0 (p100) | 1,122.2 / 1,358.6 (p102) | 1,371.3 / 1,358.6 (p104) |
| gemmL4x8x4, int8 | 1,259.5 / 1,084.4 (p095) | 1,036.6 / 1,362.2 (p097) | 1,073.5 / 1,362.2 (p099) | 1,223.5 / 1,115.2 (p101) | 1,135.4 / 1,362.2 (p103) | 1,358.0 / 1,362.2 (p105) |
| gemmL1x1x1, fp32 | 538.8 / 551.5 (p106) | - | 538.1 / 551.5 (p108) | - | - | - |
| gemmL1x1x1, int8 | 389.2 / 275.9 (p107) | - | 388.0 / 275.9 (p109) | - | - | 388.0 / 275.9 (p030) |

- **(b) The stride step** (`gemmL1x16x4` over `gemmL1x15x4`, cycles an op): fp32 1.2668, int8 1.2523 (the reference: "E169: +27-30% at its power-of-two step").
- **(c) The zeros gap** (zeros over random at the same shape and format), 12 pairs: J over idle gemmL1x1x1 int8 0.295; gemmL1x1x32 fp32 0.276; gemmL1x1x32 int8 0.448; gemmL1x1x4 fp16 0.200; gemmL1x1x4 fp32 0.185; gemmL2x4x4 fp16 0.243; gemmL2x4x4 fp32 0.220; gemmL2x4x4 int8 0.402; gemmL8x16x1 fp32 0.252; gemmL8x16x16 fp32 0.262; gemmL8x16x4 int8 0.425; gemmc16s fp32 0.243; seconds 0.9999-1.0007 (zeros change the joules, not the time).
- **(d) Card 1 over aifoundry3:** no value in this output: the scorer ran on this directory alone, one arm a directory (section 8).
- **(e) `gemmL1x1x1` against `gemmc1`** (the same work through two loop codes, cycles an op): int8 1.2944 (arm B's one such pair: its only full-chip `gemmc1` point on random data, p073, is int8).
- **(f) The tie's drift** (p001 at runs 1, 115 and 229): seconds 3.8279 / 3.8284 / 3.8286 ms; the board at work 51.42 / 51.10 / 51.66 W; J over idle 77.97 / 78.71 / 78.52 mJ (+0.71% first to last).
- **(g) P0's error:** in the summaries (section 4).
- **(h) The timing simulation against the card** (his question: "See check how well the timing simulation for the matte mold matches reality and the energy."). The scorer gives two ratios per point, in the JSON: the measured cycles a GEMM over the simulator's instruction count a minion a GEMM (the step law of E206.md 7 (h): the simulator counts instructions, not cycles), and the measured cycles an op over the tensor unit's resident floor (546 cycles an op in fp32 and fp16, 318 in int8: E101's resident loop on aifoundry3). Both exist at the 104 points with simulator steps (not at the 9 law-arm points p073, p074, p075, p076, p077, p078, p079, p092, p093). Over those 104 points (desk arithmetic over the scorer's values, post hoc: the scorer prints no median): cycles a GEMM over the simulator's steps, median **24.26** (8.21-33.82); cycles an op over the tensor floor, median **2.509** (0.985-4.86). Section 9.3 reads the floor over all 113 points.

## 7. MM1-v0 and MM1-v1 on these points, scored blind (REPORTED; no rule is registered for MM1)

**Blind.** Both MM1 forecast files were committed and pushed to the public repository's main branch before the session's first card command (00:13:26 PST Tue 17 Nov, the committed `session/session.log`), and both are unchanged at the data commit and now:

| forecast | file | commit | committed (PST) | pushed (PST) | sha256 |
|---|---|---|---|---|---|
| MM1-v0 (its frozen predictor of `2d1413f5`, unchanged, called with card 1's arguments) | [`mm1/v0/forecasts-e206-armB.csv`](../../../../tools/matmul/mm1/v0/forecasts-e206-armB.csv) | `e35a06cb` | 2026-11-16 20:13:57 | by 20:14:00 | `1edf61ff0d7a4c40c25131e79bb702bab104c6379d71a26653486ed86a798aae` |
| MM1-v1 (the landed predictor of `25d2e74e`, unchanged) | [`mm1/v1/forecasts-e206-armB.csv`](../../../../tools/matmul/mm1/v1/forecasts-e206-armB.csv) | `d3f031d1` | 2026-11-16 21:18:46 | 21:18:48 | `3f9340020c061a264254b4497039127dd46f55c37d51f891abb8930cc5b8f02a` |
| F1 and F2 (the registration) | [`forecast-e206.json`](../../../../tools/claims-v3/e206/forecast-e206.json) | `eb2f7ac2` | 2026-11-16 16:01:50 | - | `d8f3a8b1e3d22f515581aab1a9cc43ca30fbb6e1c61c96d7cc14bf32697bd888` |

MM1-v0 was frozen 3 h 59 min and MM1-v1 2 h 54 min before the first card command (from the push times). The figures below are verify-e206bd's (`HOLDS WITH FIXES`), computed with its own code from its re-derivation of the committed records, which equals the scorer's measured values to 0. **Its method:** the error is forecast / measured - 1 (rms and bias in percent; the scorer's summaries use ln(measured / forecast), and in those terms its F1 figures equal the scorer's). Cycles an op is read two ways: the counter's mean over minions, and the wall (cycles a GEMM of the slowest minion over the ops). MM1's seconds are ops x its wall cycles / 600 MHz. Given the measured seconds, MM1's W over idle is affine in the op rate, W = A + (W_forecast - A) t_forecast / t_measured, with A MM1-v0's card-1 awake power x minions / 1024 or MM1-v1's own `W_affine_A_W` column; J over idle given = that W x the measured seconds; J at rest adds the measured rest power x the seconds (MM1 froze no card-1 rest power, so every model's J at rest, seconds forecast, uses the measured rest). F1's given values are its W point x the measured seconds; F2's are the ledger form.

**Gaps:** MM1 forecasts no energy at 8 points (p111, p113, p114, p115, p116, p117, p118, p119: the real and sparse50 kinds), so its energy figures are over 105 points; F2 prices no sparse50 point (4). MM1-v0's CSV carries no seconds at its 9 law-arm points (p073, p074, p075, p076, p077, p078, p079, p092, p093): verify-e206bd derived them from v0's own cycles, as on arm A.

**All 113 points**, rms (bias) of forecast / measured - 1, and the points scored:

| quantity | MM1-v0 | MM1-v1 | F1 | F2 |
|---|---|---|---|---|
| cycles an op, the counter's mean | 9.8% (-2.9%); 113 | 4.7% (-1.6%); 113 | 19.2% (+10.7%); 113 | - |
| cycles an op, the wall (the slowest minion) | 9.2% (-2.6%); 113 | 4.6% (-0.7%); 113 | 16.5% (+6.9%); 113 | - |
| seconds a GEMM | 9.2% (-2.7%); 113 | 4.6% (-0.8%); 113 | 16.4% (+6.8%); 113 | - |
| W over idle, seconds forecast | 19.5% (+8.2%); 105 | 14.7% (+7.3%); 105 | 22.6% (-17.0%); 113 | 59.4% (+22.0%); 109 |
| J over idle, given the measured seconds | 15.5% (+6.1%); 105 | 14.3% (+6.8%); 105 | 22.6% (-17.0%); 113 | 77.0% (+33.9%); 109 |
| J over idle, seconds forecast | 15.0% (+5.2%); 105 | 14.1% (+6.5%); 105 | 19.9% (-12.3%); 113 | 76.4% (+33.2%); 109 |
| J at rest, given the measured seconds | 2.4% (+0.8%); 105 | 2.1% (+0.7%); 105 | 6.5% (-5.3%); 113 | 16.4% (+7.6%); 109 |
| J at rest, seconds forecast (the measured rest) | 7.4% (-1.0%); 105 | 4.4% (+0.2%); 105 | 13.1% (+0.9%); 113 | 25.6% (+12.3%); 109 |

In the scorer's ln terms (rms of ln(measured / forecast)): F1's cycles 0.180, seconds 0.160 and J over idle given 0.260 are the scorer's own summaries (section 4); MM1-v1's are 0.048, 0.047 and 0.124, and MM1-v0's 0.104, 0.099 and 0.134.

**Head to head** (the points where the first model is closer to the measured value / the points both forecast), all 113:

| quantity | MM1-v0 closer than F1 | MM1-v1 closer than F1 | MM1-v1 closer than MM1-v0 | MM1-v0 closer than F2 | MM1-v1 closer than F2 |
|---|---|---|---|---|---|
| cycles an op, the counter's mean | 85/113 | 87/113 | 69/113 (1 tied) | - | - |
| seconds a GEMM | 87/113 (1 tied) | 91/113 (1 tied) | 70/113 (6 tied) | - | - |
| J over idle, given the measured seconds | 83/105 | 85/105 | 66/105 | 101/105 | 99/105 |
| J over idle, seconds forecast | 80/105 | 80/105 | 41/105 | 101/105 | 99/105 |

**By shape class**, rms (bias) in percent; the last two columns count the points where each MM1 is closer than F1:

| class | points | cycles (counter): v0 / v1 / F1 | J over idle given: v0 / v1 / F1 / F2 | closer than F1, cycles: v0, v1 | closer than F1, J over idle given: v0, v1 |
|---|---|---|---|---|---|
| inside the L3 (<= 32 MB) | 21 | 6.7 (-1.9) / 5.3 (-4.3) / 22.2 (+17.6) | 5.6 (-4.0) / 5.4 (-3.8) / 25.5 (-24.1) / 26.9 (-25.5) | 20 of 21, 19 of 21 | 20 of 21, 20 of 21 |
| the knee (33-70 MB) | 5 | 12.5 (-12.2) / 4.1 (-3.5) / 25.8 (+25.2) | 4.5 (+2.6) / 5.6 (+4.6) / 24.8 (-24.6) / 105.4 (+85.5) | 5 of 5, 5 of 5 | 5 of 5, 5 of 5 |
| past the L3 (> 70 MB) | 40 | 7.7 (-3.5) / 4.1 (-0.6) / 16.6 (+10.8) | 6.3 (+4.4) / 5.8 (+4.4) / 21.9 (-20.7) / 66.6 (+55.3) | 25 of 40, 28 of 40 | 39 of 40, 39 of 40 |
| stride pair (1x15x4 / 1x16x4) | 4 | 13.2 (+5.3) / 3.6 (+0.7) / 15.8 (+9.6) | 5.1 (+4.3) / 4.3 (+3.6) / 23.6 (-21.7) / 33.4 (+31.6) | 2 of 4, 3 of 4 | 4 of 4, 4 of 4 |
| subset (mask < 32 shires) | 14 | 14.4 (+2.9) / 6.1 (-1.1) / 22.5 (+4.5) | 21.0 (+4.3) / 24.0 (+15.8) / 29.6 (-15.4) / 29.9 (-1.3) | 14 of 14, 13 of 14 | 9 of 14, 9 of 14 |
| law arms (gemmc1/c8s/c16s) | 7 | 4.8 (+1.7) / 4.2 (+2.0) / 8.2 (+4.6) | 9.7 (+2.2) / 7.4 (-0.0) / 19.4 (-18.8) / 59.2 (+14.6) | 3 of 7, 3 of 7 | 6 of 7, 7 of 7 |
| data kind: zeros | 14 | 9.2 (-4.6) / 3.9 (-1.7) / 19.0 (+10.7) | 33.7 (+31.4) / 27.8 (+25.7) / 13.5 (+5.2) / 158.3 (+103.7) | 10 of 14, 10 of 14 | 0 of 14, 1 of 14 |
| data kind: real | 4 | 14.9 (-11.4) / 5.9 (-3.6) / 21.5 (+1.2) | - / - / 17.7 (-15.5) / 36.4 (-16.4) | 3 of 4, 3 of 4 | -, - |
| data kind: sparse50 | 4 | 14.9 (-12.0) / 5.9 (-3.2) / 18.6 (-3.6) | - / - / 13.8 (-11.3) / - | 3 of 4, 3 of 4 | -, - |

**By format**, rms in percent: fp32 (50 points): cycles v0 7.9, v1 4.4, F1 19.6; J over idle given v0 15.9, v1 14.1, F1 18.4, F2 79.8; fp16 (18 points): cycles v0 5.8, v1 4.1, F1 17.7; J over idle given v0 9.1, v1 7.9, F1 20.1, F2 53.5; int8 (45 points): cycles v0 12.5, v1 5.3, F1 19.3; J over idle given v0 17.1, v1 16.5, F1 27.2, F2 81.9.

**Two blinder subsets.** 25 of arm B's 113 configurations had already run on card 1 in the model session's E208 sweep (Mon 16 Nov, README.md's never-run reading), and 3 more (p055-p057, E190's 8,192-cubed GEMMs) in E190; MM1's fit tables hold E190's card-1 rows (the data verifier's desk read). rms in percent (points):

| subset | cycles: v0 / v1 / F1 | J over idle given: v0 / v1 / F1 / F2 | MM1-v1 closer than F1: cycles; J | MM1-v1 closer than F2: J |
|---|---|---|---|---|
| without E208's 25 configurations | 9.8 / 4.7 / 18.4 (88) | 16.1 / 15.3 (80) / 23.2 (88) / 82.0 (84) | 64 of 88; 67 of 80 | 77 of 80 |
| never run on card 1 before arm B | 10.0 / 4.7 / 18.5 (85) | 16.4 / 15.5 (77) / 23.2 (85) / 82.6 (81) | 63 of 85; 64 of 77 | 74 of 77 |

**The largest misses** (post hoc readings of blind data, from verify-e206bd's point records):

- MM1-v0 reads -25.48% to -25.25% in cycles (the counter) at every int8 `gemmL1x1x1` point (p030, p081, p107, p109, p114, p118); MM1-v1 reads -6.4% to +0.8% there. At the int8 `gemmL2x4x1` points (p021, p115, p119) MM1-v1 reads -11.6% and MM1-v0 -12.5%.
- Both MM1 versions read the zeros kind high in J over idle given the seconds (bias v0 +31.4%, v1 +25.7%), where F1 is closer at 14 and 13 of 14 points (F1 13.5% rms).
- The one-shire points p107 and p095 draw 0.31 W and 0.42 W over idle (measured); MM1-v1 misses their J over idle given the seconds by +62% and +43%.

## 8. Arm A (aifoundry3) in this output: NO DATA

The scorer's output holds both arms, one arm a directory; it was run on this directory only, so every arm-A rule reads **NO DATA** (0 scored) in its printed lines above, and its 119 arm-A cells hold no measured value. Arm A ran on Mon 16 Nov 2026 on aifoundry3 card 0: its data are [`../2026-11-16-e206-matmul-sweep-aifoundry3/`](../2026-11-16-e206-matmul-sweep-aifoundry3/) (data commit `d7e4f35e`) and its scorer output and dated note were committed there in `50476f31`. So reading (d), card 1 over aifoundry3, is empty in both outputs; as `s24_score_e206.sh` says, "the records lane may score both directories together." This lane does not (section 10).

## 9. The findings, answered (dated clauses, Tue 17 Nov 2026, this lane)

1. **README.md's departure 10, on the box's python3 (the card lane's minor finding; verify-e206bd's finding 1).** It reads: "the box ran the session with its own `python3` (3.12.3 by ready-e206b's read-only look at 20:31:34 PST Mon; not re-read by this lane)". The last words are wrong: the card lane's own step 4 (its look at aifoundry1 at 00:01:03 PST Tue 17 Nov, after the booking and before the first card command) ran `python3 --version` there (the kit's box look, line 20) and it printed "Python 3.12.3". So the box's python3 was re-read by the card lane, and it read 3.12.3, the value the README gives. No number changes; README.md stays as committed, and this clause is the correction.
2. **verify-e206bd's finding 2: the scorer's outputs were not yet committed.** They are now, by this note's commit, byte for byte (sections 1 and 2), and its own code reproduces every rule, cell, measured value and summary in them (sections 3-5).
3. **verify-e206bd's finding 3: the tensor floor of reading (h).** Over all 113 points (post hoc: desk arithmetic of the measured cycles an op over the registered floor) the median is 2.507 (0.943-4.86): fp32 2.05 (50), fp16 2.05 (18), int8 3.55 (45). 6 points measure under the floor: p073 (`gemmc1`, int8, random) at 299.8 cycles an op, 0.943 of 318; and 5 fp32 resident points at 0.983-0.987 of 546 (p080 `gemmL1x1x1` zeros, p092 `gemmc1` zeros, p106 `gemmL1x1x1` random 0x1, p108 `gemmL1x1x1` random 0xff, p116 `gemmL1x1x1` sparse50). So beside the REPORTED reading: E101's resident "floor" is not a floor for `gemmc1` int8 on this card and build (p073 sits 5.7% under it), nor for the fp32 resident op (1.3-1.7% under), as arm A's note found on aifoundry3. The scorer is frozen and no reading changes; p073 is a law-arm point without simulator steps, so the scorer's own floor ratio (section 6 (h)) does not cover it.
4. **verify-e206bd's finding 4: the peak of the shires' mean.** README.md's "59.34 W at 00:46:08; 60 C at 01:33:38; 66 C / 66 C" gives the last of 40 samples at the peak of 60 C; the first was at 00:19:03 PST and the last at 01:33:38 (this lane's read of the committed `session/telemetry.jsonl.gz`: 50,820 samples, the shires' mean as the kit reads it, `temp_c.minshire[0]`). True but partial; README.md stays as committed.
5. **verify-e206bd's finding 5: the data commit's one link** is the round's standard commit trailer, not the card lane's words; nothing to change. This note carries no link outside the repository.
6. **The card lane's note on step 13's "LAB status after: 115 lines".** Those were another lane's new files, written at 01:43:10 PST under `tools/matmul/mm1/v2/` and committed by it as `3ca4b717`; none is read by the scorer, and the scorer's re-runs from a tree of the data commit alone give the same bytes (section 2).
7. **The card lane's two waits** (the model session claimed aifoundry1 again for its E208 card-1 session S3, so the rest was counted again from 22:27:12 PST Mon, README.md's departure 6; and the lab's quiet-desk flag on aifoundry2, raised for the model session's added E208 session on aifoundry2's own card, held the card lane's step 7 from 00:02:30 until 00:13:05 PST). Neither changes a datum: steps 7-9 then ran at 00:13:12-00:13:30, inside the window, and the session read 600 MHz in all 50,820 of its 50,820 samples.

## 10. Not done here

Not re-run by this lane (NOT RUN): the scorer's self-tests (they ran at step 3 with rc 0) and the kit's desk tests; verify-e206bd's code (its outputs read, not re-run): every MM1 figure in section 7 is its own. Nothing scored again: the re-runs in section 2 reproduce the registered output, byte for byte. Not done: reading (d), which needs both arms in one scoring; MM1's sensitivity to card 1's 0.499 V minion supply; the two sealed forecasts registered as arm B's freeze lines (by their sha256, under `tools/claims-v3/sealed-e206/`), which no lab rule scores.
