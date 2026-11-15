# E193 sitting B's data README, dated note 2 (Sun 15 Nov 2026): the registered reducer's and the kit's checker's outputs, run by step 13 on the data commit `96ef447c` at 12:20:54-55 PST, committed into this directory byte for byte with their printed lines; the measured, reduced prices; the data verifier's own re-derivation agrees; no reading changes

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `96ef447c`, and note 1's five files
([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and the four beside it, `3a4a53b8`), which stay as committed too. Written on
aifoundry2 from 13:28 PST on Sun 15 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no post), by Q182's lane
`reduce-e193`, after E193's data verifier `verify-e193d` (12:24-12:52 PST: holds with fixes; one minor finding and three nits, all records
lines, none in a datum, a price or a check) and note 1 (`fix-e193d`, git 13:11:55 PST), which answers those findings; this note does not
repeat them. The kit's step 13 runs only after the data commit and leaves its outputs to a later commit: KIT.md's table of steps (line 92)
gives "its outputs to RB_OUT, committed by the records lane", and its script
([`rb/s24_reduce_e193.sh`](../../../../tools/claims-v3/e193/rb/s24_reduce_e193.sh), lines 8-10) says "the records lane commits them beside
the data in a later commit". README.md says the same (lines 29-30, and its "Next", lines 195-198: "a later lane commits them beside this
directory, with this README's reduced prices in a dated note"), and note 1 names `x04-e193-B.json` and `checks-e193-B.json` as the files
the records lane commits into this directory after it. This lane is that later lane. This note commits both outputs byte for byte, with
the two programs' printed lines, states the measured, reduced prices and the checks' words as printed, and sets the data verifier's
figures beside them; E193.md 7 (line 233) lists these prices, per arm, per fit and per train, with their SEs and the checks of section 8,
as what E193 publishes. **No number, price, check, verdict or gate reading changes, and nothing is scored. The forecasts stay sealed: no
forecast number is here, and nothing here scores E193 against them; the model session scores them privately against these published
prices.** Interpreter: `/usr/bin/python3` 3.12.3 with the system's numpy 1.26.4, on aifoundry2. Labels: **registered** (E193.md and the
kit as committed), **measured** (the session's committed records, and the registered reducer's prices from them), **desk check of code**
(this lane's re-run and the verifier's figures).*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`x04-e193-B.json`](x04-e193-B.json) | the registered reducer's output ([`reduce_x04.py`](../../../../tools/claims-v3/e193/proposal/src/reduce_x04.py), registered in `b17d58a4` at `98bbc174...`, run unchanged; E193.md 7's `x04.json`, named `x04-e193-B.json` by step 13): 135 run records (passes 0-8, 15 a pass; pass 0, the registered warm-up, is in the file and in no mean), no trains (block C has none); the 14 arms' watts over idle on the board and the three rails with their denominators, the 3 fits, the rails' leakage slopes and the reducer's own check fields | 172,949 | `75c23d05...` |
| [`checks-e193-B.json`](checks-e193-B.json) | the kit's checker's output ([`check_e193.py`](../../../../tools/claims-v3/e193/check_e193.py) `checks`, kitted in `45d45c12` at `1351df2d...`): E193.md 8's nine checks (check 2 has two items), each with its verdict and numbers | 1,856 | `6fa307a9...` |
| [`x04-e193-B.txt`](x04-e193-B.txt) | the reducer's printed lines (18): step 13's copy of the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 1,132 | `87db2836...` |
| [`checks-e193-B.txt`](checks-e193-B.txt) | the checker's printed lines (11), copied byte for byte from the runbook's capture of that call | 391 | `c63ee5ba...` |
| `README.md.dated-note-2.md` | this note | | |

[`SHA256SUMS-note2`](SHA256SUMS-note2) pins these five and `SHA256SUMS-note1`. `SHA256SUMS-note1` pins `README.md`, `SHA256SUMS` and note
1's four files, and `SHA256SUMS` the 28 collected files, so every file here is pinned but `SHA256SUMS-note2` itself.

## 2. When, where and on which commit the reducer and the checker ran

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder
RB_OUT for this sitting, and from the lab clone's own log of its HEAD:

- **Step 13** ([`rb/s24_reduce_e193.sh`](../../../../tools/claims-v3/e193/rb/s24_reduce_e193.sh) `B`, the kit's, `35afddd7...` in
  `SHA256SUMS-e193-kit`): Sun 15 Nov 2026, **12:20:54-12:20:55 PST**, on aifoundry2, in the lab clone with its HEAD at **`96ef447c`**,
  this sitting's data commit (git 12:20:41 PST; the card lane's log has its commit script done, rc 0, at 12:20:44 PST), which stayed the
  clone's HEAD until the next commit, `e4c45385`, at 13:08:20 PST.
- **Its gates**, the log's lines 64-68, 12:20:54, each rc 0: the data directory committed (the call names `96ef447c` as the last commit
  touching it); the directory clean (no line); its `SHA256SUMS`, every entry (28 of 28 OK); the history check ("HISTORY OK": the
  registration `b17d58a4`, the kit `45d45c12`, nothing under `tools/claims-v3/e193` changed since); the reducer at its registered sha256
  (`98bbc174...`). The step then copied `x04/runs.jsonl` and unpacked `x04/telemetry.jsonl.gz` into RB_OUT and checked both against
  `session/MANIFEST.sha256` (the box's bytes); it stops with a gate exit otherwise, and its own line reads "x04/runs.jsonl and the
  unpacked x04/telemetry.jsonl equal the box's manifest's sha256".
- **The reducer**, line 69: `/usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py RB_OUT/e193-reduce-B/x04 --out
  RB_OUT/x04-e193-B.json`, rc 0 in 0.5 s, logged at 12:20:55 (the runner writes each line at the call's end). `x04-e193-B.json` was last
  written at 12:20:55.087, the runbook's capture of the reducer's printed lines at 12:20:55.109, and the step's copy of it,
  `x04-e193-B.txt`, at 12:20:55.125.
- **The checker**, line 70: `/usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks RB_OUT/x04-e193-B.json
  RB_OUT/e193-reduce-B/x04 --out RB_OUT/checks-e193-B.json`, rc 0 in 0.4 s, logged at 12:20:55; `checks-e193-B.json` was last written at
  12:20:55.528, its capture at 12:20:55.528. Line 70 is the log's last line (70 lines): nothing ran through the runbook in that folder
  after the checker.
- **The step's own last line**, which the card lane's log of the step holds after the captures: `[s24_reduce_e193] reduced sitting B:
  RB_OUT/x04-e193-B.json and checks-e193-B.json (CHECKS READ: 1 PASS, 2 PASS, 2 FAIL, 3 FLAGGED, 4 REPORTED, 5 REPORTED, 6 NOT COMPUTED, 7
  REPORTED, 8 REPORTED, 9 NOT COMPUTED); the records lane commits them beside the data`. `runbook.log` holds each call's line, not its
  output; the runbook's bounded runner (v3.1's `rb_run.py`, through the k6 runbook's `rb_common.sh`) writes each call's stdout and stderr,
  as they come, to that call's capture file, and the two printed-line files here are the step's sixth and seventh captures (the sixth
  through step 13's copy).
- **The inputs it read** (re-checked by this lane): the two files in RB_OUT are, byte for byte, this directory's `x04/runs.jsonl` (1,350
  launch records) and `x04/telemetry.jsonl.gz` unpacked (15,638 samples), as committed in `96ef447c`, and each equals its entry in
  `session/MANIFEST.sha256`.
- **The code as registered and kitted:** `reduce_x04.py` (`98bbc174...`, in `SHA256SUMS-e193-registration`), `check_e193.py`
  (`1351df2d...`), `rb/s24_reduce_e193.sh` (`35afddd7...`) and `rb/rb_e193.sh` (`0ca8b83f...`, all three in `SHA256SUMS-e193-kit`) are the
  same at the kit `45d45c12`, at both data commits and at LAB's HEAD as this note was written (`2d0fe517`): `tools/claims-v3/e193` is the
  tree `431bee42...` at all of them, and no commit since the kit touches it.
- **The interpreter:** `/usr/bin/python3` 3.12.3 on aifoundry2, isolated (`-I -B`), with the system's numpy 1.26.4 (the reducer imports
  numpy; the checker is standard library but for check 8, where it loads the registered reducer by path). E193.md 7 (line 231) and KIT.md
  (line 17) name the same interpreter and numpy for the desk, and README.md records the interpreter.
- **Re-run since, at the desk, on the committed bytes** (a desk check of code): by this lane at 13:20:53-13:20:55 PST (both sittings),
  from a fresh extract of `96ef447c`'s own tree (`tools/claims-v3/e193` and this directory, from git's objects), the input built as step
  13 builds it (2 of 2 against the manifest), run with the runbook's interpreter and flags, from the tree's top with the same paths and
  output names, in the round's CPU slot with no device node reachable: reducer rc 0 in 0.5 s, checker rc 0 in 0.4 s; `x04-e193-B.json` and
  `checks-e193-B.json` byte-equal, and each program's printed lines byte-equal to its capture. The runs wrote nothing into the extract.

## 3. The measured, reduced prices

From [`x04-e193-B.json`](x04-e193-B.json), generated from the file, not typed. **Measured:** the registered reducer's prices from the
session's committed records; watts over idle on the board meter (12 V input) with the lab's idle law taking out the warmer burst's extra
leakage, and the minion rail's fitted level over idle; mean ± SE over the 8 measured passes (1-8; pass 0, the registered warm-up, is in
the file and in no mean). The reducer's printed lines (`x04-e193-B.txt`) give the same figures to three places; the SRAM and NoC rails,
the electrons, and each run's own record are in the file.

**Records:** 135 runs (15 a pass), no trains, none dropped by a launch or by the clock (checks 4 and 5: 0 and 0); the dip rule dropped 5
board readings (check 8). Rails' leakage slopes, fitted to this session's idle windows: minion 0.0922, SRAM 0.0290, NoC 0.0393 W per C.

**The arms** (`x04-e193-B.json` > `arms`; pJ per worker minion-cycle = W over idle / worker minion-cycles a second):

| arm | n | board: W over idle | board: anchor-detrended | minion rail: W over idle | pJ per worker minion-cycle, board / minion rail | slots a hart-cycle |
|---|---|---|---|---|---|---|
| `spin2` | 16 | 2.518 ± 0.023 | 2.518 | 2.163 ± 0.008 | 4.246 / 3.648 | 0.3476 |
| `faddps_p1` | 8 | 8.785 ± 0.023 | 8.767 | 7.678 ± 0.013 | 14.816 / 12.947 | 0.3472 |
| `faddps_p2` | 8 | 6.200 ± 0.032 | 6.211 | 5.385 ± 0.013 | 10.457 / 9.081 | 0.3468 |
| `faddps_p4` | 8 | 4.261 ± 0.038 | 4.280 | 3.722 ± 0.012 | 7.185 / 6.276 | 0.3466 |
| `faddps_p8` | 8 | 3.081 ± 0.038 | 3.091 | 2.655 ± 0.011 | 5.196 / 4.477 | 0.3469 |
| `faddps_p16` | 8 | 2.401 ± 0.033 | 2.393 | 2.015 ± 0.013 | 4.049 / 3.399 | 0.3468 |
| `fadds_p16` | 8 | 2.372 ± 0.031 | 2.384 | 2.008 ± 0.012 | 3.999 / 3.386 | 0.3473 |
| `faddpsm1_p1` | 8 | 8.455 ± 0.023 | 8.466 | 7.388 ± 0.010 | 14.257 / 12.458 | 0.3472 |
| `faddpsm2_p1` | 8 | 8.508 ± 0.019 | 8.477 | 7.439 ± 0.015 | 14.347 / 12.545 | 0.3472 |
| `faddpsm4_p1` | 8 | 8.572 ± 0.034 | 8.572 | 7.519 ± 0.012 | 14.454 / 12.679 | 0.3472 |
| `fsgnjs_p1` | 8 | 4.625 ± 0.034 | 4.613 | 4.031 ± 0.011 | 7.800 / 6.797 | 0.3473 |
| `fsgnjs_p2` | 8 | 3.696 ± 0.035 | 3.707 | 3.180 ± 0.008 | 6.233 / 5.364 | 0.3473 |
| `fsgnjs_p4` | 8 | 2.902 ± 0.026 | 2.906 | 2.429 ± 0.006 | 4.893 / 4.095 | 0.3473 |
| `fsgnjs_p8` | 8 | 2.312 ± 0.016 | 2.317 | 1.925 ± 0.005 | 3.899 / 3.246 | 0.3472 |

**The fits** (`x04-e193-B.json` > `fits`; board W over idle; each a straight line by least squares through its points; the per-op prices are each arm's W over `spin2`'s, over its class ops a second):

| fit | through | x | slope | intercept | residuals, W |
|---|---|---|---|---|---|
| `ladder_faddps` | `faddps_p16`, `faddps_p8`, `faddps_p4`, `faddps_p2`, `faddps_p1` | class ops a second, 1e9: 25.70, 51.42, 102.78, 205.63, 411.81 | **16.305 pJ an op** | 2.3456 W | -0.3636, -0.1028, +0.2393, +0.5020, -0.2749 |
| `ladder_fsgnjs` | `fsgnjs_p8`, `fsgnjs_p4`, `fsgnjs_p2`, `fsgnjs_p1` | class ops a second, 1e9: 51.47, 102.98, 205.92, 411.90 | **6.178 pJ an op** | 2.1910 W | -0.1973, +0.0751, +0.2326, -0.1104 |
| `mask_lanes` | `faddpsm1_p1`, `faddpsm2_p1`, `faddpsm4_p1`, `faddps_p1` | lanes 1, 2, 4, 8 | **46.64 mW a lane** | 8.4051 W | +0.0031, +0.0098, -0.0201, +0.0072 |

**Per-op prices over `spin2`** (`fits` > `per_op_pj_board`, `per_op_pj_minion`; pJ an op, each arm against the same session's `spin2`):

| arm | board | minion rail |
|---|---|---|
| `faddps_p16` | -4.53 | -5.75 |
| `faddps_p8` | +10.96 | +9.56 |
| `faddps_p4` | +16.96 | +15.17 |
| `faddps_p2` | +17.91 | +15.67 |
| `faddps_p1` | +15.22 | +13.39 |
| `fsgnjs_p8` | -4.00 | -4.62 |
| `fsgnjs_p4` | +3.74 | +2.58 |
| `fsgnjs_p2` | +5.72 | +4.94 |
| `fsgnjs_p1` | +5.12 | +4.53 |

The two sparsest arms' per-op prices over `spin2` are negative, as computed: `spin2` sits above both class lines' intercepts. The lines'
slopes do not use `spin2`. Note 1 § 5 reads this, post hoc; nothing here changes it.

## 4. E193.md 8's checks, as the checker printed them

[`checks-e193-B.txt`](checks-e193-B.txt), verbatim:

```
check 1 spin2: PASS
check 2 faddps_p1: PASS
check 2 fsgnjs_p1: FAIL
check 3 anchor drift: FLAGGED
check 4 device ok: REPORTED
check 5 clock: REPORTED
check 6 duty linear: NOT COMPUTED
check 7 nulls: REPORTED
check 8 dip rule: REPORTED
check 9 stall2: NOT COMPUTED
CHECKS READ: 1 PASS, 2 PASS, 2 FAIL, 3 FLAGGED, 4 REPORTED, 5 REPORTED, 6 NOT COMPUTED, 7 REPORTED, 8 REPORTED, 9 NOT COMPUTED
```

Each check's numbers (`checks-e193-B.json` > `checks`):

| check | the numbers | verdict |
|---|---|---|
| 1 | `spin2` 2.5176 W against its catalogue row, 2.496 W scaled by 992/1024 = 2.4180 W (+4.1 %, inside the registered 15 %) | PASS |
| 2 | `faddps_p1` 8.7854 W against its catalogue row, 10.212 W scaled by 992/1024 = 9.8929 W (-11.2 %, inside the registered 15 %) | PASS |
| 2 | `fsgnjs_p1` 4.6253 W against its catalogue row, 6.122 W scaled by 992/1024 = 5.9307 W (-22.0 %, outside the registered 15 %) | FAIL |
| 3 | 2 of 8 pass/block boundaries above 0.1 W: 3/C, 8/C | FLAGGED |
| 4 | runs 135, trains 0; dropped by a launch not ok 0 | REPORTED |
| 5 | dropped by the clock 0 | REPORTED |
| 6 | the duty line needs three of its four arms (sitting A's arms; sitting A's note 2 gives it) | NOT COMPUTED |
| 7 | `fadds_p16 - faddps_p16` -0.0294 W, 95 % interval [-0.1189, +0.0601] W | REPORTED |
| 8 | 5 readings dropped (pass 2: 2, pass 7: 3; all in busy windows) of 12,115 window readings (busy 4,746, idle before 3,635, idle after 3,734) | REPORTED |
| 9 | needs spin2 and tr_tk_stall2 (sitting A); sitting A's note 2 gives it | NOT COMPUTED |

E193.md 8 (line 259): "Each check is reported PASS or FAIL (the nulls with their values and intervals) beside the prices; a failed check
removes no datum beyond the reducer's own run gates (4, 5, 8)." **Registered verdicts, unchanged.** The checker's line, as the step's last
line repeats it: `CHECKS READ: 1 PASS, 2 PASS, 2 FAIL, 3 FLAGGED, 4 REPORTED, 5 REPORTED, 6 NOT COMPUTED, 7 REPORTED, 8 REPORTED, 9 NOT
COMPUTED`.

## 5. Beside verify-e193d's independent re-derivation

`verify-e193d` (Sun 15 Nov 2026, 12:24-12:52 PST) re-derived the reduction from this directory's committed raw files, taken from
`96ef447c`, with its own code, written from E193.md 7 and the reducer's stated rules, importing nothing from the kit's reducer, runner or
checker (`/usr/bin/python3` 3.12.3, numpy 1.26.4), and check 8 with its own code too. Its figures are a desk check of code. It compared
its output with the same bytes as `x04-e193-B.json` (sha256 `75c23d05...`) field by field: **4,189 fields** (every run record, every arm
and fit, the rails' leakage slopes and the reducer's checks), **largest relative difference 5.1e-8**, every difference traced to the
reducer holding epoch seconds as float64 in each run's `wall_s`, and every check verdict the same. It also ran README.md's own re-make
commands from git's objects: `x04.json` and the printed lines came out byte-equal to step 13's. Each pair below is **the reducer /
verify-e193d**, generated from `x04-e193-B.json` and from the verifier's own output file (`mine-B-float.json`, sha256 `31c279b2...`, kept
outside the repository), not typed. Over the 318 numeric fields of the arms, the fits and the rails' leakage slopes that both files carry
(this lane's comparison), the largest relative difference is 2.6e-08 (`fits.ladder_faddps.residuals_w[1]`).

| arm or train | board: the reducer | board: verify-e193d | minion rail: the reducer | minion rail: verify-e193d |
|---|---|---|---|---|
| `spin2` | 2.517625 ± 0.023267 | 2.517625 ± 0.023267 | 2.162991 ± 0.007871 | 2.162991 ± 0.007871 |
| `faddps_p1` | 8.785437 ± 0.023415 | 8.785437 ± 0.023415 | 7.677596 ± 0.013186 | 7.677596 ± 0.013186 |
| `faddps_p2` | 6.200465 ± 0.031645 | 6.200465 ± 0.031645 | 5.384664 ± 0.013250 | 5.384664 ± 0.013250 |
| `faddps_p4` | 4.260818 ± 0.038077 | 4.260818 ± 0.038077 | 3.721895 ± 0.012257 | 3.721895 ± 0.012257 |
| `faddps_p8` | 3.081246 ± 0.037866 | 3.081246 ± 0.037866 | 2.654788 ± 0.011451 | 2.654788 ± 0.011451 |
| `faddps_p16` | 2.401104 ± 0.033320 | 2.401104 ± 0.033320 | 2.015149 ± 0.013037 | 2.015149 ± 0.013037 |
| `fadds_p16` | 2.371704 ± 0.031240 | 2.371704 ± 0.031240 | 2.007990 ± 0.012304 | 2.007990 ± 0.012304 |
| `faddpsm1_p1` | 8.454826 ± 0.023279 | 8.454826 ± 0.023279 | 7.387911 ± 0.009807 | 7.387911 ± 0.009807 |
| `faddpsm2_p1` | 8.508253 ± 0.018688 | 8.508253 ± 0.018688 | 7.439394 ± 0.014929 | 7.439394 ± 0.014929 |
| `faddpsm4_p1` | 8.571565 ± 0.033662 | 8.571565 ± 0.033662 | 7.519058 ± 0.011991 | 7.519058 ± 0.011991 |
| `fsgnjs_p1` | 4.625257 ± 0.034094 | 4.625257 ± 0.034094 | 4.030790 ± 0.011466 | 4.030790 ± 0.011466 |
| `fsgnjs_p2` | 3.695803 ± 0.035143 | 3.695803 ± 0.035143 | 3.180398 ± 0.007841 | 3.180398 ± 0.007841 |
| `fsgnjs_p4` | 2.902284 ± 0.026135 | 2.902284 ± 0.026135 | 2.428527 ± 0.005774 | 2.428527 ± 0.005774 |
| `fsgnjs_p8` | 2.311734 ± 0.015892 | 2.311734 ± 0.015892 | 1.925011 ± 0.005052 | 1.925011 ± 0.005052 |

| fit | the reducer: slope, intercept | verify-e193d: slope, intercept |
|---|---|---|
| `ladder_faddps` | 1.63052e-11 W, 2.34564 W | 1.63052e-11 W, 2.34564 W |
| `ladder_fsgnjs` | 6.17784e-12 W, 2.19103 W | 6.17784e-12 W, 2.19103 W |
| `mask_lanes` | 0.046636 W, 8.40514 W | 0.046636 W, 8.40514 W |
| `ladder_faddps`: per-op pJ over `spin2`, board | -4.534, 10.961, 16.960, 17.910, 15.220 | -4.534, 10.961, 16.960, 17.910, 15.220 |
| `ladder_fsgnjs`: per-op pJ over `spin2`, board | -4.000, 3.735, 5.722, 5.117 | -4.000, 3.735, 5.722, 5.117 |

The verifier's own checks, from its file: check 1 PASS (2.517625 W); check 2 `faddps_p1` PASS (8.785437 W), `fsgnjs_p1` FAIL (4.625257 W);
check 3 2 of 8 boundaries flagged; check 4 runs 135, dropped 0 and 0; check 7 `fadds_p16 - faddps_p16` -0.029400 W, [-0.118923,
+0.060122]; check 8 5 readings dropped. **Agree or differ: they agree.** Every figure above is the same to the places shown, and the
verdicts are the same: `CHECKS READ: 1 PASS, 2 PASS, 2 FAIL, 3 FLAGGED, 4 REPORTED, 5 REPORTED, 6 NOT COMPUTED, 7 REPORTED, 8 REPORTED, 9
NOT COMPUTED`.

## 6. Checks before the commit

- The four copied files as staged are byte-equal (`cmp`) to the card lane's RB_OUT files and to the runbook's captures of the two calls,
  and to this lane's re-run (§ 2).
- In a copy of this directory with the six new files: `SHA256SUMS` 28 of 28, `SHA256SUMS-note1` 6 of 6 and `SHA256SUMS-note2` 6 of 6
  entries OK; 41 files, every one in a list but `SHA256SUMS-note2`.
- The desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the round's folders forbidden) read the six new files with 0 hits,
  and a login check found no home path, no login, no e-mail address and no holder line in them or in this commit's subject and body.
- The public-text scan (the lab's `sanitize_extracts.py`, its fixed list and the box's local table, and the round's lists of private,
  vendor, process, access and mechanism words) found nothing in the six new files or in this commit's subject and body.

## Re-make it

From the top of the repository, nothing here opens a device; set R to an empty folder outside the repository (the first line), then run
the rest as they stand. They build step 13's input from this directory, run the registered reducer and the kit's checker with step 13's
output names, and compare the four copied files byte for byte (a re-run under `/usr/bin/python3` 3.12.3 with numpy 1.26.4 gives the same
bytes):

    D=docs/reports/data/2026-11-15-e193-x04-clock-sitting-b-aifoundry3; R=<an empty folder outside the repository>
    mkdir -p "$R/x04" && cp "$D/x04/runs.jsonl" "$R/x04/" && gzip -dc "$D/x04/telemetry.jsonl.gz" > "$R/x04/telemetry.jsonl"
    /usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py "$R/x04" --out "$R/x04-e193-B.json" > "$R/x04-e193-B.txt" 2>&1
    /usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks "$R/x04-e193-B.json" "$R/x04" --out "$R/checks-e193-B.json" > "$R/checks-e193-B.txt" 2>&1
    for f in x04-e193-B.json x04-e193-B.txt checks-e193-B.json checks-e193-B.txt; do cmp "$R/$f" "$D/$f" && echo "$f: the same bytes"; done
    (cd "$D" && sha256sum -c SHA256SUMS-note2 && sha256sum -c SHA256SUMS-note1 && sha256sum -c SHA256SUMS)

## Departure (dated Sun 15 Nov 2026)

No post in the lab's channel for this commit: the owner's standing waiver of the post, his words at 10:22:36 PST (note 1 of sitting A, §
1), stands, and this lane made none.

## What does not change

Every reading, verdict, gate, stop and figure of `README.md`, note 1 and their files stands; this note adds the reducer's and the
checker's outputs beside them and reads them, and changes nothing. The reducer and the checker read none of this note's files. This lane
reached no box, opened no device and changed no committed file. Sitting A's note 2 commits that sitting's outputs into its own directory
in the same commit.

SPDX-License-Identifier: Apache-2.0
