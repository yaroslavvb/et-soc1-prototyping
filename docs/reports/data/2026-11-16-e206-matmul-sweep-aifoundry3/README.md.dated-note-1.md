# E206 arm A's data README, dated note 1 (Mon 16 Nov 2026): the frozen scorer's output, run on the data commit `d7e4f35e`, committed beside it - R0 PASS; C1 FAIL, S1 FAIL, S6 PASS; F1: S2 FAIL, S3 FAIL, S4 PASS; F2: S2 FAIL, S3 FAIL, S4 FAIL; arm B NO DATA; the data verifier's own re-derivation gives the same words at every point

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `d7e4f35e`. Written on aifoundry2 from 18:56 PST on Mon 16 Nov 2026 (week 47) by the clock (built at 19:13:07 PST), desk only on aifoundry2 (no card, no call to another box, no device, no post), by Q198's lane `scores-e206`, after this directory's data verifier `verify-e206d` (18:32:53-18:55:17 PST: HOLDS). The kit's step 13 ([`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e206/CARD-LANE-BRIEF.md), its table of steps: "the frozen scorer: RB_OUT/scores-e206-<arm>.json and .txt (R0, C1, S1-S4, S6 per model and arm; the summaries; the readings); read its words; a later lane commits them beside the data"; [`rb/s24_score_e206.sh`](../../../../tools/claims-v3/e206/rb/s24_score_e206.sh): "a later lane (scores-e206) commits it beside the data. The other arm reads NO DATA in this output (one arm a directory); the records lane may score both directories together.") runs the frozen scorer only after the data commit and leaves its output to a later commit; [`DATA-README-FORM-e206.md`](../../../../tools/claims-v3/e206/DATA-README-FORM-e206.md) says "The scorer runs after the data commit (step 13): its words are not in this README at the commit; a later lane adds them in a dated note beside it.", and README.md says "the frozen scorer (step 13, `score_e206.py`) runs on this directory only after it is committed, and a later lane commits its words beside it." This lane is that later lane. This note commits the scorer's output byte for byte with its printed lines, sets the data verifier's figures beside the scorer's point by point, and answers the card lane's and the data verifier's findings in dated clauses (section 8). **No number, rule, verdict, forecast, band, threshold or gate reading changes, and nothing is scored again.** Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** ([`E206.md`](../../../../tools/claims-v3/e206/E206.md) with its amendment A1, and the kit, as committed), **measured** (the session's committed files), **desk check of code** (this lane's provenance check and re-run, the verifier's re-derivation), **REPORTED** (E206.md 7's summaries and readings: beside the rules, deciding nothing), **post hoc** (desk readings after the data). The verdicts are the frozen scorer's own output on the committed data. Every joule below is against the card's own meter, whose absolute scale is one fixed gain for every board (README.md, "The meter's absolute scale").*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`scores-e206-A.json`](scores-e206-A.json) | the frozen scorer's output ([`score_e206.py`](../../../../tools/claims-v3/e206/score_e206.py), registered in `eb2f7ac2` as amended before any datum (A1), unchanged since), copied byte for byte from the card lane's RB_OUT: the gate R0, the rules C1, S1, S2, S3, S4 and S6 per model and arm with their counts and verdicts; every point's measured values, errors, given values and words; the summaries; the readings (a)-(h) | 377,259 | `27630b04b65ded08bc9ef543da0f7ff880054c43d0c3c8ac997823ef107bad26` |
| [`scores-e206-A.txt`](scores-e206-A.txt) | the scorer's printed lines, as the step copied them from the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 963 | `d5bd8fb18966ae00983e9fd9b0aeda7e0c46089737ba9d9a87abd126cda5b80b` |
| `README.md.dated-note-1.md` | this note | | |

[`SHA256SUMS-note1`](SHA256SUMS-note1) pins these three and `README.md` and `SHA256SUMS` at their committed bytes. With `SHA256SUMS` (1,246 files, unchanged), every file here is pinned but `SHA256SUMS-note1` itself. The arm is named in the file names as step 13 named them (`scores-e206-<arm>`), and the scorer's output holds both arms (section 7).

## 2. When, where and on which commit the scorer ran

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder RB_OUT, and from the lab clone's own log of its HEAD (a desk check of code: this lane's provenance check, 45 checks, all OK):

- **Step 13** ([`rb/s24_score_e206.sh`](../../../../tools/claims-v3/e206/rb/s24_score_e206.sh) `A`, the kit's): Mon 16 Nov 2026 at **18:26:32 PST**, on aifoundry2, in the lab clone with its HEAD at **`d7e4f35e`**, the data commit (made at 18:26:14 PST and pushed by 18:26:19, the card lane's log), which is still the clone's HEAD, with nothing moved since, as this note is built.
- **Its gates**, the log's lines 97-100, at 18:26:32 PST, each with rc 0: the data directory committed (the last commit naming it: `d7e4f35e E206 arm A data: the matmul sweep on aifoundry3 card 0 at 600 MHz, RAN FULL - 241 of 241 runs, 88.9 card-minutes, reads only, before any score (Q198)`); the directory clean (no line); `SHA256SUMS` 1,246 of 1,246 entries OK; the history check: `HISTORY OK: HEAD descends from the registration eb2f7ac2f732 (subtree 114c094b); 46 additions and nothing else under tools/claims-v3/e206 since it; no shadowing addition under tools/ (sys.stdlib_module_names); E206's run paths clean`
- **The scorer**, the log's line 101 (its last of 101): `/usr/bin/python3 -I -B tools/claims-v3/e206/score_e206.py docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/data-e206.json --out RB_OUT/scores-e206-A.json`, rc 0 in 0.1 s. `scores-e206-A.json` was last written at 18:26:32.425 PST, inside that call (after the previous call's capture closed at 18:26:32.280, before this call's closed at 18:26:32.426); the step then copied this call's capture, the scorer's printed lines, to `scores-e206-A.txt` (18:26:32.437), and its own line reads "[s24_score_e206] scored arm A: RB_OUT/scores-e206-A.json and .txt (the scorer's printed words; a later lane commits them beside the data)".
- **No other run on data:** the log holds no earlier run of the scorer on data; its two self-tests (`--selftest-standins`, `--selftest-e190`) ran at step 3, at 16:51:46 PST, each with rc 0 (lines 23 and 24).
- **The frozen files:** `score_e206.py` at the data commit is E206.md 0's registered scorer (sha256 `65bd65fc79471c0f14b00e65476dd3b38070ca5ab113b11e93d7c677580ac1ac`); its `FORECAST_SHA256`, the sha256 of `forecast-e206.json` at the data commit and the output's own `forecast_sha256` are one value (`d8f3a8b1e3d22f515581aab1a9cc43ca30fbb6e1c61c96d7cc14bf32697bd888`), and the scorer refuses to run on any other forecast. The registration list's 25 files and the list, the forecast's 26 inputs (each at the sha256 the forecast records) and the kit list's 44 files and the list (the step's own scripts among them) are one git blob each at the registration `eb2f7ac2`, the kit `906699ea` (the kit list from there), the data commit and HEAD; both lists read OK in the lab clone. The scorer read `data-e206.json` at the data commit (sha256 `3fefd637c1d2ec8dad4712e1c3421e0ce5f62274b2fbe2c532134a559ece3318`), the file the data verifier scored.
- **Re-runs (desk checks of code):** this lane ran the frozen scorer again on the committed data, as step 13 ran it (in the lab clone's clean tree at `d7e4f35e`, one CPU slot, no device node reachable, nothing written into the clone), at 19:04:04 PST: both files came out byte for byte equal to RB_OUT. The data verifier's own re-run (its step 10, by 18:53:23 PST) also gave both files byte for byte.

## 3. The rules' words and verdicts (registered rules; the frozen scorer's output)

The scorer's printed lines, as committed in `scores-e206-A.txt`:

```
R0 PASS 
C1.A FAIL 66/119
S1.A FAIL 70/119
S6.A PASS 119/119
S2.F1.A FAIL 17/119
S3.F1.A FAIL 41/119
S4.F1.A PASS 112/119
S2.F2.A FAIL 3/115
S3.F2.A FAIL 14/115
S4.F2.A FAIL 4/115
C1.B NO DATA 0/0
S1.B NO DATA 0/0
S6.B NO DATA 0/0
S2.F1.B NO DATA 0/0
S3.F1.B NO DATA 0/0
S4.F1.B NO DATA 0/0
S2.F2.B NO DATA 0/0
S3.F2.B NO DATA 0/0
S4.F2.B NO DATA 0/0
A.all cycles_per_op rms 0.176 bias -0.085 (n 119); cycles_per_op_P0 rms 0.173 bias -0.075 (n 119); t rms 0.156 bias -0.052 (n 119); cycles_gemm rms 0.156 bias -0.053 (n 119); F1.j_over_given rms 0.258 bias +0.209 (n 119); F1.j_over_forecast rms 0.228 bias +0.156 (n 119); F1.j_rest_given rms 0.083 bias +0.068 (n 119); F1.j_rest_forecast rms 0.143 bias +0.057 (n 119); F2.j_over_given rms 0.515 bias -0.149 (n 115); F2.j_over_forecast rms 0.515 bias -0.149 (n 115); F2.j_rest_given rms 0.163 bias -0.061 (n 115); F2.j_rest_forecast rms 0.223 bias -0.052 (n 115); P0.j_over_forecast rms 0.165 bias +0.075 (n 119)
```

| rule (E206.md 7) | what | registered threshold | the scorer, arm A | verify-e206d's own scoring | points from a flip (verify-e206d) | arm B |
|---|---|---|---|---|---|---|
| R0 | the ties: every check of C exact or approx (the smoke and every run: every point run, counted or not, and every tie run, A1); the smoke's cycles an op 50-250% of F1's point | one verdict; a FAIL labels every other verdict | **PASS** (244 checks, 0 wrong) | PASS (244 checks, 0 wrong) | - | (one verdict for the day) |
| C1 | cycles (the counter): the point's cycles an op inside F1's band | per point | **FAIL** 66 of 119 | FAIL 66 of 119 | 42 | NO DATA (0 scored) |
| S1 | seconds: the point's t_gemm inside F1's band | per point | **FAIL** 70 of 119 | FAIL 70 of 119 | 38 | NO DATA (0 scored) |
| S2 F1 | J over idle, given the measured seconds: \|measured / given - 1\|, F1 | <= 10% | **FAIL** 17 of 119 | FAIL 17 of 119 | 91 | NO DATA (0 scored) |
| S3 F1 | J with the card at rest, given the measured seconds and rest: \|measured / given - 1\|, F1 | <= 5% | **FAIL** 41 of 119 | FAIL 41 of 119 | 67 | NO DATA (0 scored) |
| S4 F1 | J over idle, the whole forecast (seconds forecast): the measured value inside F1's band | per point | **PASS** 112 of 119 | PASS 112 of 119 | 5 | NO DATA (0 scored) |
| S2 F2 | the same as S2, F2 (its four sparse50 points NOT PRICED, not scored) | <= 10% | **FAIL** 3 of 115 | FAIL 3 of 115 | 101 | NO DATA (0 scored) |
| S3 F2 | the same as S3, F2 | <= 5% | **FAIL** 14 of 115 | FAIL 14 of 115 | 90 | NO DATA (0 scored) |
| S4 F2 | the same as S4, F2's band | per point | **FAIL** 4 of 115 | FAIL 4 of 115 | 100 | NO DATA (0 scored) |
| S6 | the clock: every counted sample in 590-610 MHz (the lowest and the highest counted sample, A1) | per point | **PASS** 119 of 119 | PASS 119 of 119 | 12 | NO DATA (0 scored) |

A rule's verdict per model and arm (registered): PASS if at least 90% of its scored points pass, FAIL otherwise; TOO FEW under 10 scored points; NO DATA with none. A point with no run is NO DATA, never a failure; no run was set aside (the output's `set_aside` is empty).

- **R0 in detail** (measured): 244 checks of C - the smoke's 3, the 238 point runs' and the 3 tie runs' - 0 wrong; the smoke's cycles an op p001 1,121.824 (0.826 of F1's 1,357.99), p046 819.198 (0.819 of F1's 999.67), p021 787.540 (1.103 of F1's 713.85), each inside 50-250%.
- **Margins** (verify-e206d, desk check of code; the column above): a verdict flips only when that many points change their word. Every FAIL needs at least 38 more passing points (S1 38, C1 42); S4 F1 would flip if 5 of its passing points failed, S6 if 12 did.
- **verify-e206d's alternative readings** (REPORTED, never a verdict): with p_work the median over the whole counted span and p_rest the median of the whole 10 s rest, every count is unchanged but S4 F1's, which reads 113 of 119 (still PASS).

## 4. The summaries (REPORTED): rms / mean of ln(measured / forecast), arm A

Each cell is rms / bias (the mean) of ln(measured / forecast) over the points, with the number of points; a negative bias means the model forecast more than the card measured. By format (the scorer's groups):

| quantity | all | fp32 | fp16 | int8 |
|---|---|---|---|---|
| cycles an op (the counter) against F1 | 0.176 / -0.085 (119) | 0.170 / -0.119 (53) | 0.149 / -0.118 (21) | 0.193 / -0.031 (45) |
| cycles an op against P0 | 0.173 / -0.075 (119) | 0.158 / -0.087 (53) | 0.118 / -0.059 (21) | 0.208 / -0.069 (45) |
| cycles a GEMM (the slowest minion) against F1 | 0.156 / -0.053 (119) | 0.144 / -0.091 (53) | 0.124 / -0.087 (21) | 0.180 / +0.007 (45) |
| seconds a GEMM against F1 | 0.156 / -0.052 (119) | 0.144 / -0.090 (53) | 0.123 / -0.086 (21) | 0.181 / +0.008 (45) |
| F1, J over idle, given the measured seconds | 0.258 / +0.209 (119) | 0.230 / +0.169 (53) | 0.243 / +0.227 (21) | 0.294 / +0.247 (45) |
| F1, J over idle, seconds forecast | 0.228 / +0.156 (119) | 0.175 / +0.079 (53) | 0.176 / +0.141 (21) | 0.296 / +0.254 (45) |
| F1, J with the card at rest, given | 0.083 / +0.068 (119) | 0.088 / +0.070 (53) | 0.102 / +0.094 (21) | 0.063 / +0.053 (45) |
| F1, J with the card at rest, forecast | 0.143 / +0.057 (119) | 0.104 / +0.019 (53) | 0.100 / +0.047 (21) | 0.191 / +0.108 (45) |
| F2, J over idle, given | 0.515 / -0.149 (115) | 0.492 / -0.192 (51) | 0.379 / -0.150 (21) | 0.593 / -0.098 (43) |
| F2, J over idle, forecast | 0.515 / -0.149 (115) | 0.492 / -0.191 (51) | 0.379 / -0.150 (21) | 0.593 / -0.097 (43) |
| F2, J with the card at rest, given | 0.163 / -0.061 (115) | 0.168 / -0.074 (51) | 0.153 / -0.052 (21) | 0.163 / -0.049 (43) |
| F2, J with the card at rest, forecast | 0.223 / -0.052 (115) | 0.211 / -0.088 (51) | 0.184 / -0.068 (21) | 0.252 / -0.001 (43) |
| P0, J over idle, forecast | 0.165 / +0.075 (119) | 0.142 / +0.049 (53) | 0.151 / +0.093 (21) | 0.195 / +0.096 (45) |

By regime, family and data kind (the four quantities the rules lean on most; every quantity of every group is in the JSON):

| group | points | cycles an op (F1) | seconds (F1) | F1 J over idle, given | F2 J over idle, given |
|---|---|---|---|---|---|
| all | 119 | 0.176 / -0.085 | 0.156 / -0.052 | 0.258 / +0.209 | 0.515 / -0.149 (115) |
| regime L2-resident | 18 | 0.198 / +0.104 | 0.200 / +0.108 | 0.170 / +0.086 | 0.429 / +0.370 (16) |
| regime L3-served | 30 | 0.184 / -0.136 | 0.122 / -0.034 | 0.302 / +0.278 | 0.381 / +0.325 (29) |
| regime all fresh | 18 | 0.201 / -0.172 | 0.198 / -0.169 | 0.242 / +0.155 | 0.921 / -0.871 (18) |
| regime mixed | 53 | 0.151 / -0.092 | 0.138 / -0.077 | 0.262 / +0.229 | 0.395 / -0.323 (52) |
| family anchor | 9 | 0.068 / -0.034 | 0.018 / +0.012 | 0.226 / +0.219 | 0.454 / +0.031 (9) |
| family extreme | 13 | 0.170 / -0.078 | 0.170 / -0.067 | 0.253 / +0.237 | 0.381 / -0.338 (13) |
| family kinds | 10 | 0.191 / +0.022 | 0.204 / +0.058 | 0.193 / +0.168 | 0.372 / +0.243 (6) |
| family kladder | 15 | 0.209 / -0.146 | 0.170 / -0.095 | 0.279 / +0.266 | 0.564 / -0.063 (15) |
| family square | 14 | 0.147 / -0.116 | 0.130 / -0.091 | 0.262 / +0.253 | 0.352 / -0.224 (14) |
| family star | 28 | 0.168 / -0.133 | 0.141 / -0.093 | 0.280 / +0.268 | 0.422 / -0.130 (28) |
| family subset | 16 | 0.205 / -0.017 | 0.171 / +0.017 | 0.326 / +0.255 | 0.373 / +0.070 (16) |
| family zeros | 14 | 0.180 / -0.089 | 0.167 / -0.073 | 0.134 / -0.073 | 0.934 / -0.563 (14) |
| kind random | 95 | 0.173 / -0.096 | 0.148 / -0.061 | 0.277 / +0.254 | 0.429 / -0.113 (95) |
| kind real | 6 | 0.184 / -0.000 | 0.189 / +0.039 | 0.218 / +0.196 | 0.372 / +0.243 (6) |
| kind sparse50 | 4 | 0.202 / +0.056 | 0.226 / +0.088 | 0.149 / +0.126 | not priced |
| kind zeros | 14 | 0.180 / -0.089 | 0.167 / -0.073 | 0.134 / -0.073 | 0.934 / -0.563 (14) |

verify-e206d's own code gives the same value for every one of the 256 summary entries (rms and bias: 0 difference, desk check of code).

## 5. Point by point: the scorer's words, and verify-e206d's beside them

Measured values (the scorer's, from the committed `data-e206.json`) beside F1's frozen points; the words are the scorer's per point and rule (C1, S1, S6; S2, S3, S4 for F1 and for F2; NOT PRICED: F2 has no price for the sparse50 kind). The last column sets verify-e206d's re-derivation beside them: its own words for the same nine rules, and the largest relative difference of its measured values (cycles an op and a GEMM, seconds, J over idle and with the card at rest, the board W at work and at rest) from the scorer's.

| point | shape: M x N x K (shires) | format, kind | family; regime | cycles an op: measured / F1 | ms a GEMM: measured / F1 | mJ over idle: measured / F1 forecast | C1, S1, S6 | F1: S2, S3, S4 | F2: S2, S3, S4 | verify-e206d |
|---|---|---|---|---|---|---|---|---|---|---|
| p001 | gemmL2x4x4: 2,048 x 2,048 x 2,048 | fp32, random | star; mixed | 1,121.4 / 1,358.0 | 3.832 / 4.635 | 76.09 / 69.77 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p002 | gemmL2x4x4: 2,048 x 2,048 x 8,192 | int8, random | star; mixed | 1,136.8 / 1,361.7 | 3.884 / 4.648 | 36.61 / 31.53 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p003 | gemmL2x4x4: 2,048 x 2,048 x 4,096 | fp16, random | star; mixed | 1,121.3 / 1,356.7 | 3.831 / 4.631 | 70.80 / 62.87 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p004 | gemmL1x4x4: 1,024 x 2,048 x 2,048 | fp32, random | star; L3-served | 831.8 / 1,041.8 | 1.555 / 1.778 | 38.75 / 33.81 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p005 | gemmL1x4x4: 1,024 x 2,048 x 8,192 | int8, random | star; L3-served | 866.2 / 1,084.4 | 1.657 / 1.851 | 17.45 / 13.00 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p006 | gemmL4x4x4: 4,096 x 2,048 x 2,048 | fp32, random | star; mixed | 1,121.2 / 1,358.0 | 7.661 / 9.271 | 152.3 / 139.5 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p007 | gemmL4x4x4: 4,096 x 2,048 x 8,192 | int8, random | star; mixed | 1,137.0 / 1,361.7 | 7.770 / 9.296 | 72.88 / 63.07 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p008 | gemmL8x4x4: 8,192 x 2,048 x 2,048 | fp32, random | star; mixed | 1,121.2 / 1,358.0 | 15.33 / 18.54 | 302.7 / 279.1 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p009 | gemmL8x4x4: 8,192 x 2,048 x 8,192 | int8, random | star; mixed | 1,136.9 / 1,361.7 | 15.54 / 18.59 | 146.6 / 126.1 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p010 | gemmL8x4x4: 8,192 x 2,048 x 4,096 | fp16, random | star; mixed | 1,121.4 / 1,356.7 | 15.32 / 18.52 | 284.5 / 251.5 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p011 | gemmL2x1x4: 2,048 x 512 x 2,048 | fp32, random | star; L3-served | 831.7 / 1,041.8 | 0.7775 / 0.8890 | 19.45 / 16.91 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p012 | gemmL2x1x4: 2,048 x 512 x 8,192 | int8, random | star; L3-served | 866.0 / 1,084.4 | 0.8283 / 0.9253 | 8.732 / 6.501 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p013 | gemmL2x2x4: 2,048 x 1,024 x 2,048 | fp32, random | star; L3-served | 831.8 / 1,041.8 | 1.555 / 1.778 | 38.90 / 33.81 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p014 | gemmL2x2x4: 2,048 x 1,024 x 8,192 | int8, random | star; L3-served | 866.2 / 1,084.4 | 1.657 / 1.851 | 17.47 / 13.00 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p015 | gemmL2x8x4: 2,048 x 4,096 x 2,048 | fp32, random | star; mixed | 1,374.6 / 1,358.6 | 9.409 / 9.274 | 159.3 / 139.5 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p016 | gemmL2x8x4: 2,048 x 4,096 x 8,192 | int8, random | star; mixed | 1,361.3 / 1,362.2 | 9.305 / 9.299 | 80.76 / 63.09 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p017 | gemmL2x16x4: 2,048 x 8,192 x 2,048 | fp32, random | star; mixed | 1,375.0 / 1,341.0 | 18.93 / 18.31 | 320.2 / 278.4 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p018 | gemmL2x16x4: 2,048 x 8,192 x 8,192 | int8, random | star; mixed | 1,368.4 / 1,346.8 | 18.84 / 18.39 | 164.9 / 124.9 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p019 | gemmL2x16x4: 2,048 x 8,192 x 4,096 | fp16, random | star; mixed | 1,375.7 / 1,339.7 | 18.92 / 18.29 | 301.0 / 250.6 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p020 | gemmL2x4x1: 2,048 x 2,048 x 512 | fp32, random | star; L3-served | 760.1 / 817.1 | 0.7317 / 0.6972 | 18.84 / 14.82 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p021 | gemmL2x4x1: 2,048 x 2,048 x 2,048 | int8, random | star; L3-served | 787.5 / 713.8 | 0.7564 / 0.6091 | 7.499 / 5.070 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p022 | gemmL2x4x2: 2,048 x 2,048 x 1,024 | fp32, random | star; L3-served | 819.2 / 1,000.9 | 1.545 / 1.708 | 38.91 / 33.06 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p023 | gemmL2x4x2: 2,048 x 2,048 x 4,096 | int8, random | star; L3-served | 854.1 / 1,017.0 | 1.644 / 1.736 | 17.19 / 12.48 | FAIL, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p024 | gemmL2x4x8: 2,048 x 2,048 x 4,096 | fp32, random | star; mixed | 1,434.7 / 1,446.1 | 9.804 / 9.872 | 162.1 / 141.3 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p025 | gemmL2x4x8: 2,048 x 2,048 x 16,384 | int8, random | star; mixed | 1,437.5 / 1,439.0 | 9.824 / 9.824 | 83.56 / 66.18 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p026 | gemmL2x4x16: 2,048 x 2,048 x 8,192 | fp32, random | star; all fresh | 1,521.9 / 1,886.5 | 20.80 / 25.76 | 324.0 / 303.6 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p027 | gemmL2x4x16: 2,048 x 2,048 x 32,768 | int8, random | star; all fresh | 1,529.7 / 1,825.3 | 20.90 / 24.92 | 171.7 / 163.7 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p028 | gemmL2x4x16: 2,048 x 2,048 x 16,384 | fp16, random | star; all fresh | 1,521.7 / 1,885.3 | 20.79 / 25.74 | 301.8 / 282.3 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p029 | gemmL1x1x1: 1,024 x 512 x 512 | fp32, random | kladder; L2-resident | 538.0 / 551.5 | 0.05758 / 0.05882 | 1.951 / 1.544 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p030 | gemmL1x1x1: 1,024 x 512 x 2,048 | int8, random | kladder; L2-resident | 388.0 / 275.9 | 0.04161 / 0.02943 | 0.6146 / 0.4222 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p031 | gemmL1x1x1: 1,024 x 512 x 1,024 | fp16, random | kladder; L2-resident | 538.0 / 551.1 | 0.05758 / 0.05878 | 1.783 / 1.471 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p032 | gemmL1x1x2: 1,024 x 512 x 1,024 | fp32, random | kladder; L3-served | 805.9 / 960.1 | 0.1919 / 0.2048 | 4.852 / 4.037 | FAIL, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p033 | gemmL1x1x2: 1,024 x 512 x 4,096 | int8, random | kladder; L3-served | 844.9 / 949.6 | 0.2037 / 0.2026 | 2.070 / 1.495 | FAIL, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p034 | gemmL1x1x4: 1,024 x 512 x 2,048 | fp32, random | kladder; L3-served | 831.7 / 1,041.8 | 0.3888 / 0.4445 | 9.689 / 8.453 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p035 | gemmL1x1x4: 1,024 x 512 x 8,192 | int8, random | kladder; L3-served | 866.0 / 1,084.4 | 0.4141 / 0.4627 | 4.350 / 3.251 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p036 | gemmL1x1x4: 1,024 x 512 x 4,096 | fp16, random | kladder; L3-served | 831.7 / 1,040.4 | 0.3888 / 0.4439 | 9.035 / 7.434 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p037 | gemmL1x1x8: 1,024 x 512 x 4,096 | fp32, random | kladder; L3-served | 831.1 / 1,041.8 | 0.7771 / 0.8890 | 19.32 / 16.91 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p038 | gemmL1x1x8: 1,024 x 512 x 16,384 | int8, random | kladder; L3-served | 866.3 / 1,084.4 | 0.8280 / 0.9253 | 8.644 / 6.501 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p039 | gemmL1x1x16: 1,024 x 512 x 8,192 | fp32, random | kladder; all fresh | 1,395.1 / 1,886.5 | 2.403 / 3.220 | 38.66 / 37.95 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p040 | gemmL1x1x16: 1,024 x 512 x 32,768 | int8, random | kladder; all fresh | 1,426.6 / 1,825.3 | 2.474 / 3.115 | 19.59 / 20.47 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p041 | gemmL1x1x32: 1,024 x 512 x 16,384 | fp32, random | kladder; all fresh | 1,579.2 / 1,886.5 | 5.393 / 6.439 | 82.16 / 75.89 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p042 | gemmL1x1x32: 1,024 x 512 x 65,536 | int8, random | kladder; all fresh | 1,546.3 / 1,825.3 | 5.281 / 6.230 | 44.02 / 40.94 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p043 | gemmL1x1x32: 1,024 x 512 x 32,768 | fp16, random | kladder; all fresh | 1,580.2 / 1,885.3 | 5.391 / 6.435 | 77.07 / 70.58 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p044 | gemmL1x2x2: 1,024 x 1,024 x 1,024 | fp32, random | square; L3-served | 819.3 / 1,000.9 | 0.3864 / 0.4271 | 9.735 / 8.264 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p045 | gemmL1x2x1: 1,024 x 1,024 x 1,024 | fp16, random | square; L3-served | 744.6 / 795.8 | 0.1796 / 0.1698 | 4.315 / 3.330 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p046 | gemmL2x4x2: 2,048 x 2,048 x 2,048 | fp16, random | square; L3-served | 819.2 / 999.7 | 1.545 / 1.706 | 36.14 / 29.22 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p047 | gemmL3x6x6: 3,072 x 3,072 x 3,072 | fp32, random | square; mixed | 1,150.5 / 1,370.3 | 13.27 / 15.79 | 255.5 / 235.9 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p048 | gemmL3x6x3: 3,072 x 3,072 x 3,072 | fp16, random | square; mixed | 1,117.5 / 1,369.0 | 6.443 / 7.885 | 120.9 / 106.4 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p049 | gemmL4x8x8: 4,096 x 4,096 x 4,096 | fp32, random | square; mixed | 1,418.3 / 1,419.7 | 38.77 / 38.77 | 637.5 / 562.9 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p050 | gemmL4x8x4: 4,096 x 4,096 x 4,096 | fp16, random | square; mixed | 1,376.4 / 1,357.3 | 18.83 / 18.53 | 300.5 / 251.5 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p051 | gemmL4x8x2: 4,096 x 4,096 x 4,096 | int8, random | square; mixed | 1,110.6 / 1,294.8 | 7.588 / 8.839 | 73.43 / 60.94 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p052 | gemmL6x12x12: 6,144 x 6,144 x 6,144 | fp32, random | square; mixed | 1,435.7 / 1,604.9 | 132.5 / 147.9 | 2,160 / 1,955 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p053 | gemmL6x12x6: 6,144 x 6,144 x 6,144 | fp16, random | square; mixed | 1,229.5 / 1,345.5 | 56.81 / 62.00 | 986.8 / 846.8 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p054 | gemmL6x12x3: 6,144 x 6,144 x 6,144 | int8, random | square; mixed | 1,129.5 / 1,351.9 | 26.05 / 31.15 | 252.4 / 211.5 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p055 | gemmL8x16x16: 8,192 x 8,192 x 8,192 | fp32, random | square; all fresh | 1,450.1 / 1,886.5 | 317.3 / 412.1 | 5,141 / 4,857 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p056 | gemmL8x16x8: 8,192 x 8,192 x 8,192 | fp16, random | square; mixed | 1,388.7 / 1,405.1 | 152.5 / 153.5 | 2,406 / 2,032 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p057 | gemmL8x16x4: 8,192 x 8,192 x 8,192 | int8, random | square; mixed | 1,368.6 / 1,346.8 | 75.32 / 73.55 | 656.4 / 499.7 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p058 | gemmL8x1x4: 8,192 x 512 x 2,048 | fp32, random | extreme; mixed | 1,407.4 / 1,323.4 | 4.859 / 4.517 | 79.18 / 69.45 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p059 | gemmL8x1x4: 8,192 x 512 x 8,192 | int8, random | extreme; mixed | 1,448.3 / 1,331.3 | 5.026 / 4.544 | 40.82 / 30.92 | FAIL, FAIL, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p060 | gemmL1x16x4: 1,024 x 8,192 x 2,048 | fp32, random | extreme; mixed | 1,368.4 / 1,323.4 | 9.454 / 9.034 | 159.6 / 138.9 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p061 | gemmL1x16x4: 1,024 x 8,192 x 8,192 | int8, random | extreme; mixed | 1,365.2 / 1,331.3 | 9.427 / 9.089 | 81.49 / 61.84 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p062 | gemmL1x15x4: 1,024 x 7,680 x 2,048 | fp32, random | extreme; mixed | 1,082.1 / 1,323.4 | 7.019 / 8.469 | 144.3 / 130.2 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p063 | gemmL1x15x4: 1,024 x 7,680 x 8,192 | int8, random | extreme; mixed | 1,093.5 / 1,331.3 | 7.097 / 8.521 | 69.23 / 57.98 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p064 | gemmL8x16x1: 8,192 x 8,192 x 512 | fp32, random | extreme; mixed | 1,141.6 / 1,100.9 | 15.94 / 15.03 | 309.9 / 241.9 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p065 | gemmL8x16x1: 8,192 x 8,192 x 2,048 | int8, random | extreme; mixed | 1,166.3 / 951.0 | 16.28 / 12.98 | 149.6 / 99.50 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p066 | gemmL8x1x16: 8,192 x 512 x 8,192 | fp32, random | extreme; all fresh | 1,395.5 / 1,886.5 | 19.23 / 25.76 | 309.0 / 303.6 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p067 | gemmL1x16x16: 1,024 x 8,192 x 8,192 | fp32, random | extreme; all fresh | 1,436.8 / 1,886.5 | 39.27 / 51.51 | 640.0 / 607.2 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p068 | gemmL3x5x7: 3,072 x 2,560 x 3,584 | fp32, random | extreme; mixed | 1,173.4 / 1,379.7 | 13.15 / 15.45 | 253.1 / 229.6 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p069 | gemmL3x5x7: 3,072 x 2,560 x 7,168 | fp16, random | extreme; mixed | 1,173.7 / 1,378.4 | 13.16 / 15.44 | 234.2 / 207.2 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p070 | gemmL3x5x7: 3,072 x 2,560 x 14,336 | int8, random | extreme; mixed | 1,179.5 / 1,380.7 | 13.23 / 15.46 | 122.7 / 104.7 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p071 | gemmc1: 1,024 x 512 x 512 | fp32, random | anchor; L2-resident | 536.9 / 538.0 | 0.05745 / 0.05739 | 1.933 / 1.506 | PASS, PASS, PASS | FAIL, FAIL, FAIL | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p072 | gemmc1: 1,024 x 512 x 1,024 | fp16, random | anchor; L2-resident | 536.9 / 538.1 | 0.05745 / 0.05739 | 1.760 / 1.437 | PASS, PASS, PASS | FAIL, FAIL, FAIL | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p073 | gemmc1: 1,024 x 512 x 2,048 | int8, random | anchor; L2-resident | 299.8 / 291.8 | 0.03218 / 0.03112 | 0.5997 / 0.4464 | PASS, FAIL, PASS | FAIL, FAIL, FAIL | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p074 | gemmc8s: 8,192 x 512 x 512 | fp32, random | anchor; L3-served | 753.9 / 856.9 | 0.7338 / 0.7313 | 19.39 / 15.02 | FAIL, PASS, PASS | FAIL, FAIL, FAIL | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p075 | gemmc8s: 8,192 x 512 x 1,024 | fp16, random | anchor; L3-served | 753.9 / 856.7 | 0.7338 / 0.7310 | 17.92 / 13.51 | FAIL, PASS, PASS | FAIL, FAIL, FAIL | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p076 | gemmc8s: 8,192 x 512 x 2,048 | int8, random | anchor; L3-served | 786.4 / 861.7 | 0.7653 / 0.7353 | 7.972 / 5.774 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p077 | gemmc16s: 16,384 x 512 x 512 | fp32, random | anchor; all fresh | 1,410.8 / 1,406.4 | 2.410 / 2.400 | 38.26 / 32.30 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p078 | gemmc16s: 16,384 x 512 x 1,024 | fp16, random | anchor; all fresh | 1,410.8 / 1,406.6 | 2.410 / 2.401 | 36.03 / 30.23 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p079 | gemmc16s: 16,384 x 512 x 2,048 | int8, random | anchor; all fresh | 1,403.9 / 1,384.0 | 2.398 / 2.362 | 18.95 / 16.68 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p080 | gemmL1x1x1: 1,024 x 512 x 512 | fp32, zeros | zeros; L2-resident | 538.0 / 551.5 | 0.05758 / 0.05882 | 0.2361 / 0.2783 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p081 | gemmL1x1x1: 1,024 x 512 x 2,048 | int8, zeros | zeros; L2-resident | 388.0 / 275.9 | 0.04161 / 0.02943 | 0.1785 / 0.1373 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p082 | gemmL1x1x4: 1,024 x 512 x 2,048 | fp32, zeros | zeros; L3-served | 831.7 / 1,041.8 | 0.3887 / 0.4445 | 1.707 / 1.952 | FAIL, FAIL, PASS | PASS, PASS, PASS | PASS, PASS, PASS | same 9 of 9; 0 |
| p083 | gemmL1x1x4: 1,024 x 512 x 4,096 | fp16, zeros | zeros; L3-served | 831.7 / 1,040.4 | 0.3888 / 0.4439 | 1.677 / 1.834 | FAIL, FAIL, PASS | PASS, PASS, PASS | FAIL, PASS, PASS | same 9 of 9; 0 |
| p084 | gemmL1x1x32: 1,024 x 512 x 16,384 | fp32, zeros | zeros; all fresh | 1,576.2 / 1,886.5 | 5.386 / 6.439 | 21.29 / 30.99 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p085 | gemmL1x1x32: 1,024 x 512 x 65,536 | int8, zeros | zeros; all fresh | 1,545.4 / 1,825.3 | 5.282 / 6.230 | 20.05 / 23.33 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p086 | gemmL2x4x4: 2,048 x 2,048 x 2,048 | fp32, zeros | zeros; mixed | 1,121.4 / 1,358.0 | 3.832 / 4.635 | 16.19 / 21.42 | FAIL, FAIL, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p087 | gemmL2x4x4: 2,048 x 2,048 x 4,096 | fp16, zeros | zeros; mixed | 1,121.2 / 1,356.7 | 3.831 / 4.631 | 16.25 / 19.73 | FAIL, FAIL, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p088 | gemmL2x4x4: 2,048 x 2,048 x 8,192 | int8, zeros | zeros; mixed | 1,136.9 / 1,361.7 | 3.884 / 4.648 | 14.49 / 15.98 | FAIL, FAIL, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p089 | gemmL8x16x16: 8,192 x 8,192 x 8,192 | fp32, zeros | zeros; all fresh | 1,450.5 / 1,886.5 | 317.3 / 412.1 | 1,272 / 1,983 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p090 | gemmL8x16x4: 8,192 x 8,192 x 8,192 | int8, zeros | zeros; mixed | 1,368.8 / 1,346.8 | 75.36 / 73.55 | 281.8 / 251.8 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p091 | gemmL8x16x1: 8,192 x 8,192 x 512 | fp32, zeros | zeros; mixed | 1,141.4 / 1,100.9 | 15.94 / 15.03 | 71.09 / 71.18 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p092 | gemmc1: 1,024 x 512 x 512 | fp32, zeros | zeros; L2-resident | 536.9 / 538.0 | 0.05745 / 0.05739 | 0.2216 / 0.2715 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p093 | gemmc16s: 16,384 x 512 x 512 | fp32, zeros | zeros; all fresh | 1,410.9 / 1,406.4 | 2.410 / 2.400 | 8.682 / 11.53 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p094 | gemmL4x8x4: 512 x 1,024 x 2,048 (1 shire, 0x1) | fp32, random | subset; L3-served | 1,215.4 / 1,041.8 | 16.61 / 14.22 | 11.79 / 8.453 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p095 | gemmL4x8x4: 512 x 1,024 x 8,192 (1 shire, 0x1) | int8, random | subset; L3-served | 1,258.8 / 1,084.4 | 17.20 / 14.81 | 7.138 / 3.251 | PASS, PASS, PASS | FAIL, PASS, FAIL | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p096 | gemmL4x8x4: 512 x 4,096 x 2,048 (4 shires, 0xf) | fp32, random | subset; mixed | 1,003.0 / 1,358.6 | 16.63 / 18.55 | 45.65 / 34.89 | FAIL, FAIL, PASS | FAIL, PASS, PASS | PASS, PASS, PASS | same 9 of 9; 0 |
| p097 | gemmL4x8x4: 512 x 4,096 x 8,192 (4 shires, 0xf) | int8, random | subset; mixed | 1,037.1 / 1,362.2 | 17.20 / 18.60 | 24.26 / 15.77 | FAIL, FAIL, PASS | FAIL, PASS, FAIL | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p098 | gemmL4x8x4: 1,024 x 4,096 x 2,048 (8 shires, 0xff) | fp32, random | subset; mixed | 1,037.4 / 1,358.6 | 15.16 / 18.55 | 82.09 / 69.77 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p099 | gemmL4x8x4: 1,024 x 4,096 x 8,192 (8 shires, 0xff) | int8, random | subset; mixed | 1,074.2 / 1,362.2 | 15.80 / 18.60 | 44.78 / 31.54 | FAIL, FAIL, PASS | FAIL, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p100 | gemmL4x8x4: 4,096 x 1,024 x 2,048 (8 shires, 0x11111111) | fp32, random | subset; mixed | 1,231.9 / 1,077.0 | 16.83 / 14.70 | 75.67 / 67.75 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p101 | gemmL4x8x4: 4,096 x 1,024 x 8,192 (8 shires, 0x11111111) | int8, random | subset; mixed | 1,226.6 / 1,115.2 | 16.76 / 15.23 | 39.77 / 26.61 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p102 | gemmL4x8x4: 2,048 x 4,096 x 2,048 (16 shires, 0xffff) | fp32, random | subset; mixed | 1,123.5 / 1,358.6 | 15.35 / 18.55 | 154.0 / 139.5 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p103 | gemmL4x8x4: 2,048 x 4,096 x 8,192 (16 shires, 0xffff) | int8, random | subset; mixed | 1,136.3 / 1,362.2 | 15.53 / 18.60 | 80.01 / 63.09 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p104 | gemmL4x8x4: 4,096 x 4,096 x 2,048 | fp32, random | subset; mixed | 1,375.6 / 1,358.6 | 18.83 / 18.55 | 316.0 / 279.1 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p105 | gemmL4x8x4: 4,096 x 4,096 x 8,192 | int8, random | subset; mixed | 1,359.3 / 1,362.2 | 18.58 / 18.60 | 162.3 / 126.2 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p106 | gemmL1x1x1: 128 x 128 x 512 (1 shire, 0x1) | fp32, random | subset; L2-resident | 538.8 / 551.5 | 0.05752 / 0.05882 | 0.05206 / 0.04825 | PASS, PASS, PASS | FAIL, PASS, PASS | PASS, PASS, PASS | same 9 of 9; 0 |
| p107 | gemmL1x1x1: 128 x 128 x 2,048 (1 shire, 0x1) | int8, random | subset; L2-resident | 389.3 / 275.9 | 0.04155 / 0.02943 | 0.01756 / 0.01319 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p108 | gemmL1x1x1: 256 x 512 x 512 (8 shires, 0xff) | fp32, random | subset; L2-resident | 538.0 / 551.5 | 0.05753 / 0.05882 | 0.4421 / 0.3860 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p109 | gemmL1x1x1: 256 x 512 x 2,048 (8 shires, 0xff) | int8, random | subset; L2-resident | 388.0 / 275.9 | 0.04159 / 0.02943 | 0.1427 / 0.1055 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, PASS, FAIL | same 9 of 9; 0 |
| p110 | gemmL1x1x1: 1,024 x 512 x 512 | fp32, real | kinds; L2-resident | 538.0 / 551.5 | 0.05758 / 0.05882 | 1.923 / 1.537 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p111 | gemmL2x4x4: 2,048 x 2,048 x 2,048 | fp32, real | kinds; mixed | 1,121.4 / 1,358.0 | 3.832 / 4.635 | 74.24 / 69.51 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p112 | gemmL1x1x1: 1,024 x 512 x 1,024 | fp16, real | kinds; L2-resident | 538.0 / 551.1 | 0.05758 / 0.05878 | 1.756 / 1.450 | PASS, PASS, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p113 | gemmL2x4x2: 2,048 x 2,048 x 2,048 | fp16, real | kinds; L3-served | 819.2 / 999.7 | 1.545 / 1.706 | 35.16 / 28.84 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p114 | gemmL1x1x1: 1,024 x 512 x 2,048 | int8, real | kinds; L2-resident | 388.0 / 275.9 | 0.04161 / 0.02943 | 0.5170 / 0.3629 | PASS, PASS, PASS | PASS, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p115 | gemmL2x4x1: 2,048 x 2,048 x 2,048 | int8, real | kinds; L3-served | 787.5 / 713.8 | 0.7564 / 0.6091 | 6.456 / 4.442 | PASS, PASS, PASS | FAIL, PASS, PASS | FAIL, FAIL, FAIL | same 9 of 9; 0 |
| p116 | gemmL1x1x1: 1,024 x 512 x 512 | fp32, sparse50 | kinds; L2-resident | 538.0 / 551.5 | 0.05758 / 0.05882 | 0.8768 / 0.7649 | PASS, PASS, PASS | FAIL, FAIL, PASS | NOT PRICED | same 9 of 9; 0 |
| p117 | gemmL2x4x4: 2,048 x 2,048 x 2,048 | fp32, sparse50 | kinds; mixed | 1,121.5 / 1,358.0 | 3.831 / 4.635 | 41.45 / 41.52 | FAIL, FAIL, PASS | FAIL, FAIL, PASS | NOT PRICED | same 9 of 9; 0 |
| p118 | gemmL1x1x1: 1,024 x 512 x 2,048 | int8, sparse50 | kinds; L2-resident | 388.0 / 275.9 | 0.04161 / 0.02943 | 0.5118 / 0.3664 | PASS, PASS, PASS | PASS, PASS, PASS | NOT PRICED | same 9 of 9; 0 |
| p119 | gemmL2x4x1: 2,048 x 2,048 x 2,048 | int8, sparse50 | kinds; L3-served | 787.5 / 713.8 | 0.7564 / 0.6091 | 6.239 / 4.246 | PASS, PASS, PASS | FAIL, PASS, PASS | NOT PRICED | same 9 of 9; 0 |

Counts over the table: C1 66 PASS / 53 FAIL; S1 70 / 49; S6 119 / 0; F1 S2 17 / 102, S3 41 / 78, S4 112 / 7; F2 S2 3 / 112, S3 14 / 101, S4 4 / 111, and 4 NOT PRICED. Each count equals its rule's in section 3. verify-e206d (desk check of code, its own code from the committed raw files, nothing imported from the kit): the same nine words at 119 of 119 points, 0 relative difference in every measured value, and F2's given values tied to the frozen F2 at all 115 priced points to 0.

## 6. The readings (REPORTED: registered before the data, never verdicts)

- **(a) Contention** (cycles an op against shires; F1 holds each subset at its own lines' time), measured / F1:

| shape, format | 1 shire | 4 | 8 | 8 (0x11111111) | 16 | 32 |
|---|---|---|---|---|---|---|
| gemmL4x8x4, fp32 | 1,215.4 / 1,041.8 (p094) | 1,003.0 / 1,358.6 (p096) | 1,037.4 / 1,358.6 (p098) | 1,231.9 / 1,077.0 (p100) | 1,123.5 / 1,358.6 (p102) | 1,375.6 / 1,358.6 (p104) |
| gemmL4x8x4, int8 | 1,258.8 / 1,084.4 (p095) | 1,037.1 / 1,362.2 (p097) | 1,074.2 / 1,362.2 (p099) | 1,226.6 / 1,115.2 (p101) | 1,136.3 / 1,362.2 (p103) | 1,359.3 / 1,362.2 (p105) |
| gemmL1x1x1, fp32 | 538.8 / 551.5 (p106) | - | 538.0 / 551.5 (p108) | - | - | 538.0 / 551.5 (p029) |
| gemmL1x1x1, int8 | 389.3 / 275.9 (p107) | - | 388.0 / 275.9 (p109) | - | - | 388.0 / 275.9 (p030) |

- **(b) The stride step** (`gemmL1x16x4` over `gemmL1x15x4`, cycles an op): fp32 1.2646, int8 1.2484 (the reference: "E169: +27-30% at its power-of-two step").
- **(c) The zeros gap** (zeros over random at the same shape and format), 14 pairs: J over idle gemmL1x1x1 fp32 0.121; gemmL1x1x1 int8 0.290; gemmL1x1x32 fp32 0.259; gemmL1x1x32 int8 0.455; gemmL1x1x4 fp16 0.186; gemmL1x1x4 fp32 0.176; gemmL2x4x4 fp16 0.230; gemmL2x4x4 fp32 0.213; gemmL2x4x4 int8 0.396; gemmL8x16x1 fp32 0.229; gemmL8x16x16 fp32 0.247; gemmL8x16x4 int8 0.429; gemmc1 fp32 0.115; gemmc16s fp32 0.227; seconds 0.9987-1.0005 (zeros change the joules, not the time).
- **(d) Card 1 over aifoundry3:** no value (arm B did not run, section 7).
- **(e) `gemmL1x1x1` against `gemmc1`** (the same work through two loop codes, cycles an op): fp32 1.0021, fp16 1.0021, int8 1.2945.
- **(f) The tie's drift** (p001 at runs 1, 121 and 241): seconds 3.8314 / 3.8310 / 3.8309 ms; the board at work 43.69 / 43.99 / 44.75 W; J over idle 75.25 / 75.89 / 76.35 mJ (+1.46% first to last).
- **(g) P0's error:** in the summaries (section 4).
- **(h) The timing simulation against the card** (his question: "See check how well the timing simulation for the matte mold matches reality and the energy."). The scorer gives two ratios per point, in the JSON: the measured cycles a GEMM over the simulator's instruction count a minion a GEMM (the step law of E206.md 7 (h): the simulator counts instructions, not cycles), and the measured cycles an op over the tensor unit's resident floor (546 cycles an op in fp32 and fp16, 318 in int8: E101's resident loop on aifoundry3). Both exist at the 108 points with simulator steps (not at the 11 law-arm points p071, p072, p073, p074, p075, p076, p077, p078, p079, p092, p093). Over those 108 points (desk arithmetic over the scorer's values, post hoc: the scorer prints no median): cycles a GEMM over the simulator's steps, median **24.05** (8.22-33.87); cycles an op over the tensor floor, median **2.49** (0.985-4.86). Sections 8.1 and 8.2 add to this reading.

## 7. Arm B (aifoundry1 card 1): NO DATA

The scorer's output holds both arms, one arm a directory; it was run on this directory only, so every arm-B rule reads **NO DATA** (0 scored) in its printed lines above, and its 113 arm-B cells hold no measured value. Arm B did not run: its card lane read the round's queue at 16:46:55 and 16:47:34 PST as cancelled by the orchestrator (aifoundry1 yielded at 11:04:17 PST Mon 16 Nov to the model session's matmul sweeps) and returned SKIPPED: no booking, no call to aifoundry1, no device opened, no session (0 card-minutes), no data, no data directory. As registered (E206.md 6): "**Arm B runs only if aifoundry1 comes back to the lab before its window closes; otherwise its points are NO DATA**, every rule that needs them reads NO DATA (never a failure), and E206 is arm A alone." and "if it does not, E206 says nothing about card 1" (E206.md 8). **No arm-B data directory exists, so this note is E206's only scores note and records arm B here;** if arm B runs on a later day under a new card lane, its own directory takes its own scorer output and note.

## 8. The findings, answered (dated clauses, Mon 16 Nov 2026, this lane)

1. **verify-e206d's finding 1 (low): reading (h)'s medians in the card lane's result** (a file outside the repository; README.md carries none of these figures). Its "median 24.1" and "median 2.51" are each the 55th of the 108 sorted values (24.098 and 2.506), not the median. The true medians are **24.05** (8.22-33.87) and **2.49** (0.985-4.86), over the same 108 points (this lane's desk arithmetic over the committed output; verify-e206d's figures are the same). Its die-gate waits "1-14 s" were 0.5-14 s: 181 runs waited 0 s and 60 waited 0.5-14 s (the committed `session/runs/*/run.json`), each under the registered 300 s. The round's records use these figures.
2. **verify-e206d's finding 2 (post hoc, reading h): the tensor floor read over all 119 points, and the resident op under it.** The scorer gives the floor ratio only where simulator steps exist; over all 119 points the measured cycles an op over the floor have median **2.48** (0.943-4.86): fp32 2.05 (53), fp16 2.05 (21), int8 3.55 (45). 12 points measure under the registered floor, all at the resident shapes (`gemmc1` and `gemmL1x1x1`, fp32 and fp16, and `gemmc1` int8, subsets included): `gemmc1` fp32 536.86 cycles an op (0.983 of 546), fp16 536.87 (0.983), int8 299.75 (0.943 of 318); `gemmL1x1x1` fp32 537.98 (0.985). So on this card and build the measured resident op sits below E101's "floor": the 12 points at 0.943-0.987 of it (1.3-5.7% below; verify-e206d's three named points 0.943-0.985, 1.5-5.7%): it is not a floor here. The scorer is frozen and no reading changes; a later matmul model's tensor term takes this.
3. **verify-e206d's finding 3 (nit): the peak die time.** README.md's "61 C at 18:10:25" is the last of 32 samples at the peak; the first was at 17:16:39 PST (this lane's read of the committed `session/telemetry.jsonl.gz`: 53,265 samples, the shires' mean as the kit reads it, `temp_c.minshire[0]`). True but partial; README.md stays as committed.
4. **The never-run reading (card-e206a's medium finding; verify-e206d's finding 4).** README.md's REPORTED post hoc reading, "75 of 119 never run on any card (95 registered; the 20 more are all that dry pass's commands)", counts as runs the records of the model session's dry pass at 15:40 PST, which verify-e206d inspected: a dry queue on a fake device folder, no device opened. Read without them, **95 of 119 points never ran on any card and 108 never on aifoundry3, as registered** (E206.md 1 and 4), in every folder searched; aifoundry1's folders were not searched (the gap registered in E206.md 4). A REPORTED reading: it changes no rule. For later re-runs, the scanner should skip dry and stand-in record trees (a question for the round, not for this directory).
5. **verify-e206d's finding 5 (outside E206).** It concerns another session's card session on aifoundry2's own card, not E206. card-e206a's steps 12 and 13 ran on aifoundry2 in that span as desk steps (git, the reducer, the frozen scorer), none of which opens a device. Nothing here changes; it is left to the round's own record.
6. **verify-e206d's finding 6 and card-e206a's low finding: a desk-rule slip.** The card lane ran one foreground wait of 1 s in a desk call (about 16:53:42 PST), against the round's own desk rule; it held nothing and touched no datum.
7. **card-e206a's note finding** restates the verdicts: they are the scorer's words in section 3, unchanged.

## 9. Not done here

Not re-run by this lane (NOT RUN): the scorer's self-tests (they ran at step 3 with rc 0) and the kit's desk tests; verify-e206d's code (its outputs read, not re-run). Nothing scored again: the re-run in section 2 reproduces the registered output, byte for byte. Arm B: no data to score. MM1-v0's blind score on these data is not part of this note.
